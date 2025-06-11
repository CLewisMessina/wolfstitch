# wolfscribe/processing/extractors/epub_extractor.py
"""
EPUB file extractor for Wolfscribe

Handles .epub files by extracting text from HTML content using BeautifulSoup.
"""

import os
import zipfile
from typing import List


def extract_text(path: str) -> str:
    """
    Extract text from EPUB files using zipfile and BeautifulSoup
    
    Args:
        path (str): Path to the EPUB file
        
    Returns:
        str: Extracted text content from all HTML files in the EPUB
        
    Raises:
        RuntimeError: If EPUB extraction fails due to corruption, missing library,
                     or other issues
    """
    if not os.path.exists(path):
        raise RuntimeError(f"EPUB file not found: {path}")
    
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise RuntimeError(
            "EPUB extraction requires BeautifulSoup library. "
            "Install with: pip install beautifulsoup4"
        )
    
    try:
        all_text = []

        with zipfile.ZipFile(path, 'r') as zip_ref:
            # Find all HTML/XHTML files in the EPUB
            html_files = [
                file for file in zip_ref.namelist() 
                if file.endswith((".htm", ".html", ".xhtml"))
            ]
            
            if not html_files:
                raise RuntimeError("No HTML content found in EPUB file")
            
            for file in html_files:
                try:
                    with zip_ref.open(file) as f:
                        soup = BeautifulSoup(f.read(), "html.parser")
                        
                        # Remove scripts, styles, and other non-content elements
                        for tag in soup(["script", "style", "meta", "link"]):
                            tag.decompose()
                        
                        # Extract text content
                        body_text = soup.get_text(separator="\n", strip=True)
                        if body_text:
                            all_text.append(body_text)
                            
                except Exception as e:
                    # Log the error but continue with other files
                    print(f"Warning: Failed to process {file} in EPUB: {str(e)}")
                    continue

        if not all_text:
            raise RuntimeError("No readable text content found in EPUB file")

        return "\n\n".join(all_text)
        
    except zipfile.BadZipFile:
        raise RuntimeError("EPUB file is corrupted or not a valid ZIP archive")
    except Exception as e:
        if "EPUB extraction" in str(e):
            # Re-raise our custom errors
            raise
        else:
            raise RuntimeError(f"EPUB extraction failed: {str(e)}")