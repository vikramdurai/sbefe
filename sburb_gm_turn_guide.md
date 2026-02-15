# SBURB RPG: Game Manager Turn-by-Turn Guide

## Overview

This document provides instructions for operating as the Game Manager on a per-turn basis using a Retrieval-Augmented Generation (RAG) system. By storing all game state in structured markdown files and retrieving them before each response, the GM maintains perfect consistency and never forgets important details.

---

## File Organization System

### Directory Structure

```
/game_session/
├── characters/
│   ├── [player_name]_sheet.md
│   ├── [player_name]_inventory.md
│   └── [player_name]_quest_log.md
├── session/
│   ├── session_overview.md
│   ├── timeline.md
│   ├── derse_state.md
│   ├── prospit_state.md
│   └── skaia_state.md
├── lands/
│   ├── [land_abbreviation]_state.md
│   └── [land_abbreviation]_locations.md
├── npcs/
│   ├── sprites/
│   │   └── [sprite_name].md
│   ├── consorts/
│   │   └── [consort_type]_dialogue.md
│   └── denizens/
│       └── [denizen_name].md
├── alchemy/
│   └── item_catalog.md
└── combat/
    └── active_encounters.md
```

---

## Turn Sequence Protocol

### Phase 1: Context Retrieval (ALWAYS FIRST)

Before responding to ANY player action, retrieve these files in order:

1. **Player's character sheet** - Get current stats, location, quest progress
2. **Player's inventory** - Know what items/weapons they have available
3. **Current location state** - Understand the environment they're in
4. **Session overview** - Check session-wide status and ongoing events
5. **Active encounters** - If in combat, get enemy status
6. **Recent timeline** - Review last 5-10 events for context

**Example retrieval query:**
```
RETRIEVE:
- characters/john_egbert_sheet.md
- characters/john_egbert_inventory.md
- lands/lowas_state.md
- session/session_overview.md
- combat/active_encounters.md (if applicable)
- session/timeline.md (last 10 entries)
```

### Phase 2: Action Processing

Analyze the player's action against retrieved context:

1. **Validity check:** Can they do this action? (Do they have required items? Are they in the right location?)
2. **Difficulty assessment:** How challenging is this action given their level/stats?
3. **Consequence determination:** What happens as a result? (Success/failure/partial success)
4. **Narrative consistency:** Does this fit with established facts and character personality?

### Phase 3: Response Generation

Generate the response following these principles:

1. **Acknowledge previous context** - Reference recent events naturally
2. **Describe outcome** - What happens as a result of their action
3. **Environmental details** - Paint the scene with Land-appropriate descriptions
4. **Consequence indication** - Make clear what has changed
5. **Forward momentum** - Provide hooks for next actions

**Response Structure:**
```
[Acknowledgment of action]
[Outcome description with sensory details]
[Environmental/NPC reactions]
[Status changes if any]
[Options/hooks for continuation]
```

### Phase 4: State Updates (ALWAYS LAST)

After generating response, update all affected files:

1. **Character sheet** - Update XP, level, location, quest flags
2. **Inventory** - Add/remove items, update grist counts
3. **Location state** - Mark areas explored, NPCs met, puzzles solved
4. **Timeline** - Add new event entry with timestamp
5. **Combat tracker** - Update if in combat
6. **Session overview** - Update if major milestone reached

**Update checklist:**
- [ ] Character XP/level updated?
- [ ] Inventory modified correctly?
- [ ] Location state reflects changes?
- [ ] Timeline entry added?
- [ ] Any triggered events noted?

### Phase 5: Trigger Check

After updates, check for automatic triggers:

- **Level up** - Did XP cross threshold? Announce new Echeladder rung
- **Quest completion** - Did they finish a quest objective?
- **Area unlock** - Did they gain access to new location?
- **Event trigger** - Did action cause a scheduled event?
- **NPC reaction** - Do any NPCs need to respond to changes?

---

## File Templates and Usage

### Character Sheet Template

**Filename:** `characters/[player_name]_sheet.md`

```markdown
# [Player Name] - Character Sheet

## Core Identity
- **Class:** [Class]
- **Aspect:** [Aspect]
- **Title:** [Class] of [Aspect]
- **Land:** [Land Full Name] ([Abbreviation])
- **Denizen:** [Denizen Name]

## Stats
- **Current Level:** [Number]
- **Current Rung:** [Echeladder Rung Name]
- **XP:** [Current]/[Next Level Threshold]
- **HP:** [Current]/[Max]
- **Aspect Power:** [Current]/[Max]

## Location & Status
- **Current Location:** [Specific location on Land or in session]
- **Current Activity:** [What they're doing]
- **Status Effects:** [Any buffs/debuffs]
- **God Tier Status:** [Not Achieved / Achieved - Date]

## Combat Stats
- **Strife Specibus:** [Weapon Type]kind
- **Equipped Weapon:** [Current weapon name]
- **Attack Power:** [Number]
- **Defense:** [Number]
- **Speed:** [Number]

## Quest Progress

### Personal Quest
- **Theme:** [Core character flaw/strength to overcome]
- **Current Stage:** [Stage name/number]
- **Progress Notes:** 
  - [Key milestone achieved]
  - [Current objective]

### Land Quest
- **Land Problem:** [The crisis affecting the land]
- **Current Stage:** [Where in solving the problem]
- **Consorts Met:** [List of consort NPCs encountered]
- **Denizen Status:** [Not Met / Met / Defeated]

### God Tier Quest
- **Quest Bed Location:** [Unknown / Found at [location] / Used]
- **Death Status:** [Alive / Died - Heroic/Just on [date]]

## Relationships
- **Sprite:** [Sprite name and prototypings]
- **Coplayers:** [Other players and relationship status]
- **Key NPCs:** [Important NPCs and relationship notes]

## Character Development
- **Growth Moments:** [Key character development scenes]
- **Personality Notes:** [Relevant personality traits and quirks]
- **Motivations:** [What drives this character]

## Last Updated
[Timestamp]
```

**When to update:** After every action that changes stats, location, quest progress, or relationships.

---

### Inventory Template

**Filename:** `characters/[player_name]_inventory.md`

```markdown
# [Player Name] - Inventory

## Sylladex
- **Fetch Modus:** [Modus Name]
- **Capacity:** [Current]/[Max] items
- **Modus Properties:** [How it works, quirks]

## Strife Deck
### Allocated Specibus
- **Type:** [Weapon Type]kind
- **Equipped:** [Weapon Name]

### Available Weapons
1. **[Weapon Name]**
   - Code: [Alchemy Code]
   - Type: [Weapon Type]
   - Power: [Number]
   - Special Properties: [Abilities]
   - Grist Cost: [Original crafting cost]

## Captchalogue Cards
1. **[Item Name]**
   - Code: [Alchemy Code]
   - Description: [What it is]
   - Properties: [What it does]
   - Quantity: [Number]

## Grist Cache
- **Build Grist:** [Amount]
- **Shale:** [Amount]
- **Amber:** [Amount]
- **Ruby:** [Amount]
- **[Other Grist Types]:** [Amounts]
- **Zillium:** [Amount]

## Alchemy History
Recent creations (for reference):
1. **[Item Name]** = [Item 1] && [Item 2] - [Date created]

## Quest Items
Special items relevant to quests:
- **[Item Name]:** [Why it's important]

## Last Updated
[Timestamp]
```

**When to update:** After any alchemy, item acquisition/loss, grist gain/spend, or equipment change.

---

### Quest Log Template

**Filename:** `characters/[player_name]_quest_log.md`

```markdown
# [Player Name] - Quest Log

## Active Quests

### [Quest Name]
- **Type:** [Personal/Land/Session]
- **Giver:** [Who gave this quest]
- **Objective:** [What needs to be done]
- **Progress:** [Current status]
- **Rewards:** [What they'll get]
- **Notes:** [Relevant details]

## Completed Quests

### [Quest Name] - Completed [Date]
- **Resolution:** [How it was completed]
- **Rewards Received:** [What they got]

## Quest Hooks
Potential quests or storylines to follow up on:
- [Hook description]

## Last Updated
[Timestamp]
```

**When to update:** When quests are started, progressed, or completed.

---

### Session Overview Template

**Filename:** `session/session_overview.md`

```markdown
# Session Overview

## Session Info
- **Session Type:** [Scratch/Normal/Void/Dead]
- **Session ID:** [Identifier]
- **Start Date:** [Game start date]
- **Current Day:** [Session day count]

## Players
1. **[Player Name]** - [Class] of [Aspect] - [Land Abbreviation]
   - Status: [Active/God Tier/Dead/Other]
   - Current Level: [Number]

## Critical Session Stats
- **Players Entered:** [X]/[Total]
- **God Tiers Achieved:** [X]/[Total]
- **Denizens Defeated:** [X]/[Total]
- **Genesis Frog Progress:** [Percentage or status]
- **Black King Status:** [Alive/Weakened/Defeated]

## Current Session Phase
[Entry/Early Game/Mid Game/Late Game/Endgame]

**Phase Description:** [What's happening now]

## Major Events Timeline
1. **[Date]** - [Event description]

## Active Threats
- **[Threat Name]:** [Description and status]

## Session Goals Remaining
- [ ] All players reach God Tier
- [ ] Complete Genesis Frog breeding
- [ ] Light all Forges
- [ ] Defeat Black King
- [ ] Create new universe

## Last Updated
[Timestamp]
```

**When to update:** After any major session milestone or daily.

---

### Derse State Template

**Filename:** `session/derse_state.md`

```markdown
# Derse - Current State

## Overview
Derse is the dark moon of the battlefield, home to the forces of darkness and carapacians serving the Black King.

## Current Status
- **Ruler:** [Black King/Black Queen/Other]
- **Military Strength:** [Description]
- **Threat Level:** [Low/Medium/High/Extreme]
- **Activity Level:** [What they're currently doing]

## Key Locations

### Derse Palace
- **Status:** [Intact/Damaged/Destroyed]
- **Occupants:** [Who's there]
- **Notes:** [Important details]

### Prison Cells
- **Occupied By:** [Who's imprisoned]
- **Security Level:** [Description]

### Battlefield Access
- **Status:** [Open/Guarded/Closed]
- **Military Presence:** [Troop descriptions]

## Dersite Dreamers
Players whose dream selves are on Derse:
- **[Player Name]:** [Dream self status]

## Recent Activity
- **[Date]:** [Event]

## Agents and Notable NPCs
- **[Agent Name]:** [Current activity and location]

## Strategic Notes
[Observations about Derse's plans or weaknesses]

## Last Updated
[Timestamp]
```

**When to update:** After events involving Derse, or daily if Derse is actively plotting.

---

### Prospit State Template

**Filename:** `session/prospit_state.md`

```markdown
# Prospit - Current State

## Overview
Prospit is the golden moon of the battlefield, home to the forces of light and carapacians serving the White King.

## Current Status
- **Ruler:** [White King/White Queen/Other]
- **Military Strength:** [Description]
- **Defensive Posture:** [How they're defending]
- **Activity Level:** [What they're currently doing]

## Key Locations

### Prospit Palace
- **Status:** [Intact/Damaged/Destroyed]
- **Occupants:** [Who's there]
- **Notes:** [Important details]

### The White Queen's Chambers
- **Status:** [State of the area]
- **Oracle Clouds:** [What they're showing]

### Battlefield Access
- **Status:** [Open/Guarded/Closed]
- **Defensive Preparations:** [Description]

## Prospitian Dreamers
Players whose dream selves are on Prospit:
- **[Player Name]:** [Dream self status]

## Recent Activity
- **[Date]:** [Event]

## Agents and Notable NPCs
- **[Agent Name]:** [Current activity and location]

## Strategic Notes
[Observations about Prospit's situation or opportunities]

## Last Updated
[Timestamp]
```

**When to update:** After events involving Prospit, or daily if Prospit is under threat.

---

### Skaia State Template

**Filename:** `session/skaia_state.md`

```markdown
# Skaia - Current State

## Overview
Skaia is the dormant creative force at the center of the Medium, appearing as a massive clouded sphere.

## Current Status
- **Awakening Progress:** [Percentage]
- **Battlefield Activity:** [Current state of the war]
- **Clouds Status:** [What visions they're showing]

## Battlefield

### Black Army
- **Strength:** [Troop counts and types]
- **Position:** [Where they are]
- **Strategy:** [What they're doing]

### White Army
- **Strength:** [Troop counts and types]
- **Position:** [Where they are]
- **Strategy:** [What they're doing]

### Battlefield Control
- **Territory:** [Who controls what percentage]
- **Major Fortifications:** [Key positions]

## The Seven Gates
Gates connecting Lands to Skaia and each other:
- **Gate 1:** [Status and destination]
- **Gate 2:** [Status and destination]
- **Gate 3:** [Status and destination]
- **Gate 4:** [Status and destination]
- **Gate 5:** [Status and destination]
- **Gate 6:** [Status and destination]
- **Gate 7:** [Status and destination]

## Prophetic Clouds
Recent visions shown by Skaia:
- **[Date]:** [Vision description]

## Critical Events
- **Black King Activity:** [What he's doing]
- **Prospit Status:** [How Prospit is faring in the war]
- **Derse Status:** [How Derse is advancing]

## Last Updated
[Timestamp]
```

**When to update:** After major battlefield events or when players interact with Skaia.

---

### Land State Template

**Filename:** `lands/[land_abbreviation]_state.md`

```markdown
# [Full Land Name] - Current State

## Overview
- **Abbreviation:** [LOAAG format]
- **Owner:** [Player Name] - [Class] of [Aspect]
- **Denizen:** [Denizen Name]

## Physical Environment
- **Biome:** [Type]
- **Dominant Colors:** [Color palette]
- **Climate:** [Weather and atmosphere]
- **Primary Features:** [Major terrain elements]

## The Problem
**Central Crisis:** [What's wrong with the Land]

**Current State:** [How bad it is now]

**Potential Solutions:** [What might fix it]

## Consort Population
- **Species:** [Type of consorts]
- **Population Status:** [Healthy/Suffering/Endangered]
- **Main Settlement:** [Village name and location]
- **Notable Consorts:**
  - **[Name]:** [Role and personality]

## Locations

### [Location Name]
- **Status:** [Explored/Unexplored/Partially Explored]
- **Features:** [What's here]
- **Enemies:** [What enemies are found here]
- **Secrets:** [Hidden things, puzzles]
- **Player Notes:** [What player has discovered]

## Quest Progress
- **Stage:** [Current stage of Land quest]
- **Completed Objectives:**
  - [Objective]
- **Active Objectives:**
  - [Objective]
- **Available Hints:** [Consort dialogue or clues]

## Denizen Status
- **Location:** [Where denizen resides]
- **Encountered:** [Yes/No]
- **Choice Offered:** [Yes - What choice / No]
- **Resolution:** [Not Yet / Player chose [option]]

## Quest Bed
- **Location:** [Discovered at [location] / Not yet found]
- **Accessibility:** [How to reach it]
- **Used:** [Yes/No]

## Recent Events
- **[Date]:** [Event description]

## Environmental Changes
Changes made by player actions:
- **[Date]:** [What changed]

## Last Updated
[Timestamp]
```

**When to update:** After any exploration, quest progress, or environmental changes.

---

### Timeline Template

**Filename:** `session/timeline.md`

```markdown
# Session Timeline

## Current Session Day: [Number]

## Recent Events (Last 10)

### Day [N], Entry [X] - [Timestamp]
**Player:** [Player Name]
**Location:** [Where it happened]
**Event:** [Description]
**Result:** [Outcome]
**Significance:** [Why this matters]

---

### Day [N-1], Entry [X-1] - [Timestamp]
...

## Major Milestones

### [Milestone Name] - Day [N]
**Description:** [What happened]
**Players Involved:** [Who was there]
**Impact:** [How this changed the session]

---

## Archive (Older Events)
[Move entries here after they're more than 20 entries old]

## Last Updated
[Timestamp]
```

**When to update:** After every significant player action or event.

---

### Sprite Template

**Filename:** `npcs/sprites/[sprite_name].md`

```markdown
# [Sprite Name]

## Identity
- **Owner:** [Player Name]
- **Full Name:** [Name including prototyping components]
- **Prototyped With:** 
  1. [First prototyping - pre/post entry]
  2. [Second prototyping - pre/post entry]

## Personality
**Core Traits:** [Key personality characteristics]

**Speech Pattern:** [How they talk - formal, cryptic, specific quirks]

**Relationship with Player:** [How they feel about their player]

## Knowledge
**What They Know:**
- [Topic]: [Level of knowledge]
- [Topic]: [Level of knowledge]

**What They Hide:** [Information they have but won't share directly]

## Abilities
**Granted by Prototypings:**
1. [Ability from first prototyping]
2. [Ability from second prototyping]

**Combat Capability:** [How strong they are]

## Current Status
- **Location:** [Where they are now]
- **Current Activity:** [What they're doing]
- **Mood:** [Current emotional state]

## Dialogue History
Recent important conversations:
- **[Date]:** [Topic discussed and key points]

## Plot Hooks
Things the sprite might reveal or do:
- [Hook]

## Last Updated
[Timestamp]
```

**When to update:** After any sprite interaction or when sprite does something significant.

---

### Alchemy Catalog Template

**Filename:** `alchemy/item_catalog.md`

```markdown
# Session Alchemy Catalog

This file tracks all items created through alchemy for reference and consistency.

## Weapons

### [Item Name]
- **Code:** [Alchemy Code]
- **Recipe:** [Item 1] && [Item 2]
- **Type:** [Weapon Type]kind
- **Power:** [Number]
- **Special Properties:** [Abilities]
- **Grist Cost:** [Detailed breakdown]
- **Creator:** [Player Name]
- **Created:** [Date]
- **Description:** [Full description of item]

## Armor

### [Item Name]
- **Code:** [Alchemy Code]
- **Recipe:** [Components]
- **Defense:** [Number]
- **Special Properties:** [Abilities]
- **Grist Cost:** [Detailed breakdown]
- **Creator:** [Player Name]
- **Created:** [Date]
- **Description:** [Full description]

## Tools

### [Item Name]
- **Code:** [Alchemy Code]
- **Recipe:** [Components]
- **Function:** [What it does]
- **Grist Cost:** [Detailed breakdown]
- **Creator:** [Player Name]
- **Created:** [Date]
- **Description:** [Full description]

## Consumables

### [Item Name]
- **Code:** [Alchemy Code]
- **Recipe:** [Components]
- **Effect:** [What it does when used]
- **Grist Cost:** [Detailed breakdown]
- **Creator:** [Player Name]
- **Created:** [Date]

## Failed Experiments
Items that didn't work or were rejected:
- **[Recipe]:** [Why it failed]

## Last Updated
[Timestamp]
```

**When to update:** Every time an item is alchemized.

---

### Active Encounters Template

**Filename:** `combat/active_encounters.md`

```markdown
# Active Combat Encounters

## [Player Name] vs [Enemies]

### Combat Status
- **Active:** [Yes/No]
- **Turn Count:** [Number]
- **Location:** [Where combat is happening]

### Player Status
- **HP:** [Current]/[Max]
- **Equipped Weapon:** [Weapon Name] (Power: [Number])
- **Status Effects:** [Any buffs/debuffs]
- **Available Actions:** [What they can do]

### Enemies

#### [Enemy Name/Type] #1
- **HP:** [Current]/[Max]
- **Type:** [Imp/Ogre/Basilisk/etc]
- **Prototyped Traits:** [Traits from session prototyping]
- **Abilities:** [What it can do]
- **Status Effects:** [Buffs/debuffs]
- **Behavior:** [How it's acting]

### Combat Log
- **Turn [N]:** [Player Action] → [Result] → [Enemy Action] → [Result]

### Environmental Factors
- [Terrain advantages/disadvantages]
- [Weather effects]
- [Other relevant factors]

### Victory Conditions
- **Player:** [How player wins]
- **Enemy:** [How enemies win]

### Expected Rewards
- **Grist:** [Types and amounts]
- **XP:** [Amount]
- **Special:** [Any unique rewards]

## Last Updated
[Timestamp]
```

**When to update:** Every combat turn, and when combat ends.

---

## Turn-by-Turn Example

### Example Turn Flow

**Player Action:**
> "I use my hammer to smash open the sealed door to the Denizen's lair."

**GM Turn Sequence:**

**1. Context Retrieval:**
```
RETRIEVE:
- characters/dave_strider_sheet.md
  → Level 15, Knight of Time, LOHAC
  → Currently at "Sealed Denizen Door"
- characters/dave_strider_inventory.md
  → Equipped: Temporal Warhammer (Power: 85)
- lands/lohac_state.md
  → Denizen: Abraxas
  → Sealed Door location and properties
- session/timeline.md
  → Last 5 events for context
```

**2. Action Processing:**
✓ Has hammer (in inventory)
✓ At correct location (confirmed in character sheet)
✓ Sufficient power level (Level 15 appropriate for this stage)
→ Action is valid and should succeed

**3. Response Generation:**
```
You raise the Temporal Warhammer, its surface rippling with 
distorted reflections of moments yet to come. The sealed door 
before you thrums with an ancient power—the same dull crimson 
pulse that permeates every crumbling tower of the Land of Heat 
and Clockwork.

The hammer crashes against the seal. Reality fractures at the 
point of impact, cracks spreading like frozen lightning through 
time itself. The door shudders, its gears grinding backward 
through centuries of rust, and then—

*CRASH*

The seal shatters. The door yawns open, revealing a massive 
chamber bathed in impossible red light. At its center, coiled 
around a pillar of brass gears that stretches into darkness above,
is Abraxas.

The Denizen's eyes open.

"Knight of Time," the serpent's voice echoes through your mind more
than your ears. "You have come seeking answers. But first, you must
choose."
```

**4. State Updates:**

**Update `characters/dave_strider_sheet.md`:**
```markdown
## Location & Status
- **Current Location:** Denizen Chamber (LOHAC)
- **Current Activity:** Confronting Abraxas
```

**Update `lands/lohac_state.md`:**
```markdown
### Sealed Denizen Door
- **Status:** Destroyed
- **Destroyed By:** Dave Strider using Temporal Warhammer
- **Date:** [Timestamp]

## Denizen Status
- **Encountered:** Yes - Day [N]
```

**Update `session/timeline.md`:**
```markdown
### Day [N], Entry [X] - [Timestamp]
**Player:** Dave Strider
**Location:** LOHAC - Sealed Denizen Door
**Event:** Dave destroyed the sealed door to Abraxas's chamber using 
his Temporal Warhammer. The seal shattered with temporal energy.
**Result:** Access to Denizen chamber gained. Abraxas encounter begun.
**Significance:** Major Land Quest milestone - Denizen confrontation 
imminent.
```

**5. Trigger Check:**
- Quest progress trigger → Update Dave's quest log with "Confronting Denizen" stage
- Event trigger → Abraxas encounter begins (prepare Denizen dialogue)
- No level up needed
- No new location unlocked (already at destination)

---

## Best Practices

### Consistency Rules

1. **Always retrieve before responding** - Never rely on memory alone
2. **Update immediately after response** - Don't wait, files must stay current
3. **Cross-reference facts** - If unsure, check multiple files
4. **Timestamp everything** - Track when changes happen
5. **Be specific with locations** - "LOWAS - Consort Village" not just "the village"

### Memory Management

1. **Recent events prioritized** - Timeline's last 10 entries are most relevant
2. **Character sheet is truth** - If files conflict, character sheet wins
3. **Session overview is anchor** - Defines what's possible session-wide
4. **Archive old data** - Move events older than 50 entries to archive section

### Error Prevention

1. **Validate actions against inventory** - Can't use items they don't have
2. **Check prerequisites** - Some actions need prior completion of others
3. **Respect established facts** - Don't contradict previous descriptions
4. **Maintain power scaling** - Level 5 player can't defeat Level 20 enemy
5. **Track resources** - Grist costs must be paid, HP must be tracked

### Narrative Quality

1. **Use specific details from files** - Reference actual item names, location descriptions
2. **Maintain character voice** - Personality notes guide how NPCs speak
3. **Build on previous events** - Callback to timeline entries naturally
4. **Respect pacing** - Check quest stage before introducing major reveals
5. **Stay true to Land themes** - Environmental descriptions match Land state file

---

## Retrieval Query Patterns

### Standard Turn Query
```
RETRIEVE:
- characters/[player]_sheet.md
- characters/[player]_inventory.md
- lands/[current_land]_state.md
- session/timeline.md (last 10 entries)
```

### Combat Turn Query
```
RETRIEVE:
- characters/[player]_sheet.md
- characters/[player]_inventory.md
- combat/active_encounters.md
- session/timeline.md (last 5 entries)
```

### Alchemy Turn Query
```
RETRIEVE:
- characters/[player]_inventory.md
- alchemy/item_catalog.md
- session/session_overview.md (for grist availability)
```

### NPC Interaction Query
```
RETRIEVE:
- characters/[player]_sheet.md
- npcs/[npc_type]/[npc_name].md
- [relevant_location]_state.md
- session/timeline.md (last 10 entries)
```

### Quest Progress Query
```
RETRIEVE:
- characters/[player]_quest_log.md
- characters/[player]_sheet.md
- lands/[land]_state.md
- session/session_overview.md
```

---

## Common Scenarios

### Scenario: Player Explores New Area

1. Retrieve: character sheet, inventory, land state
2. Check if area exists in land state file
3. Generate description matching Land themes
4. Add enemies appropriate to level
5. Update land state with new location entry
6. Add timeline entry
7. Check for quest-relevant discoveries

### Scenario: Player Attempts Alchemy

1. Retrieve: inventory, alchemy catalog, session overview
2. Verify player has both items
3. Check grist cache for sufficient resources
4. Generate logical combination result
5. Calculate grist cost
6. Add to alchemy catalog
7. Update inventory with new item and reduced grist
8. Add timeline entry

### Scenario: Player Levels Up

1. Retrieve: character sheet
2. Calculate new XP threshold
3. Generate creative Echeladder rung name
4. Determine stat increases
5. Check for ability unlocks
6. Update character sheet completely
7. Add timeline entry noting level up
8. Announce new rung dramatically

### Scenario: Player Talks to NPC

1. Retrieve: character sheet, NPC file, location state, timeline
2. Check relationship status in character sheet
3. Reference NPC personality and knowledge
4. Check what information NPC should know
5. Generate dialogue in NPC's voice
6. Update NPC dialogue history
7. Update character relationships if changed
8. Add timeline entry if significant

### Scenario: Combat Turn

1. Retrieve: character sheet, inventory, active encounters, timeline
2. Process player's combat action
3. Calculate damage/effects
4. Update enemy HP
5. Generate enemy response
6. Calculate enemy damage/effects
7. Update player HP
8. Add to combat log
9. Check for combat end conditions
10. If combat ends: award grist/XP, update files, archive encounter

---

## Startup Checklist

When starting a new session:

1. [ ] Create directory structure
2. [ ] Initialize session overview file
3. [ ] Create character sheets for all players
4. [ ] Create inventory files for all players
5. [ ] Create quest log files for all players
6. [ ] Generate Land state files for each player's Land
7. [ ] Initialize Derse state file
8. [ ] Initialize Prospit state file
9. [ ] Initialize Skaia state file
10. [ ] Create timeline file with "Session Start" entry
11. [ ] Create empty alchemy catalog
12. [ ] Create sprite files as they're prototyped

---

## Shutdown Checklist

At the end of each session:

1. [ ] Verify all character sheets updated
2. [ ] Verify all inventories updated
3. [ ] Verify timeline has all recent events
4. [ ] Verify all location states updated
5. [ ] Archive any completed combat encounters
6. [ ] Update session overview with current phase
7. [ ] Timestamp all modified files
8. [ ] Back up all files
9. [ ] Note any pending events for next session

---

## Emergency Recovery

If files are inconsistent or corrupted:

1. Check timeline for last verified state
2. Use character sheet as primary truth
3. Reconstruct from timeline entries
4. Ask player what they remember
5. Make conservative assumptions
6. Document the inconsistency in timeline
7. Rebuild from last known good state

---

## Advanced: Dynamic Event System

Some events trigger automatically based on state:

### Check Every Turn:

```python
# Pseudocode for automatic checks

if session.days_passed % 7 == 0:
    update_battlefield_state()
    
if player.xp >= next_level_threshold:
    trigger_level_up()
    
if land.denizen_encountered and not land.denizen_resolved:
    if days_since_encounter > 3:
        denizen_sends_message()
        
if session.god_tiers_achieved == session.total_players:
    unlock_final_phase()
```

### Event Triggers to Monitor:

- **Daily:** Check Derse/Prospit activity, battlefield progression
- **Per Level:** New rung, potential ability unlock
- **Quest Milestones:** Land problem progress, Denizen status
- **Session Milestones:** All players entered, first God Tier, etc.
- **Resource Thresholds:** First Zillium drop, 10000 grist cache, etc.

---

## Conclusion

By following this turn-by-turn protocol religiously, the GM maintains perfect consistency, never forgets details, and can scale to arbitrarily long campaigns. The key is discipline: always retrieve context before acting, always update state after acting, and always check for triggered events.

The RAG system is only as good as the maintenance of the files. Keep them updated, keep them organized, and keep them consistent.
