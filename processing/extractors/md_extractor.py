# wolfscribe/processing/extractors/md_extractor.py
"""
Markdown file extractor for Wolfscribe

Handles .md and .markdown files by converting markdown to clean text
while preserving structure and optionally including/excluding code blocks.
"""

import os
import re
from typing import List, Optional


def extract_text(path: str, include_code_blocks: bool = True) -> str:
    """
    Extract text from Markdown files

    Args:
        path (str): Path to the Markdown file
        include_code_blocks (bool): Whether to include code block content

    Returns:
        str: Clean text content with markdown syntax removed

    Raises:
        RuntimeError: If markdown extraction fails
    """
    if not os.path.exists(path):
        raise RuntimeError(f"Markdown file not found: {path}")

    try:
        # Try to use markdown library for proper conversion
        try:
            import markdown
            from markdown.extensions import codehilite, tables, toc

            # Read the markdown file
            with open(path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # Configure markdown with useful extensions
            md = markdown.Markdown(
                extensions=['tables', 'toc', 'fenced_code'],
                extension_configs={}
            )

            # Convert to HTML then extract text
            html_content = md.convert(md_content)

            # Extract text from HTML
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                # Handle code blocks based on preference
                if not include_code_blocks:
                    for code_block in soup.find_all(['code', 'pre']):
                        code_block.decompose()

                clean_text = soup.get_text(separator='\n', strip=True)
                return clean_text

            except ImportError:
                # Fallback to regex-based HTML stripping
                clean_text = _strip_html_tags(html_content)
                return clean_text

        except ImportError:
            # Fallback to manual markdown parsing
            return _extract_text_manual(path, include_code_blocks)

    except Exception as e:
        if "Markdown" in str(e):
            raise
        else:
            raise RuntimeError(f"Markdown extraction failed: {str(e)}")


def _extract_text_manual(path: str, include_code_blocks: bool = True) -> str:
    """
    Manually extract text from markdown using regex patterns

    This is a fallback method when markdown library is not available.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as inner_e:
            raise RuntimeError(f"Cannot read markdown file with any encoding: {str(inner_e)}")

    # Clean the markdown content
    clean_content = _clean_markdown_manual(content, include_code_blocks)

    return clean_content


def _clean_markdown_manual(content: str, include_code_blocks: bool = True) -> str:
    """Clean markdown syntax manually using regex patterns"""

    # Handle code blocks first
    if not include_code_blocks:
        # Remove fenced code blocks (```...```)
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        # Remove indented code blocks (4+ spaces at start of line)
        content = re.sub(r'^ {4,}.*', '', content, flags=re.MULTILINE)
        # Remove inline code (`...`)
        content = re.sub(r'`[^`]*`', '', content)
    else:
        # Keep code blocks but remove the fencing
        content = re.sub(r'```(\w+)?\n', '', content)  # Remove opening fences
        content = re.sub(r'\n```', '', content)  # Remove closing fences
        content = re.sub(r'`([^`]*)`', r'\1', content)  # Remove inline code backticks

    # Remove headers but keep the text
    content = re.sub(r'^#{1,6}\s*', '', content, flags=re.MULTILINE)

    # Remove horizontal rules
    content = re.sub(r'^[-*_]{3,}$', '', content, flags=re.MULTILINE)

    # Clean up links - keep the link text, remove the URL
    content = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', content)  # [text](url) -> text
    content = re.sub(r'\[([^\]]*)\]\[[^\]]*\]', r'\1', content)  # [text][ref] -> text

    # Clean up images - keep alt text
    content = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', content)  # ![alt](url) -> alt

    # Remove emphasis markers but keep text
    content = re.sub(r'\*\*([^*]*)\*\*', r'\1', content)  # **bold** -> bold
    content = re.sub(r'\*([^*]*)\*', r'\1', content)  # *italic* -> italic
    content = re.sub(r'__([^_]*)__', r'\1', content)  # __bold__ -> bold
    content = re.sub(r'_([^_]*)_', r'\1', content)  # _italic_ -> italic

    # Clean up lists - remove markers but keep content
    content = re.sub(r'^\s*[-*+]\s+', '', content, flags=re.MULTILINE)  # Unordered lists
    content = re.sub(r'^\s*\d+\.\s+', '', content, flags=re.MULTILINE)  # Ordered lists

    # Clean up blockquotes
    content = re.sub(r'^>\s*', '', content, flags=re.MULTILINE)

    # Clean up tables - replace pipe separators with spaces and remove separator lines
    content = re.sub(r'\|', ' ', content)  # Replace table pipes with spaces
    content = re.sub(r'^[-\s:|]+', '', content, flags=re.MULTILINE)  # Remove table separator lines

    # Clean up extra whitespace
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Multiple newlines -> double newline
    content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces/tabs -> single space

    return content.strip()


def _strip_html_tags(html_content: str) -> str:
    """Strip HTML tags using regex (fallback when BeautifulSoup not available)"""
    # Remove script and style elements
    html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

    # Remove all HTML tags
    html_content = re.sub(r'<[^>]+>', '', html_content)

    # Decode common HTML entities
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' '
    }

    for entity, char in html_entities.items():
        html_content = html_content.replace(entity, char)

    # Clean up whitespace
    html_content = re.sub(r'\n\s*\n\s*\n', '\n\n', html_content)
    html_content = re.sub(r'[ \t]+', ' ', html_content)

    return html_content.strip()
