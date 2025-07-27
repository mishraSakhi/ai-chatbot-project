# backend/test_chat_endpoint.py

import requests
import json

base_url = "http://localhost:8001"  # Change port if needed

print("🔍 Testing Chat Endpoint\n")

# Test questions
test_questions = [
    "What is OSSU?",
    "Which programming languages are taught?",
    "How long does the curriculum take?",
    "What are the core CS courses?",
    "Tell me about the math requirements"
]

for question in test_questions:
    print(f"\n📝 Question: {question}")
    
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={"message": question, "history": []},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data.get('response', '')[:200]}...")
            print(f"📚 Sources: {len(data.get('sources', []))}")
            for source in data.get('sources', [])[:2]:
                print(f"   - {source.get('source', 'Unknown')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

# Also test the health endpoint
print("\n🏥 Testing health endpoint:")
try:
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")