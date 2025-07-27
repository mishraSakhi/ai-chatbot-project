# backend/test_gemini_models.py

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("🔍 Testing Gemini Models\n")

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    
    print("Available models:")
    try:
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"  ✓ {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
    
    print("\nTesting models:")
    # Try different model names
    models_to_test = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    
    for model_name in models_to_test:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello")
            print(f"  ✓ {model_name}: {response.text[:50]}...")
        except Exception as e:
            print(f"  ✗ {model_name}: {str(e)[:100]}...")
else:
    print("No API key found!")