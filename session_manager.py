"""
Session Manager for Sburb RPG Multiplayer

Manages session lifecycle, player registration, and session state.
Uses hybrid storage: markdown files for game state, in-memory for real-time data.
"""

import os
import json
import random
import string
import hashlib
import secrets
import re
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict
from config import SESSION_CODE_LENGTH, CHARACTER_COLORS
from game_manager import GameManager


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-SHA256 with a random salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{key.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        salt, key_hex = stored_hash.split(':', 1)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return secrets.compare_digest(key.hex(), key_hex)
    except Exception:
        return False


class SessionState(Enum):
    """Session lifecycle states"""
    LOBBY = "lobby"
    CHARACTER_CREATION = "character_creation"
    ACTIVE = "active"
    ENDED = "ended"


@dataclass
class PlayerInfo:
    """Information about a player in a session"""
    player_id: str
    name: str
    username: str = ""
    password_hash: str = ""
    character_data: Optional[dict] = None
    character_color: str = "#ffffff"
    connected: bool = False
    current_location: Optional[str] = None
    current_context: str = "navigation"
    party_id: Optional[str] = None
    ready: bool = False  # Ready to start game
    player_class: str = "Heir"
    aspect: str = "Breath"
    title: str = "Heir of Breath"
    land: str = "LOWAS"
    denizen: str = "Typheus"
    echeladder_rung: str = "Lint-Licker"
    strife_specibus: str = "Hammerkind"
    current_weapon: str = "Claw Hammer"
    sprite: str = "Unprototyped Kernel"
    
    def to_dict(self):
        return asdict(self)

    def __getattr__(self, name: str):
        if name == "class":
            return self.player_class
        raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}'")


class Session:
    """Represents a game session"""
    
    def __init__(self, code: str, base_dir: str = "."):
        self.code = code
        self.base_dir = base_dir
        self.state = SessionState.LOBBY
        self.players: Dict[str, PlayerInfo] = {}
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.game_manager = None  # Will be initialized when session starts
        
        # In-memory state (not persisted)
        self.action_queue = []  # Queue of pending actions with timestamps
        self.staging_drafts = {}  # player_id -> current draft text
        self.dynamic_action_cache: Dict[str, List[dict]] = {}
        self.player_runtime_state: Dict[str, dict] = {}
        self.pesterlog_messages: List[dict] = []
        
    def add_player(
        self,
        player_id: str,
        name: str,
        username: str = "",
        password_hash: str = "",
        player_class: str = "Heir",
        aspect: str = "Breath",
        title: str = "Heir of Breath",
        land: str = "LOWAS",
        denizen: str = "Typheus",
        echeladder_rung: str = "Lint-Licker",
        strife_specibus: str = "Hammerkind",
        current_weapon: str = "Claw Hammer",
        sprite: str = "Unprototyped Kernel",
        character_data: Optional[dict] = None
    ) -> PlayerInfo:
        """Add a player to the session"""
        if len(self.players) >= 8:  # MAX_PLAYERS_PER_SESSION
            raise ValueError("Session is full")

        # Check for duplicate username within this session
        if username:
            for p in self.players.values():
                if p.username.lower() == username.lower():
                    raise ValueError(f"Username '{username}' is already taken in this session")

        # Assign character color
        color_index = len(self.players) % len(CHARACTER_COLORS)
        color = CHARACTER_COLORS[color_index]

        player = PlayerInfo(
            player_id=player_id,
            name=name,
            username=username,
            password_hash=password_hash,
            character_color=color,
            player_class=player_class,
            aspect=aspect,
            title=title,
            land=land,
            denizen=denizen,
            echeladder_rung=echeladder_rung,
            strife_specibus=strife_specibus,
            current_weapon=current_weapon,
            sprite=sprite,
            character_data=character_data
        )
        self.players[player_id] = player
        return player
    
    def get_player(self, player_id: str) -> Optional[PlayerInfo]:
        """Get player info by ID"""
        return self.players.get(player_id)
    
    def set_player_ready(self, player_id: str, ready: bool = True):
        """Mark player as ready to start"""
        if player_id in self.players:
            self.players[player_id].ready = ready

    def find_player_by_credentials(self, username: str, password: str) -> Optional['PlayerInfo']:
        """Find a player by username and verify their password."""
        for player in self.players.values():
            if player.username.lower() == username.lower() and player.password_hash:
                if verify_password(password, player.password_hash):
                    return player
        return None

    def all_players_ready(self) -> bool:
        """Check if all players are ready to start"""
        if not self.players:
            return False
        return all(p.ready for p in self.players.values())
    
    def start_session(self):
        """Transition session to active state"""
        if not self.all_players_ready():
            raise ValueError("Not all players are ready")
        
        self.state = SessionState.ACTIVE
        self.started_at = datetime.now()

        if not self.game_manager:
            game_dir = os.path.join(self.base_dir, "sessions", self.code, "game")
            self.game_manager = GameManager(
                game_dir,
                list(self.players.values())
            )
        self._initialize_action_catalog()
        self._initialize_player_runtime_state()

    def _initialize_player_runtime_state(self):
        """Populate lightweight runtime inventory/grist state used by fast UI endpoints."""
        for player in self.players.values():
            self.player_runtime_state[player.player_id] = {
                "grist": {
                    "Build": 450,
                    "Amber": 120,
                    "Ruby": 40,
                },
                "items": [
                    {"name": player.current_weapon, "quantity": 1, "icon": "W"},
                    {"name": "Claw Hammer", "quantity": 1, "icon": "H"},
                    {"name": "Laptop", "quantity": 1, "icon": "L"},
                    {"name": "Sunglasses", "quantity": 1, "icon": "S"},
                ],
                "recipe_history": [],
            }

    def _initialize_action_catalog(self):
        """Create starter location action JSON files and player action state."""
        game_dir = os.path.join(self.base_dir, "sessions", self.code, "game")
        locations_dir = os.path.join(game_dir, "locations")
        os.makedirs(locations_dir, exist_ok=True)

        for player in self.players.values():
            player.current_context = "navigation"
            if not player.current_location:
                player.current_location = f"{player.land}:entry_point"

            self.dynamic_action_cache[player.player_id] = []
            location_key = player.current_location.split(":", 1)[-1]
            location_payload = {
                "location": location_key.replace("_", " ").title(),
                "description": "The starting area of your Land hums with weird possibility.",
                "actions": [
                    {
                        "label": "Look Around",
                        "action_type": "examine",
                        "target": "surroundings",
                        "icon": "[?]",
                        "tooltip": "Get a quick read on your immediate environment.",
                    },
                    {
                        "label": "Talk To Nearby Consort",
                        "action_type": "dialogue",
                        "target": "consort",
                        "icon": "[chat]",
                        "tooltip": "Ask for rumors, guidance, or nonsense wisdom.",
                    },
                    {
                        "label": "Move Deeper Into Area",
                        "action_type": "navigate",
                        "target": "interior_path",
                        "icon": "[go]",
                        "tooltip": "Travel toward the next point of interest.",
                    },
                    {
                        "label": "Open Alchemy Menu",
                        "action_type": "alchemy",
                        "target": "alchemiter",
                        "icon": "[&&]",
                        "tooltip": "Switch to crafting and combination actions.",
                    },
                ],
            }

            file_name = f"{player.land.lower()}_{location_key}.json"
            with open(os.path.join(locations_dir, file_name), "w") as f:
                json.dump(location_payload, f, indent=2)

        self.save_metadata(self.base_dir)

    def _load_location_actions(self, player: PlayerInfo) -> List[dict]:
        game_dir = os.path.join(self.base_dir, "sessions", self.code, "game")
        locations_dir = os.path.join(game_dir, "locations")
        location_key = (player.current_location or f"{player.land}:entry_point").split(":", 1)[-1]
        file_name = f"{player.land.lower()}_{location_key}.json"
        full_path = os.path.join(locations_dir, file_name)
        if not os.path.exists(full_path):
            return []

        try:
            with open(full_path, "r") as f:
                payload = json.load(f)
            return payload.get("actions", [])
        except Exception:
            return []

    def get_player_action_set(self, player_id: str) -> List[dict]:
        """Return context-aware actions for a specific player."""
        player = self.get_player(player_id)
        if not player:
            return []

        if player.current_context == "combat":
            actions = [
                {"label": "Attack", "action_type": "combat", "target": "attack", "icon": "[ATK]", "tooltip": "Strike the active target."},
                {"label": "Defend", "action_type": "combat", "target": "defend", "icon": "[DEF]", "tooltip": "Reduce incoming damage."},
                {"label": "Use Item", "action_type": "combat", "target": "item", "icon": "[ITEM]", "tooltip": "Use a captchalogued item."},
                {"label": "Abscond", "action_type": "combat", "target": "flee", "icon": "[RUN]", "tooltip": "Attempt to escape strife."},
            ]
        elif player.current_context == "dialogue":
            actions = [
                {"label": "Ask About Area", "action_type": "dialogue", "target": "area_info", "icon": "[?]", "tooltip": "Request local info."},
                {"label": "Ask About Quest", "action_type": "dialogue", "target": "quest_hint", "icon": "[Q]", "tooltip": "Request quest hint."},
                {"label": "Leave Conversation", "action_type": "navigate", "target": "exit_dialogue", "icon": "[go]", "tooltip": "Return to exploration."},
            ]
        elif player.current_context == "alchemy":
            actions = [
                {"label": "Combine Items", "action_type": "alchemy", "target": "combine", "icon": "[&&]", "tooltip": "Choose two inventory items."},
                {"label": "Check Recipe Book", "action_type": "alchemy", "target": "recipes", "icon": "[book]", "tooltip": "Review known combinations."},
                {"label": "Cancel Alchemy", "action_type": "navigate", "target": "exit_alchemy", "icon": "[x]", "tooltip": "Return to exploration context."},
            ]
        else:
            actions = self._load_location_actions(player)

        dynamic = self.dynamic_action_cache.get(player_id, [])
        return actions + dynamic

    def _compute_recipe(self, item1: str, item2: str, mode: str) -> dict:
        """Generate deterministic alchemy preview data for two items and an operator."""
        i1 = (item1 or "Item One").strip()
        i2 = (item2 or "Item Two").strip()
        op = (mode or "&&").strip()

        normalized = f"{i1.lower()}::{i2.lower()}::{op}"
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        power_seed = int(digest[:8], 16)
        attack = 12 + (power_seed % 44)

        if op == "&&":
            result_name = f"{i1[: max(2, len(i1)//2)]}{i2[max(1, len(i2)//2):]}"
            ability = "Combined force"
        elif op == "||":
            result_name = f"{i1}-{i2} Hybrid"
            ability = "Adaptive mode shift"
        else:
            result_name = f"Null {i1[:4]}{i2[:4]}"
            ability = "Unstable paradox burst"

        result_name = re.sub(r"\s+", " ", result_name).strip()
        build_cost = 80 + attack * 6
        amber_cost = 20 + attack * 2
        ruby_cost = 8 + attack // 3

        description = (
            f"You slam {i1} {op} {i2} into the Alchemiter and it coughs up {result_name}. "
            f"It looks questionably safe, which is how you know it probably rules."
        )

        return {
            "key": normalized,
            "result": result_name,
            "attack": attack,
            "special": ability,
            "cost": {
                "Build": build_cost,
                "Amber": amber_cost,
                "Ruby": ruby_cost,
            },
            "description": description,
        }

    def preview_alchemy(self, player_id: str, item1: str, item2: str, mode: str) -> dict:
        player_state = self.player_runtime_state.get(player_id)
        if not player_state:
            raise ValueError("Player runtime state is unavailable")
        return self._compute_recipe(item1, item2, mode)

    def _append_recipe_to_catalog(self, recipe: dict, player_name: str, item1: str, item2: str, mode: str):
        game_dir = os.path.join(self.base_dir, "sessions", self.code, "game")
        alchemy_dir = os.path.join(game_dir, "alchemy")
        os.makedirs(alchemy_dir, exist_ok=True)
        catalog_path = os.path.join(alchemy_dir, "item_catalog.md")

        if not os.path.exists(catalog_path):
            with open(catalog_path, "w") as f:
                f.write("# Session Alchemy Catalog\n\n")

        entry = (
            f"## {recipe['result']}\n"
            f"- Created by: {player_name}\n"
            f"- Recipe: {item1} {mode} {item2}\n"
            f"- Attack: {recipe['attack']}\n"
            f"- Special: {recipe['special']}\n"
            f"- Cost: Build {recipe['cost']['Build']}, Amber {recipe['cost']['Amber']}, Ruby {recipe['cost']['Ruby']}\n"
            f"- Description: {recipe['description']}\n"
            f"- Timestamp: {datetime.now().isoformat()}\n\n"
        )

        with open(catalog_path, "a") as f:
            f.write(entry)

    def create_alchemy(self, player_id: str, item1: str, item2: str, mode: str) -> dict:
        player = self.get_player(player_id)
        if not player:
            raise ValueError("Player not found")

        player_state = self.player_runtime_state.get(player_id)
        if not player_state:
            raise ValueError("Player runtime state is unavailable")

        recipe = self._compute_recipe(item1, item2, mode)
        cost = recipe["cost"]

        for grist_type, needed in cost.items():
            have = player_state["grist"].get(grist_type, 0)
            if have < needed:
                raise ValueError(f"Not enough {grist_type} grist ({have}/{needed})")

        for grist_type, needed in cost.items():
            player_state["grist"][grist_type] = player_state["grist"].get(grist_type, 0) - needed

        player_state["items"].append(
            {
                "name": recipe["result"],
                "quantity": 1,
                "icon": "A",
                "attack": recipe["attack"],
                "special": recipe["special"],
            }
        )
        player_state["recipe_history"].append(
            {
                "item1": item1,
                "item2": item2,
                "mode": mode,
                "result": recipe["result"],
            }
        )

        self._append_recipe_to_catalog(recipe, player.name, item1, item2, mode)

        return {
            "created": recipe,
            "gristRemaining": player_state["grist"],
            "inventory": player_state["items"],
            "recipeHistory": player_state["recipe_history"][-20:],
        }

    def get_alchemy_state(self, player_id: str) -> dict:
        player_state = self.player_runtime_state.get(player_id)
        if not player_state:
            raise ValueError("Player runtime state is unavailable")
        return {
            "grist": player_state["grist"],
            "inventory": player_state["items"],
            "recipeHistory": player_state["recipe_history"][-20:],
        }

    def append_pesterlog_message(self, from_player_id: str, from_player_name: str, text: str):
        """Persist a pesterlog message in memory and markdown log file."""
        msg = {
            "timestamp": datetime.now().isoformat(),
            "from_player_id": from_player_id,
            "from_player_name": from_player_name,
            "message": text,
        }
        self.pesterlog_messages.append(msg)

        game_dir = os.path.join(self.base_dir, "sessions", self.code, "game")
        session_dir = os.path.join(game_dir, "session")
        os.makedirs(session_dir, exist_ok=True)
        pesterlog_path = os.path.join(session_dir, "pesterlogs.md")
        line = f"[{msg['timestamp']}] {from_player_name}: {text}\n"

        if not os.path.exists(pesterlog_path):
            with open(pesterlog_path, "w") as f:
                f.write("# Session Pesterlogs\n\n")

        with open(pesterlog_path, "a") as f:
            f.write(line)

    def append_broadcast_pesterlog(self, text: str):
        msg = {
            "timestamp": datetime.now().isoformat(),
            "from_player_id": "broadcast",
            "from_player_name": "BROADCAST",
            "message": text,
            "is_broadcast": True,
        }
        self.pesterlog_messages.append(msg)

        game_dir = os.path.join(self.base_dir, "sessions", self.code, "game")
        session_dir = os.path.join(game_dir, "session")
        os.makedirs(session_dir, exist_ok=True)
        pesterlog_path = os.path.join(session_dir, "pesterlogs.md")
        line = f"[{msg['timestamp']}] [BROADCAST] {text}\n"

        if not os.path.exists(pesterlog_path):
            with open(pesterlog_path, "w") as f:
                f.write("# Session Pesterlogs\n\n")

        with open(pesterlog_path, "a") as f:
            f.write(line)

    def get_recent_scene_pesterlog_context(self, player_id: str, limit: int = 12) -> str:
        """Return recent pesterlog lines only when other players share this player's scene."""
        actor = self.get_player(player_id)
        if not actor or not actor.current_location:
            return ""

        scene_player_ids = {
            p.player_id
            for p in self.players.values()
            if p.current_location == actor.current_location
        }

        if len(scene_player_ids) < 2:
            return ""

        scene_messages = [
            m for m in self.pesterlog_messages
            if m.get("from_player_id") in scene_player_ids or m.get("is_broadcast")
        ]
        if not scene_messages:
            return ""

        recent = scene_messages[-limit:]
        lines = [
            f"[{m['timestamp']}] {m.get('from_player_name', 'Unknown')}: {m.get('message', '')}"
            for m in recent
        ]
        return "\n".join(lines)
    
    def end_session(self):
        """Transition session to ended state"""
        self.state = SessionState.ENDED
    
    def save_metadata(self, base_dir: Optional[str] = None):
        """Save session metadata to disk"""
        resolved_base_dir = base_dir or self.base_dir
        session_dir = os.path.join(resolved_base_dir, "sessions", self.code)
        os.makedirs(session_dir, exist_ok=True)
        
        metadata = {
            "code": self.code,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "players": {pid: p.to_dict() for pid, p in self.players.items()}
        }
        
        metadata_path = os.path.join(session_dir, "session_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
    
    @staticmethod
    def load_metadata(code: str, base_dir: str = ".") -> Optional['Session']:
        """Load session from disk"""
        metadata_path = os.path.join(base_dir, "sessions", code, "session_metadata.json")
        
        if not os.path.exists(metadata_path):
            return None
        
        with open(metadata_path, "r") as f:
            data = json.load(f)
        
        session = Session(data["code"], base_dir=base_dir)
        session.state = SessionState(data["state"])
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.started_at = datetime.fromisoformat(data["started_at"]) if data["started_at"] else None
        
        # Restore players
        for pid, pdata in data["players"].items():
            player = PlayerInfo(**pdata)
            session.players[pid] = player

        # If the session was already active, rebuild the GameManager so players
        # can continue submitting actions immediately after a server restart.
        if session.state == SessionState.ACTIVE:
            game_dir = os.path.join(base_dir, "sessions", code, "game")
            session.game_manager = GameManager(game_dir, list(session.players.values()))
            session._initialize_action_catalog()
            session._initialize_player_runtime_state()

        return session


class SessionManager:
    """Manages all active sessions"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.sessions: Dict[str, Session] = {}
        self._load_existing_sessions()
    
    def _load_existing_sessions(self):
        """Load existing sessions from disk on startup"""
        sessions_dir = os.path.join(self.base_dir, "sessions")
        if not os.path.exists(sessions_dir):
            return
        
        for code in os.listdir(sessions_dir):
            session_path = os.path.join(sessions_dir, code)
            if os.path.isdir(session_path):
                session = Session.load_metadata(code, self.base_dir)
                if session and session.state != SessionState.ENDED:
                    self.sessions[code] = session
                    print(f"Loaded session: {code} ({session.state.value})")
    
    def generate_session_code(self) -> str:
        """Generate a unique session code"""
        while True:
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits,
                k=SESSION_CODE_LENGTH
            ))
            if code not in self.sessions:
                return code
    
    def create_session(self) -> Session:
        """Create a new session"""
        code = self.generate_session_code()
        session = Session(code, base_dir=self.base_dir)
        self.sessions[code] = session
        session.save_metadata(self.base_dir)
        return session
    
    def get_session(self, code: str) -> Optional[Session]:
        """Get session by code"""
        return self.sessions.get(code.upper())
    
    def join_session(
        self,
        code: str,
        player_id: str,
        player_name: str,
        username: str = "",
        password: str = "",
        player_class: str = "Heir",
        aspect: str = "Breath",
        title: str = "Heir of Breath",
        land: str = "LOWAS",
        denizen: str = "Typheus",
        echeladder_rung: str = "Lint-Licker",
        strife_specibus: str = "Hammerkind",
        current_weapon: str = "Claw Hammer",
        sprite: str = "Unprototyped Kernel",
        character_data: Optional[dict] = None
    ) -> PlayerInfo:
        """Join an existing session"""
        session = self.get_session(code)
        if not session:
            raise ValueError(f"Session {code} not found")
        
        if session.state != SessionState.LOBBY:
            raise ValueError("Session has already started")
        
        password_hash = hash_password(password) if password else ""
        player = session.add_player(
            player_id,
            player_name,
            username=username,
            password_hash=password_hash,
            player_class=player_class,
            aspect=aspect,
            title=title,
            land=land,
            denizen=denizen,
            echeladder_rung=echeladder_rung,
            strife_specibus=strife_specibus,
            current_weapon=current_weapon,
            sprite=sprite,
            character_data=character_data
        )
        session.save_metadata(self.base_dir)
        return player
    
    def remove_session(self, code: str):
        """Remove a session (when ended)"""
        if code in self.sessions:
            self.sessions[code].end_session()  # Ensure session is marked as ended
            del self.sessions[code]

    def rejoin_session(self, code: str, username: str, password: str) -> 'PlayerInfo':
        """Verify credentials and return the matching player for a session rejoin."""
        session = self.get_session(code)
        if not session:
            raise ValueError(f"Session {code} not found")

        player = session.find_player_by_credentials(username, password)
        if not player:
            raise ValueError("Invalid username or password")

        return player
