from fastapi import APIRouter, HTTPException, Request
from ..models import ChatRequest, ChatResponse, ChatMessage
from ..services.ai_service import AIService
from typing import Dict, List
import uuid

router = APIRouter()

# In-memory session storage
sessions: Dict[str, list] = {}

@router.post("/", response_model=ChatResponse)
async def chat(request: Request, chat_request: ChatRequest):
    """Handle chat requests."""
    try:
        # Get vector store from app state
        vector_store = request.app.state.vector_store
        
        # Initialize AI service (with fallback)
        ai_service = AIService()
        
        # Get or create session
        session_id = chat_request.session_id or str(uuid.uuid4())
        if session_id not in sessions:
            sessions[session_id] = []
        
        # Search for relevant documents
        search_results = vector_store.similarity_search(
            chat_request.message, 
            k=4
        )
        
        # Convert search results to consistent format
        context_dicts = []
        sources = []
        
        for result in search_results:
            # Handle both dict and Document object formats
            if isinstance(result, dict):
                # It's already a dict
                context_dicts.append({
                    'content': result.get('content', result.get('page_content', '')),
                    'metadata': result.get('metadata', {})
                })
                if result.get('metadata', {}).get('source'):
                    sources.append(result['metadata']['source'])
            else:
                # It's a Document object
                context_dicts.append({
                    'content': getattr(result, 'page_content', str(result)),
                    'metadata': getattr(result, 'metadata', {})
                })
                if hasattr(result, 'metadata') and result.metadata.get('source'):
                    sources.append(result.metadata['source'])
        
        # Generate response using AI service with fallback
        response_text = ai_service.generate_response(
            query=chat_request.message,
            context=context_dicts,
            history=sessions[session_id][-10:]
        )
        
        # Update session history
        sessions[session_id].append(ChatMessage(
            role="user",
            content=chat_request.message
        ))
        sessions[session_id].append(ChatMessage(
            role="assistant",
            content=response_text
        ))
        
        # Get unique sources (only first 3)
        unique_sources = list(set(sources[:3])) if sources else []
        
        return ChatResponse(
            response=response_text,
            sources=unique_sources,
            session_id=session_id
        )
        
    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{session_id}")
async def clear_session(session_id: str):
    """Clear chat session."""
    if session_id in sessions:
        del sessions[session_id]
    return {"message": "Session cleared"}