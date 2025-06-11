# wolfscribe/processing/extractors/pdf_extractor.py
"""
PDF file extractor for Wolfscribe

Handles .pdf files using pdfminer library for text extraction.
"""

import os


def extract_text(path: str) -> str:
    """
    Extract text from PDF files using pdfminer
    
    Args:
        path (str): Path to the PDF file
        
    Returns:
        str: Extracted text content from all pages
        
    Raises:
        RuntimeError: If PDF extraction fails due to corruption, protection, 
                     missing library, or other issues
    """
    if not os.path.exists(path):
        raise RuntimeError(f"PDF file not found: {path}")
    
    try:
        from pdfminer.high_level import extract_text as pdfminer_extract
        
        # Extract text from the PDF
        content = pdfminer_extract(path)
        
        if content is None:
            raise RuntimeError("PDF extraction returned no content")
            
        return content
        
    except ImportError:
        raise RuntimeError(
            "PDF extraction requires pdfminer library. "
            "Install with: pip install pdfminer.six"
        )
    except Exception as e:
        error_msg = str(e).lower()
        
        # Provide specific error messages for common issues
        if "password" in error_msg or "encrypted" in error_msg:
            raise RuntimeError("PDF file is password protected - cannot extract text")
        elif "corrupted" in error_msg or "invalid" in error_msg:
            raise RuntimeError("PDF file appears to be corrupted or invalid")
        elif "permission" in error_msg:
            raise RuntimeError("Permission denied when accessing PDF file")
        else:
            raise RuntimeError(f"PDF extraction failed: {str(e)}")