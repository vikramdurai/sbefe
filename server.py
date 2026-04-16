"""
Sburb RPG Multiplayer Server

FastAPI server providing REST API and WebSocket endpoints for multiplayer sessions.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import asyncio
from datetime import datetime

from config import SERVER_HOST, SERVER_PORT, FRONTEND_URL
from session_manager import SessionManager, SessionState, PlayerInfo
from websocket_manager import ConnectionManager, MessageType
from game_manager import GameManager


# Initialize FastAPI app
app = FastAPI(title="Sburb RPG Multiplayer Server", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
session_manager = SessionManager()
connection_manager = ConnectionManager()


# Pydantic models for API requests/responses
class CreateSessionResponse(BaseModel):
    session_code: str
    created_at: str


class JoinSessionRequest(BaseModel):
    player_name: str
    username: str
    password: str
    player_class: str
    aspect: str
    title: str
    land: str
    denizen: str
    echeladder_rung: str
    strife_specibus: str
    current_weapon: str
    sprite: str
    character_data: Optional[dict] = None


class JoinSessionResponse(BaseModel):
    player_id: str
    player_name: str
    player_color: str
    session_code: str


class PlayerStatus(BaseModel):
    player_id: str
    name: str
    color: str
    connected: bool
    ready: bool


class SessionStatusResponse(BaseModel):
    session_code: str
    state: str
    players: List[PlayerStatus]
    created_at: str
    started_at: Optional[str]


class SetReadyRequest(BaseModel):
    ready: bool


# REST API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Sburb RPG Multiplayer Server"}


@app.post("/api/sessions", response_model=CreateSessionResponse)
async def create_session():
    """Create a new game session"""
    session = session_manager.create_session()
    
    return CreateSessionResponse(
        session_code=session.code,
        created_at=session.created_at.isoformat()
    )


@app.post("/api/sessions/{session_code}/join", response_model=JoinSessionResponse)
async def join_session(session_code: str, request: JoinSessionRequest):
    """Join an existing session"""
    try:
        # Generate unique player ID
        import uuid
        player_id = str(uuid.uuid4())[:8]
        
        player = session_manager.join_session(
            session_code.upper(),
            player_id,
            request.player_name,
            username=request.username,
            password=request.password,
            player_class=request.player_class,
            aspect=request.aspect,
            title=request.title,
            land=request.land,
            denizen=request.denizen,
            echeladder_rung=request.echeladder_rung,
            strife_specibus=request.strife_specibus,
            current_weapon=request.current_weapon,
            sprite=request.sprite,
            character_data=request.character_data
        )
        
        return JoinSessionResponse(
            player_id=player.player_id,
            player_name=player.name,
            player_color=player.character_color,
            session_code=session_code.upper()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class RejoinSessionRequest(BaseModel):
    username: str
    password: str


class RejoinSessionResponse(BaseModel):
    player_id: str
    player_name: str
    player_color: str
    session_code: str
    session_state: str


@app.post("/api/sessions/{session_code}/rejoin", response_model=RejoinSessionResponse)
async def rejoin_session(session_code: str, request: RejoinSessionRequest):
    """Rejoin an existing session using stored username and password credentials."""
    try:
        player = session_manager.rejoin_session(
            session_code.upper(),
            request.username,
            request.password,
        )
        session = session_manager.get_session(session_code.upper())
        return RejoinSessionResponse(
            player_id=player.player_id,
            player_name=player.name,
            player_color=player.character_color,
            session_code=session_code.upper(),
            session_state=session.state.value,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/sessions/{session_code}/status", response_model=SessionStatusResponse)
async def get_session_status(session_code: str):
    """Get current session status and player list"""
    session = session_manager.get_session(session_code.upper())
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get connected players
    connected_players = connection_manager.get_connected_players(session_code.upper())
    
    players = [
        PlayerStatus(
            player_id=p.player_id,
            name=p.name,
            color=p.character_color,
            connected=p.player_id in connected_players,
            ready=p.ready
        )
        for p in session.players.values()
    ]
    
    return SessionStatusResponse(
        session_code=session.code,
        state=session.state.value,
        players=players,
        created_at=session.created_at.isoformat(),
        started_at=session.started_at.isoformat() if session.started_at else None
    )


@app.post("/api/sessions/{session_code}/players/{player_id}/ready")
async def set_player_ready(session_code: str, player_id: str, request: SetReadyRequest):
    """Mark player as ready to start"""
    session = session_manager.get_session(session_code.upper())
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.set_player_ready(player_id, request.ready)
    session.save_metadata()
    
    # Notify all players of ready status change
    await connection_manager.broadcast_to_session(
        session_code.upper(),
        {
            "type": "player_ready_status",
            "player_id": player_id,
            "ready": request.ready,
            "all_ready": session.all_players_ready()
        }
    )
    
    return {"success": True}


@app.post("/api/sessions/{session_code}/start")
async def start_session(session_code: str):
    """Start the game session"""
    session = session_manager.get_session(session_code.upper())
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        await asyncio.to_thread(session.start_session)
        session.save_metadata()
        
        # Notify all players that session has started
        await connection_manager.broadcast_to_session(
            session_code.upper(),
            {
                "type": "session_started",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return {"success": True, "message": "Session started"}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# WebSocket Endpoint

def get_party_members(session, player_id: str) -> set[str]:
    """Party formation rules: same location or same explicit party_id."""
    actor = session.get_player(player_id)
    if not actor:
        return {player_id}

    members = {player_id}
    for other in session.players.values():
        if other.player_id == player_id:
            continue
        same_location = bool(actor.current_location and actor.current_location == other.current_location)
        same_party_id = bool(actor.party_id and actor.party_id == other.party_id)
        if same_location or same_party_id:
            members.add(other.player_id)

    return members

@app.websocket("/ws/{session_code}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, session_code: str, player_id: str):
    """WebSocket connection for real-time communication"""
    session_code = session_code.upper()
    session = session_manager.get_session(session_code)
    
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return
    
    player = session.get_player(player_id)
    if not player:
        await websocket.close(code=4004, reason="Player not found")
        return
    
    # Accept connection
    await connection_manager.connect(websocket, session_code, player_id)
    player.connected = True

    if session.state == SessionState.ACTIVE:
        actions = session.get_player_action_set(player_id)
        await connection_manager.send_action_buttons_update(session_code, player_id, actions)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == MessageType.PLAYER_ACTION.value:
                # Player submitted an action
                await handle_player_action(session_code, player_id, data)
            
            elif message_type == MessageType.STAGING_UPDATE.value:
                # Player is drafting an action (staging window)
                await handle_staging_update(session_code, player_id, data)
            
            elif message_type == MessageType.PESTERLOG_MESSAGE.value:
                # Player sent a pesterlog message
                await handle_pesterlog_message(session_code, player_id, player, data)
            
            else:
                await connection_manager.send_error(
                    session_code,
                    player_id,
                    f"Unknown message type: {message_type}"
                )
    
    except WebSocketDisconnect:
        pending_draft = session.staging_drafts.get(player_id, "").strip() if session else ""
        if pending_draft:
            await handle_player_action(session_code, player_id, {"action": pending_draft})
        connection_manager.disconnect(session_code, player_id)
        player.connected = False
        
        # Notify others of disconnection
        await connection_manager.broadcast_to_session(
            session_code,
            {
                "type": MessageType.CONNECTION_STATUS.value,
                "player_id": player_id,
                "connected": False,
                "timestamp": datetime.now().isoformat()
            },
            exclude_player=player_id
        )


async def handle_player_action(session_code: str, player_id: str, data: dict):
    """Handle player action submission"""
    session = session_manager.get_session(session_code)
    player_input = data.get("action", "")
    player = session.get_player(player_id) if session else None

    if not session or not session.game_manager:
        await connection_manager.send_error(
            session_code,
            player_id,
            "Session not started yet. Please wait for all players to be ready."
        )
        return

    action_type = data.get("action_type")
    action_target = data.get("target")
    action_label = data.get("label")
    if action_type and action_target:
        player_input = player_input or f"{action_label or action_target}"

        if action_type == "combat":
            player.current_context = "combat"
        elif action_type == "dialogue":
            player.current_context = "dialogue"
        elif action_type == "alchemy":
            player.current_context = "alchemy"
        elif action_type in {"navigate", "examine"}:
            player.current_context = "navigation"

        if action_type == "navigate":
            player.current_location = f"{player.land}:{action_target}"
        session.save_metadata()

    normalized_input = player_input.strip().lower()
    if normalized_input.startswith("join "):
        target_name = normalized_input.split("join ", 1)[-1].strip()
        target = next((p for p in session.players.values() if p.name.lower() == target_name), None)
        if target:
            party_id = f"party:{'_'.join(sorted([player.name.lower(), target.name.lower()]))}"
            player.party_id = party_id
            target.party_id = party_id
            session.save_metadata()

    if player_input and not action_type:
        available_actions = session.get_player_action_set(player_id)
        labels = {a.get("label", "").strip().lower() for a in available_actions}
        if player_input.strip().lower() not in labels:
            custom_action = {
                "label": f"Repeat: {player_input.strip()[:28]}",
                "action_type": "custom",
                "target": "freeform_cached",
                "icon": "[+]",
                "tooltip": "Recently used freeform action.",
            }
            existing = session.dynamic_action_cache.get(player_id, [])
            if all(a.get("label") != custom_action["label"] for a in existing):
                session.dynamic_action_cache[player_id] = [custom_action] + existing[:4]

    scene_pesterlog = session.get_recent_scene_pesterlog_context(player_id, limit=14)
    if scene_pesterlog:
        player_input = (
            f"{player_input}\n\n"
            f"### RECENT PESTERLOG CONVERSATION\n"
            f"{scene_pesterlog}\n"
            f"The GM should be aware of this context when narrating this shared scene."
        )

    try:
        # Run the blocking Gemini call in a thread pool so the event loop stays free.
        # wait_for enforces a hard 45 s deadline — surfaces the error fast if the
        # API is rate-limited or down instead of hanging indefinitely.
        narrative, updates_count = await asyncio.wait_for(
            asyncio.to_thread(session.game_manager.process_turn, player_input, player),
            timeout=360.0
        )

        actions = session.get_player_action_set(player_id)
        await connection_manager.send_gm_response_stream(
            session_code,
            player_id,
            narrative,
            updates_count,
            actions=actions,
        )

    except asyncio.TimeoutError:
        await connection_manager.send_error(
            session_code,
            player_id,
            "GM timed out. The AI API may be slow or rate-limited. Try again shortly."
        )
    except Exception as e:
        msg = str(e)
        if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
            hint = "API quota exhausted. Set a different GEMINI_MODEL in .env or wait for the quota to reset."
        else:
            hint = f"Error processing action: {msg[:300]}"
        await connection_manager.send_error(session_code, player_id, hint)


async def handle_staging_update(session_code: str, player_id: str, data: dict):
    """Handle staging window draft update"""
    session = session_manager.get_session(session_code)
    draft_text = data.get("draft", "")
    
    # Store draft in session
    session.staging_drafts[player_id] = draft_text

    party_members = get_party_members(session, player_id)
    active = len(party_members) > 1
    
    # Send staging update to party members
    await connection_manager.send_staging_update(
        session_code,
        player_id,
        draft_text,
        party_members
    )

    reason = "same location or party id" if active else "solo play"
    for member_id in party_members:
        await connection_manager.send_party_status(
            session_code,
            member_id,
            active=active,
            party_members=sorted(list(party_members)),
            reason=reason,
        )


async def handle_pesterlog_message(session_code: str, player_id: str, player: 'PlayerInfo', data: dict):
    """Handle pesterlog chat message"""
    message_text = data.get("message", "")
    session = session_manager.get_session(session_code)
    if session:
        session.append_pesterlog_message(player_id, player.name, message_text)
    
    # Send to all players in session
    await connection_manager.send_pesterlog_message(
        session_code,
        player_id,
        player.name,
        player.character_color,
        message_text
    )

class BroadcastEventRequest(BaseModel):
    event_type: str
    event_text: str
    event_data: Optional[dict] = None


class GenerateCharacterRequest(BaseModel):
    character_data: dict


class AlchemyPreviewRequest(BaseModel):
    item1: str
    item2: str
    mode: str


class AlchemyCreateRequest(BaseModel):
    item1: str
    item2: str
    mode: str


@app.post("/api/generate-character")
async def generate_character(request: GenerateCharacterRequest):
    """Use Gemini to generate mechanical character fields from creator questionnaire data."""
    from game_manager import generate_character_fields
    try:
        fields = await asyncio.wait_for(
            asyncio.to_thread(generate_character_fields, request.character_data),
            timeout=90.0,
        )
        return fields
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Character generation timed out. Try again.")
    except Exception as e:
        msg = str(e)
        if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
            raise HTTPException(status_code=429, detail="API quota exhausted. Please try again shortly.")
        raise HTTPException(status_code=500, detail=msg)


@app.get("/api/sessions/{session_code}/players/{player_id}/alchemy/state")
async def get_alchemy_state(session_code: str, player_id: str):
    session = session_manager.get_session(session_code.upper())
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.get_player(player_id):
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        return session.get_alchemy_state(player_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/sessions/{session_code}/players/{player_id}/alchemy/preview")
async def preview_alchemy(session_code: str, player_id: str, request: AlchemyPreviewRequest):
    session = session_manager.get_session(session_code.upper())
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.get_player(player_id):
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        return session.preview_alchemy(player_id, request.item1, request.item2, request.mode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/sessions/{session_code}/players/{player_id}/alchemy/create")
async def create_alchemy(session_code: str, player_id: str, request: AlchemyCreateRequest):
    session = session_manager.get_session(session_code.upper())
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.get_player(player_id):
        raise HTTPException(status_code=404, detail="Player not found")

    try:
        result = session.create_alchemy(player_id, request.item1, request.item2, request.mode)
        await connection_manager.send_action_buttons_update(
            session_code.upper(),
            player_id,
            session.get_player_action_set(player_id),
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/sessions/{session_code}/broadcast")
async def broadcast_event(session_code: str, request: BroadcastEventRequest):
    """Send a universe-wide broadcast event to all players in a session"""
    session = session_manager.get_session(session_code.upper())

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.append_broadcast_pesterlog(request.event_text)

    await connection_manager.send_broadcast_event(
        session_code.upper(),
        request.event_type,
        request.event_text,
        request.event_data
    )

    return {"success": True}


@app.post("/api/sessions/{session_code}/end")
async def end_session(session_code: str):
    """End a session"""
    session_manager.remove_session(session_code)
    return {"message": f"Session {session_code} ended"}

# Run server
if __name__ == "__main__":
    print(f"Starting Sburb RPG Multiplayer Server on {SERVER_HOST}:{SERVER_PORT}")
    print(f"Frontend URL: {FRONTEND_URL}")
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
