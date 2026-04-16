import os
import datetime
import string

class StateManager:
    # Absolute path to the directory containing state_manager.py (project root)
    _PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self.dirs = [
            "characters",
            "session",
            "lands",
            "npcs/sprites",
            "npcs/consorts",
            "npcs/denizens",
            "alchemy",
            "combat"
        ]

    def ensure_directories(self):
        for d in self.dirs:
            os.makedirs(os.path.join(self.base_dir, d), exist_ok=True)

    def write_file(self, path, content):
        full_path = os.path.join(self.base_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    def read_file(self, path):
        full_path = os.path.join(self.base_dir, path)
        if not os.path.exists(full_path):
            return None
        with open(full_path, "r") as f:
            return f.read()

    def read_template(self, path):
        """Read a file relative to the project root (not the per-session base_dir)."""
        full_path = os.path.join(self._PROJECT_ROOT, path)
        if not os.path.exists(full_path):
            return None
        with open(full_path, "r") as f:
            return f.read()
    
    def list_files(self, subdir):
        path = os.path.join(self.base_dir, subdir)
        if not os.path.isdir(path):
            return []
        return os.listdir(path)

    def initialize_game(self, players):
        """Create minimal initial files if they don't exist"""
        if self.read_file("session/session_overview.md"):
            return # Already initialized

        sheet_template = string.Template(self.read_template("templates/character_sheet.md") or "")

        # Session Overview
        session_overview = f"""# Session Overview
## Session Info
- **Session Type:** Normal
- **Start Date:** {datetime.date.today()}
- **Current Day:** 1

## Players\n"""
        
        session_timeline = f"""# Session Timeline
## Current Session Day: 1
### Day 1, Entry 1 - {datetime.datetime.now()}
**Players:** {', '.join(player.name for player in players)}
**Event:** Session started. Players have entered the Medium.
**Result:** {', '.join(player.land for player in players)} created.

## Last Updated
{datetime.datetime.now()}"""
        
        for i, player in enumerate(players):
            session_overview += f"""{i+1}. **{player.name}** - {player.title} - {player.land}
   - Status: Active
   - Current Level: 1\n"""

            # Build narrative sections from character_data if available
            cd = player.character_data or {}

            def _section(data, *keys):
                parts = [data.get(k, '').strip() for k in keys if data.get(k, '').strip()]
                return '\n'.join(parts) if parts else 'Not yet revealed.'

            personality_text = _section(
                cd.get('personality', {}),
                'description', 'biggest_flaw', 'greatest_strength',
                'conflict_handling', 'relationships'
            )
            backstory_text = _section(
                cd.get('backstory', {}),
                'life_story', 'defining_event', 'guardian_relationship', 'deepest_want'
            )
            interests_text = _section(
                cd.get('interests', {}),
                'time_spent', 'obsessions', 'collections', 'media', 'creations'
            )
            hidden_text = _section(
                cd.get('hidden_questions', {}),
                'sacrifice', 'expertise', 'reliance',
                'time_perception', 'hidden_depths', 'problem_response'
            )

            session_prefs = cd.get('session', {})
            content_flags = session_prefs.get('content_flags', '').strip()
            content_flags_line = f"- **Content to Avoid:** {content_flags}" if content_flags else ''
            identity = cd.get('identity', {})
            generated = cd.get('generated', {})

            mapping = {
                'name':              player.name,
                'cls':               player.player_class,
                'aspect':            player.aspect,
                'title':             player.title,
                'land':              player.land,
                'land_full':         generated.get('land_full', player.land),
                'lunar_sway':        generated.get('lunar_sway', 'Unknown'),
                'denizen':           player.denizen,
                'species':           identity.get('species', 'Human'),
                'age':               str(identity.get('age', 15)),
                'pronouns':          identity.get('pronouns', 'they/them'),
                'appearance':        identity.get('appearance', 'Not described.'),
                'echeladder':        player.echeladder_rung,
                'specibus':          player.strife_specibus,
                'weapon':            player.current_weapon,
                'sprite':            player.sprite,
                'personality':       personality_text,
                'backstory':         backstory_text,
                'interests':         interests_text,
                'hidden':            hidden_text,
                'experience_type':   session_prefs.get('experience_type', 'Balanced'),
                'permadeath':        session_prefs.get('permadeath', 'Embrace it'),
                'content_flags_line': content_flags_line,
                'date':              str(datetime.datetime.now()),
            }

            p_file = player.name.lower().replace(" ", "_")
            self.write_file(
                f"characters/{p_file}_sheet.md",
                sheet_template.safe_substitute(mapping)
            )

            # Inventory
            inv_template = string.Template(self.read_template("templates/inventory.md") or "")
            if inv_template.template.strip():
                self.write_file(f"characters/{p_file}_inventory.md",
                                inv_template.safe_substitute(mapping))
            else:
                self.write_file(f"characters/{p_file}_inventory.md", f"""# {player.name} - Inventory

## Sylladex
- **Fetch Modus:** Stack
- **Capacity:** 0/5 items

## Strife Deck
- **Equipped:** {player.current_weapon} ({player.strife_specibus})

## Captchalogue Cards
- None

## Grist Cache
- **Build Grist:** 0

## Last Updated
{datetime.datetime.now()}
""")

            # Land state
            land_template = string.Template(self.read_template("templates/land_state.md") or "")
            if land_template.template.strip():
                self.write_file(f"lands/{player.land}_state.md",
                                land_template.safe_substitute(mapping))
            else:
                self.write_file(f"lands/{player.land}_state.md", f"""# {player.land} - Current State

## Overview
- **Owner:** {player.name}
- **Denizen:** {player.denizen}

## Physical Environment
- **Biome:** Unknown
- **Atmosphere:** Mysterious

## The Problem
**Central Crisis:** Unknown — yet to be discovered.

## Locations
### {player.name}'s Entry Point
- **Status:** Just arrived

## Last Updated
{datetime.datetime.now()}
""")

        # Timeline
        self.write_file("session/timeline.md", session_timeline)
        self.write_file("session/session_overview.md",
                        session_overview + f"## Last Updated\n{datetime.datetime.now()}")
        print(f"Game initialized for {', '.join(player.name for player in players)}!")
