# backend/check_main_routes.py

import os

print("🔍 Checking main.py routes\n")

try:
    with open("app/main.py", "r") as f:
        content = f.read()
        
    print("Looking for route definitions:")
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Look for route decorators
        if '@app.' in line or '@router.' in line:
            print(f"\nLine {i+1}: {line.strip()}")
            # Print the next few lines to see the function
            for j in range(1, min(5, len(lines) - i)):
                print(f"Line {i+1+j}: {lines[i+j]}")
                if lines[i+j].strip() and not lines[i+j].startswith(' ') and not lines[i+j].startswith('\t'):
                    break
                    
except Exception as e:
    print(f"Error reading main.py: {e}")

# Also check for imported routers
print("\n\nChecking API folder for routers:")
api_dir = "app/api"
if os.path.exists(api_dir):
    for file in os.listdir(api_dir):
        if file.endswith('.py') and file != '__init__.py':
            print(f"\nChecking {file}:")
            try:
                with open(os.path.join(api_dir, file), 'r') as f:
                    content = f.read()
                    if 'router' in content or '@' in content:
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if '@router.' in line or 'def ' in line:
                                print(f"  {line.strip()}")
            except:
                pass