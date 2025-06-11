# wolfscribe/processing/extractors/csv_extractor.py
"""
CSV file extractor for Wolfscribe

Handles .csv files by intelligently extracting text content from relevant columns,
automatically detecting delimiters and text vs numeric data.
"""

import os
import csv
import pandas as pd
from typing import List, Dict, Any, Tuple
from io import StringIO
import re


def extract_text(path: str) -> str:
    """
    Extract text from CSV files with intelligent column detection
    
    Args:
        path (str): Path to the CSV file
        
    Returns:
        str: Extracted text content from text-containing columns
        
    Raises:
        RuntimeError: If CSV extraction fails due to encoding issues,
                     malformed data, or other problems
    """
    if not os.path.exists(path):
        raise RuntimeError(f"CSV file not found: {path}")
    
    try:
        # Analyze the CSV file to determine structure
        delimiter, encoding, has_header = _analyze_csv_file(path)
        
        # Read the CSV file with detected parameters
        df = pd.read_csv(
            path,
            delimiter=delimiter,
            encoding=encoding,
            header=0 if has_header else None,
            dtype=str,  # Read everything as strings initially
            na_filter=False  # Don't convert empty strings to NaN
        )
        
        if df.empty:
            return ""  # Empty CSV is valid
        
        # Identify text columns vs numeric/date columns
        text_columns = _identify_text_columns(df)
        
        if not text_columns:
            # If no text columns found, treat all columns as potential text
            text_columns = list(df.columns)
        
        # Extract and combine text content
        extracted_text = _extract_text_content(df, text_columns)
        
        return extracted_text
        
    except Exception as e:
        if "CSV" in str(e):
            # Re-raise our custom errors
            raise
        else:
            raise RuntimeError(f"CSV extraction failed: {str(e)}")


def _analyze_csv_file(path: str) -> Tuple[str, str, bool]:
    """
    Analyze CSV file to detect delimiter, encoding, and header presence
    
    Returns:
        tuple: (delimiter, encoding, has_header)
    """
    # Try different encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as f:
                # Read first few lines to analyze structure
                sample = f.read(8192)  # 8KB sample
                
                # Detect delimiter
                delimiter = _detect_csv_delimiter(sample)
                
                # Check if first row looks like headers
                f.seek(0)
                reader = csv.reader(f, delimiter=delimiter)
                first_row = next(reader, None)
                second_row = next(reader, None)
                
                has_header = _detect_headers(first_row, second_row)
                
                return delimiter, encoding, has_header
                
        except UnicodeDecodeError:
            continue
        except Exception:
            continue
    
    # Fallback defaults
    return ',', 'utf-8', True


def _detect_csv_delimiter(sample: str) -> str:
    """Detect the most likely delimiter for the CSV"""
    delimiters = [',', ';', '\t', '|']
    delimiter_counts = {}
    
    lines = sample.split('\n')[:10]  # Check first 10 lines
    
    for delimiter in delimiters:
        counts = [line.count(delimiter) for line in lines if line.strip()]
        if counts:
            # Good delimiter should have consistent counts across lines
            avg_count = sum(counts) / len(counts)
            consistency = len([c for c in counts if abs(c - avg_count) <= 1])
            delimiter_counts[delimiter] = (avg_count, consistency)
    
    if not delimiter_counts:
        return ','  # Default fallback
    
    # Choose delimiter with highest average count and good consistency
    best_delimiter = max(
        delimiter_counts.items(),
        key=lambda x: (x[1][1], x[1][0])  # Prioritize consistency, then count
    )[0]
    
    return best_delimiter


def _detect_headers(first_row: List[str], second_row: List[str]) -> bool:
    """Detect if the first row contains headers"""
    if not first_row or not second_row:
        return True  # Default to assuming headers
    
    # Headers are likely if first row has text and second row has different patterns
    first_row_numeric = sum(1 for cell in first_row if _is_numeric(cell.strip()))
    second_row_numeric = sum(1 for cell in second_row if _is_numeric(cell.strip()))
    
    # If first row is mostly text and second row is mostly numeric, likely headers
    total_cols = len(first_row)
    if total_cols > 0:
        first_row_text_ratio = (total_cols - first_row_numeric) / total_cols
        second_row_text_ratio = (total_cols - second_row_numeric) / total_cols
        
        if first_row_text_ratio > 0.7 and second_row_text_ratio < 0.5:
            return True
    
    # Check for common header patterns
    header_patterns = [
        r'^(name|title|description|text|content|message|comment)',
        r'^(id|index|number|count|amount|price|date|time)',
        r'^\w+$'  # Single words are often headers
    ]
    
    header_matches = 0
    for cell in first_row:
        cell_lower = cell.lower().strip()
        if any(re.match(pattern, cell_lower) for pattern in header_patterns):
            header_matches += 1
    
    return header_matches / len(first_row) > 0.5 if first_row else True


def _identify_text_columns(df: pd.DataFrame) -> List[str]:
    """Identify columns that contain meaningful text content"""
    text_columns = []
    
    for column in df.columns:
        # Sample some non-empty values from the column
        sample_values = df[column].dropna().astype(str)
        sample_values = sample_values[sample_values.str.strip() != '']
        
        if len(sample_values) == 0:
            continue  # Skip empty columns
        
        # Take a sample of up to 100 values for analysis
        sample = sample_values.head(100).tolist()
        
        # Check if column contains meaningful text
        if _is_text_column(sample):
            text_columns.append(column)
    
    return text_columns


def _is_text_column(sample_values: List[str]) -> bool:
    """Determine if a column contains meaningful text content"""
    if not sample_values:
        return False
    
    text_indicators = 0
    total_values = len(sample_values)
    
    for value in sample_values:
        value = str(value).strip()
        
        # Skip very short values (likely codes or IDs)
        if len(value) < 3:
            continue
        
        # Skip purely numeric values
        if _is_numeric(value):
            continue
        
        # Skip date-like values
        if _is_date_like(value):
            continue
        
        # Check for text indicators
        has_spaces = ' ' in value
        has_multiple_words = len(value.split()) > 1
        has_letters = any(c.isalpha() for c in value)
        reasonable_length = 3 <= len(value) <= 1000
        
        if has_letters and (has_spaces or has_multiple_words) and reasonable_length:
            text_indicators += 1
    
    # Column is considered text if at least 30% of values look like text
    return (text_indicators / total_values) >= 0.3 if total_values > 0 else False


def _is_numeric(value: str) -> bool:
    """Check if a value is numeric (int, float, percentage, currency)"""
    value = value.strip()
    
    # Remove common numeric formatting
    cleaned = re.sub(r'[$,%]', '', value)
    cleaned = cleaned.replace('(', '-').replace(')', '')  # Handle negative numbers in parentheses
    
    try:
        float(cleaned)
        return True
    except ValueError:
        return False


def _is_date_like(value: str) -> bool:
    """Check if a value looks like a date"""
    value = value.strip()
    
    # Common date patterns
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
        r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        r'\d{1,2}/\d{1,2}/\d{2,4}',  # M/D/YY or MM/DD/YYYY
    ]
    
    return any(re.match(pattern, value) for pattern in date_patterns)


def _extract_text_content(df: pd.DataFrame, text_columns: List[str]) -> str:
    """Extract and combine text content from identified text columns"""
    all_text = []
    
    for column in text_columns:
        column_values = df[column].dropna().astype(str)
        column_values = column_values[column_values.str.strip() != '']
        
        if len(column_values) > 0:
            # Add column header if it looks like meaningful text
            if str(column) != '0' and len(str(column)) > 1:  # Skip numeric column names
                all_text.append(f"=== {column} ===")
            
            # Add all text values from this column
            for value in column_values:
                cleaned_value = str(value).strip()
                if len(cleaned_value) >= 3:  # Only include substantial text
                    all_text.append(cleaned_value)
            
            all_text.append("")  # Add spacing between columns
    
    # Join all text with newlines
    result = "\n".join(all_text).strip()
    
    # Clean up multiple consecutive newlines
    result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)
    
    return result