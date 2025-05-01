# ui/app_frame.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Toplevel
from ttkbootstrap import Frame, Label, Button, Entry, Combobox
from ttkbootstrap.constants import *
from controller import process_book, get_token_count
from export.dataset_exporter import save_as_txt, save_as_csv
from tkinterdnd2 import DND_FILES  # Add this line

TOKEN_LIMIT = 512  # Adjust if needed

class AppFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)

        self.file_path = None
        self.chunks = []

        # File selection
        self.file_label = Label(self, text="📂 No file selected", anchor="w")
        self.file_label.pack(fill=X, pady=(0, 10))

        file_btn = Button(self, text="Select File", command=self.select_file)
        file_btn.pack(fill=X, pady=(0, 10))

        # Enable drag-and-drop on the whole frame
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_file_drop)

        # Split method
        self.split_method = tk.StringVar(value="paragraph")
        split_label = Label(self, text="✂️ Split Method:")
        split_label.pack(anchor="w")
        self.split_dropdown = Combobox(self, textvariable=self.split_method, values=["paragraph", "sentence", "custom"])
        self.split_dropdown.pack(fill=X, pady=(0, 10))

        # Custom delimiter input (optional)
        self.delimiter_entry = Entry(self)
        self.delimiter_entry.insert(0, "")
        self.delimiter_entry.pack(fill=X, pady=(0, 10))

        # Process button
        process_btn = Button(self, text="🛠️ Process Text", command=self.process_text)
        process_btn.pack(fill=X, pady=(10, 10))

        # Preview and export
        preview_btn = Button(self, text="👀 Preview Chunks", command=self.preview_chunks)
        preview_btn.pack(fill=X, pady=(0, 10))

        export_txt_btn = Button(self, text="💾 Export as .txt", command=self.export_txt)
        export_txt_btn.pack(fill=X, pady=(0, 5))

        export_csv_btn = Button(self, text="📊 Export as .csv", command=self.export_csv)
        export_csv_btn.pack(fill=X)

    def select_file(self):
        path = filedialog.askopenfilename(title="Select Book or Document", filetypes=[
            ("Text or Document Files", "*.txt *.pdf *.epub")
        ])
        if path:
            self.file_path = path
            self.file_label.config(text=f"📂 {os.path.basename(path)}")
            self.chunks = []

    def handle_file_drop(self, event):
        path = event.data.strip("{}")  # Remove surrounding braces if present
        if os.path.isfile(path) and path.lower().endswith((".txt", ".pdf", ".epub")):
            self.file_path = path
            self.file_label.config(text=f"📂 {os.path.basename(path)}")
            self.chunks = []
        else:
            messagebox.showerror("Invalid File", "Please drop a valid .txt, .pdf, or .epub file.")

    def process_text(self):
        if not self.file_path:
            messagebox.showerror("Missing File", "Please select a file first.")
            return

        method = self.split_method.get()
        delimiter = self.delimiter_entry.get() if method == "custom" else None

        try:
            clean_opts = {
                "remove_headers": True,
                "normalize_whitespace": True,
                "strip_bullets": True
            }
            self.chunks = process_book(self.file_path, clean_opts, method, delimiter)
            too_long = sum(1 for c in self.chunks if get_token_count(c) > TOKEN_LIMIT)

            msg = f"Processed {len(self.chunks)} chunks."
            if too_long > 0:
                msg += f" ⚠️ {too_long} chunks exceed {TOKEN_LIMIT} tokens."
            messagebox.showinfo("✅ Success", msg)
        except Exception as e:
            messagebox.showerror("Processing Error", str(e))

    def preview_chunks(self):
        if not self.chunks:
            messagebox.showwarning("No Data", "You must process a file first.")
            return

        window = Toplevel()
        window.title("Preview: First 10 Chunks")
        window.geometry("700x500")

        text_widget = Text(window, wrap="word")
        text_widget.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        for i, chunk in enumerate(self.chunks[:10]):
            token_count = get_token_count(chunk)
            prefix = f"{i+1}: [{token_count} tokens]"
            if token_count > TOKEN_LIMIT:
                prefix += " ⚠️"
            text_widget.insert("end", f"{prefix}\n{chunk}\n\n")

        text_widget.config(state="disabled")

    def export_txt(self):
        if not self.chunks:
            messagebox.showwarning("No Data", "Please process a file first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt")])
        if path:
            save_as_txt(self.chunks, path)
            messagebox.showinfo("Saved", f"Dataset saved to {path}")

    def export_csv(self):
        if not self.chunks:
            messagebox.showwarning("No Data", "Please process a file first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV File", "*.csv")])
        if path:
            save_as_csv(self.chunks, path)
            messagebox.showinfo("Saved", f"Dataset saved to {path}")
