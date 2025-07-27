# backend/rebuild_vector_store.py

import os
import shutil
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStore
from app.config import settings

print("🔄 Rebuilding Vector Store with ALL markdown files\n")

# Clear existing vector store
if os.path.exists(settings.CHROMA_DIR):
    print("📁 Clearing existing vector store...")
    shutil.rmtree(settings.CHROMA_DIR)
    os.makedirs(settings.CHROMA_DIR)

# Process all documents including subdirectories
print("📄 Processing all markdown files...")
processor = DocumentProcessor(settings.MARKDOWN_DIR)
documents = processor.process_documents()

print(f"\n✅ Found {len(documents)} document chunks")

# Create new vector store
print("\n🗄️ Creating new vector store...")
vector_store = VectorStore()
vector_store.create_or_load_vectorstore(documents)

print("\n✅ Vector store rebuilt successfully!")

# Test with a query
print("\n🔍 Testing with sample query...")
results = vector_store.similarity_search("Introduction to Programming with Python CS50", k=3)
for i, result in enumerate(results):
    print(f"\nResult {i+1}:")
    print(f"Source: {result['metadata']['source']}")
    print(f"Content: {result['content'][:100]}...")