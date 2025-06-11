# wolfscribe/processing/extractors/txt_extractor.py
"""
Plain text file extractor for Wolfscribe

Handles .txt files with proper encoding detection and error handling.
"""

import os
from typing import List


def extract_text(path: str) -> str:
    """
    Extract text from plain text files (.txt)
    
    Args:
        path (str): Path to the text file
        
    Returns:
        str: The complete file content as text
        
    Raises:
        RuntimeError: If file cannot be read or encoding issues occur
    """
    if not os.path.exists(path):
        raise RuntimeError(f"Text file not found: {path}")
    
    # List of encodings to try, in order of preference
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(path, "r", encoding=encoding) as f:
                content = f.read()
                
            # Validate that we got meaningful content
            if content.strip():
                return content
            else:
                # Empty file is valid
                return content
                
        except UnicodeDecodeError:
            continue
        except Exception as e:
            raise RuntimeError(f"Failed to read text file {path}: {str(e)}")
    
    # If all encodings failed
    raise RuntimeError(f"Unable to decode text file {path} with any supported encoding")