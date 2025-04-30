# export/dataset_exporter.py
import csv

def save_as_txt(chunks, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(chunk + "\n")

def save_as_csv(chunks, output_path):
    with open(output_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["text"],
            delimiter=",",             # Standard CSV
            quotechar='"',             # Explicit quoting char
            quoting=csv.QUOTE_ALL,     # Quote everything
            escapechar="\\"            # Escape any embedded quote chars
        )
        writer.writeheader()
        for c in chunks:
            writer.writerow({"text": c})