# backend/check_chat_implementation.py

import os
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("🔍 Checking Chat Implementation\n")

# Check main.py for routes
print("1. Checking main.py for routes:")
try:
    with open('app/main.py', 'r') as f:
        content = f.read()
        if 'chat' in content:
            print("✓ Found 'chat' references in main.py")
            # Show relevant lines
            for i, line in enumerate(content.split('\n')):
                if 'chat' in line.lower():
                    print(f"  Line {i+1}: {line.strip()}")
except Exception as e:
    print(f"❌ Error reading main.py: {e}")

# Check for chat routes in api folder
print("\n2. Checking API folder:")
api_dir = Path('app/api')
if api_dir.exists():
    for file in api_dir.glob('*.py'):
        print(f"  Found: {file.name}")
        if 'chat' in file.name:
            print(f"    ✓ This might be the chat endpoint!")

# Let's check if there's a chat endpoint directly
print("\n3. Looking for chat endpoint implementation:")
for root, dirs, files in os.walk('app'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    if '@app.post("/chat")' in content or '@router.post("/chat")' in content:
                        print(f"✓ Found chat endpoint in: {filepath}")
                        # Show the endpoint
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if '@' in line and '/chat' in line:
                                print(f"\nChat endpoint implementation:")
                                for j in range(i, min(i+20, len(lines))):
                                    print(f"  {lines[j]}")
                                break
            except Exception as e:
                pass

# Check vector store documents
print("\n4. Checking Vector Store contents:")
try:
    from app.services.vector_store import VectorStore
    vector_store = VectorStore()
    
    # Test a basic search
    test_results = vector_store.similarity_search("OSSU", k=2)
    print(f"✓ Vector store is accessible, found {len(test_results)} results for 'OSSU'")
    
    if test_results:
        print("\nSample document:")
        print(f"  Source: {test_results[0].get('metadata', {}).get('source', 'Unknown')}")
        print(f"  Content preview: {test_results[0].get('content', '')[:100]}...")
except Exception as e:
    print(f"❌ Error accessing vector store: {e}")

# Check AI service
print("\n5. Checking AI Service:")
try:
    from app.services.ai_service import AIService
    ai_service = AIService()
    print(f"✓ Gemini enabled: {ai_service.use_gemini}")
    print(f"✓ HuggingFace enabled: {ai_service.use_hf_api}")
except Exception as e:
    print(f"❌ Error accessing AI service: {e}")

# List all Python files in services
print("\n6. All files in services folder:")
services_dir = Path('app/services')
if services_dir.exists():
    for file in services_dir.glob('*.py'):
        print(f"  - {file.name}")