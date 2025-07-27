# backend/test_chat_flow.py

import os
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Let's trace through the chat flow
print("🔍 Checking Chat Service Implementation\n")

# First, check if chat_service exists
try:
    from app.services.chat_service import ChatService
    print("✓ ChatService found")
    
    # Create instance
    chat_service = ChatService()
    
    # Test a simple query
    test_query = "Which programming languages are taught in OSSU?"
    print(f"\nTesting query: '{test_query}'")
    
    response = chat_service.process_message(test_query, [])
    print(f"Response type: {type(response)}")
    print(f"Response: {response.get('response', 'No response')[:200]}...")
    
except ImportError:
    print("❌ ChatService not found - checking API routes directly")
    
    # Check the API implementation
    try:
        from app.api import chat
        print("✓ Chat API routes found")
    except ImportError:
        print("❌ Chat API routes not found")