from google import genai
from config import GEMINI_API_KEY
import os

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # try loading again just in case
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model='gemini-3-flash-preview',
        contents='Hello',
        config=genai.types.GenerateContentConfig(
            temperature=0.7
        )
    )
    print(f"Response text: {response.text}")
except Exception as e:
    print(f"Error: {e}")
