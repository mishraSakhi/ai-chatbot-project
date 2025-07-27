import re
from typing import List, Dict

class CourseParser:
    @staticmethod
    def extract_programming_languages(text: str) -> List[str]:
        """Extract programming languages mentioned in the text."""
        languages = set()

        language_patterns = [
            r'\b(Python)\b',
            r'\b(Java)(?!Script)\b',
            r'\b(JavaScript|JS)\b',
            r'\b(C\+\+|C)\b',
            r'\b(Scheme)\b',
            r'\b(Racket)\b',
            r'\b(ML|OCaml|SML)\b',
            r'\b(Haskell)\b',
            r'\b(Ruby)\b',
            r'\b(Rust)\b',
            r'\b(Go|Golang)\b',
            r'\b(SQL)\b',
            r'\b(Assembly)\b',
            r'\b(MATLAB)\b',
            r'\b(R)\b',
        ]

        for pattern in language_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            languages.update(m.capitalize() if isinstance(m, str) else m[0].capitalize() for m in matches)

        # Normalize language names
        normalized = set()
        for lang in languages:
            if lang.lower() in ['c', 'c++']:
                normalized.add(lang.upper())
            elif lang.upper() in ['SQL', 'ML', 'JS', 'R']:
                normalized.add(lang.upper())
            else:
                normalized.add(lang.capitalize())

        return sorted(normalized)

    @staticmethod
    def extract_courses(text: str) -> List[Dict[str, str]]:
        """Extract course information from markdown tables."""
        courses = []
        lines = text.split('\n')

        in_table = False
        for line in lines:
            if '|' in line and line.count('|') >= 2:
                if '---' in line:  # Start of table
                    in_table = True
                    continue

                if in_table:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3 and parts[1]:  # Has course name
                        course_name = parts[1]

                        # Clean up markdown links: [Name](URL) → Name
                        match = re.match(r'\[([^\]]+)\]\([^)]+\)', course_name)
                        if match:
                            course_name = match.group(1)

                        if course_name and not course_name.startswith('-'):
                            course_info = {
                                'name': course_name,
                                'duration': parts[2] if len(parts) > 2 else '',
                                'effort': parts[3] if len(parts) > 3 else ''
                            }
                            courses.append(course_info)

        return courses
