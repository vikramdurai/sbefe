import os
import json
import re
from config import (
    ENABLE_CONTEXT_CACHING,
    TEMPERATURE,
    SMALL_MODEL,
    MEDIUM_MODEL,
    LARGE_MODEL,
    SMALL_MODEL_BACKUPS,
    MEDIUM_MODEL_BACKUPS,
    LARGE_MODEL_BACKUPS,
    LLM_ROUTING_DEBUG,
)
from llm_client import LLMClient
from state_manager import StateManager
from cache_manager import CacheManager

class GameManager:
    def __init__(self, base_dir=".", players=[]):
        self.state_manager = StateManager(base_dir)
        self.state_manager.ensure_directories()
        
        # Initialize default game if needed, assume "Player"
        # self.state_manager.initialize_game("Player")
        self.state_manager.initialize_game(players)

        # timeout is handled at the asyncio level in server.py — no SDK-level timeout here
        self.llm = LLMClient()
        
        # Load Design Docs
        self.design_doc = self.read_local_file("docs/sburb_game_design.md")
        self.turn_guide = self.read_local_file("docs/sburb_gm_turn_guide.md")
        self.difficulty_guide = self.read_local_file("docs/sburb_difficulty_enforcement.md")
        self.multiplayer_guide = self.read_local_file("docs/sburb_multiplayer_design.md")
        
        # Initialize context caching
        self.cache_manager = None
        self.cached_context_name = None
        if ENABLE_CONTEXT_CACHING:
            self._initialize_cached_context()

    def read_local_file(self, filename):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return f.read()
        # Fallback to absolute path check if running from somewhere else
        abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if os.path.exists(abs_path):
             with open(abs_path, "r") as f:
                return f.read()
        return ""
    
    def _initialize_cached_context(self):
        """
        Initialize context caching for design documents.
        This significantly reduces token usage on subsequent turns.
        """
        try:
            self.cache_manager = CacheManager()
            design_docs = {
                'design_doc': self.design_doc,
                'turn_guide': self.turn_guide,
                'difficulty_guide': self.difficulty_guide,
                'multiplayer_guide': self.multiplayer_guide
            }
            self.cached_context_name = self.cache_manager.refresh_cache_if_needed(design_docs)
        except Exception as e:
            print(f"⚠ Context caching initialization failed: {e}")
            print("  Continuing without caching...")
            self.cache_manager = None
            self.cached_context_name = None

    def _detect_action_type(self, player_input):
        """
        Detect the type of action from player input for selective context loading.
        Returns: 'combat', 'exploration', 'social', 'inventory', or 'general'
        """
        input_lower = player_input.lower()
        
        # Combat keywords
        combat_keywords = ['attack', 'fight', 'battle', 'strike', 'defend', 'dodge', 'cast', 'strife']
        if any(kw in input_lower for kw in combat_keywords):
            return 'combat'
        
        # Inventory/Alchemy keywords
        inventory_keywords = ['alchemize', 'combine', 'inventory', 'use item', 'equip', 'craft']
        if any(kw in input_lower for kw in inventory_keywords):
            return 'inventory'
        
        # Social keywords
        social_keywords = ['talk', 'speak', 'ask', 'tell', 'pester', 'message', 'sprite']
        if any(kw in input_lower for kw in social_keywords):
            return 'social'
        
        # Exploration keywords
        exploration_keywords = ['explore', 'look', 'examine', 'search', 'go to', 'move', 'enter']
        if any(kw in input_lower for kw in exploration_keywords):
            return 'exploration'
        
        return 'general'

    def route_to_model(self, player_input: str, context: str, player=None) -> str:
        """Pick small/medium/large model tier based on action complexity and stakes."""
        input_lower = (player_input or "").lower()
        context_lower = (context or "").lower()

        navigation_keywords = ['go', 'move', 'enter', 'leave', 'travel', 'walk']
        examine_keywords = ['look', 'examine', 'inspect', 'search']
        combat_keywords = ['attack', 'fight', 'defend', "beat", 'abscond', 'strife', 'combat']
        alchemy_keywords = ['alchemize', 'combine', 'recipe', 'craft']
        high_stakes_keywords = ['denizen', 'god tier', 'ascend', 'session-wide', 'black king']

        if any(k in input_lower for k in high_stakes_keywords):
            return 'large'

        multiplayer_active = bool(player and getattr(player, 'party_id', None))
        if multiplayer_active:
            return 'large'

        if any(k in input_lower for k in combat_keywords):
            return 'medium'

        if any(k in input_lower for k in alchemy_keywords):
            if 'item_catalog' in context_lower:
                return 'small'
            return 'medium'

        if any(k in input_lower for k in navigation_keywords):
            return 'small'

        if any(k in input_lower for k in examine_keywords):
            if 'locations' in context_lower or 'land' in context_lower:
                return 'small'

        return 'medium'

    def _tone_prompt_section(self, model_tier: str) -> str:
        """Return tone rules tuned for Homestuck-style narration and model tier."""
        model_tuning = {
            'small': (
                "For smaller models: prioritize concise and casual over complex snark. "
                "Keep routine responses very short and clear."
            ),
            'medium': (
                "For medium models: maintain concise and snarky tone while staying readable."
            ),
            'large': (
                "For larger models: avoid verbosity drift. Keep your response under 50 words "
                "unless this is a dramatic moment."
            ),
        }.get(model_tier, "Be concise and casual.")

        return f"""
### TONE AND STYLE REQUIREMENTS

You are narrating a Homestuck-inspired RPG.

1. BE CONVERSATIONAL
- Write like you're texting a friend, not writing a novel.
- Sentence fragments are fine.
- Start sentences with "And" or "But" if it fits.
- Use second person perspective.

2. BE CONCISE
- Most routine responses should be 2-4 sentences.
- Exploration is usually 1-2 sentences.
- Combat is stat line + 1 sentence.
- Save longer prose for major dramatic moments.

3. BE SNARKY
- You can comment on dumb decisions.
- Acknowledge absurd situations without over-explaining.
- Mock failures lightly; celebrate wins loudly.

4. PROFANITY POLICY
- Mild profanity like "fuck," "shit," "damn," "hell," "ass" is allowed naturally.
- Use at most 1-2 times per response.
- Never use slurs or discriminatory language.

5. HOMESTUCK VOCAB
- Use terms like Captchalogue, Strife, Abscond, Echeladder naturally.
- Do not explain these terms unless directly asked.

6. RESPONSE LENGTH RULES
- Simple actions: 1-3 sentences max.
- Combat turns: stat line + 1-2 sentences.
- Dialogue: NPC speech + 1 sentence context.
- Complex actions: 3-5 sentences max.
- Go longer only for God Tier ascension, Denizen encounters, major reveals, session finales.

7. ANTI-PURPLE-PROSE RULES
- Avoid "You find yourself...", "The X seems to...", "As you approach..."
- Avoid flowery metaphor chains.
- Prefer blunt, direct description.

8. MODEL TUNING
- {model_tuning}
"""

    def _tone_examples_section(self) -> str:
        """Few-shot examples that anchor style and formatting."""
        return """
### TONE EXAMPLES

Example 1 - Navigation
Player: "go to consort village"
GM: "You head to the village. Takes a few minutes through purple sand.
The salamanders are doing salamander logistics: standing around and gossiping."

Example 2 - Combat
Player: "attack the imp"
GM: "You swing.
-> Hit! 18 damage
Imp HP: 12/50
The imp looks absolutely wrecked."

Example 3 - Failed Action
Player: "i jump the chasm"
GM: "You jump. You do not clear it.
-20 HP
Your HP: 45/100
That was a terrible plan."

Example 4 - Alchemy
Player: "combine hammer and laptop"
GM: "HAMMER && LAPTOP
Result: DIGITAL MALLET
It's a hammer with a keyboard welded into it. Obviously.
Attack: 30 (+5)
Cost: 300 Build, 50 Amber"

Example 5 - Discovery
Player: "examine weird pillar"
GM: "It's a crystal pillar that hums when you get close.
There are symbols cut into it your sprite pretends not to recognize.
[Touch it] [Ask sprite] [Leave]"
"""
    
    def get_game_context(self, player_input="", player=None):
        """
        Retrieves relevant game state files based on action type.
        Uses selective loading to reduce token usage.
        When a player is provided, loads that player's specific files.
        """
        context_parts = []
        
        # Helper to append content
        def add_file(path):
            content = self.state_manager.read_file(path)
            if content:
                context_parts.append(f"\n--- FILE: {path} ---\n{content}\n")
        
        # Derive player-specific file slugs
        if player:
            p_file = player.name.lower().replace(" ", "_")
            land_file = f"lands/{player.land}_state.md"
        else:
            p_file = "player"
            land_file = "lands/lowas_state.md"

        # Always load core files
        add_file("session/session_overview.md")
        add_file(f"characters/{p_file}_sheet.md")
        add_file("session/timeline.md")
        
        # Selective loading based on action type
        action_type = self._detect_action_type(player_input)
        
        if action_type == 'combat':
            add_file("combat/active_encounters.md")
            add_file(f"characters/{p_file}_inventory.md")
        elif action_type == 'inventory':
            add_file(f"characters/{p_file}_inventory.md")
            add_file("alchemy/recipes.md")
        elif action_type == 'social':
            add_file("npcs/sprites.md")
        elif action_type == 'exploration':
            add_file(land_file)
            add_file(f"characters/{p_file}_inventory.md")
        else:  # general
            add_file(f"characters/{p_file}_inventory.md")
            add_file(land_file)
            add_file("combat/active_encounters.md")
        
        return "".join(context_parts)

    def process_turn(self, player_input, player=None):
        # Get selective context based on action type
        context = self.get_game_context(player_input, player)
        model_tier = self.route_to_model(player_input, context, player)
        
        # System instruction (without design docs - those are cached)
        system_instruction = f"""
You are the Sburb Game Manager, an AI system running a Tabletop RPG session of Sburb (Homestuck).
Your goal is to provide a rich, narrative experience while strictly maintaining the game state in markdown files.

The design documents (DESIGN_DOC, TURN_GUIDE, DIFFICULTY_GUIDE, MULTIPLAYER_GUIDE) contain the rules and mechanics you must follow.

    {self._tone_prompt_section(model_tier)}

    {self._tone_examples_section()}

### INSTRUCTIONS
1. Analyze the PLAYER INPUT and the CURRENT CONTEXT.
2. Determine the outcome based on the rules (skills, items, location).
3. Generate a NARRATIVE RESPONSE describing the result.
4. Generate the STATE UPDATES required to reflect the changes in the files.
   - You MUST update the files to track location, inventory, health, quests, etc.
   - You MUST append to the timeline.
   - For any file you update, provide the **entire** new content of the file inside `<FILE path="...">` tags.

### RESPONSE FORMAT
You must output your response in the following strict format:

<NARRATIVE>
[Your narrative response to the player here]
</NARRATIVE>

<UPDATES>
<FILE path="path/to/file.md">
[FULL NEW CONTENT OF THE FILE]
</FILE>
...
</UPDATES>
"""

        active_player_section = ""
        if player:
            active_player_section = f"""\n### ACTIVE PLAYER
- **Name:** {player.name}
- **Title:** {player.title}
- **Land:** {player.land}
- **Player ID:** {player.player_id}
"""

        user_message = f"""
### CURRENT CONTEXT
{context}{active_player_section}
### PLAYER INPUT
"{player_input}"

Process this turn.
"""
        
        # Refresh cache if needed (handles expiry automatically)
        if self.cache_manager:
            design_docs = {
                'design_doc': self.design_doc,
                'turn_guide': self.turn_guide,
                'difficulty_guide': self.difficulty_guide,
                'multiplayer_guide': self.multiplayer_guide
            }
            self.cached_context_name = self.cache_manager.refresh_cache_if_needed(design_docs)

        # Build effective system instruction — design docs are inlined when
        # Gemini context caching is unavailable (other providers always inline).
        if self.cached_context_name:
            effective_system = system_instruction
        else:
            effective_system = f"""
{system_instruction}

### DESIGN DOCUMENTS
<DESIGN_DOC>
{self.design_doc}
</DESIGN_DOC>

<TURN_GUIDE>
{self.turn_guide}
</TURN_GUIDE>

<DIFFICULTY_GUIDE>
{self.difficulty_guide}
</DIFFICULTY_GUIDE>

<MULTIPLAYER_GUIDE>
{self.multiplayer_guide}
</MULTIPLAYER_GUIDE>
"""

        tier_model_map = {
            'small': [SMALL_MODEL] + SMALL_MODEL_BACKUPS,
            'medium': [MEDIUM_MODEL] + MEDIUM_MODEL_BACKUPS,
            'large': [LARGE_MODEL] + LARGE_MODEL_BACKUPS,
        }

        if model_tier == 'small':
            effective_system = (
                f"{effective_system}\n\n"
                "You are presenting pre-generated content. Do NOT invent major new details. "
                "Keep responses concise."
            )

        warnings = []
        tier_fallback_order = {
            'large': ['large', 'medium', 'small'],
            'medium': ['medium', 'small'],
            'small': ['small'],
        }

        # Build model attempts so each tier uses its own backups first.
        # Example (medium): medium primary -> medium backups -> small primary -> small backups.
        model_attempts: list[tuple[str, str]] = []
        seen_models = set()
        for tier_name in tier_fallback_order[model_tier]:
            for configured_model in tier_model_map[tier_name]:
                if not configured_model or configured_model in seen_models:
                    continue
                seen_models.add(configured_model)
                model_attempts.append((tier_name, configured_model))

        last_error = None
        text = ""
        for idx, (tier_name, model_hint) in enumerate(model_attempts):
            try:
                if LLM_ROUTING_DEBUG:
                    active = self.llm.active_provider_names
                    provider = active[0] if active else "unknown"
                    print(f"[LLM routing] tier={tier_name} provider={provider} model={model_hint}")
                text = self.llm.generate(
                    system_instruction=effective_system,
                    user_message=user_message,
                    temperature=TEMPERATURE,
                    cached_context_name=self.cached_context_name,
                    model_hint=model_hint,
                )
                if idx > 0:
                    if tier_name != model_tier:
                        warnings.append(f"Model fallback engaged: using {tier_name} tier model '{model_hint}'.")
                    else:
                        warnings.append(f"Model backup engaged for {tier_name} tier: '{model_hint}'.")
                break
            except Exception as e:
                last_error = e
                continue

        if not text:
            raise RuntimeError(
                f"All routed models failed for tier '{model_tier}'. Last error: {last_error}"
            )
        
        # Parse Response
        narrative = "No narrative generated."
        
        # Extract Narrative
        n_match = re.search(r"<NARRATIVE>(.*?)</NARRATIVE>", text, re.DOTALL)
        if n_match:
            narrative = n_match.group(1).strip()
        if warnings:
            narrative = f"[Routing Notice] {' '.join(warnings)}\n\n{narrative}"
        
        # Extract Updates using regex for <FILE> tags
        # We look for <FILE path="...">...</FILE>
        # Note: creates risk if file content contains </FILE>, but unlikely in MD context unless malicious.
        file_matches = re.finditer(r'<FILE path="(.*?)">(.*?)</FILE>', text, re.DOTALL)
        
        updates_count = 0
        for match in file_matches:
            path = match.group(1)
            content = match.group(2).strip()
            self.state_manager.write_file(path, content)
            updates_count += 1
            
        return narrative, updates_count

def generate_character_fields(character_data: dict) -> dict:
    """
    Use Gemini to generate mechanical character fields (class, aspect, land, etc.)
    from the character creator questionnaire, following the creator plan document.
    Returns a dict with all fields needed to join a session.
    Called before a session is joined — no GameManager instance needed.
    """
    _root = os.path.dirname(os.path.abspath(__file__))

    try:
        with open(os.path.join(_root, "docs/sburb_character_creator_plan.md")) as f:
            creator_plan = f.read()
    except FileNotFoundError:
        creator_plan = ""

    llm = LLMClient()

    system_instruction = (
        "You are the Sburb game engine performing character initialization. "
        "Given a player's questionnaire, assign their mechanical attributes following "
        "the Sburb Character Creator Plan. Respond ONLY with a single valid JSON object — "
        "no markdown fences, no commentary."
    )

    identity = character_data.get("identity", {})
    player_name = identity.get("name", "Player")

    prompt = f"""<CHARACTER_CREATOR_PLAN>
{creator_plan}
</CHARACTER_CREATOR_PLAN>

<CHARACTER_QUESTIONNAIRE>
{json.dumps(character_data, indent=2)}
</CHARACTER_QUESTIONNAIRE>

Assign mechanical attributes for the player named "{player_name}".
Return ONLY a valid JSON object with exactly these fields:
{{
  "player_name": "{player_name}",
  "player_class": "one of the 12 Homestuck classes",
  "aspect": "one of the 12 Homestuck aspects",
  "land": "SHORT LAND ACRONYM in caps, e.g. LOWAS, LOLAR, LOPAV (derive creatively from aspect + character theme)",
  "land_full": "Full land name, e.g. Land of Wind and Shade",
  "denizen": "The canonical Denizen matching their aspect",
  "echeladder_rung": "Creative first rung name — a punny nickname, 2-4 words",
  "strife_specibus": "Weapon type derived from interests, e.g. Hammerkind, Bladekind",
  "current_weapon": "Specific first weapon name matching the specibus",
  "sprite": "A home object or item that reflects their personality and interests, e.g. a harlequin doll",
  "lunar_sway": "Prospit or Derse"
}}

Do NOT include class or aspect in any explanation — they will be hidden from the player.
Title will be derived as "{{class}} of {{aspect}}" server-side.
Return ONLY the JSON object."""

    text = llm.generate(
        system_instruction=system_instruction,
        user_message=prompt,
        temperature=0.8,
    ).strip()
    # Strip markdown code fences if the model wraps them
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)

    fields = json.loads(text)

    # Derive title server-side — never trust model formatting
    fields["title"] = f"{fields['player_class']} of {fields['aspect']}"
    
    # Ensure player_name comes from identity, not the model
    fields["player_name"] = player_name

    return fields


if __name__ == "__main__":
    # Test
    gm = GameManager()
    print("GM Initialized.")
    resp = gm.process_turn("I look around my room.")
    print(resp)
