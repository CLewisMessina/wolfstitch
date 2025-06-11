# wolfscribe/processing/extractors/xml_extractor.py
"""
XML file extractor for Wolfscribe

Handles .xml files by extracting text content from XML elements and attributes,
with intelligent handling of document-oriented vs data-oriented XML.
"""

import os
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Set, Optional


def extract_text(path: str) -> str:
    """
    Extract text from XML files
    
    Args:
        path (str): Path to the XML file
        
    Returns:
        str: Extracted text content from XML elements and attributes
        
    Raises:
        RuntimeError: If XML extraction fails
    """
    if not os.path.exists(path):
        raise RuntimeError(f"XML file not found: {path}")
    
    try:
        # Try BeautifulSoup first for more robust parsing
        try:
            from bs4 import BeautifulSoup
            return _extract_with_beautifulsoup(path)
        except ImportError:
            # Fallback to built-in XML parser
            return _extract_with_elementtree(path)
            
    except Exception as e:
        if "XML" in str(e):
            raise
        else:
            raise RuntimeError(f"XML extraction failed: {str(e)}")


def _extract_with_beautifulsoup(path: str) -> str:
    """Extract text using BeautifulSoup for robust XML parsing"""
    
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as f:
                xml_content = f.read()
            break
        except UnicodeDecodeError:
            continue
    else:
        raise RuntimeError(f"Cannot read XML file with any supported encoding")
    
    # Parse with BeautifulSoup using XML parser
    soup = BeautifulSoup(xml_content, 'xml')
    
    # Analyze XML structure to determine extraction strategy
    analysis = _analyze_xml_structure(soup)
    
    # Extract text based on analysis
    if analysis['is_document_oriented']:
        return _extract_document_oriented_text(soup, analysis)
    else:
        return _extract_data_oriented_text(soup, analysis)


def _extract_with_elementtree(path: str) -> str:
    """Fallback extraction using built-in ElementTree"""
    
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except ET.ParseError as e:
        raise RuntimeError(f"Invalid XML format: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Cannot parse XML file: {str(e)}")
    
    # Extract all text content recursively
    all_texts = []
    _extract_text_recursive_et(root, all_texts, set())
    
    if not all_texts:
        return ""
    
    # Clean and join the extracted text
    cleaned_texts = []
    for text in all_texts:
        cleaned = text.strip()
        if len(cleaned) >= 3 and _is_meaningful_text(cleaned):
            cleaned_texts.append(cleaned)
    
    return '\n'.join(cleaned_texts)


def _analyze_xml_structure(soup) -> Dict[str, any]:
    """Analyze XML structure to determine the best extraction strategy"""
    
    analysis = {
        'is_document_oriented': False,
        'total_elements': 0,
        'text_elements': 0,
        'common_tags': {},
        'has_mixed_content': False,
        'root_tag': ''
    }
    
    # Get root element info
    if soup.contents:
        root = soup.contents[0] if hasattr(soup.contents[0], 'name') else None
        if root:
            analysis['root_tag'] = root.name
    
    # Count elements and analyze content
    all_elements = soup.find_all()
    analysis['total_elements'] = len(all_elements)
    
    tag_counts = {}
    text_element_count = 0
    mixed_content_count = 0
    
    for element in all_elements:
        tag_name = element.name
        tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1
        
        # Check if element has text content
        if element.string and element.string.strip():
            text_element_count += 1
        
        # Check for mixed content (text + child elements)
        if element.string and len(element.find_all()) > 0:
            mixed_content_count += 1
    
    analysis['text_elements'] = text_element_count
    analysis['common_tags'] = tag_counts
    analysis['has_mixed_content'] = mixed_content_count > 0
    
    # Determine if document-oriented based on common patterns
    document_indicators = [
        'document', 'article', 'book', 'chapter', 'section', 'paragraph',
        'title', 'heading', 'text', 'content', 'body', 'html', 'div', 'p'
    ]
    
    data_indicators = [
        'data', 'record', 'row', 'item', 'entry', 'config', 'settings',
        'property', 'field', 'value', 'id', 'name', 'type'
    ]
    
    doc_score = sum(tag_counts.get(tag, 0) for tag in document_indicators)
    data_score = sum(tag_counts.get(tag, 0) for tag in data_indicators)
    
    # Also consider root tag name
    root_tag_lower = analysis['root_tag'].lower()
    if any(indicator in root_tag_lower for indicator in document_indicators):
        doc_score += 10
    elif any(indicator in root_tag_lower for indicator in data_indicators):
        data_score += 10
    
    # Document-oriented if more document indicators or has mixed content
    analysis['is_document_oriented'] = (
        doc_score > data_score or 
        analysis['has_mixed_content'] or
        analysis['text_elements'] / max(analysis['total_elements'], 1) > 0.3
    )
    
    return analysis


def _extract_document_oriented_text(soup, analysis: Dict) -> List[str]:
    """Extract text from document-oriented XML (like DocBook, XHTML, etc.)"""
    
    content_parts = []
    
    # Extract title/heading elements first
    title_tags = ['title', 'heading', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    for tag_name in title_tags:
        elements = soup.find_all(tag_name)
        for element in elements:
            text = element.get_text(strip=True)
            if text and len(text) > 2:
                content_parts.append(f"Title: {text}")
    
    # Extract paragraph-like content
    content_tags = ['p', 'paragraph', 'text', 'content', 'section', 'div']
    for tag_name in content_tags:
        elements = soup.find_all(tag_name)
        for element in elements:
            text = element.get_text(strip=True)
            if text and len(text) > 10:
                content_parts.append(text)
    
    # Extract any remaining text content
    all_text = soup.get_text(separator='\n', strip=True)
    if all_text and not content_parts:
        # If no structured content found, use all text
        content_parts.append(all_text)
    
    return '\n\n'.join(content_parts) if content_parts else ""


def _extract_data_oriented_text(soup, analysis: Dict) -> str:
    """Extract text from data-oriented XML (like config files, data exports)"""
    
    text_contents = []
    
    # Find all elements with text content
    for element in soup.find_all():
        # Skip elements that are likely metadata
        if _is_metadata_element(element.name):
            continue
        
        # Get direct text content (not from children)
        if element.string:
            text = element.string.strip()
            if len(text) >= 3 and _is_meaningful_text(text):
                # Include element name for context if it's descriptive
                if _is_descriptive_tag(element.name):
                    text_contents.append(f"{element.name}: {text}")
                else:
                    text_contents.append(text)
        
        # Extract meaningful attribute values
        for attr_name, attr_value in element.attrs.items():
            if _is_text_attribute(attr_name, str(attr_value)):
                text_contents.append(f"{attr_name}: {attr_value}")
    
    return '\n'.join(text_contents) if text_contents else ""


def _extract_text_recursive_et(element, texts: List[str], seen_elements: Set) -> None:
    """Recursively extract text from ElementTree elements"""
    
    # Prevent infinite recursion
    element_id = id(element)
    if element_id in seen_elements:
        return
    seen_elements.add(element_id)
    
    # Extract text content
    if element.text and element.text.strip():
        texts.append(element.text.strip())
    
    # Extract tail text (text after the element)
    if element.tail and element.tail.strip():
        texts.append(element.tail.strip())
    
    # Extract meaningful attribute values
    for attr_name, attr_value in element.attrib.items():
        if _is_text_attribute(attr_name, attr_value):
            texts.append(f"{attr_name}: {attr_value}")
    
    # Recursively process children
    for child in element:
        _extract_text_recursive_et(child, texts, seen_elements)
    
    seen_elements.remove(element_id)


def _is_metadata_element(tag_name: str) -> bool:
    """Check if an element is likely metadata rather than content"""
    metadata_tags = {
        'id', 'uuid', 'timestamp', 'created', 'modified', 'version',
        'status', 'type', 'format', 'encoding', 'size', 'length',
        'count', 'index', 'position', 'ref', 'href', 'src', 'url'
    }
    
    return tag_name.lower() in metadata_tags


def _is_descriptive_tag(tag_name: str) -> bool:
    """Check if a tag name is descriptive enough to include as context"""
    # Include tag name if it's descriptive
    descriptive_indicators = [
        'name', 'title', 'description', 'content', 'text', 'message',
        'comment', 'note', 'summary', 'abstract', 'label', 'caption'
    ]
    
    tag_lower = tag_name.lower()
    return (
        any(indicator in tag_lower for indicator in descriptive_indicators) or
        len(tag_name) > 2  # Include longer tag names as they're usually meaningful
    )


def _is_text_attribute(attr_name: str, attr_value: str) -> bool:
    """Check if an attribute contains meaningful text content"""
    
    # Common text attributes
    text_attributes = {
        'title', 'alt', 'description', 'label', 'caption', 'summary',
        'name', 'value', 'content', 'text', 'comment', 'note'
    }
    
    attr_lower = attr_name.lower()
    
    # Check if attribute name suggests text content
    if attr_lower in text_attributes:
        return True
    
    # Check if value looks like meaningful text
    if len(attr_value) >= 10 and _is_meaningful_text(attr_value):
        return True
    
    return False


def _is_meaningful_text(text: str) -> bool:
    """Check if text is meaningful content (not just IDs, codes, etc.)"""
    
    text = text.strip()
    
    # Skip very short text
    if len(text) < 3:
        return False
    
    # Must contain at least one letter
    if not any(c.isalpha() for c in text):
        return False
    
    # Skip if it looks like a UUID
    if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', text, re.IGNORECASE):
        return False
    
    # Skip if it looks like a hash
    if re.match(r'^[0-9a-f]{16,}$', text, re.IGNORECASE):
        return False
    
    # Skip simple timestamps
    if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', text):
        return False
    
    # Skip URLs
    if text.startswith(('http://', 'https://', 'ftp://', 'file://')):
        return False
    
    return True