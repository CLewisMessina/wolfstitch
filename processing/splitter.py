#processing/splitter.py
def split_text(text, method="paragraph", delimiter=None):
    if method == "paragraph":
        return [p.strip() for p in text.split("\n\n") if p.strip()]
    elif method == "sentence":
        import re
        return re.split(r'(?<=[.!?]) +', text)
    elif method == "custom" and delimiter:
        return [s.strip() for s in text.split(delimiter)]
    else:
        raise ValueError("Invalid split method.")
