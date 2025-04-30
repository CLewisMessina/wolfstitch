# processing/extract.py
import os
import zipfile
from bs4 import BeautifulSoup

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