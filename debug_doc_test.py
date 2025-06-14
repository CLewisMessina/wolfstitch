#!/usr/bin/env python3
# debug_doc_test.py
"""
Debug the specific document cleaning test that's failing
"""

import sys
import os

# Add the project root to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from processing.clean import clean_document_content


def debug_document_test():
    """Debug the exact test that's failing"""
    
    # Exact text from the test
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
    
    print("Full cleaned text:")
    print(repr(cleaned))
    print("\nSplit into lines:")
    lines = cleaned.split('\n')
    for i, line in enumerate(lines):
        print(f"Line {i}: {repr(line)}")
    
    print("\nLooking for the document sentence:")
    # The test expects this specific text to be in the cleaned output
    expected = "This is a sample document with excessive whitespace and formatting issues."
    
    # Check if it exists as a complete sentence
    if expected in cleaned:
        print(f"✅ Found expected text in cleaned output")
    else:
        print(f"❌ Expected text not found")
        
        # Check if parts exist
        for i, line in enumerate(lines):
            if "This" in line and "sample" in line:
                print(f"\nLine {i} contains 'This' and 'sample': {repr(line)}")
                if "excessive" in line and "whitespace" in line:
                    print("  This line also has 'excessive' and 'whitespace'")
                else:
                    print("  But it's missing 'excessive' and 'whitespace'")
                    # The original has the sentence split across two lines!


if __name__ == "__main__":
    debug_document_test()