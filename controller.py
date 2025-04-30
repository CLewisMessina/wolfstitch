# controller.py
from processing.extract import load_file
from processing.clean import clean_text
from processing.splitter import split_text
from transformers import AutoTokenizer

# Tokenizer instance (you can replace 'gpt2' with a model of your choice)
tokenizer = AutoTokenizer.from_pretrained("gpt2")

def process_book(path, clean_opts, split_method, delimiter=None):
    raw = load_file(path)
    cleaned = clean_text(raw, **clean_opts)
    chunks = split_text(cleaned, split_method, delimiter)
    return chunks

def get_token_count(text):
    return len(tokenizer.encode(text, truncation=False))
