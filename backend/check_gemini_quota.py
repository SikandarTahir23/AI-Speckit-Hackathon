"""
Check Gemini API quota and test model access
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

print("=" * 60)
print("GEMINI API QUOTA CHECK")
print("=" * 60)

# Test models with simple request
test_models = [
    'gemini-flash-latest',
    'gemini-2.5-flash',
    'gemini-2.0-flash',
]

for model_name in test_models:
    print(f"\nTesting: {model_name}")
    print("-" * 60)

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            "Translate 'Hello' to Urdu in Urdu script:",
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=50,
            )
        )

        result = response.text.strip()
        print(f"[OK] Model accessible")
        print(f"Sample response: {result[:80]}")

        # Check if response has Urdu characters
        has_urdu = any(ord(c) >= 1536 and ord(c) <= 1920 for c in result[:100])
        print(f"Contains Urdu script: {has_urdu}")

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            print(f"[QUOTA ERROR] {error_msg[:150]}")
        elif "404" in error_msg:
            print(f"[NOT FOUND] Model not available")
        else:
            print(f"[ERROR] {error_msg[:150]}")

print("\n" + "=" * 60)
print("CHECK COMPLETE")
print("=" * 60)
