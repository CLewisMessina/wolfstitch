# wolfstitch/processing/extractors/code_extractor.py
"""
Source code file text extraction module for Wolfstitch

This module extracts text content from various programming language files including:
- Python (.py)
- JavaScript (.js)
- Java (.java)
- C/C++ (.c, .cpp, .h, .hpp)
- Configuration files (.toml, .yaml, .yml)
- Other text-based code files

Features:
- Quality control to skip minified/auto-generated files
- Encoding detection and handling
- File size limits for performance
- Whitespace and structure preservation
"""

import os
import chardet
from typing import Optional, Dict, Any
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Configuration constants
MAX_FILE_SIZE = 1_000_000  # 1MB limit for individual files
MIN_WHITESPACE_RATIO = 0.05  # Minimum 5% whitespace for non-minified code
MIN_LINE_LENGTH_FOR_MINIFIED_CHECK = 1000  # Check minification for files > 1KB
ENCODING_CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for encoding detection

# Common auto-generated file patterns
AUTO_GENERATED_PATTERNS = [
    'generated', 'auto-generated', 'autogenerated',
    'do not edit', 'do not modify', 
    'this file is automatically generated',
    'machine generated', 'compiled from',
    'generated by', 'auto-generated by'
]


def extract_text(file_path: str, encoding: Optional[str] = None) -> str:
    """
    Extract text content from source code files
    
    Extracts source code as plain text with quality checks to ensure
    the code is suitable for training data. Skips minified and 
    auto-generated files.
    
    Args:
        file_path (str): Path to the source code file
        encoding (Optional[str]): Force specific encoding (auto-detected if None)
        
    Returns:
        str: Extracted source code text
        
    Raises:
        ValueError: If file is minified, auto-generated, or unsupported
        RuntimeError: If extraction fails due to encoding or read errors
        
    Examples:
        >>> text = extract_text("script.py")
        >>> text = extract_text("config.yaml", encoding="utf-8")
    """
    # Check file size first
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {file_size:,} bytes (max: {MAX_FILE_SIZE:,} bytes). "
            f"File: {file_path}"
        )
    
    # Detect encoding if not specified
    if encoding is None:
        encoding = detect_file_encoding(file_path)
    
    try:
        # Read file content
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read file {file_path}: {str(e)}")
    
    # Quality control checks
    if is_minified_code(content):
        raise ValueError(
            f"Skipping minified file (low whitespace ratio): {file_path}"
        )
    
    if is_auto_generated(content):
        raise ValueError(
            f"Skipping auto-generated file: {file_path}"
        )
    
    # Additional quality checks based on file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext in ['.json', '.xml', '.html', '.css']:
        # These formats have their own extractors, but might be included in code dirs
        logger.warning(
            f"Code extractor used for {file_ext} file. "
            f"Consider using dedicated extractor: {file_path}"
        )
    
    return content


def detect_file_encoding(file_path: str) -> str:
    """
    Detect the encoding of a text file
    
    Uses chardet library to detect encoding with fallback to utf-8.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Detected encoding name
    """
    try:
        # Read raw bytes for detection
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB for detection
        
        # Detect encoding
        result = chardet.detect(raw_data)
        
        if result['confidence'] >= ENCODING_CONFIDENCE_THRESHOLD:
            return result['encoding']
        else:
            logger.warning(
                f"Low confidence encoding detection ({result['confidence']:.2f}) "
                f"for {file_path}. Using UTF-8."
            )
            return 'utf-8'
            
    except Exception as e:
        logger.error(f"Encoding detection failed for {file_path}: {str(e)}")
        return 'utf-8'  # Default fallback


def is_minified_code(content: str) -> bool:
    """
    Detect if code is minified based on whitespace ratio and line length
    
    Minified code typically has:
    - Very long lines
    - Minimal whitespace
    - No formatting or indentation
    
    Args:
        content (str): Source code content
        
    Returns:
        bool: True if code appears to be minified
    """
    if len(content) < MIN_LINE_LENGTH_FOR_MINIFIED_CHECK:
        return False  # Too small to reliably check
    
    # Check whitespace ratio
    whitespace_count = sum(1 for c in content if c.isspace())
    whitespace_ratio = whitespace_count / len(content)
    
    if whitespace_ratio < MIN_WHITESPACE_RATIO:
        return True
    
    # Check average line length
    lines = content.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    
    if non_empty_lines:
        avg_line_length = sum(len(line) for line in non_empty_lines) / len(non_empty_lines)
        
        # If average line length is very high, likely minified
        if avg_line_length > 500:
            return True
    
    # Check for specific minification patterns
    minified_indicators = [
        '){', '};', ']{', '];',  # No spacing around brackets
        'var a=', 'let a=', 'const a=',  # Single letter variables
        'function(a,b,c,d,e)',  # Many single letter parameters
    ]
    
    indicator_count = sum(1 for indicator in minified_indicators if indicator in content)
    if indicator_count > 10:  # Many minification patterns found
        return True
    
    return False


def is_auto_generated(content: str) -> bool:
    """
    Detect if code is auto-generated based on common markers
    
    Checks for common auto-generation markers in comments and headers.
    
    Args:
        content (str): Source code content
        
    Returns:
        bool: True if code appears to be auto-generated
    """
    # Check first 1000 characters for auto-generated markers
    header_content = content[:1000].lower()
    
    for pattern in AUTO_GENERATED_PATTERNS:
        if pattern in header_content:
            return True
    
    # Check for specific auto-generation tools
    tool_markers = [
        'generated by protoc',
        'generated by thrift',
        'generated by swagger',
        'generated by graphql',
        'automatically produced by aclocal',
        'generated by configure',
        'autogenerated on',
        'this file was generated',
    ]
    
    for marker in tool_markers:
        if marker in header_content:
            return True
    
    return False


def get_code_metrics(content: str) -> Dict[str, Any]:
    """
    Calculate metrics about code content for quality assessment
    
    Args:
        content (str): Source code content
        
    Returns:
        Dict[str, Any]: Metrics including line count, whitespace ratio, etc.
    """
    lines = content.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    
    # Calculate metrics
    metrics = {
        'total_lines': len(lines),
        'non_empty_lines': len(non_empty_lines),
        'total_characters': len(content),
        'whitespace_ratio': sum(1 for c in content if c.isspace()) / max(len(content), 1),
        'average_line_length': sum(len(line) for line in lines) / max(len(lines), 1),
        'max_line_length': max((len(line) for line in lines), default=0),
        'has_comments': any(marker in content for marker in ['#', '//', '/*', '"""', "'''"]),
        'appears_minified': is_minified_code(content),
        'appears_generated': is_auto_generated(content),
    }
    
    # Detect primary language based on content patterns
    if 'def ' in content and 'import ' in content:
        metrics['likely_language'] = 'python'
    elif 'function' in content or 'const ' in content or 'var ' in content:
        metrics['likely_language'] = 'javascript'
    elif 'public class' in content or 'public static' in content:
        metrics['likely_language'] = 'java'
    elif '#include' in content or 'int main' in content:
        metrics['likely_language'] = 'c/c++'
    else:
        metrics['likely_language'] = 'unknown'
    
    return metrics


# Utility function for batch processing
def validate_code_file(file_path: str) -> Dict[str, Any]:
    """
    Validate a code file without extracting content
    
    Useful for pre-screening files in batch processing.
    
    Args:
        file_path (str): Path to validate
        
    Returns:
        Dict[str, Any]: Validation results
    """
    result = {
        'valid': True,
        'file_path': file_path,
        'file_size': os.path.getsize(file_path),
        'issues': []
    }
    
    # Check file size
    if result['file_size'] > MAX_FILE_SIZE:
        result['valid'] = False
        result['issues'].append(f"File too large: {result['file_size']:,} bytes")
    
    # Try to detect if file is binary
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:  # Null byte indicates binary
                result['valid'] = False
                result['issues'].append("Appears to be a binary file")
    except Exception as e:
        result['valid'] = False
        result['issues'].append(f"Cannot read file: {str(e)}")
    
    return result