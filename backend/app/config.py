from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    GEMINI_API_KEY: Optional[str] = None
    HF_TOKEN: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Get the backend directory
    BACKEND_DIR: Path = Path(__file__).resolve().parent.parent
    
    # Directory paths (use absolute paths)
    MARKDOWN_DIR: str = str(BACKEND_DIR / "data" / "markdown_files")
    CHROMA_DIR: str = str(BACKEND_DIR / "data" / "chroma_db")
    UPLOAD_DIR: str = str(BACKEND_DIR / "data" / "uploads")
    LOG_DIR: str = str(BACKEND_DIR / "logs")
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Chatbot"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    RELOAD: bool = True
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",
    ]
    
    # Vector Store Settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_CHUNKS_PER_DOC: int = 100
    
    # AI Model Settings
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"
    HF_MODEL: str = "google/flan-t5-base"
    MAX_TOKENS: int = 500
    TEMPERATURE: float = 0.7
    
    # Chat Settings
    MAX_HISTORY_LENGTH: int = 10
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_SESSIONS: int = 1000
    
    # Search Settings
    SEARCH_K: int = 4
    MIN_RELEVANCE_SCORE: float = 0.5
    
    # File Settings
    ALLOWED_EXTENSIONS: List[str] = [".md", ".txt", ".pdf", ".docx"]
    MAX_FILE_SIZE_MB: int = 10
    
    # Database Settings (if needed in future)
    DATABASE_URL: Optional[str] = None
    
    # Redis Settings (for session management if needed)
    REDIS_URL: Optional[str] = None
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        
    def get_markdown_files(self) -> List[Path]:
        """Get all markdown files from the markdown directory."""
        markdown_path = Path(self.MARKDOWN_DIR)
        if markdown_path.exists():
            return list(markdown_path.glob("*.md"))
        return []
    
    def validate_directories(self):
        """Validate and create necessary directories."""
        directories = [
            self.MARKDOWN_DIR,
            self.CHROMA_DIR,
            self.UPLOAD_DIR,
            self.LOG_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.DEBUG
    
    @property
    def has_ai_keys(self) -> bool:
        """Check if any AI API keys are configured."""
        return bool(
            (self.GEMINI_API_KEY and self.GEMINI_API_KEY != "your_gemini_api_key_here") or
            (self.HF_TOKEN and self.HF_TOKEN != "your_huggingface_token_here") or
            (self.OPENAI_API_KEY and self.OPENAI_API_KEY != "your_openai_api_key_here")
        )

# Create settings instance
settings = Settings()

# Validate and create directories
settings.validate_directories()

# Debug: Print configuration info
if settings.DEBUG:
    print("🔧 Configuration loaded:")
    print(f"📁 Backend directory: {settings.BACKEND_DIR}")
    print(f"📁 Markdown directory: {settings.MARKDOWN_DIR}")
    print(f"📁 Chroma directory: {settings.CHROMA_DIR}")
    print(f"📁 Upload directory: {settings.UPLOAD_DIR}")
    print(f"📁 Log directory: {settings.LOG_DIR}")
    print(f"🔑 AI Keys configured: {settings.has_ai_keys}")
    print(f"🌐 CORS origins: {settings.BACKEND_CORS_ORIGINS}")
    
    # Check for markdown files
    md_files = settings.get_markdown_files()
    print(f"📄 Markdown files found: {len(md_files)}")
    if md_files:
        for file in md_files[:5]:  # Show first 5 files
            print(f"   - {file.name}")
        if len(md_files) > 5:
            print(f"   ... and {len(md_files) - 5} more")

# Export settings
__all__ = ["settings"]