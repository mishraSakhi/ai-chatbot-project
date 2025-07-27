#!/usr/bin/env python3
"""Check configuration and setup."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from pathlib import Path

def check_config():
    """Check configuration and environment."""
    print("🔍 Checking AI Chatbot Configuration...\n")
    
    # Check directories
    print("📁 Directory Status:")
    dirs = {
        "Markdown": settings.MARKDOWN_DIR,
        "Chroma": settings.CHROMA_DIR,
        "Upload": settings.UPLOAD_DIR,
        "Logs": settings.LOG_DIR
    }
    
    for name, path in dirs.items():
        exists = os.path.exists(path)
        status = "✅" if exists else "❌"
        print(f"  {status} {name}: {path}")
    
    # Check markdown files
    print("\n📄 Markdown Files:")
    md_files = list(Path(settings.MARKDOWN_DIR).glob("*.md"))
    if md_files:
        print(f"  ✅ Found {len(md_files)} markdown files")
        for file in md_files[:5]:
            print(f"     - {file.name}")
    else:
        print("  ❌ No markdown files found!")
        print(f"     Please add .md files to: {settings.MARKDOWN_DIR}")
    
    # Check API keys
    print("\n🔑 API Keys:")
    keys = {
        "Gemini": settings.GEMINI_API_KEY,
        "Hugging Face": settings.HF_TOKEN,
        "OpenAI": settings.OPENAI_API_KEY
    }
    
    for name, key in keys.items():
        if key and key not in ["your_gemini_api_key_here", "your_huggingface_token_here", "your_openai_api_key_here", None]:
            print(f"  ✅ {name}: Configured")
        else:
            print(f"  ❌ {name}: Not configured")
    
    # Check environment
    print("\n🌐 Environment:")
    print(f"  Debug Mode: {settings.DEBUG}")
    print(f"  Host: {settings.HOST}:{settings.PORT}")
    print(f"  CORS Origins: {len(settings.BACKEND_CORS_ORIGINS)} configured")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if not md_files:
        print("  1. Add markdown files to the markdown directory")
    if not settings.has_ai_keys:
        print("  2. Configure at least one AI API key in .env file")
    if settings.DEBUG:
        print("  3. Set DEBUG=False for production")

if __name__ == "__main__":
    check_config()


# # Find all markdown files in your project
# find /Users/sakshimishra/ai-chatbot-project -name "*.md" -type f | grep -v venv | grep -v node_modules

# # Check the parent directory
# ls -la ../
# ls -la ../../

# # Check if there's a docs or documentation folder
# find .. -type d -name "*doc*" -o -name "*data*" -o -name "*markdown*" | grep -v venv