# backend/app/services/chat_service.py

from typing import List, Dict, Optional
from .vector_store import VectorStore
from .ai_service import AIService
from ..models import ChatMessage
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        """Initialize chat service with vector store and AI service"""
        try:
            self.vector_store = VectorStore()
            self.ai_service = AIService()
            logger.info("ChatService initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ChatService: {e}")
            raise
    
    def process_message(self, message: str, history: List[ChatMessage]) -> Dict:
        """
        Process a chat message and return response with sources
        
        Args:
            message: User's message
            history: Chat history
            
        Returns:
            Dict with 'response' and 'sources' keys
        """
        try:
            # Log the incoming message
            logger.info(f"Processing message: {message[:100]}...")
            
            # Search for relevant documents
            relevant_docs = self.vector_store.similarity_search(message, k=4)
            logger.info(f"Found {len(relevant_docs)} relevant documents")
            
            # Generate response using AI service
            response = self.ai_service.generate_response(
                query=message,
                context=relevant_docs,
                history=history
            )
            
            # Format sources - remove duplicates and clean up
            sources = []
            seen_sources = set()
            
            for doc in relevant_docs:
                source_name = doc.get('metadata', {}).get('source', 'Unknown')
                
                # Skip if we've already added this source
                if source_name in seen_sources:
                    continue
                    
                seen_sources.add(source_name)
                
                # Extract meaningful content preview
                content = doc.get('content', '')
                # Try to get the first paragraph or meaningful chunk
                content_preview = content[:300].strip()
                if len(content) > 300:
                    # Find a good break point
                    last_period = content_preview.rfind('.')
                    if last_period > 150:
                        content_preview = content_preview[:last_period + 1]
                    else:
                        content_preview += "..."
                
                sources.append({
                    'source': source_name,
                    'content': content_preview
                })
            
            # Limit to 3 most relevant sources
            sources = sources[:3]
            
            return {
                'response': response,
                'sources': sources
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            
            # Try to provide a helpful fallback response
            fallback_response = self._get_fallback_response(message)
            
            return {
                'response': fallback_response,
                'sources': []
            }
    
    def _get_fallback_response(self, message: str) -> str:
        """Provide a fallback response when AI services fail"""
        message_lower = message.lower()
        
        if 'programming language' in message_lower:
            return """The OSSU curriculum teaches multiple programming languages:
            
• **Python** - Used in introductory courses and data science
• **JavaScript** - For web development and full-stack applications  
• **C** - For systems programming and understanding low-level concepts
• **Java** - For object-oriented programming and algorithms
• **Haskell** - For functional programming paradigms
• **SQL** - For database management
• **Assembly** - In computer architecture courses (Nand2Tetris)

Each language is chosen to teach specific concepts and paradigms."""

        elif 'ossu' in message_lower and ('what' in message_lower or 'about' in message_lower):
            return """OSSU (Open Source Society University) is a complete, free, self-taught education in Computer Science using online materials. It follows the curriculum standards of undergraduate CS programs at top universities.

Key features:
• Completely free education using MOOCs and online resources
• Comprehensive curriculum covering all major CS topics
• Project-based learning with real-world applications
• Active community of learners worldwide
• Self-paced learning with suggested timelines"""

        elif 'how long' in message_lower or 'duration' in message_lower:
            return """The OSSU Computer Science curriculum typically takes 2-4 years to complete, depending on your pace:

• **Part-time (10-20 hours/week)**: 4-6 years
• **Half-time (20-30 hours/week)**: 2-3 years  
• **Full-time (40+ hours/week)**: 1.5-2 years

The curriculum includes approximately 2000 hours of study, similar to a traditional CS degree."""

        else:
            return """I apologize, but I'm having trouble accessing my knowledge base at the moment. 

Here are some topics I can help you with:
• Information about the OSSU curriculum structure
• Programming languages used in the courses
• Course prerequisites and difficulty levels
• Time commitment and duration estimates
• Specific course recommendations

Please feel free to ask about any of these topics!"""
    
    def get_suggested_questions(self) -> List[str]:
        """Return a list of suggested questions for the user"""
        return [
            "What is OSSU?",
            "Which programming languages are taught?",
            "How long does the curriculum take to complete?",
            "What are the prerequisites?",
            "Tell me about the Core CS courses",
            "What mathematics courses are included?",
            "How is OSSU different from a traditional CS degree?",
            "What projects will I build?"
        ]