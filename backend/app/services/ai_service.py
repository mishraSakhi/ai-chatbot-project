# backend/app/services/ai_service.py

import google.generativeai as genai
import requests
import os
from typing import List, Dict
from ..config import settings
from ..models import ChatMessage

class AIService:
    def __init__(self):
        self.use_gemini = False
        self.use_hf_api = False
        
        # Try to initialize Gemini with the correct model
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip() != "":
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                # Use gemini-1.5-flash which we confirmed works
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                # Test the model with a simple request
                test_response = self.gemini_model.generate_content("test")
                self.use_gemini = True
                print("✓ Gemini API initialized with gemini-1.5-flash")
            except Exception as e:
                print(f"✗ Gemini API failed: {e}")
                # Still try to set up the model for later use
                try:
                    self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                    self.use_gemini = True  # Enable it anyway, handle errors during generation
                except:
                    pass
        
        # Setup Hugging Face as fallback
        self.hf_token = os.getenv("HF_TOKEN", "")
        if self.hf_token and self.hf_token.strip() != "":
            self.use_hf_api = True
            # Try multiple models in order of preference
            self.hf_models = [
                "mistralai/Mistral-7B-Instruct-v0.2",
                "meta-llama/Llama-2-7b-chat-hf",
                "google/flan-t5-large"
            ]
            self.current_hf_model = 0
            print("✓ Hugging Face API initialized as fallback")
    
    def _get_hf_url(self):
        """Get the current HF model URL"""
        return f"https://api-inference.huggingface.co/models/{self.hf_models[self.current_hf_model]}"
    
    def generate_response(self, query: str, context: List[Dict], history: List[ChatMessage]) -> str:
        """Generate response using available AI service."""
        
        # Format context - limit length to avoid token limits
        context_texts = []
        for item in context[:3]:  # Only use top 3 results
            source = item.get('metadata', {}).get('source', 'Unknown')
            content = item.get('content', '')[:500]  # Limit content length
            context_texts.append(f"From {source}:\n{content}")
        
        context_text = "\n\n".join(context_texts)
        
        # Debug print
        print(f"Query: {query}")
        print(f"Context items: {len(context)}")
        print(f"Using Gemini: {self.use_gemini}, Using HF: {self.use_hf_api}")
        
        # Try Gemini first
        if self.use_gemini:
            prompt = f"""You are a helpful and knowledgeable assistant for the OSSU (Open Source Society University) Computer Science curriculum.

IMPORTANT INSTRUCTIONS:
1. Always provide comprehensive, helpful answers even if the exact information isn't in the provided context
2. Use your knowledge about computer science education to supplement the context
3. For programming language questions, mention ALL languages used in OSSU: Python, JavaScript, C, Java, Haskell, SQL, Scheme/Racket, ML/OCaml, Ruby, etc.
4. For specific course questions like "Introduction to Programming with Python", provide details about CS50P from Harvard
5. Don't say "the document doesn't contain" - instead provide the best answer you can

Context from documentation:
{context_text}

User Question: {query}

Please provide a clear, concise answer based on the context above. If the answer is not in the context, say so."""
            
            try:
                response = self.gemini_model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    print(f"Gemini quota exceeded, falling back to HuggingFace...")
                else:
                    print(f"Gemini error: {e}, falling back...")
        
        # Fallback to Hugging Face
        if self.use_hf_api:
            return self._try_huggingface(query, context_text)
        
        # Final fallback - format context nicely
        return self._format_context_response(context_text, query)
    
    def _try_huggingface(self, query: str, context_text: str) -> str:
        """Try HuggingFace models with fallback"""
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        # Try each model until one works
        for i in range(len(self.hf_models)):
            model_name = self.hf_models[self.current_hf_model]
            print(f"Trying HF model: {model_name}")
            
            # Format prompt based on model type
            if "mistral" in model_name.lower() or "llama" in model_name.lower():
                prompt = f"[INST] You are a helpful assistant. Based on this context:\n{context_text[:1000]}\n\nAnswer this question: {query} [/INST]"
            else:  # T5 style
                prompt = f"Answer based on context. Context: {context_text[:500]} Question: {query} Answer:"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 300,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            try:
                response = requests.post(
                    self._get_hf_url(), 
                    headers=headers, 
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        answer = result[0].get('generated_text', '').strip()
                        if answer:
                            return answer
                    elif isinstance(result, dict):
                        answer = result.get('generated_text', '').strip()
                        if answer:
                            return answer
                elif response.status_code == 503:
                    # Model is loading, try next one
                    self.current_hf_model = (self.current_hf_model + 1) % len(self.hf_models)
                    continue
                else:
                    print(f"HF API error for {model_name}: {response.status_code}")
                    self.current_hf_model = (self.current_hf_model + 1) % len(self.hf_models)
                    continue
            except Exception as e:
                print(f"HF error for {model_name}: {e}")
                self.current_hf_model = (self.current_hf_model + 1) % len(self.hf_models)
                continue
        
        # If all HF models fail, return formatted context
        return self._format_context_response(context_text, query)
    
    def _format_context_response(self, context_text: str, query: str) -> str:
        """Format context as a response when AI is not available."""
        query_lower = query.lower()
        
        # Provide structured answers for common questions
        if 'ossu' in query_lower and ('what' in query_lower or 'about' in query_lower):
            return """OSSU (Open Source Society University) is a complete, self-taught education in Computer Science using free online materials. 

It's designed to mirror the curriculum of an undergraduate CS degree and includes:
- Rigorous coursework from MIT, Harvard, Princeton, and other top universities
- Projects and assignments to build practical skills
- A supportive community of learners
- No tuition fees - completely free

The curriculum covers everything from programming basics to advanced topics like machine learning and distributed systems."""

        elif 'core cs' in query_lower or 'core curriculum' in query_lower:
            return """The Core CS curriculum consists of the following courses:

**Core Programming** (3 courses):
• How to Code: Simple Data
• How to Code: Complex Data
• Programming Languages (Parts A, B, C)

**Core Math** (3 courses):
• Mathematics for Computer Science
• Linear Algebra
• Calculus

**Core Systems** (3 courses):
• Build a Modern Computer (Nand2Tetris)
• Operating Systems: Three Easy Pieces
• Computer Networking

**Core Theory** (3 courses):
• Algorithms and Data Structures
• Computability and Complexity
• Computer Science Theory

**Core Security** (2 courses):
• Information Security
• Cryptography I

**Core Applications** (4 courses):
• Databases
• Machine Learning
• Computer Graphics
• Software Engineering"""

        elif 'programming language' in query_lower:
            return """The OSSU curriculum teaches various programming languages:

**Introductory**: Python, Scheme/Racket  
**Systems**: C, Assembly  
**Object-Oriented**: Java, C++  
**Functional**: Haskell, ML/OCaml  
**Web**: JavaScript, HTML/CSS  
**Databases**: SQL

Each language is chosen to teach specific programming paradigms and concepts."""

        # Default context response
        if context_text:
            return f"Based on the documentation:\n\n{context_text[:800]}"
        else:
            return "I couldn't find relevant information in the documentation for your question. Try asking about the OSSU curriculum, core CS courses, or programming languages used."