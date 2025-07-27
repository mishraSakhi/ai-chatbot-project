# backend/test_chat_api.py

import requests
import json
import time

print("🔍 Testing Chat API\n")

base_url = "http://localhost:8001"

# Wait a moment for server to fully initialize
print("⏳ Waiting for server to initialize...")
time.sleep(2)

# 1. Check health
print("\n1️⃣ Health Check:")
try:
    response = requests.get(f"{base_url}/health", timeout=5)
    health = response.json()
    print(f"   Status: {health.get('status')}")
    print(f"   Vector Store Ready: {health.get('vector_store_ready')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Check root endpoint
print("\n2️⃣ Root Endpoint:")
try:
    response = requests.get(base_url, timeout=5)
    data = response.json()
    print(f"   Message: {data.get('message')}")
    print(f"   Chat endpoint: {data.get('endpoints', {}).get('chat')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Test chat endpoint
print("\n3️⃣ Chat Endpoint Test:")
chat_url = f"{base_url}/api/chat/"

test_messages = [
    "What is OSSU?",
    "Which programming languages are taught?",
    "How long does it take to complete?"
]

for msg in test_messages:
    print(f"\n   Q: {msg}")
    try:
        response = requests.post(
            chat_url,
            json={"message": msg, "history": []},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('response', 'No response')
            print(f"   A: {answer[:150]}...")
            print(f"   Sources: {len(data.get('sources', []))}")
        else:
            print(f"   ❌ Error {response.status_code}: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Request error: {e}")

# 4. Check available endpoints
print("\n4️⃣ Available Endpoints:")
try:
    response = requests.get(f"{base_url}/docs", timeout=5)
    if response.status_code == 200:
        print("   ✅ API documentation available at: http://localhost:8001/docs")
except:
    pass