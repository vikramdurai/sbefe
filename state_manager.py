import os
import datetime

class StateManager:
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
    
    def list_files(self, subdir):
        path = os.path.join(self.base_dir, subdir)
        if not os.path.isdir(path):
            return []
        return os.listdir(path)

    def initialize_game(self, player_name="Player"):
        """Create minimal initial files if they don't exist"""
        if self.read_file("session/session_overview.md"):
            return # Already initialized

        # Basic Templates (Simplified for prototype, real ones should parse the MD)
        
        # Session Overview
        self.write_file("session/session_overview.md", f"""# Session Overview
## Session Info
- **Session Type:** Normal
- **Start Date:** {datetime.date.today()}
- **Current Day:** 1

## Players
1. **{player_name}** - Heir of Breath (Default) - LOWAS
   - Status: Active
   - Current Level: 1

## Last Updated
{datetime.datetime.now()}
""")

        # Determine Filename
        p_file = player_name.lower().replace(" ", "_")

        # Characters
        self.write_file(f"characters/{p_file}_sheet.md", f"""# {player_name} - Character Sheet

## Core Identity
- **Class:** Heir
- **Aspect:** Breath
- **Title:** Heir of Breath
- **Land:** Land of Wind and Shade (LOWAS)
- **Denizen:** Typheus

## Stats
- **Current Level:** 1
- **Current Rung:** Lint-Licker
- **XP:** 0/100
- **HP:** 10/10
- **Aspect Power:** 5/5

## Location & Status
- **Current Location:** Player's House (Earth)
- **Current Activity:** Just started the game
- **Status Effects:** None

## Combat Stats
- **Strife Specibus:** Hammerkind
- **Equipped Weapon:** Claw Hammer
- **Attack Power:** 2
- **Defense:** 1
- **Speed:** 3

## Relationships
- **Sprite:** Unprototyped Kernel
- **Coplayers:** None yet

## Last Updated
{datetime.datetime.now()}
""")

        self.write_file(f"characters/{p_file}_inventory.md", f"""# {player_name} - Inventory

## Sylladex
- **Fetch Modus:** Stack
- **Capacity:** 1/5 items

## Strife Deck
- **Equipped:** Claw Hammer (Hammerkind)

## Captchalogue Cards
- None

## Grist Cache
- **Build Grist:** 0

## Last Updated
{datetime.datetime.now()}
""")

        # Locations (LOWAS)
        self.write_file("lands/lowas_state.md", f"""# Land of Wind and Shade (LOWAS) - Current State

## Overview
- **Owner:** {player_name}
- **Denizen:** Typheus

## Physical Environment
- **Biome:** Oil Ocean / Piping
- **Dominant Colors:** Blue, Cyan, Black
- **Atmosphere:** Windy, dark, glowing oil

## The Problem
**Central Crisis:** The fireflies are trapped in the oil, and the land is dark.

## Locations
### Player's House
- **Status:** Explored
- **Notes:** Transported to the land.

### Pipe Crossroads
- **Status:** Unexplored

## Last Updated
{datetime.datetime.now()}
""")

        # Timeline
        self.write_file("session/timeline.md", f"""# Session Timeline
## Current Session Day: 1

## Recent Events
### Day 1, Entry 1 - {datetime.datetime.now()}
**Player:** {player_name}
**Event:** Session started. {player_name} entered the Medium.
**Result:** Land of Wind and Shade created.

## Last Updated
{datetime.datetime.now()}
""")

        print(f"Game initialized for {player_name}!")
