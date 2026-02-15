import os
from google import genai
from config import GEMINI_API_KEY

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Hello',
        config=genai.types.GenerateContentConfig(
            temperature=0.7
        )
    )
    print(f"Response text: {response.text}")
except Exception as e:
    print(f"Error: {e}")
