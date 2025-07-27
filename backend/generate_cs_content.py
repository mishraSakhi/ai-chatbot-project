import os
from pathlib import Path

# Define the content to add
cs_topics = {
    "intro_to_programming.md": """# Introduction to Programming

## Overview
Programming is the process of creating a set of instructions that tell a computer how to perform a task. This course covers fundamental programming concepts.

## Key Concepts
- Variables and Data Types
- Control Structures (if/else, loops)
- Functions and Procedures
- Data Structures (arrays, lists)
- Object-Oriented Programming basics
- Debugging and Testing

## Popular First Languages
- Python: Great for beginners, readable syntax
- JavaScript: Essential for web development
- Java: Widely used in enterprise and Android
- C: Low-level, teaches computer architecture
""",
    
    "data_structures_algorithms.md": """# Data Structures and Algorithms

## Overview
Data structures and algorithms form the foundation of computer science and software engineering.

## Core Data Structures
- Arrays and Dynamic Arrays
- Linked Lists (Singly, Doubly, Circular)
- Stacks and Queues
- Trees (Binary, BST, AVL, Red-Black)
- Heaps and Priority Queues
- Hash Tables
- Graphs

## Essential Algorithms
- Sorting: QuickSort, MergeSort, HeapSort
- Searching: Binary Search, DFS, BFS
- Dynamic Programming
- Greedy Algorithms
- Graph Algorithms: Dijkstra's, Kruskal's, Prim's
""",
    
    "computer_systems.md": """# Computer Systems

## Overview
Understanding how computers work at a systems level is crucial for any computer scientist.

## Topics Covered
- Computer Architecture
- Operating Systems
- Memory Management
- Process Management
- File Systems
- Networking Basics
- System Programming
- Virtualization

## Key Concepts
- CPU Architecture and Instruction Sets
- Memory Hierarchy (Cache, RAM, Storage)
- Concurrency and Parallelism
- System Calls and Kernel Mode
""",
    
    "mathematics_for_cs.md": """# Mathematics for Computer Science

## Overview
Mathematical foundations are essential for computer science.

## Core Topics
- Discrete Mathematics
- Linear Algebra
- Calculus
- Probability and Statistics
- Logic and Proofs
- Number Theory
- Graph Theory

## Applications in CS
- Algorithm Analysis (Big-O notation)
- Machine Learning (Linear Algebra, Calculus)
- Cryptography (Number Theory)
- Computer Graphics (Linear Algebra)
- Network Analysis (Graph Theory)
"""
}

def create_supplementary_content():
    # Get the markdown directory
    md_dir = Path("/Users/sakshimishra/ai-chatbot-project/backend/data/markdown_files")
    supplementary_dir = md_dir / "supplementary"
    supplementary_dir.mkdir(exist_ok=True)
    
    for filename, content in cs_topics.items():
        filepath = supplementary_dir / filename
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Created: {filepath}")
    
    # Create an index file
    index_content = """# Computer Science Topics - Supplementary Content

This directory contains supplementary content to enhance the OSSU Computer Science curriculum.

## Topics Covered

1. **Introduction to Programming** - Fundamental programming concepts
2. **Data Structures and Algorithms** - Core CS data structures and algorithms
3. **Computer Systems** - How computers work at a systems level
4. **Mathematics for CS** - Mathematical foundations for computer science

These materials complement the OSSU curriculum by providing quick reference guides and overviews of key topics.
"""
    
    with open(supplementary_dir / "index.md", 'w') as f:
        f.write(index_content)
    
    print(f"\nCreated {len(cs_topics) + 1} supplementary files in {supplementary_dir}")

if __name__ == "__main__":
    create_supplementary_content()