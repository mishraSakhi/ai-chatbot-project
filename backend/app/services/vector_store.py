# backend/app/services/vector_store.py

import os
from typing import List, Dict, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
import chromadb
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.chroma_dir = settings.CHROMA_DIR
        os.makedirs(self.chroma_dir, exist_ok=True)
        
        # Initialize embeddings
        if settings.GEMINI_API_KEY:
            try:
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=settings.GEMINI_API_KEY
                )
                print("✓ Using Gemini embeddings")
            except Exception as e:
                print(f"Failed to initialize Gemini embeddings: {e}")
                self._use_fallback_embeddings()
        else:
            self._use_fallback_embeddings()
        
        # Don't initialize vector store here - wait for create_or_load_vectorstore
        self.vectorstore = None
    
    def _use_fallback_embeddings(self):
        """Use HuggingFace embeddings as fallback"""
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print("✓ Using HuggingFace embeddings (fallback)")
    
    def create_or_load_vectorstore(self, documents: List[Document]) -> None:
        """Create or load vector store with documents"""
        try:
            # Check if vector store already exists
            if os.path.exists(os.path.join(self.chroma_dir, "chroma.sqlite3")):
                logger.info("Loading existing vector store...")
                self.vectorstore = Chroma(
                    persist_directory=self.chroma_dir,
                    embedding_function=self.embeddings
                )
                
                # Check document count
                try:
                    existing_count = self.vectorstore._collection.count()
                    logger.info(f"✅ Loaded vector store with {existing_count} documents")
                    
                    # If empty, add documents
                    if existing_count == 0 and documents:
                        self._add_documents_batch(documents)
                except:
                    # If count fails, assume empty and add documents
                    if documents:
                        self._add_documents_batch(documents)
            else:
                # Create new vector store
                logger.info("Creating new vector store...")
                self.vectorstore = Chroma(
                    persist_directory=self.chroma_dir,
                    embedding_function=self.embeddings
                )
                
                if documents:
                    self._add_documents_batch(documents)
                else:
                    logger.warning("No documents provided for vector store")
                    
        except Exception as e:
            logger.error(f"Error creating/loading vector store: {e}")
            # Create minimal vector store
            self.vectorstore = Chroma(
                embedding_function=self.embeddings
            )
            logger.info("Created minimal in-memory vector store")
    
    def _add_documents_batch(self, documents: List[Document]) -> None:
        """Add documents in batches"""
        try:
            logger.info(f"Adding {len(documents)} documents to vector store...")
            
            # Add documents in batches to avoid memory issues
            batch_size = 10
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                self.vectorstore.add_documents(batch)
                logger.info(f"Added batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
            
            # Persist the vector store
            self.vectorstore.persist()
            logger.info(f"✅ Added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
    
    def similarity_search(self, query: str, k: int = 4) -> List[Dict]:
        """Search for similar documents"""
        try:
            if not self.vectorstore:
                logger.error("Vector store not initialized")
                return []
                
            results = self.vectorstore.similarity_search(query, k=k)
            
            # Convert results to dict format
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def add_documents(self, documents: List[Dict]) -> bool:
        """Add documents to the vector store"""
        try:
            if not self.vectorstore:
                logger.error("Vector store not initialized")
                return False
                
            # Convert dicts to Document objects if needed
            docs = []
            for doc in documents:
                if isinstance(doc, dict):
                    docs.append(Document(
                        page_content=doc.get('content', ''),
                        metadata=doc.get('metadata', {})
                    ))
                else:
                    docs.append(doc)
            
            self.vectorstore.add_documents(docs)
            self.vectorstore.persist()
            return True
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False
    
    def clear_vectorstore(self) -> bool:
        """Clear all documents from the vector store"""
        try:
            # Delete the persist directory
            import shutil
            if os.path.exists(self.chroma_dir):
                shutil.rmtree(self.chroma_dir)
                os.makedirs(self.chroma_dir, exist_ok=True)
            
            # Reinitialize
            self.vectorstore = None
            logger.info("✅ Vector store cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            return False
    
    def get_document_count(self) -> int:
        """Get the number of documents in the vector store"""
        try:
            if self.vectorstore:
                return self.vectorstore._collection.count()
            return 0
        except:
            return 0