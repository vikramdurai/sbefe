from game_manager import GameManager
import sys
import os

def main():
    print("Welcome to SBURB RPG Manager")
    print("----------------------------")
    
    # Check for .env
    if not os.path.exists(".env"):
        print("Warning: .env file not found. Please ensure GEMINI_API_KEY is set.")
    
    try:
        gm = GameManager()
        print("Game Initialized.")
    except Exception as e:
        print(f"Failed to initialize Game Manager: {e}")
        return

    print("You are the Heir of Breath in the Land of Wind and Shade.")
    print("Type 'quit' or 'exit' to stop.")
    print("----------------------------")

    while True:
        try:
            user_input = input("\n> ")
        except KeyboardInterrupt:
            break
            
        if user_input.lower() in ['quit', 'exit']:
            break
            
        if not user_input.strip():
            continue
            
        print("\nGM is thinking...")
        try:
            narrative, updates = gm.process_turn(user_input)
            print("\n" + narrative)
            if updates > 0:
                print(f"\n[System: Updated {updates} game state files]")
        except Exception as e:
            print(f"\n[Error: {e}]")

    print("\nSession saved. Goodbye.")

if __name__ == "__main__":
    main()
