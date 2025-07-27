import os
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, markdown_dir: str):
        self.markdown_dir = markdown_dir
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def process_documents(self) -> List[Document]:
        """Process all markdown files in the directory and subdirectories."""
        documents = []
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(self.markdown_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Create relative path for source
                        rel_path = os.path.relpath(file_path, self.markdown_dir)
                        
                        # Split into chunks
                        chunks = self.text_splitter.create_documents(
                            texts=[content],
                            metadatas=[{"source": rel_path, "file": file}]
                        )
                        
                        documents.extend(chunks)
                        logger.info(f"Processed: {rel_path} ({len(chunks)} chunks)")
                        
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
        
        logger.info(f"Total documents processed: {len(documents)}")
        return documents
