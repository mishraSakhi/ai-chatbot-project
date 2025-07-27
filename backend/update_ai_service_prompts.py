# backend/update_ai_service_prompts.py

print("🔧 Updating AI Service for better responses\n")

# Read current ai_service.py
with open('app/services/ai_service.py', 'r') as f:
    content = f.read()

# Find and update the generate_response method
updated_content = content.replace(
    'prompt = f"""You are a helpful assistant answering questions about the OSSU Computer Science curriculum.',
    '''prompt = f"""You are a helpful and knowledgeable assistant for the OSSU (Open Source Society University) Computer Science curriculum.

IMPORTANT INSTRUCTIONS:
1. Always provide comprehensive, helpful answers even if the exact information isn't in the provided context
2. Use your knowledge about computer science education to supplement the context
3. For programming language questions, mention ALL languages used in OSSU: Python, JavaScript, C, Java, Haskell, SQL, Scheme/Racket, ML/OCaml, Ruby, etc.
4. For specific course questions like "Introduction to Programming with Python", provide details about CS50P from Harvard
5. Don't say "the document doesn't contain" - instead provide the best answer you can'''
)

# Write back
with open('app/services/ai_service.py', 'w') as f:
    f.write(updated_content)

print("✅ Updated AI service prompts")