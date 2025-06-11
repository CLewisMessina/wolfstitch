# wolfscribe/processing/extractors/html_extractor.py
"""
HTML file extractor for Wolfscribe

Handles .html and .htm files by extracting clean text content while
removing navigation, scripts, and other non-content elements.
"""

import os
import re
from typing import List, Optional


def extract_text(path: str) -> str:
    """
    Extract text from HTML files
    
    Args:
        path (str): Path to the HTML file
        
    Returns:
        str: Clean text content with HTML markup removed
        
    Raises:
        RuntimeError: If HTML extraction fails
    """
    if not os.path.exists(path):
        raise RuntimeError(f"HTML file not found: {path}")
    
    try:
        # Try to use BeautifulSoup for proper HTML parsing
        try:
            from bs4 import BeautifulSoup
            return _extract_with_beautifulsoup(path)
        except ImportError:
            # Fallback to regex-based extraction
            return _extract_with_regex(path)
            
    except Exception as e:
        if "HTML" in str(e):
            raise
        else:
            raise RuntimeError(f"HTML extraction failed: {str(e)}")


def _extract_with_beautifulsoup(path: str) -> str:
    """Extract text using BeautifulSoup for proper HTML parsing"""
    
    # Try different encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as f:
                html_content = f.read()
            break
        except UnicodeDecodeError:
            continue
    else:
        raise RuntimeError(f"Cannot read HTML file with any supported encoding")
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted elements
    _remove_unwanted_elements(soup)
    
    # Extract text from main content areas
    main_content = _extract_main_content(soup)
    
    if main_content:
        return main_content
    
    # Fallback: extract all remaining text
    return soup.get_text(separator='\n', strip=True)


def _extract_with_regex(path: str) -> str:
    """Fallback extraction using regex (when BeautifulSoup not available)"""
    
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as f:
                html_content = f.read()
            break
        except UnicodeDecodeError:
            continue
    else:
        raise RuntimeError(f"Cannot read HTML file with any supported encoding")
    
    # Remove script and style elements
    html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove common navigation and footer elements
    html_content = re.sub(r'<nav.*?</nav>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<header.*?</header>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<footer.*?</footer>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove comments
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    # Remove all HTML tags
    html_content = re.sub(r'<[^>]+>', '', html_content)
    
    # Decode HTML entities
    html_content = _decode_html_entities(html_content)
    
    # Clean up whitespace
    html_content = re.sub(r'\n\s*\n\s*\n', '\n\n', html_content)
    html_content = re.sub(r'[ \t]+', ' ', html_content)
    
    return html_content.strip()


def _remove_unwanted_elements(soup) -> None:
    """Remove elements that typically don't contain main content"""
    
    # Remove scripts, styles, and meta elements
    for tag in soup(['script', 'style', 'meta', 'link', 'noscript']):
        tag.decompose()
    
    # Remove navigation elements
    for tag in soup.find_all(['nav', 'header', 'footer']):
        tag.decompose()
    
    # Remove common navigation/sidebar classes and IDs
    unwanted_selectors = [
        '[class*="nav"]', '[class*="menu"]', '[class*="sidebar"]',
        '[class*="footer"]', '[class*="header"]', '[class*="breadcrumb"]',
        '[id*="nav"]', '[id*="menu"]', '[id*="sidebar"]',
        '[id*="footer"]', '[id*="header"]', '[role="navigation"]',
        '[class*="advertisement"]', '[class*="ads"]', '[class*="promo"]'
    ]
    
    for selector in unwanted_selectors:
        try:
            for element in soup.select(selector):
                element.decompose()
        except Exception:
            # Ignore selector errors and continue
            continue
    
    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, type(soup.new_string('')))):
        if '<!--' in str(comment):
            comment.extract()


def _extract_main_content(soup) -> str:
    """Extract text from main content areas of the page"""
    
    content_parts = []
    
    # Look for main content containers (in order of preference)
    main_selectors = [
        'main', 'article', '[role="main"]',
        '.content', '.main-content', '.post-content',
        '#content', '#main-content', '#post-content',
        '.entry-content', '.page-content', '.article-content'
    ]
    
    main_content_found = False
    
    for selector in main_selectors:
        try:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    text = element.get_text(separator='\n', strip=True)
                    if len(text) > 100:  # Only include substantial content
                        content_parts.append(text)
                        main_content_found = True
        except Exception:
            continue
    
    # If no main content containers found, look for content in common elements
    if not main_content_found:
        content_elements = soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for element in content_elements:
            # Skip elements that are likely navigation or metadata
            if _is_likely_content_element(element):
                text = element.get_text(strip=True)
                if len(text) > 20:  # Only include meaningful text blocks
                    content_parts.append(text)
    
    # Extract title if available
    title_text = _extract_title(soup)
    if title_text:
        content_parts.insert(0, f"Title: {title_text}")
    
    # Extract headings for structure
    headings = _extract_headings(soup)
    if headings:
        content_parts.extend(headings)
    
    # Extract alt text from images
    alt_texts = _extract_alt_texts(soup)
    if alt_texts:
        content_parts.extend(alt_texts)
    
    if content_parts:
        return '\n\n'.join(content_parts)
    
    return ""


def _extract_title(soup) -> Optional[str]:
    """Extract page title"""
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        return title_tag.string.strip()
    return None


def _extract_headings(soup) -> List[str]:
    """Extract heading text for document structure"""
    headings = []
    
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        text = heading.get_text(strip=True)
        if text and len(text) > 2:
            headings.append(f"Heading: {text}")
    
    return headings


def _extract_alt_texts(soup) -> List[str]:
    """Extract alt text from images"""
    alt_texts = []
    
    for img in soup.find_all('img', alt=True):
        alt_text = img.get('alt', '').strip()
        if alt_text and len(alt_text) > 3:
            alt_texts.append(f"Image: {alt_text}")
    
    return alt_texts


def _is_likely_content_element(element) -> bool:
    """Check if an element is likely to contain main content"""
    
    # Check element attributes for navigation indicators
    element_class = ' '.join(element.get('class', [])).lower()
    element_id = element.get('id', '').lower()
    
    # Skip navigation-related elements
    nav_indicators = [
        'nav', 'menu', 'sidebar', 'footer', 'header', 'breadcrumb',
        'advertisement', 'ads', 'promo', 'social', 'share', 'related'
    ]
    
    for indicator in nav_indicators:
        if indicator in element_class or indicator in element_id:
            return False
    
    # Check if element has substantial text content
    text = element.get_text(strip=True)
    if len(text) < 10:
        return False
    
    # Check text-to-tag ratio (content should have more text than tags)
    tag_count = len(element.find_all())
    text_length = len(text)
    
    if tag_count > 0 and text_length / tag_count < 10:
        return False  # Too many tags relative to text
    
    return True


def _decode_html_entities(text: str) -> str:
    """Decode common HTML entities"""
    
    entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&apos;': "'",
        '&nbsp;': ' ',
        '&copy;': '©',
        '&reg;': '®',
        '&trade;': '™',
        '&hellip;': '...',
        '&mdash;': '—',
        '&ndash;': '–',
        '&lsquo;': ''',
        '&rsquo;': ''',
        '&ldquo;': '"',
        '&rdquo;': '"'
    }
    
    for entity, char in entities.items():
        text = text.replace(entity, char)
    
    # Handle numeric entities
    import re
    
    def replace_numeric_entity(match):
        try:
            if match.group(1).startswith('x'):
                # Hexadecimal
                code = int(match.group(1)[1:], 16)
            else:
                # Decimal
                code = int(match.group(1))
            return chr(code)
        except (ValueError, OverflowError):
            return match.group(0)  # Return original if conversion fails
    
    text = re.sub(r'&#(x?[0-9a-fA-F]+);', replace_numeric_entity, text)
    
    return text