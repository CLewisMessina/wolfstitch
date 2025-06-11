# wolfscribe/processing/extractors/json_extractor.py
"""
JSON and JSONL file extractor for Wolfscribe

Handles .json and .jsonl files by recursively extracting text content
from structured data, with special handling for chat logs and API responses.
"""

import os
import json
from typing import List, Dict, Any, Union, Set


def extract_text(path: str) -> str:
    """
    Extract text from JSON or JSONL files
    
    Args:
        path (str): Path to the JSON/JSONL file
        
    Returns:
        str: Extracted text content from the JSON structure
        
    Raises:
        RuntimeError: If JSON extraction fails
    """
    if not os.path.exists(path):
        raise RuntimeError(f"JSON file not found: {path}")
    
    file_ext = os.path.splitext(path)[1].lower()
    
    try:
        if file_ext == '.jsonl':
            return _extract_jsonl(path)
        else:
            return _extract_json(path)
            
    except Exception as e:
        if "JSON" in str(e):
            raise
        else:
            raise RuntimeError(f"JSON extraction failed: {str(e)}")


def _extract_json(path: str) -> str:
    """Extract text from a standard JSON file"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except UnicodeDecodeError:
        # Try different encoding
        try:
            with open(path, 'r', encoding='latin-1') as f:
                data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Cannot read JSON file with any encoding: {str(e)}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON format: {str(e)}")
    
    # Extract text content recursively
    extracted_texts = []
    _extract_text_recursive(data, extracted_texts, set())
    
    if not extracted_texts:
        return ""
    
    return "\n".join(extracted_texts)


def _extract_jsonl(path: str) -> str:
    """Extract text from a JSONL (JSON Lines) file"""
    extracted_texts = []
    line_number = 0
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line_number += 1
                line = line.strip()
                
                if not line:  # Skip empty lines
                    continue
                
                try:
                    data = json.loads(line)
                    line_texts = []
                    _extract_text_recursive(data, line_texts, set())
                    
                    if line_texts:
                        extracted_texts.extend(line_texts)
                        
                except json.JSONDecodeError as e:
                    # Log error but continue processing other lines
                    print(f"Warning: Invalid JSON on line {line_number}: {str(e)}")
                    continue
                    
    except UnicodeDecodeError:
        # Try different encoding
        try:
            with open(path, 'r', encoding='latin-1') as f:
                for line in f:
                    line_number += 1
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        line_texts = []
                        _extract_text_recursive(data, line_texts, set())
                        
                        if line_texts:
                            extracted_texts.extend(line_texts)
                            
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            raise RuntimeError(f"Cannot read JSONL file: {str(e)}")
    
    if not extracted_texts:
        return ""
    
    return "\n".join(extracted_texts)


def _extract_text_recursive(obj: Any, texts: List[str], seen_objects: Set[id]) -> None:
    """
    Recursively extract text content from JSON objects
    
    Args:
        obj: The JSON object/value to process
        texts: List to append extracted text to
        seen_objects: Set of object IDs to prevent infinite recursion
    """
    # Prevent infinite recursion on circular references
    if isinstance(obj, (dict, list)) and id(obj) in seen_objects:
        return
    
    if isinstance(obj, dict):
        seen_objects.add(id(obj))
        _extract_from_dict(obj, texts, seen_objects)
        seen_objects.remove(id(obj))
        
    elif isinstance(obj, list):
        seen_objects.add(id(obj))
        _extract_from_list(obj, texts, seen_objects)
        seen_objects.remove(id(obj))
        
    elif isinstance(obj, str):
        _extract_from_string(obj, texts)


def _extract_from_dict(obj: Dict[str, Any], texts: List[str], seen_objects: Set[id]) -> None:
    """Extract text from dictionary objects with intelligent key prioritization"""
    
    # Define priority keys that typically contain meaningful text content
    text_priority_keys = [
        'content', 'message', 'text', 'body', 'description', 'title', 
        'name', 'summary', 'comment', 'note', 'value', 'data'
    ]
    
    # Define keys that typically contain chat/conversation data
    chat_keys = [
        'role', 'content', 'message', 'text', 'assistant', 'user', 'system'
    ]
    
    # Check if this looks like a chat message
    is_chat_message = any(key in obj for key in chat_keys)
    
    if is_chat_message:
        _extract_chat_message(obj, texts, seen_objects)
    else:
        # Process high-priority text keys first
        processed_keys = set()
        
        for key in text_priority_keys:
            if key in obj:
                value = obj[key]
                if isinstance(value, str) and len(value.strip()) > 0:
                    _extract_from_string(value, texts)
                    processed_keys.add(key)
                elif isinstance(value, (dict, list)):
                    _extract_text_recursive(value, texts, seen_objects)
                    processed_keys.add(key)
        
        # Process remaining keys, skipping metadata-like keys
        metadata_keys = {
            'id', 'timestamp', 'created_at', 'updated_at', 'version', 
            'status', 'type', 'format', 'encoding', 'size', 'length',
            'count', 'index', 'position', 'offset', 'score', 'weight'
        }
        
        for key, value in obj.items():
            if key not in processed_keys and key.lower() not in metadata_keys:
                _extract_text_recursive(value, texts, seen_objects)


def _extract_from_list(obj: List[Any], texts: List[str], seen_objects: Set[id]) -> None:
    """Extract text from list objects"""
    for item in obj:
        _extract_text_recursive(item, texts, seen_objects)


def _extract_from_string(text: str, texts: List[str]) -> None:
    """Extract meaningful text from string values"""
    text = text.strip()
    
    # Skip very short strings (likely IDs or codes)
    if len(text) < 3:
        return
    
    # Skip strings that look like IDs, UUIDs, or hashes
    if _looks_like_id(text):
        return
    
    # Skip strings that look like timestamps or dates
    if _looks_like_timestamp(text):
        return
    
    # Skip strings that look like URLs or file paths
    if _looks_like_url_or_path(text):
        return
    
    # Add the text if it passes our filters
    texts.append(text)


def _extract_chat_message(obj: Dict[str, Any], texts: List[str], seen_objects: Set[id]) -> None:
    """Special handling for chat message objects"""
    # Common chat message formats:
    # {"role": "user", "content": "message"}
    # {"message": "text", "role": "assistant"}
    # {"text": "content", "user": "name"}
    
    role = ""
    content = ""
    
    # Extract role information
    for role_key in ['role', 'sender', 'user', 'author', 'from']:
        if role_key in obj and isinstance(obj[role_key], str):
            role = obj[role_key].strip()
            break
    
    # Extract message content
    for content_key in ['content', 'message', 'text', 'body']:
        if content_key in obj:
            if isinstance(obj[content_key], str):
                content = obj[content_key].strip()
                break
            elif isinstance(obj[content_key], (dict, list)):
                # Handle nested content
                content_texts = []
                _extract_text_recursive(obj[content_key], content_texts, seen_objects)
                content = " ".join(content_texts)
                break
    
    # Format the chat message
    if content:
        if role:
            texts.append(f"{role}: {content}")
        else:
            texts.append(content)
    
    # Process any remaining fields
    processed_keys = {'role', 'sender', 'user', 'author', 'from', 'content', 'message', 'text', 'body'}
    for key, value in obj.items():
        if key not in processed_keys:
            _extract_text_recursive(value, texts, seen_objects)


def _looks_like_id(text: str) -> bool:
    """Check if text looks like an ID, UUID, or hash"""
    import re
    
    # UUID pattern
    if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', text, re.IGNORECASE):
        return True
    
    # Hash-like (long string of hex characters)
    if re.match(r'^[0-9a-f]{16,}$', text, re.IGNORECASE):
        return True
    
    # Simple numeric ID
    if re.match(r'^\d+$', text) and len(text) > 8:
        return True
    
    # Base64-like
    if re.match(r'^[A-Za-z0-9+/]+=*$', text) and len(text) > 20:
        return True
    
    return False


def _looks_like_timestamp(text: str) -> bool:
    """Check if text looks like a timestamp or date"""
    import re
    
    timestamp_patterns = [
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO format
        r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # SQL format
        r'^\d{10,13}$',  # Unix timestamp
        r'^\d{4}-\d{2}-\d{2}$',  # Date only
        r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
    ]
    
    return any(re.match(pattern, text) for pattern in timestamp_patterns)


def _looks_like_url_or_path(text: str) -> bool:
    """Check if text looks like a URL or file path"""
    # URL patterns
    if text.startswith(('http://', 'https://', 'ftp://', 'file://')):
        return True
    
    # File path patterns
    if ('/' in text and len(text.split('/')) > 2) or ('\\' in text and len(text.split('\\')) > 2):
        return True
    
    # Email addresses
    if '@' in text and '.' in text.split('@')[-1]:
        return True
    
    return False