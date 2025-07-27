from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from .api import chat
from .services.document_processor import DocumentProcessor
from .services.vector_store import VectorStore
from .config import settings
import os
import json

app = FastAPI(title="AI Chatbot API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    """Initialize vector store with documents on startup."""
    try:
        print("🚀 Starting AI Chatbot API...")
        
        # Check if markdown directory exists
        if not os.path.exists(settings.MARKDOWN_DIR):
            print(f"Creating markdown directory: {settings.MARKDOWN_DIR}")
            os.makedirs(settings.MARKDOWN_DIR, exist_ok=True)
        
        # List files in markdown directory
        print(f"📁 Checking markdown directory: {settings.MARKDOWN_DIR}")
        if os.path.exists(settings.MARKDOWN_DIR):
            files = os.listdir(settings.MARKDOWN_DIR)
            md_files = [f for f in files if f.endswith('.md')]
            print(f"   Found {len(md_files)} markdown files")
            
        # Process documents
        print("📄 Processing documents...")
        processor = DocumentProcessor(settings.MARKDOWN_DIR)
        documents = processor.process_documents()
        
        if not documents:
            print("⚠️  Warning: No documents found!")
            print(f"   Directory checked: {settings.MARKDOWN_DIR}")
        else:
            print(f"✅ Processed {len(documents)} document chunks")
            
        # Initialize vector store
        print("🗄️  Initializing vector store...")
        vector_store = VectorStore()
        
        # Create vector store with documents
        if documents:
            vector_store.create_or_load_vectorstore(documents)
        else:
            print("⚠️  Creating empty vector store (no documents)")
            vector_store.create_or_load_vectorstore([])
        
        # Store in app state - THIS IS CRITICAL
        app.state.vector_store = vector_store
        app.state.processor = processor
        app.state.is_ready = True  # Add this flag
        
        # Verify storage
        print("🔍 Verifying app state...")
        print(f"   Vector store stored: {hasattr(app.state, 'vector_store')}")
        print(f"   Processor stored: {hasattr(app.state, 'processor')}")
        
        print("✅ AI Chatbot API ready!")
        
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        import traceback
        traceback.print_exc()
        
        # Create minimal state even on error
        try:
            print("⚠️  Attempting to create minimal vector store...")
            app.state.vector_store = VectorStore()
            app.state.processor = None
            app.state.is_ready = True  # Still mark as ready for testing
            print("✅ Created minimal vector store")
        except Exception as fallback_error:
            print(f"❌ Could not create fallback vector store: {fallback_error}")
            app.state.vector_store = None
            app.state.processor = None
            app.state.is_ready = False

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
async def root():
    return {
        "message": "AI Chatbot API is running",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat/",
            "websocket": "/ws",
            "health": "/health",
            "docs": "/docs",
            "debug": "/debug"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint that frontend expects."""
    has_vector_store = hasattr(app.state, 'vector_store')
    vector_store_initialized = False
    
    if has_vector_store and app.state.vector_store:
        vector_store_initialized = hasattr(app.state.vector_store, 'vectorstore') and app.state.vector_store.vectorstore is not None
    
    # Add the field that frontend expects
    is_ready = hasattr(app.state, 'is_ready') and app.state.is_ready
    
    return {
        "status": "healthy" if has_vector_store else "unhealthy",
        "vector_store_ready": is_ready and vector_store_initialized,  # Frontend expects this field
        "services": {
            "vector_store": has_vector_store,
            "vector_store_initialized": vector_store_initialized,
            "processor": hasattr(app.state, 'processor'),
            "markdown_dir": settings.MARKDOWN_DIR,
            "markdown_dir_exists": os.path.exists(settings.MARKDOWN_DIR)
        }
    }

# ADD THIS NEW WEBSOCKET ENDPOINT
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for chat communication."""
    await websocket.accept()
    print("WebSocket connection established")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get('message', '')
            
            print(f"Received message: {user_message}")
            
            # Check if vector store is available
            if not hasattr(app.state, 'vector_store') or not app.state.vector_store:
                await websocket.send_json({
                    "response": "Sorry, the AI service is still initializing. Please try again in a moment.",
                    "sources": []
                })
                continue
            
            try:
                # Use your existing chat logic
                # Get the vector store
                vector_store = app.state.vector_store
                
                # Search for relevant documents
                relevant_docs = vector_store.similarity_search(user_message, k=3)
                
                # Format context from documents
                context = "\n\n".join([doc.page_content for doc in relevant_docs])
                
                # Create a response (you can integrate with your AI service here)
                if context:
                    response = f"Based on the available documentation:\n\n{context[:500]}..."
                    sources = [{"page_content": doc.page_content[:100], "metadata": doc.metadata} for doc in relevant_docs]
                else:
                    response = "I couldn't find relevant information in the documentation. Could you please rephrase your question?"
                    sources = []
                
                # Send response back to client
                await websocket.send_json({
                    "response": response,
                    "sources": sources
                })
                
            except Exception as e:
                print(f"Error processing message: {e}")
                await websocket.send_json({
                    "response": f"Sorry, I encountered an error: {str(e)}",
                    "sources": []
                })
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("WebSocket connection closed")
def _generate_answer(self, question: str, context: str, docs: list) -> str:
    """Generate a better answer based on the context."""
    question_lower = question.lower()
    
    # Extract key information based on question type
    if 'programming language' in question_lower or 'language' in question_lower:
        # Look for programming language mentions
        languages = []
        common_languages = ['python', 'java', 'javascript', 'c++', 'c', 'scheme', 'racket', 'ml', 'haskell', 'ruby', 'rust', 'go', 'kotlin', 'swift']
        
        for lang in common_languages:
            if lang.lower() in context.lower():
                languages.append(lang.capitalize())
        
        # Look for specific course mentions
        if 'cs50' in context.lower():
            languages.extend(['C', 'Python', 'SQL', 'JavaScript', 'HTML/CSS'])
        if 'intro' in context.lower() and 'programming' in context.lower():
            languages.append('Python')
        
        # Remove duplicates
        languages = list(set(languages))
        
        if languages:
            response = f"Based on the OSSU curriculum, the following programming languages are taught:\n\n"
            response += "• " + "\n• ".join(sorted(set(languages)))
            response += "\n\nThe curriculum typically starts with languages like Python or Scheme for introductory courses, "
            response += "then progresses to languages like C for systems programming, and includes various languages for specialized topics."
        else:
            response = "The curriculum covers multiple programming languages throughout different courses. "
            response += "Typically, introductory courses use Python or Scheme, systems courses use C, "
            response += "and various other languages are introduced for specific topics like web development (JavaScript) and functional programming (Haskell)."
        
        return response
    
    elif 'what is' in question_lower and 'ossu' in question_lower:
        # Extract OSSU description
        lines = context.split('\n')
        relevant_lines = []
        for line in lines:
            if any(term in line.lower() for term in ['ossu', 'open source society', 'curriculum', 'complete education']):
                relevant_lines.append(line.strip())
        
        if relevant_lines:
            return "OSSU (Open Source Society University) provides:\n\n" + '\n'.join(relevant_lines[:5])
        else:
            return "OSSU (Open Source Society University) offers a complete, free computer science education using online materials from top universities."
    
    elif 'course' in question_lower:
        # Extract course information
        courses = []
        lines = context.split('\n')
        for line in lines:
            if '|' in line and any(term in line.lower() for term in ['weeks', 'hours', 'course']):
                parts = line.split('|')
                if len(parts) >= 2:
                    course_name = parts[0].strip()
                    if course_name and not course_name.startswith('-'):
                        courses.append(course_name)
        
        if courses:
            response = "Here are some relevant courses:\n\n"
            for course in courses[:10]:  # Limit to 10 courses
                response += f"• {course}\n"
            return response
    
    # Default: Extract most relevant sentences
    return self._extract_relevant_sentences(context, question, max_sentences=5)

def _extract_relevant_sentences(self, context: str, question: str, max_sentences: int = 5) -> str:
    """Extract most relevant sentences from context."""
    # Split into sentences
    sentences = []
    for paragraph in context.split('\n\n'):
        sentences.extend(paragraph.split('. '))
    
    # Score sentences by relevance
    question_words = set(question.lower().split())
    scored_sentences = []
    
    for sentence in sentences:
        if len(sentence.strip()) < 10:  # Skip very short sentences
            continue
        sentence_words = set(sentence.lower().split())
        score = len(question_words.intersection(sentence_words))
        
        # Boost score for sentences with key terms
        if any(term in sentence.lower() for term in ['curriculum', 'course', 'programming', 'computer science']):
            score += 2
        
        scored_sentences.append((score, sentence.strip()))
    
    # Sort by score and return top sentences
    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    relevant = [sent for score, sent in scored_sentences[:max_sentences] if score > 0]
    
    if relevant:
        return '. '.join(relevant) + '.'
    else:
        return context[:500] + '...'
@app.get("/debug")
async def debug_info():
    """Debug endpoint to check system state."""
    debug_data = {
        "app_state": {
            "has_vector_store": hasattr(app.state, 'vector_store'),
            "has_processor": hasattr(app.state, 'processor'),
            "is_ready": hasattr(app.state, 'is_ready') and app.state.is_ready,
            "state_attributes": list(dir(app.state))
        },
        "settings": {
            "markdown_dir": settings.MARKDOWN_DIR,
            "chroma_dir": settings.CHROMA_DIR,
            "backend_dir": str(settings.BACKEND_DIR)
        },
        "files": {
            "markdown_files": [],
            "markdown_dir_exists": os.path.exists(settings.MARKDOWN_DIR)
        }
    }
    
    # List markdown files if directory exists
    if os.path.exists(settings.MARKDOWN_DIR):
        try:
            files = os.listdir(settings.MARKDOWN_DIR)
            debug_data["files"]["markdown_files"] = [f for f in files if f.endswith('.md')]
        except Exception as e:
            debug_data["files"]["error"] = str(e)
    
    return debug_data