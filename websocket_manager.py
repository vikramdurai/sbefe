"""
WebSocket Manager for Sburb RPG Multiplayer

Handles WebSocket connections and message routing for real-time communication.
"""

from typing import Dict, Set, Optional
from fastapi import WebSocket
from enum import Enum
import json
from datetime import datetime
import asyncio


class MessageType(Enum):
    """Types of WebSocket messages"""
    PLAYER_ACTION = "player_action"
    GM_RESPONSE = "gm_response"
    GM_STREAM_START = "gm_stream_start"
    GM_STREAM_CHUNK = "gm_stream_chunk"
    GM_STREAM_END = "gm_stream_end"
    STAGING_UPDATE = "staging_update"
    PESTERLOG_MESSAGE = "pesterlog_message"
    BROADCAST_EVENT = "broadcast_event"
    ACTION_BUTTONS_UPDATE = "action_buttons_update"
    PARTY_STATUS = "party_status"
    CONNECTION_STATUS = "connection_status"
    ERROR = "error"


class ConnectionManager:
    """Manages WebSocket connections for all sessions"""
    
    def __init__(self):
        # session_code -> player_id -> WebSocket
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_code: str, player_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        if session_code not in self.active_connections:
            self.active_connections[session_code] = {}
        
        self.active_connections[session_code][player_id] = websocket
        
        # Notify others in session that player connected
        await self.broadcast_to_session(
            session_code,
            {
                "type": MessageType.CONNECTION_STATUS.value,
                "player_id": player_id,
                "connected": True,
                "timestamp": datetime.now().isoformat()
            },
            exclude_player=player_id
        )
    
    def disconnect(self, session_code: str, player_id: str):
        """Remove a WebSocket connection"""
        if session_code in self.active_connections:
            if player_id in self.active_connections[session_code]:
                del self.active_connections[session_code][player_id]
            
            # Clean up empty sessions
            if not self.active_connections[session_code]:
                del self.active_connections[session_code]
    
    async def send_to_player(self, session_code: str, player_id: str, message: dict):
        """Send message to a specific player"""
        if session_code in self.active_connections:
            if player_id in self.active_connections[session_code]:
                websocket = self.active_connections[session_code][player_id]
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    print(f"Error sending to player {player_id}: {e}")
                    self.disconnect(session_code, player_id)
    
    async def broadcast_to_session(
        self,
        session_code: str,
        message: dict,
        exclude_player: Optional[str] = None
    ):
        """Broadcast message to all players in a session"""
        if session_code not in self.active_connections:
            return
        
        for player_id, websocket in list(self.active_connections[session_code].items()):
            if exclude_player and player_id == exclude_player:
                continue
            
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to player {player_id}: {e}")
                self.disconnect(session_code, player_id)
    
    async def broadcast_to_party(
        self,
        session_code: str,
        party_player_ids: Set[str],
        message: dict,
        exclude_player: Optional[str] = None
    ):
        """Broadcast message to specific party members"""
        if session_code not in self.active_connections:
            return
        
        for player_id in party_player_ids:
            if exclude_player and player_id == exclude_player:
                continue
            
            await self.send_to_player(session_code, player_id, message)
    
    async def send_staging_update(
        self,
        session_code: str,
        player_id: str,
        draft_text: str,
        party_members: Set[str]
    ):
        """Send staging window update to party members"""
        message = {
            "type": MessageType.STAGING_UPDATE.value,
            "player_id": player_id,
            "draft_text": draft_text,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast_to_party(
            session_code,
            party_members,
            message,
            exclude_player=player_id
        )
    
    async def send_pesterlog_message(
        self,
        session_code: str,
        from_player_id: str,
        from_player_name: str,
        from_player_color: str,
        message_text: str
    ):
        """Send pesterlog message to all players in session"""
        message = {
            "type": MessageType.PESTERLOG_MESSAGE.value,
            "from_player_id": from_player_id,
            "from_player_name": from_player_name,
            "from_player_color": from_player_color,
            "message": message_text,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast_to_session(session_code, message)
    
    async def send_broadcast_event(
        self,
        session_code: str,
        event_type: str,
        event_text: str,
        event_data: Optional[dict] = None
    ):
        """Send universe-wide broadcast event to all players"""
        message = {
            "type": MessageType.BROADCAST_EVENT.value,
            "event_type": event_type,
            "event_text": event_text,
            "event_data": event_data or {},
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast_to_session(session_code, message)
    
    async def send_gm_response(
        self,
        session_code: str,
        player_id: str,
        narrative: str,
        updates_count: int,
        actions: Optional[list[dict]] = None,
    ):
        """Send GM response to a specific player"""
        message = {
            "type": MessageType.GM_RESPONSE.value,
            "narrative": narrative,
            "updates_count": updates_count,
            "timestamp": datetime.now().isoformat()
        }
        if actions is not None:
            message["actions"] = actions
        
        await self.send_to_player(session_code, player_id, message)

    async def send_gm_response_stream(
        self,
        session_code: str,
        player_id: str,
        narrative: str,
        updates_count: int,
        actions: Optional[list[dict]] = None,
    ):
        """Send GM narrative in chunks so clients can render progressively."""
        await self.send_to_player(
            session_code,
            player_id,
            {
                "type": MessageType.GM_STREAM_START.value,
                "timestamp": datetime.now().isoformat(),
            },
        )

        chunk_size = 48
        for i in range(0, len(narrative), chunk_size):
            await self.send_to_player(
                session_code,
                player_id,
                {
                    "type": MessageType.GM_STREAM_CHUNK.value,
                    "chunk": narrative[i:i + chunk_size],
                    "timestamp": datetime.now().isoformat(),
                },
            )
            await asyncio.sleep(0.015)

        end_message = {
            "type": MessageType.GM_STREAM_END.value,
            "narrative": narrative,
            "updates_count": updates_count,
            "timestamp": datetime.now().isoformat(),
        }
        if actions is not None:
            end_message["actions"] = actions

        await self.send_to_player(session_code, player_id, end_message)

    async def send_action_buttons_update(
        self,
        session_code: str,
        player_id: str,
        actions: list[dict],
    ):
        """Push updated context-sensitive action buttons to one player."""
        message = {
            "type": MessageType.ACTION_BUTTONS_UPDATE.value,
            "actions": actions,
            "timestamp": datetime.now().isoformat(),
        }
        await self.send_to_player(session_code, player_id, message)

    async def send_party_status(
        self,
        session_code: str,
        player_id: str,
        active: bool,
        party_members: list[str],
        reason: str,
    ):
        message = {
            "type": MessageType.PARTY_STATUS.value,
            "player_id": player_id,
            "active": active,
            "party_members": party_members,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        }
        await self.send_to_player(session_code, player_id, message)
    
    async def send_error(
        self,
        session_code: str,
        player_id: str,
        error_message: str
    ):
        """Send error message to a player"""
        message = {
            "type": MessageType.ERROR.value,
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.send_to_player(session_code, player_id, message)
    
    def get_connected_players(self, session_code: str) -> Set[str]:
        """Get set of connected player IDs for a session"""
        if session_code in self.active_connections:
            return set(self.active_connections[session_code].keys())
        return set()
