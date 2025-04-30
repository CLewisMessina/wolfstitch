# processing/extract.py
import os

def load_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        return load_txt(path)
    elif ext == ".pdf":
        return load_pdf(path)
    elif ext == ".epub":
        return load_epub(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def load_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_pdf(path):
    try:
        from pdfminer.high_level import extract_text
        return extract_text(path)
    except Exception as e:
        raise RuntimeError(f"PDF extraction failed: {str(e)}")

def load_epub(path):
    try:
        from ebooklib import epub
        from bs4 import BeautifulSoup

        book = epub.read_epub(path)
        all_text = []

        for item in book.get_items():
            if item.get_type() == epub.EpubHtml:
                soup = BeautifulSoup(item.get_content(), "html.parser")
                # Remove scripts/styles
                for tag in soup(["script", "style"]):
                    tag.decompose()
                # Extract all visible text
                body_text = soup.get_text(separator="\n", strip=True)
                if body_text:
                    all_text.append(body_text)

        return "\n\n".join(all_text)
    except Exception as e:
        raise RuntimeError(f"EPUB extraction failed: {str(e)}")

