#!/usr/bin/env python3
# diagnostic_test.py
"""
Diagnostic script to understand what's happening with the failing tests
"""

import sys
import os

# Add the project root to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from processing.clean import (
    clean_text, clean_code_content, clean_document_content
)


def diagnose_code_cleaning():
    """Diagnose the code cleaning blank line issue"""
    print("🔍 DIAGNOSING CODE CLEANING")
    print("=" * 60)
    
    # Same test input as in the test
    python_code = '''def fibonacci(n):
    """Calculate fibonacci sequence with proper docstring"""
    if n <= 1:
        return n
    else:
        # Recursive case with proper indentation
        return fibonacci(n-1) + fibonacci(n-2)


class Calculator:
    """Example class with various indentation levels"""
    
    def __init__(self):
        self.result = 0
        self.history = []
        
    def add(self, x, y):
        """Add two numbers"""
        result = x + y
        self.history.append(f"{x} + {y} = {result}")
        return result


if __name__ == "__main__":
    calc = Calculator()
    print(calc.add(2, 3))'''
    
    cleaned = clean_code_content(python_code)
    
    # Count newline patterns
    double_count = cleaned.count('\n\n')
    triple_count = cleaned.count('\n\n\n')
    quad_count = cleaned.count('\n\n\n\n')
    
    print(f"Original length: {len(python_code)}")
    print(f"Cleaned length: {len(cleaned)}")
    print(f"Double newlines (\\n\\n): {double_count}")
    print(f"Triple newlines (\\n\\n\\n): {triple_count}")
    print(f"Quad newlines (\\n\\n\\n\\n): {quad_count}")
    
    # Show where triple newlines occur
    if triple_count > 0:
        print("\nTriple newline locations:")
        idx = 0
        while True:
            idx = cleaned.find('\n\n\n', idx)
            if idx == -1:
                break
            # Show context around triple newline
            start = max(0, idx - 30)
            end = min(len(cleaned), idx + 30)
            context = cleaned[start:end]
            print(f"  Position {idx}: ...{repr(context)}...")
            idx += 1
    
    print("\n")


def diagnose_document_cleaning():
    """Diagnose the document cleaning issue"""
    print("🔍 DIAGNOSING DOCUMENT CLEANING")
    print("=" * 60)
    
    # The problematic text from the test
    document_text = '''
    *** START OF PROJECT GUTENBERG EBOOK: SAMPLE ***
    
    Chapter 1: Introduction to Advanced Topics
    
    This    is   a    sample     document    with
    excessive    whitespace    and    formatting    issues.
    
    • First bullet point with important information
    • Second bullet point  
    - Another bullet style for variety
    1. Numbered list item with details
    2. Another numbered item
    * Yet another bullet type
    
    
    
    
    Multiple blank lines above this paragraph.
    
    Some more normal text with    scattered    spaces.
    
    *** END OF PROJECT GUTENBERG EBOOK ***
    '''
    
    cleaned = clean_document_content(document_text)
    
    # Find the specific line that's failing
    lines = cleaned.split('\n')
    for i, line in enumerate(lines):
        if "This" in line and "sample" in line:
            print(f"Line {i}: {repr(line)}")
            print(f"  Length: {len(line)}")
            print(f"  Expected: 'This is a sample document with'")
            print(f"  Match: {line == 'This is a sample document with'}")
            
            # Check character by character
            expected = "This is a sample document with"
            if len(line) > len(expected):
                print(f"  Line is {len(line) - len(expected)} chars longer than expected")
            
    print("\n")


def diagnose_bullet_removal():
    """Diagnose the bullet removal issue"""
    print("🔍 DIAGNOSING BULLET REMOVAL")
    print("=" * 60)
    
    test_text = 'This    has    excessive     spacing   and   • bullets'
    
    # Test with different approaches
    print("Original text:", repr(test_text))
    
    # Direct document cleaning
    cleaned_doc = clean_document_content(test_text)
    print("Direct clean_document_content:", repr(cleaned_doc))
    
    # Via clean_text with file extension
    cleaned_pdf = clean_text(test_text, file_extension='.pdf')
    print("clean_text with .pdf extension:", repr(cleaned_pdf))
    
    # Via clean_text with no parameters (legacy)
    cleaned_legacy = clean_text(test_text)
    print("clean_text with no params:", repr(cleaned_legacy))
    
    # Via clean_text with explicit parameters
    cleaned_params = clean_text(
        test_text,
        remove_headers=True,
        normalize_whitespace=True,
        strip_bullets=True
    )
    print("clean_text with explicit params:", repr(cleaned_params))
    
    print("\n")


def diagnose_full_document_flow():
    """Trace through the full document cleaning flow"""
    print("🔍 FULL DOCUMENT CLEANING FLOW")
    print("=" * 60)
    
    test_input = 'This    has    • bullets    and    spacing'
    
    print("Input:", repr(test_input))
    
    # Step by step through clean_document_content
    text = test_input
    
    # Step 1: Headers (no change expected)
    import re
    text1 = re.sub(r"\*\*\* START OF.*?\*\*\*", "", text, flags=re.IGNORECASE | re.DOTALL)
    text1 = re.sub(r"\*\*\* END OF.*?\*\*\*", "", text1, flags=re.IGNORECASE | re.DOTALL)
    print("After header removal:", repr(text1))
    
    # Step 2: Bullets
    text2 = re.sub(r"^\s*[\d\-\*\•]+\s+", "", text1, flags=re.MULTILINE)
    print("After bullet removal:", repr(text2))
    
    # Step 3: Whitespace normalization
    text3 = re.sub(r"[ \t]+", " ", text2)
    print("After space normalization:", repr(text3))
    
    text4 = re.sub(r"^ +", "", text3, flags=re.MULTILINE)
    print("After leading space removal:", repr(text4))
    
    text5 = re.sub(r" +$", "", text4, flags=re.MULTILINE)
    print("After trailing space removal:", repr(text5))
    
    text6 = re.sub(r"\n{3,}", "\n\n", text5)
    print("After newline normalization:", repr(text6))
    
    final = text6.strip()
    print("Final result:", repr(final))
    
    print("\n")


if __name__ == "__main__":
    print("Wolfstitch Context-Aware Cleaning Diagnostic")
    print("=" * 60)
    print()
    
    diagnose_code_cleaning()
    diagnose_document_cleaning()
    diagnose_bullet_removal()
    diagnose_full_document_flow()