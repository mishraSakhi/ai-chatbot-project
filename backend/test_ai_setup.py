import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 AI Service Configuration Test\n")

# Check environment variables
gemini_key = os.getenv("GEMINI_API_KEY", "")
hf_token = os.getenv("HF_TOKEN", "")

print("1️⃣ Environment Variables:")
print(f"   GEMINI_API_KEY: {'✅ Set' if gemini_key and gemini_key != '.' else '❌ Not set'} ({gemini_key[:10] + '...' if len(gemini_key) > 10 else gemini_key})")
print(f"   HF_TOKEN: {'✅ Set' if hf_token and hf_token != '.' else '❌ Not set'} ({hf_token[:10] + '...' if len(hf_token) > 10 else hf_token})")

# Test imports and initialization
print("\n2️⃣ Testing AI Service:")
try:
    from app.services.ai_service import AIService
    ai_service = AIService()
    print(f"   Gemini enabled: {'✅' if ai_service.use_gemini else '❌'}")
    print(f"   HuggingFace enabled: {'✅' if ai_service.use_hf_api else '❌'}")
    
    # Test a simple generation
    if ai_service.use_gemini or ai_service.use_hf_api:
        print("\n3️⃣ Testing generation:")
        test_response = ai_service.generate_response(
            "What is OSSU?",
            [{"content": "OSSU is Open Source Society University", "metadata": {"source": "test"}}],
            []
        )
        print(f"   Response: {test_response[:100]}...")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n📝 Next Steps:")
if not (gemini_key and gemini_key != '.'):
    print("1. Get Gemini API key: https://makersuite.google.com/app/apikey")
    print("2. Update .env: GEMINI_API_KEY=your-actual-key")
if not (hf_token and hf_token != '.'):
    print("3. Get HuggingFace token: https://huggingface.co/settings/tokens")
    print("4. Update .env: HF_TOKEN=your-actual-token")