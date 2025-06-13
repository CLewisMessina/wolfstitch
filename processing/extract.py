# wolfstitch/processing/extract.py
"""
Enhanced file extraction dispatcher for Wolfstitch

This module provides a clean, modular interface for extracting text from various
file formats. Each format is handled by a dedicated extractor module, making
the system easy to maintain and extend.

Supported formats:
- TXT: Plain text files
- PDF: Adobe PDF documents  
- EPUB: Electronic publication format
- DOCX: Microsoft Word documents
- CSV: Comma-separated values
- MD/Markdown: Markdown documents
- JSON/JSONL: JSON and JSON Lines data
- XLSX/XLS: Microsoft Excel spreadsheets
- HTML/HTM: Web pages and HTML documents
- XML: Extensible markup language documents
- PPTX/PPT: Microsoft PowerPoint presentations (NEW)
"""

import os
from typing import Dict, Callable

# Import all extractor modules
from processing.extractors import (
    txt_extractor,
    pdf_extractor, 
    epub_extractor,
    docx_extractor,
    csv_extractor,
    md_extractor,
    json_extractor,
    xlsx_extractor,
    html_extractor,
    xml_extractor,
    pptx_extractor  # NEW: PowerPoint support
)

# Extension to extractor function mapping
EXTENSION_LOADERS: Dict[str, Callable[[str], str]] = {
    # Text formats
    ".txt": txt_extractor.extract_text,
    
    # Document formats
    ".pdf": pdf_extractor.extract_text,
    ".epub": epub_extractor.extract_text,
    ".docx": docx_extractor.extract_text,
    
    # Presentation formats (NEW)
    ".pptx": pptx_extractor.extract_text,
    ".ppt": pptx_extractor.extract_text,  # Legacy support
    
    # Data formats
    ".csv": csv_extractor.extract_text,
    
    # Markup formats
    ".md": md_extractor.extract_text,
    ".markdown": md_extractor.extract_text,
    
    # Structured data formats
    ".json": json_extractor.extract_text,
    ".jsonl": json_extractor.extract_text,
    
    # Spreadsheet formats
    ".xlsx": xlsx_extractor.extract_text,
    ".xls": xlsx_extractor.extract_text,
    ".xlsm": xlsx_extractor.extract_text,
    
    # Web formats
    ".html": html_extractor.extract_text,
    ".htm": html_extractor.extract_text,
    
    # XML formats
    ".xml": xml_extractor.extract_text
}


def load_file(path: str) -> str:
    """
    Load and extract text content from various file formats
    
    This is the main entry point for file loading. It automatically detects
    the file format based on extension and dispatches to the appropriate
    extractor module.
    
    Args:
        path (str): Path to the file to extract text from
        
    Returns:
        str: Extracted text content from the file
        
    Raises:
        ValueError: If the file type is not supported
        RuntimeError: If extraction fails for any reason
        
    Examples:
        >>> text = load_file("document.pdf")
        >>> text = load_file("data.csv") 
        >>> text = load_file("readme.md")
        >>> text = load_file("presentation.pptx")  # NEW
    """
    if not os.path.exists(path):
        raise RuntimeError(f"File not found: {path}")
    
    # Get file extension
    ext = os.path.splitext(path)[1].lower()
    
    # Check if format is supported
    if ext not in EXTENSION_LOADERS:
        supported_formats = ", ".join(sorted(EXTENSION_LOADERS.keys()))
        raise ValueError(f"Unsupported file type: {ext}. "
                        f"Supported formats: {supported_formats}")
    
    # Dispatch to appropriate extractor
    try:
        extractor_func = EXTENSION_LOADERS[ext]
        return extractor_func(path)
    except Exception as e:
        # Re-raise extraction errors with context
        if isinstance(e, (ValueError, RuntimeError)):
            raise
        else:
            raise RuntimeError(f"Failed to extract text from {path}: {str(e)}")


def get_supported_extensions() -> list[str]:
    """
    Get list of all supported file extensions
    
    Returns:
        list[str]: List of supported file extensions (with dots)
    """
    return sorted(EXTENSION_LOADERS.keys())


def is_supported_format(path: str) -> bool:
    """
    Check if a file format is supported for extraction
    
    Args:
        path (str): File path or extension to check
        
    Returns:
        bool: True if format is supported, False otherwise
    """
    ext = os.path.splitext(path)[1].lower()
    return ext in EXTENSION_LOADERS


def get_format_info() -> Dict[str, Dict[str, any]]:
    """
    Get information about supported formats and their capabilities
    
    Returns:
        dict: Format information including extensions, descriptions, and features
    """
    return {
        "text": {
            "extensions": [".txt"],
            "description": "Plain text files",
            "features": ["encoding detection", "multi-encoding support"]
        },
        "documents": {
            "extensions": [".pdf", ".epub", ".docx"],
            "description": "Document formats",
            "features": ["structured content", "metadata extraction", "formatting preservation"]
        },
        "presentations": {  # NEW
            "extensions": [".pptx", ".ppt"],
            "description": "PowerPoint presentations",
            "features": ["slide text extraction", "speaker notes", "table content", "error handling"]
        },
        "data": {
            "extensions": [".csv", ".xlsx", ".xls", ".xlsm"],
            "description": "Spreadsheet and tabular data",
            "features": ["intelligent column detection", "text vs numeric filtering", "multi-sheet support"]
        },
        "markup": {
            "extensions": [".md", ".markdown", ".html", ".htm", ".xml"],
            "description": "Markup and structured text",
            "features": ["syntax cleaning", "content extraction", "structure preservation"]
        },
        "structured": {
            "extensions": [".json", ".jsonl"],
            "description": "Structured data formats", 
            "features": ["recursive text extraction", "chat format detection", "metadata filtering"]
        }
    }


# Enhanced validation function for batch processing
def validate_file_batch(file_paths: list[str]) -> Dict[str, any]:
    """
    Validate a batch of files for processing
    
    Args:
        file_paths (list[str]): List of file paths to validate
        
    Returns:
        Dict[str, any]: Validation results with supported/unsupported files
    """
    results = {
        'supported_files': [],
        'unsupported_files': [],
        'missing_files': [],
        'format_distribution': {},
        'total_files': len(file_paths)
    }
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            results['missing_files'].append(file_path)
            continue
            
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in EXTENSION_LOADERS:
            results['supported_files'].append(file_path)
            # Track format distribution
            results['format_distribution'][ext] = results['format_distribution'].get(ext, 0) + 1
        else:
            results['unsupported_files'].append({
                'file': file_path,
                'extension': ext,
                'reason': f'Unsupported format: {ext}'
            })
    
    return results


# Legacy compatibility functions (maintain backward compatibility)
def load_txt(path: str) -> str:
    """Legacy compatibility function for TXT files"""
    return txt_extractor.extract_text(path)


def load_pdf(path: str) -> str:
    """Legacy compatibility function for PDF files"""
    return pdf_extractor.extract_text(path)


def load_epub(path: str) -> str:
    """Legacy compatibility function for EPUB files"""
    return epub_extractor.extract_text(path)


def load_docx(path: str) -> str:
    """Legacy compatibility function for DOCX files"""
    return docx_extractor.extract_text(path)


def load_pptx(path: str) -> str:  # NEW
    """Legacy compatibility function for PowerPoint files"""
    return pptx_extractor.extract_text(path)


def load_csv(path: str) -> str:
    """Legacy compatibility function for CSV files"""
    return csv_extractor.extract_text(path)
