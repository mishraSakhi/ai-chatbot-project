from pathlib import Path
import re

# Path to the markdown file
readme_path = Path("/Users/sakshimishra/ai-chatbot-project/backend/data/markdown_files/README.md")

# Read the content
content = readme_path.read_text()

# === Searching for course information ===
print("=== Searching for course headers ===\n")

# Find course-related headers
course_sections = []
lines = content.split('\n')

for i, line in enumerate(lines):
    if any(keyword in line.lower() for keyword in ['course', 'introduction to', 'intro to', 'fundamentals', 'core cs', 'advanced']):
        if '#' in line:  # Check if it's a markdown header
            print(f"Line {i}: {line.strip()}")

# === Course Links ===
print("\n=== Course Links ===")

# Markdown-style links: [title](URL)
course_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

# Filter and print relevant course links
for name, link in course_links[:30]:  # Limit to first 30 for preview
    if any(term in name.lower() for term in ['course', 'cs', 'programming', 'math', 'systems', 'software']):
        print(f"- {name.strip()}: {link.strip()}")
