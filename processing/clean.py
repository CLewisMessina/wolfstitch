# processing/clean.py

import re

def clean_text(raw_text, remove_headers=True, normalize_whitespace=True, strip_bullets=True):
    text = raw_text

    if remove_headers:
        # Strip Project Gutenberg headers/footers or similar markers
        text = re.sub(r"\*\*\* START OF.*?\*\*\*", "", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"\*\*\* END OF.*?\*\*\*", "", text, flags=re.IGNORECASE | re.DOTALL)

    if strip_bullets:
        # Remove leading bullets or numbering
        text = re.sub(r"^\s*[\d\-\*\•]+\s+", "", text, flags=re.MULTILINE)

    if normalize_whitespace:
        # Replace multiple newlines or excessive spacing
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)

    return text
