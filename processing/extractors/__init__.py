# wolfscribe/processing/extractors/__init__.py
"""
Modular extractors package for Wolfscribe

This package contains format-specific text extraction modules.
Each module handles one or more related file formats and provides
a standardized extract_text(path) interface.
"""

# Version info
__version__ = "1.0.0"

# Optional: Import all extractors for convenience
# Uncomment these as we create each module
# from .txt_extractor import extract_text as extract_txt
# from .pdf_extractor import extract_text as extract_pdf
# from .epub_extractor import extract_text as extract_epub
# from .docx_extractor import extract_text as extract_docx
# from .csv_extractor import extract_text as extract_csv
# from .md_extractor import extract_text as extract_md
# from .json_extractor import extract_text as extract_json
# from .xlsx_extractor import extract_text as extract_xlsx
# from .html_extractor import extract_text as extract_html
# from .xml_extractor import extract_text as extract_xml