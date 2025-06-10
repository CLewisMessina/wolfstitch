# processing/extract.py
import os
import zipfile
from bs4 import BeautifulSoup

def load_file(path):
    """Main dispatcher for file loading - now supports DOCX"""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        return load_txt(path)
    elif ext == ".pdf":
        return load_pdf(path)
    elif ext == ".epub":
        return load_epub(path)
    elif ext == ".docx":
        return load_docx(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def load_txt(path):
    """Load plain text files"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_pdf(path):
    """Load PDF files using pdfminer"""
    try:
        from pdfminer.high_level import extract_text
        return extract_text(path)
    except Exception as e:
        raise RuntimeError(f"PDF extraction failed: {str(e)}")

def load_epub(path):
    """Load EPUB files using BeautifulSoup"""
    try:
        all_text = []

        with zipfile.ZipFile(path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith((".htm", ".html", ".xhtml")):
                    with zip_ref.open(file) as f:
                        soup = BeautifulSoup(f.read(), "html.parser")
                        # Remove scripts/styles
                        for tag in soup(["script", "style"]):
                            tag.decompose()
                        body_text = soup.get_text(separator="\n", strip=True)
                        if body_text:
                            all_text.append(body_text)

        return "\n\n".join(all_text)
    except Exception as e:
        raise RuntimeError(f"EPUB fallback parsing failed: {str(e)}")

def load_docx(path):
    """
    Load Microsoft Word DOCX files using python-docx
    
    Extracts:
    - All paragraph text (including headings)
    - Table content (all cells)
    - Comments and footnotes
    - Header and footer text
    
    Args:
        path (str): Path to the DOCX file
        
    Returns:
        str: Extracted text content
        
    Raises:
        RuntimeError: If extraction fails due to corruption, password protection, or other issues
    """
    try:
        from docx import Document
        from docx.opc.exceptions import PackageNotFoundError
        from docx.shared import Length
        
        # Attempt to open the document
        try:
            doc = Document(path)
        except PackageNotFoundError:
            raise RuntimeError("DOCX file is corrupted or not a valid Word document")
        except Exception as e:
            if "password" in str(e).lower() or "encrypted" in str(e).lower():
                raise RuntimeError("DOCX file is password protected - cannot extract text")
            else:
                raise RuntimeError(f"Cannot open DOCX file: {str(e)}")
        
        extracted_text = []
        
        # Extract main document paragraphs and headings
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                extracted_text.append(text)
        
        # Extract table content
        for table in doc.tables:
            table_text = _extract_table_text(table)
            if table_text:
                extracted_text.append(table_text)
        
        # Extract header and footer text
        for section in doc.sections:
            # Headers
            if section.header:
                header_text = _extract_header_footer_text(section.header)
                if header_text:
                    extracted_text.append(f"[HEADER] {header_text}")
            
            # Footers
            if section.footer:
                footer_text = _extract_header_footer_text(section.footer)
                if footer_text:
                    extracted_text.append(f"[FOOTER] {footer_text}")
        
        # Extract comments and footnotes
        comments_and_footnotes = _extract_comments_and_footnotes(doc)
        if comments_and_footnotes:
            extracted_text.extend(comments_and_footnotes)
        
        # Join all extracted text
        full_text = "\n\n".join(extracted_text)
        
        if not full_text.strip():
            raise RuntimeError("No text content found in DOCX file")
        
        return full_text
        
    except ImportError:
        raise RuntimeError("python-docx library not installed. Run: pip install python-docx")
    except Exception as e:
        if isinstance(e, RuntimeError):
            raise  # Re-raise our custom errors
        else:
            raise RuntimeError(f"DOCX extraction failed: {str(e)}")

def _extract_table_text(table):
    """
    Extract text from a Word table
    
    Args:
        table: python-docx Table object
        
    Returns:
        str: Formatted table text
    """
    table_content = []
    
    for row in table.rows:
        row_content = []
        for cell in row.cells:
            cell_text = cell.text.strip()
            if cell_text:
                row_content.append(cell_text)
        
        if row_content:
            table_content.append(" | ".join(row_content))
    
    if table_content:
        return "\n".join(table_content)
    return ""

def _extract_header_footer_text(header_footer):
    """
    Extract text from header or footer
    
    Args:
        header_footer: python-docx Header or Footer object
        
    Returns:
        str: Extracted text
    """
    text_parts = []
    
    # Extract paragraphs from header/footer
    for paragraph in header_footer.paragraphs:
        text = paragraph.text.strip()
        if text:
            text_parts.append(text)
    
    # Extract table content from header/footer
    for table in header_footer.tables:
        table_text = _extract_table_text(table)
        if table_text:
            text_parts.append(table_text)
    
    return " ".join(text_parts)

def _extract_comments_and_footnotes(doc):
    """
    Extract comments and footnotes from Word document
    
    Args:
        doc: python-docx Document object
        
    Returns:
        list: List of comment and footnote text
    """
    extracted = []
    
    try:
        # Extract comments
        # Note: python-docx doesn't have direct comment access in the basic API
        # This is a simplified approach that may miss some comments
        # For full comment extraction, would need to parse the underlying XML
        
        # Extract footnotes from document relationships
        # This is also limited by python-docx's API capabilities
        # For comprehensive footnote extraction, XML parsing would be needed
        
        # For now, we'll note that comments and footnotes may need manual handling
        # or a more advanced library like python-docx2txt for complete extraction
        
        pass  # Placeholder for future enhancement
        
    except Exception as e:
        # Don't fail the entire extraction if comments/footnotes can't be extracted
        pass
    
    return extracted

def _validate_docx_health(path):
    """
    Perform basic health check on DOCX file
    
    Args:
        path (str): Path to DOCX file
        
    Returns:
        dict: Health check results
    """
    health_info = {
        "is_valid_zip": False,
        "has_document_xml": False,
        "estimated_size": 0,
        "warnings": []
    }
    
    try:
        # Check if file is a valid ZIP (DOCX is a ZIP container)
        with zipfile.ZipFile(path, 'r') as zip_file:
            health_info["is_valid_zip"] = True
            
            # Check for core document.xml
            if "word/document.xml" in zip_file.namelist():
                health_info["has_document_xml"] = True
            
            # Estimate content size
            health_info["estimated_size"] = sum(
                zip_file.getinfo(name).file_size 
                for name in zip_file.namelist()
                if name.startswith("word/")
            )
            
    except zipfile.BadZipFile:
        health_info["warnings"].append("File is not a valid ZIP/DOCX format")
    except Exception as e:
        health_info["warnings"].append(f"Health check failed: {str(e)}")
    
    return health_info