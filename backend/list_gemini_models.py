"""
List available Gemini models
"""
import google.generativeai as genai
import os
from utils.config import settings

# Get API key
gemini_api_key = os.getenv('GEMINI_API_KEY') or settings.GEMINI_API_KEY if hasattr(settings, 'GEMINI_API_KEY') else None

if not gemini_api_key:
    print("ERROR: GEMINI_API_KEY not found")
    exit(1)

genai.configure(api_key=gemini_api_key)

print("Available Gemini Models:")
print("=" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"[OK] {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description[:80]}")
        print()
