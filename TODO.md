# Sburb RPG: Implementation TODO List

## 1. UI Component Architecture

### Core Objective
Build a persistent, always-visible game state display with React components that update independently without full page rerenders.

### Components to Create

#### 1.1 Health/HP Display
- **Component:** `<HealthBar />`
- **Props:** `current`, `max`, `showNumbers` (bool)
- **Visual:** CSS-based bar that fills/empties smoothly (transition animation)
- **State updates:** WebSocket listener or polling from backend state file
- **Features:**
  - Color-coded: green (>70%), yellow (40-70%), red (<40%)
  - Flash red briefly when damage taken
  - Pulse/glow effect when healing
- **Location:** Top-left corner, always visible

#### 1.2 Experience/Level Display
- **Component:** `<ExperienceBar />`
- **Props:** `currentXP`, `xpToNextLevel`, `currentRung`, `level`
- **Visual:** 
  - Horizontal progress bar showing XP toward next level
  - Current Echeladder rung name displayed above bar
  - Level number prominently shown
- **Animations:**
  - Bar fills smoothly when XP gained
  - "Level Up!" explosion effect when threshold crossed
  - New rung name flies in from top
- **Location:** Top-center, below HP

#### 1.3 Grist Cache Display
- **Component:** `<GristDisplay />`
- **Props:** `gristCounts` (object: { Build: 450, Amber: 120, ... })
- **Visual:**
  - Compact list of grist types and amounts
  - Color-coded by grist type (Build=gray, Amber=orange, Ruby=red, etc.)
  - Shows only non-zero grist types by default, expandable to show all
- **Animations:**
  - Numbers count up/down when changed
  - Flash green when grist gained, red when spent
- **Location:** Top-right corner, collapsible

#### 1.4 Equipment Display
- **Component:** `<EquipmentPanel />`
- **Props:** `specibus`, `equippedWeapon` (object with name, attack, special)
- **Visual:**
  - Shows Strife Specibus type (e.g., "Hammerkind")
  - Current weapon with icon/name
  - Attack stat prominently displayed
  - Special abilities listed below
- **Interactive:** Click to expand full inventory
- **Location:** Bottom-left corner

#### 1.5 Inventory Panel (Expandable)
- **Component:** `<InventoryGrid />`
- **Props:** `items` (array), `fetchModus`, `modusRules`
- **Visual:**
  - Grid or list depending on Fetch Modus
  - Each item shows name, icon (if available), quantity
  - Grayed out if item is blocked by modus rules
- **Interactive:**
  - Click item to examine details
  - Drag-and-drop for certain modi
  - Special UI per modus type (e.g., Stack shows LIFO order, Hashmap shows keyword inputs)
- **Location:** Overlay that slides in from right when inventory button clicked

#### 1.6 Combat Status (Conditional)
- **Component:** `<CombatHUD />`
- **Props:** `enemies` (array), `turnState`, `availableActions`
- **Visibility:** Only renders when `inCombat === true`
- **Visual:**
  - Enemy list with HP bars
  - Turn indicator ("Your Turn" vs "Enemy Turn")
  - Action buttons generated dynamically
  - AP/resource meter if applicable
- **Layout:** Takes over bottom half of screen during combat
- **Location:** Bottom-center overlay

### State Management
- **Use React Context** or **Redux** for global game state
- WebSocket connection to backend pushes state updates
- Components subscribe to relevant slices of state
- Optimistic UI updates (instant feedback, confirmed by server)

### Implementation Priority
1. Health + XP bars first (most visible, most important)
2. Equipment display (needed for combat)
3. Combat HUD (needed before combat testing)
4. Inventory + Grist (can be placeholders initially)

---

## 2. Dynamic Action Buttons (LLM-Generated)

### Core Objective
Replace freeform text input with context-sensitive buttons for common actions, while still allowing custom text input for creativity.

### Implementation

#### 2.1 Button Generation at Session Start
- **When:** Big model (70B+) generates explorable world at session start
- **What to generate:** For each location, create a JSON structure:
```json
{
  "location": "Consort Village",
  "description": "Stone plaza with salamanders milling about",
  "actions": [
    {
      "label": "Talk to Village Elder",
      "action_type": "dialogue",
      "target": "village_elder",
      "icon": "💬"
    },
    {
      "label": "Examine Central Statue", 
      "action_type": "examine",
      "target": "statue",
      "icon": "🔍"
    },
    {
      "label": "Visit Market",
      "action_type": "navigate",
      "target": "market",
      "icon": "🛒"
    },
    {
      "label": "Leave Village",
      "action_type": "navigate",
      "target": "exit_menu",
      "icon": "🚶"
    }
  ]
}
```
- **Storage:** Save to `locations/[land_abbreviation]_[location_name].json`

#### 2.2 Dynamic Button Rendering
- **Component:** `<ActionButtons />`
- **Props:** `actions` (from location JSON), `customInputEnabled` (bool)
- **Rendering:**
  - Map through `actions` array
  - Create button for each with icon + label
  - Style based on `action_type` (dialogue=blue, examine=yellow, navigate=green, combat=red)
- **Interaction:**
  - Click button → send `action_type` + `target` to small model
  - Small model retrieves appropriate content and narrates
  - Custom text input always available below buttons

#### 2.3 Context-Sensitive Button Updates
- **Triggers:** When game state changes, update available actions
  - Combat starts → replace with `[Attack] [Defend] [Item] [Flee]`
  - Talking to NPC → replace with dialogue options from pre-generated tree
  - Alchemy screen → replace with `[Combine Items] [Check Recipe] [Cancel]`
- **Implementation:**
  - Backend tracks `current_context` in player state
  - Frontend requests button set for current context
  - Cache common button sets (combat, inventory, navigation) client-side

#### 2.4 Fallback for Unknown Actions
- **When:** Player types something not covered by buttons
- **Behavior:**
  - Check if action matches cached location content
  - If yes → small model narrates from cache
  - If no → escalate to big model, generate new content, add to cache
- **Example:**
  - Pre-generated: "Examine statue" → instant response
  - Player types: "Try to climb the statue" → escalate to big model → generate outcome → cache for future

### Button UX Details
- **Keyboard shortcuts:** Number keys (1-9) to click buttons
- **Hover tooltips:** Show brief description of what action does
- **Cooldowns:** Gray out buttons temporarily after use (e.g., can't spam "Attack")
- **Visual feedback:** Button glows when pressed, dims when action completes

---

## 3. Alchemy Interface

### Core Objective
Create a dedicated crafting screen that feels like a game (Minecraft, Terraria) rather than text commands.

### UI Design

#### 3.1 Layout
```
┌────────────────────────────────────────┐
│ ALCHEMITER                       [X]   │
├────────────────────────────────────────┤
│                                        │
│  ┌────────┐      ┌────────┐           │
│  │ SLOT 1 │  +   │ SLOT 2 │    →  ?   │
│  │ [____] │      │ [____] │           │
│  └────────┘      └────────┘           │
│                                        │
│  MODE: [&&] [||] [XOR]                 │
│        ⬆selected                       │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ COST: ??? grist                  │ │
│  │ (select items to see cost)       │ │
│  └──────────────────────────────────┘ │
│                                        │
│  [ALCHEMIZE] (grayed until ready)     │
│                                        │
├────────────────────────────────────────┤
│ YOUR INVENTORY                         │
│ ┌───┬───┬───┬───┬───┬───┬───┬───┐    │
│ │ H ││ S ││ L ││...│   │   │   │   │    │
│ └───┴───┴───┴───┴───┴───┴───┴───┘    │
│ H=Hammer, S=Shades, L=Laptop, ...     │
└────────────────────────────────────────┘
```

#### 3.2 Interaction Flow
1. **Open alchemy:** Click "Alchemize" button or use shortcut key (A)
2. **Select items:** Click inventory items to place in Slot 1 and Slot 2
3. **Choose mode:** Click &&, ||, or XOR operator
4. **Preview result:** Once both slots filled + mode selected, call backend:
   - **Endpoint:** `POST /api/alchemy/preview`
   - **Payload:** `{ item1: "hammer", item2: "laptop", mode: "&&" }`
   - **Response:** `{ result: "Technohammer", attack: 45, cost: {...}, description: "..." }`
5. **Show preview:** Display result item stats and grist cost
6. **Confirm or adjust:** Player can swap items/mode or click [Alchemize]
7. **Execute:** Call `POST /api/alchemy/create` → deduct grist → add item to inventory
8. **Close:** Return to main game view

#### 3.3 Backend Logic
- **Model to use:** 13B model (Mixtral or Qwen)
- **Prompt structure:**
```
You are generating an alchemy result for Sburb.

Item 1: {item1_name} (properties: {item1_props})
Item 2: {item2_name} (properties: {item2_props})
Mode: {mode}

Generate:
1. Result name (portmanteau or reference)
2. Result stats (attack/defense/special ability)
3. Grist cost (base cost * 2, scaled by power)
4. Brief description (1-2 sentences, Homestuck tone)

Output as JSON.
```
- **Caching:** Store generated recipes in `alchemy/item_catalog.md` so identical combinations are instant on repeat

#### 3.4 Special Features
- **Recipe book:** Button to view previously created items
- **Suggested combos:** If player hovers an item, show "pairs well with [X]" based on past successful recipes
- **Failed experiments:** Some combinations produce nothing → model decides if items are incompatible

---

## 4. Pesterlog Integration

### Core Objective
Allow players to message each other in-character, and make those messages visible to the GM when relevant.

### UI Design

#### 4.1 Pesterlog Window
- **Component:** `<PesterlogPanel />`
- **Visual:** Chat window styled like Pesterchum (Homestuck's chat client)
  - Player names in their typing color
  - Timestamps
  - Scrollable message history
- **Location:** Slide-in panel from right side, always accessible via button or hotkey (P)
- **Size:** Takes up 30% of screen width when open, collapsible to icon when closed

#### 4.2 Typing Quirks (Optional)
- **Feature:** Apply character-specific text transformations
- **Examples:**
  - Replace "b" with "8"
  - ALL CAPS WITH LOTS OF !!!
  - Replace "o" with "0"
- **Implementation:** Client-side string transformation before sending to backend
- **Storage:** Save quirk preference in character sheet

#### 4.3 Message Persistence
- **Storage:** `session/pesterlogs.md` or per-player `characters/[name]_pesterlogs.md`
- **Format:**
```markdown
## Pesterlog: [Player A] <--> [Player B]

[Timestamp] Player A: hey did you see that symbol in the sky
[Timestamp] Player B: yeah what the fuck was that
[Timestamp] Player A: i think someone just god tiered
[Timestamp] Player B: already??? we just started
```

#### 4.4 LLM Context Integration
- **When to include:** Only when players are in the same party/scene
- **How to include:** Append recent pesterlog (last 10-20 messages) to GM context:
```
### RECENT PESTERLOG CONVERSATION
Player A and Player B have been discussing:
[last 10 messages]

The GM should be aware of this context when narrating their shared scene.
```
- **Why:** GM can reference things they talked about, create callbacks, acknowledge their coordination

#### 4.5 Broadcast Messages
- **Special type:** Server-sent messages that appear in ALL pesterlogs simultaneously
- **Triggers:** God Tier ascension, major events, universe-wide announcements
- **Format:** 
```
[BROADCAST] The symbol of Breath blazes across the sky of every Land.
```
- **Styling:** Different color/font to distinguish from player messages

---

## 5. Staging Window Location Logic

### Core Objective
Only show the staging window when players are narratively in the same place, hide it otherwise.

### Implementation

#### 5.1 Location Tracking
- **Backend state:** Each player has `current_location` field in character sheet
  - Format: `[land_abbreviation]:[location_name]` 
  - Example: `"LOWAS:consort_village"` or `"LOHAC:denizen_chamber"`
- **Special locations:** `"party:[player1_name]_[player2_name]"` when actively in party

#### 5.2 Party Formation Detection
- **Trigger conditions:**
  - Two+ players have identical `current_location`
  - OR players explicitly form party via command ("join [player]")
  - OR combat encounter includes multiple players
- **Backend logic:**
```python
def check_party_formation(player_a, player_b):
    if player_a.location == player_b.location:
        return True
    if player_a.party_id == player_b.party_id:
        return True
    return False
```

#### 5.3 Staging Window Visibility
- **Component:** `<StagingWindow />`
- **Props:** `isVisible`, `partyMembers`, `currentDrafts`
- **Visibility logic:**
```javascript
const shouldShowStaging = () => {
  const playerLocation = gameState.player.location;
  const otherPlayers = gameState.session.players.filter(p => p.id !== gameState.player.id);
  
  return otherPlayers.some(p => 
    p.location === playerLocation || 
    p.partyId === gameState.player.partyId
  );
};
```

#### 5.4 UI Behavior
- **When staging activates:**
  - Slide in from bottom, above main input box
  - Show message: "You are now in a party with [Player B]"
  - Display both players' draft actions in real-time
- **When staging deactivates:**
  - Slide out with message: "Party disbanded" or "[Player B] left the area"
  - Return to solo play UI

#### 5.5 Edge Cases
- **Player leaves mid-turn:** Their action auto-submits if they disconnect
- **3+ players:** Staging shows all players' drafts, grid layout if needed
- **Rapid location changes:** Debounce party formation (2-second delay before staging activates) to avoid flickering

---

## 6. Multi-Tier LLM Routing

### Core Objective
Route requests to appropriately-sized models based on task complexity to balance speed and quality.

### Model Selection

#### 6.1 Small Model (7B-13B)
- **Recommended:** `meta-llama/llama-3.2-11b-vision-instruct` or `mistralai/mistral-7b-instruct`
- **Use cases:**
  - Navigation between pre-generated locations
  - Examining pre-generated objects/scenery
  - Retrieving consort dialogue from pre-generated trees
  - Presenting pre-generated action buttons
- **Expected latency:** < 2 seconds
- **Cost:** Nearly free on OpenRouter

#### 6.2 Medium Model (22B-72B)
- **Recommended:** `mistralai/mixtral-8x22b-instruct` or `qwen/qwen-2.5-72b-instruct`
- **Use cases:**
  - Combat encounters (action resolution, enemy AI)
  - Simple alchemy (common item combinations)
  - Basic quest progression
  - NPC conversations (non-critical NPCs)
- **Expected latency:** 5-15 seconds
- **Cost:** Low on OpenRouter free tier

#### 6.3 Large Model (405B+)
- **Recommended:** `nousresearch/hermes-3-llama-3.1-405b` or fallback to `anthropic/claude-3.5-sonnet`
- **Use cases:**
  - Complex multiplayer coordination
  - Denizen encounters (critical narrative moments)
  - Novel alchemy combinations (never seen before)
  - Session-wide state reasoning
  - God Tier ascension narration
- **Expected latency:** 15-60 seconds
- **Cost:** Use sparingly (50 requests/day limit on free tier)

### Routing Logic

#### 6.4 Decision Tree
```python
def route_to_model(player_input, game_state):
    # Check for pre-generated content match
    if is_navigation_command(player_input):
        return "small_model"
    
    if is_examination(player_input) and content_exists(player_input):
        return "small_model"
    
    # Check for state-changing actions
    if is_combat(game_state):
        return "medium_model"
    
    if is_alchemy(player_input):
        if recipe_cached(player_input):
            return "small_model"  # Just retrieve
        else:
            return "medium_model"  # Generate new
    
    # Check for high-stakes moments
    if is_denizen_encounter(game_state):
        return "large_model"
    
    if is_multiplayer_active(game_state):
        return "large_model"
    
    if is_god_tier_moment(game_state):
        return "large_model"
    
    # Default to medium for anything uncertain
    return "medium_model"
```

#### 6.5 Fallback Handling
- **If large model unavailable:** Fall back to medium model with warning to player
- **If medium model unavailable:** Fall back to small model, may produce lower quality output
- **If all unavailable:** Queue request and notify player of delay

#### 6.6 Prompt Differences by Model Size
**Small model prompt:**
```
You are presenting pre-generated content. Do NOT invent new details.

Available content:
{cached_content}

Player action: {input}

Present the relevant content naturally and concisely.
```

**Medium/Large model prompt:**
```
You are the Sburb Game Manager. Generate narrative and update game state.

[Full design docs + RAG context]

Player action: {input}
```

---

## 7. Response Streaming

### Core Objective
Display LLM output as it's being generated rather than waiting for completion, making long responses feel faster.

### Implementation

#### 7.1 Backend Streaming
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", ...)

def stream_gm_response(player_input, context):
    response = client.chat.completions.create(
        model="mistralai/mixtral-8x22b-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        stream=True  # Key parameter
    )
    
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

#### 7.2 Frontend Streaming (Server-Sent Events)
```javascript
// In your Next.js API route
export async function POST(request) {
  const encoder = new TextEncoder();
  
  const stream = new ReadableStream({
    async start(controller) {
      for await (const chunk of streamGMResponse(input, context)) {
        controller.enqueue(encoder.encode(`data: ${chunk}\n\n`));
      }
      controller.close();
    }
  });
  
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    }
  });
}
```

#### 7.3 Client-Side Rendering
```javascript
const [narrativeText, setNarrativeText] = useState('');
const [isStreaming, setIsStreaming] = useState(false);

const submitAction = async (action) => {
  setIsStreaming(true);
  setNarrativeText('');
  
  const response = await fetch('/api/game-turn', {
    method: 'POST',
    body: JSON.stringify({ action, context }),
  });
  
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    setNarrativeText(prev => prev + chunk);
  }
  
  setIsStreaming(false);
};
```

#### 7.4 XML Parsing During Streaming
- **Challenge:** State updates are in XML at the end of response
- **Solution:** Buffer full response, parse XML only after stream completes
```javascript
let fullResponse = '';

// During streaming
setNarrativeText(prev => prev + chunk);
fullResponse += chunk;

// After streaming completes
const narrativePart = extractNarrative(fullResponse);
const updatesPart = extractUpdates(fullResponse);
applyStateUpdates(updatesPart);
```

#### 7.5 Visual Indicators
- **Typing cursor:** Show blinking cursor at end of text while streaming
- **Streaming badge:** Display "GM is thinking..." badge while active
- **Progress:** Estimate progress based on token count (if available from API)

---

## 8. Homestuck Tone Adjustment

### Core Objective
Make the LLM's output match Homestuck's style: casual, snarky, profane, and weird.

### System Prompt Additions

#### 8.1 Tone Section
Add this to your system prompt:

```markdown
### TONE AND STYLE REQUIREMENTS

You are narrating a Homestuck-inspired RPG. Your narration must:

1. BE CONVERSATIONAL
   - Write like you're texting a friend, not writing a novel
   - Sentence fragments are fine
   - Start sentences with "And" or "But" freely
   - Use second person ("You do X") not third person

2. BE CONCISE
   - Most responses should be 2-4 sentences for simple actions
   - Combat: stat line + 1 sentence narration
   - Exploration: 1-2 sentences of description
   - Save long prose for dramatic moments only

3. BE SNARKY
   - Comment on player's dumb decisions
   - Acknowledge ridiculous situations
   - Mock failures (gently)
   - Celebrate successes with enthusiasm

4. USE PROFANITY NATURALLY
   - "fuck," "shit," "damn," "hell," "ass" are all fine
   - Use when appropriate for emphasis or frustration
   - Don't overdo it - maybe 1-2 per response at most
   - Never use slurs or discriminatory language

5. EMBRACE ABSURDITY
   - Sburb is weird. Treat weird things as normal.
   - Meteors, chess people, sprite fusions - all routine
   - Don't explain why things are weird

6. USE HOMESTUCK VOCABULARY
   - Captchalogue (verb: store item)
   - Strife (combat)
   - Abscond (flee)
   - Echeladder (levels)
   - Don't explain these - player knows them

EXAMPLES:

Bad (too formal):
"You successfully navigate to the northern section of the village."

Good (Homestuck style):
"You head north. The village elder's hut is right ahead."

Bad (too wordy):
"You swing your hammer with great force, striking the imp solidly and causing significant damage to its carapace."

Good (Homestuck style):
"You smash the imp with your hammer.
→ 25 damage
The imp staggers. That hurt."

Bad (no personality):
"You fail to open the door."

Good (Homestuck style):
"You try to force the door. It doesn't budge.
Strength check: 8 (needed 15+)
Yeah, that wasn't happening."
```

#### 8.2 Few-Shot Examples
Include 5-10 example interactions demonstrating the tone:

```markdown
### TONE EXAMPLES

Example 1 - Navigation:
Player: "go to consort village"
GM: "You head to the village. Takes like five minutes of walking through purple sand. 
The salamanders are doing their salamander thing - which is mostly standing around and talking."

Example 2 - Combat:
Player: "attack the imp"
GM: "You swing at the imp.
→ Hit! 18 damage
Imp HP: 12/50
The imp looks fucked up. One more hit should do it."

Example 3 - Failed Action:
Player: "i try to jump across the chasm"
GM: "You try to jump. You fail to jump.
You fall into the chasm.
-20 HP
Your HP: 45/100
That was dumb. There was a bridge right there."

Example 4 - Alchemy:
Player: "combine hammer and laptop"
GM: "HAMMER && LAPTOP
Result: DIGITAL MALLET
It's a hammer with a built-in keyboard. For... reasons.
Attack: 30 (+5)
Cost: 300 Build Grist, 50 Amber
[Alchemize] [Cancel]"

Example 5 - Discovery:
Player: "examine the weird pillar"
GM: "It's a pillar. Made of some kind of crystal that hums when you get close.
There are symbols carved into it you don't recognize.
Your sprite hovers nearby, watching you.
[Touch the pillar] [Ask sprite about it] [Leave it alone]"
```

#### 8.3 Response Length Constraints
Add explicit length guidance:

```markdown
RESPONSE LENGTH RULES:
- Simple actions (navigation, examination): 1-3 sentences MAX
- Combat turns: Stat line + 1-2 sentences
- Dialogue: NPC speech + 1 sentence of context
- Complex actions: 3-5 sentences MAX
- Only use more than 5 sentences for:
  * God Tier ascension
  * Denizen encounters  
  * Major story reveals
  * Session-ending moments

If you write more than 5 sentences for a routine action, you're doing it wrong.
```

#### 8.4 Anti-Purple-Prose Prompting
```markdown
BANNED PHRASES AND STYLES:
- "You find yourself..." (just say where they are)
- "The [object] seems to..." (just describe it)
- "As you approach..." (skip the preamble)
- Long descriptive metaphors
- Flowery adjectives
- Dramatic inner monologue

GOOD: "It's a tower. Looks important. There's probably a boss inside."
BAD: "The ancient tower looms before you, its weathered stones whispering secrets of ages past..."
```

#### 8.5 Model-Specific Tuning
Some models need different approaches:

**For Mixtral/Llama (naturally verbose):**
- Add to every prompt: "Keep your response under 50 words unless this is a dramatic moment."
- Use stop sequences to cut off after first 2-3 sentences

**For Hermes 3 (good at following tone):**
- The tone instructions above should work as-is
- May need to add: "Be slightly more casual than you think is appropriate"

**For smaller models (<13B):**
- Simplify tone instructions - focus on "be concise" and "be casual"
- May not be able to maintain snark consistently

### Testing Tone
Create a test suite of 10 common actions and verify tone:
```markdown
Test 1: "examine tower" 
Expected: 1-2 sentences, casual
Pass if: No purple prose, under 3 sentences

Test 2: "attack imp"
Expected: Stat line + 1 sentence
Pass if: Uses "→" notation, mentions damage number

Test 3: "try to do something impossible"
Expected: Failure + snarky comment
Pass if: Acknowledges stupidity, uses profanity optionally

[etc for other common actions]
```

Run this test suite against your model with the new system prompt. If >7/10 pass, tone is good enough.

---

## Implementation Priority

1. **UI components** (1-2 weeks)
   - Health/XP bars first (most visible)
   - Combat HUD (needed for testing)
   - Inventory/equipment (can be placeholder initially)

2. **LLM routing** (3-5 days)
   - Set up model switching logic
   - Test small model for navigation
   - Verify medium model for combat

3. **Response streaming** (2-3 days)
   - Implement SSE
   - Test with different model sizes
   - Polish UI rendering

4. **Tone adjustment** (1-2 days)
   - Update system prompts
   - Test against example interactions
   - Iterate based on output quality

5. **Alchemy interface** (3-5 days)
   - Build UI
   - Connect to backend
   - Test item generation

6. **Pesterlog system** (2-3 days)
   - Build chat UI
   - Implement persistence
   - Connect to LLM context

7. **Staging window** (2-3 days)
   - Location tracking logic
   - Visibility toggling
   - Multi-player testing

Total estimated time: 3-4 weeks for full implementation