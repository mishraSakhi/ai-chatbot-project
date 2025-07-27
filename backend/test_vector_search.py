# backend/test_vector_search.py

import os
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.vector_store import VectorStore

# Initialize vector store
vector_store = VectorStore()

# Test queries
test_queries = [
    "Which programming languages are taught?",
    "programming languages",
    "languages used in OSSU",
    "What is OSSU?",
    "core curriculum",
    "Python",
    "JavaScript",
    "Haskell"
]

print("🔍 Testing Vector Store Search\n")

for query in test_queries:
    print(f"Query: '{query}'")
    try:
        results = vector_store.similarity_search(query, k=3)
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results):
            source = result.get('metadata', {}).get('source', 'Unknown')
            content_preview = result.get('content', '')[:150] + "..."
            print(f"  {i+1}. Source: {source}")
            print(f"     Content: {content_preview}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()

# Let's also check what documents are in the vector store
print("\n📊 Vector Store Statistics:")
try:
    # Get collection info
    collection = vector_store.vectorstore._collection
    print(f"Total documents: {collection.count()}")
except Exception as e:
    print(f"Could not get stats: {e}")