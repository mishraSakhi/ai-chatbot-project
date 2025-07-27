# backend/test_server_status.py

import requests
import time

base_url = "http://localhost:8001"

print("🔍 Testing Server Status\n")

# Test basic connectivity
print("1. Testing server connectivity:")
try:
    response = requests.get(base_url, timeout=5)
    print(f"✅ Server is reachable at {base_url}")
    print(f"   Status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print(f"❌ Cannot connect to server at {base_url}")
    print("   Make sure the server is running: uvicorn app.main:app --reload --port 8001")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test common endpoints
print("\n2. Testing endpoints:")
endpoints = [
    ("/", "GET"),
    ("/health", "GET"),
    ("/chat", "POST"),
    ("/docs", "GET"),
    ("/api", "GET"),
]

for endpoint, method in endpoints:
    try:
        if method == "GET":
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
        else:
            response = requests.post(
                f"{base_url}{endpoint}", 
                json={"message": "test", "history": []},
                timeout=5
            )
        print(f"   {method} {endpoint}: {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"   {method} {endpoint}: ⏱️ Timeout")
    except Exception as e:
        print(f"   {method} {endpoint}: ❌ {type(e).__name__}")

# Check OpenAPI docs
print("\n3. Available routes (from /docs):")
try:
    response = requests.get(f"{base_url}/openapi.json", timeout=5)
    if response.status_code == 200:
        api_spec = response.json()
        for path, methods in api_spec.get("paths", {}).items():
            for method in methods:
                print(f"   {method.upper()} {path}")
except:
    print("   Could not fetch OpenAPI spec")