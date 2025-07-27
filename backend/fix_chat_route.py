# backend/fix_chat_route.py

import re

print("🔧 Checking and fixing chat route registration\n")

# Read main.py
with open("app/main.py", "r") as f:
    content = f.read()

# Check if chat router is imported
has_import = "from app.api import chat" in content or "from .api import chat" in content
has_router_include = "chat.router" in content

print(f"✓ Chat import found: {has_import}")
print(f"✓ Chat router included: {has_router_include}")

if not has_import or not has_router_include:
    print("\n📝 Adding missing chat router registration...")
    
    lines = content.split('\n')
    new_lines = []
    
    # Find where to add import
    import_added = False
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Add import after other app imports
        if not has_import and not import_added and line.startswith("from app.") and i < len(lines) - 1:
            if not lines[i+1].startswith("from app."):
                new_lines.append("from app.api import chat")
                import_added = True
    
    # Find where to add router inclusion
    if not has_router_include:
        # Look for after middleware setup or after app creation
        for i, line in enumerate(new_lines):
            if "app.add_middleware" in line:
                # Find the end of middleware setup
                j = i
                while j < len(new_lines) and new_lines[j].strip() != "":
                    j += 1
                # Insert after middleware
                new_lines.insert(j, "\n# Include routers")
                new_lines.insert(j+1, "app.include_router(chat.router, prefix=\"/chat\", tags=[\"chat\"])")
                break
            elif "app = FastAPI" in line:
                # Find the end of FastAPI initialization
                j = i
                paren_count = 0
                for k in range(i, len(new_lines)):
                    paren_count += new_lines[k].count('(') - new_lines[k].count(')')
                    if paren_count == 0:
                        j = k + 1
                        break
                # Insert after app creation
                new_lines.insert(j, "\n# Include routers")
                new_lines.insert(j+1, "app.include_router(chat.router, prefix=\"/chat\", tags=[\"chat\"])")
                break
    
    # Write back
    with open("app/main.py", "w") as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Fixed! The chat router has been registered.")
else:
    print("\n✅ Chat router is already properly registered!")

# Show where the chat endpoint should be available
print("\n📍 Chat endpoint should be available at:")
print("   POST http://localhost:8001/chat")
print("   GET  http://localhost:8001/docs (to see all endpoints)")