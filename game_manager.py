import os
import json
import re
from google import genai
from config import GEMINI_API_KEY
from state_manager import StateManager

class GameManager:
    def __init__(self, base_dir="."):
        self.state_manager = StateManager(base_dir)
        self.state_manager.ensure_directories()
        
        # Initialize default game if needed, assume "Player"
        self.state_manager.initialize_game("Player")
        
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        # Using gemini-3-flash-preview as requested/available
        self.model_name = 'gemini-3-flash-preview'
        
        # Load Design Docs
        self.design_doc = self.read_local_file("sburb_game_design.md")
        self.turn_guide = self.read_local_file("sburb_gm_turn_guide.md")
        
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

    def get_game_context(self):
        """
        Retrieves relevant game state files.
        For prototype simplicity, we retrieve the active character, 
        current land, session overview, timeline, and active combat.
        """
        # In a real implementation, we'd parse the request to know which files.
        # Here we just grab the basics for "Player".
        
        context_parts = []
        
        # Helper to append content
        def add_file(path):
            content = self.state_manager.read_file(path)
            if content:
                context_parts.append(f"\n--- FILE: {path} ---\n{content}\n")
        
        # Hardcoded context scope for "Player" (MVP)
        # TODO: Make this dynamic based on player name/action
        add_file("session/session_overview.md")
        add_file("characters/player_sheet.md")
        add_file("characters/player_inventory.md")
        add_file("lands/lowas_state.md") # Assuming Player is in LOWAS
        add_file("session/timeline.md")
        
        # Check for active combat
        # (Naive check: if file exists and has content)
        add_file("combat/active_encounters.md")
        
        return "".join(context_parts)

    def process_turn(self, player_input):
        context = self.get_game_context()
        
        system_prompt = f"""
You are the Sburb Game Manager, an AI system running a Tabletop RPG session of Sburb (Homestuck).
Your goal is to provide a rich, narrative experience while strictly maintaining the game state in markdown files.

### DESIGN DOCUMENTS
You must follow the rules and mechanics described in these documents:

<DESIGN_DOC>
{self.design_doc}
</DESIGN_DOC>

<TURN_GUIDE>
{self.turn_guide}
</TURN_GUIDE>

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

        user_message = f"""
### CURRENT CONTEXT
{context}

### PLAYER INPUT
"{player_input}"

Process this turn.
"""
        
        # Call Gemini (google-genai)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=system_prompt + user_message,
            config=genai.types.GenerateContentConfig(
                temperature=0.7 
            )
        )
        
        text = response.text
        
        # Parse Response
        narrative = "No narrative generated."
        
        # Extract Narrative
        n_match = re.search(r"<NARRATIVE>(.*?)</NARRATIVE>", text, re.DOTALL)
        if n_match:
            narrative = n_match.group(1).strip()
        
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

if __name__ == "__main__":
    # Test
    gm = GameManager()
    print("GM Initialized.")
    resp = gm.process_turn("I look around my room.")
    print(resp)
