# ui/app_frame.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Toplevel, PhotoImage
from ttkbootstrap import Frame, Label, Button, Entry, Combobox
from ttkbootstrap.constants import *
from controller import process_book, get_token_count
from session import Session
from export.dataset_exporter import save_as_txt, save_as_csv
from tkinterdnd2 import DND_FILES

TOKEN_LIMIT = 512

class AppFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=24)
        self.session = Session()
        self.file_path = None
        self.chunks = []

        self.icon = lambda name: PhotoImage(file=f"assets/icons/{name}")
        self.icons = {
            "file": self.icon("icon-file-upload.png"),
            "text": self.icon("icon-file-text.png"),
            "clean": self.icon("icon-clean.png"),
            "split_paragraph": self.icon("icon-split-paragraph.png"),
            "split_sentence": self.icon("icon-split-sentence.png"),
            "split_custom": self.icon("icon-split-custom.png"),
            "preview": self.icon("icon-preview.png"),
            "export_txt": self.icon("icon-export-txt.png"),
            "export_csv": self.icon("icon-export-csv.png")
        }

        # === File Loader Section ===
        lbl = Label(self, text="File Loader")
        lbl.configure(font=("Arial", 16, "bold"))
        lbl.grid(row=0, column=0, sticky="w")

        self.file_label = Label(self, text="No file selected", anchor="w")
        self.file_label.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        file_btn = Button(self, image=self.icons["file"], text=" Select File", compound="left", command=self.select_file, bootstyle="primary")
        file_btn.grid(row=2, column=0, sticky="ew", pady=(0, 16))

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_file_drop)

        # === Preprocessing Section ===
        lbl = Label(self, text="Preprocessing")
        lbl.configure(font=("Arial", 16, "bold"))
        lbl.grid(row=3, column=0, sticky="w")

        Label(self, text="Split Method:").grid(row=4, column=0, sticky="w")
        self.split_method = tk.StringVar(value="paragraph")
        self.split_dropdown = Combobox(self, textvariable=self.split_method, values=["paragraph", "sentence", "custom"])
        self.split_dropdown.grid(row=5, column=0, sticky="ew", pady=(0, 10))

        self.delimiter_entry = Entry(self)
        self.delimiter_entry.insert(0, "")
        self.delimiter_entry.grid(row=6, column=0, sticky="ew", pady=(0, 16))

        process_btn = Button(self, image=self.icons["clean"], text=" Process Text", compound="left", command=self.process_text, bootstyle="success")
        process_btn.grid(row=7, column=0, sticky="ew", pady=(0, 16))

        # === Preview Section ===
        lbl = Label(self, text="Preview")
        lbl.configure(font=("Arial", 16, "bold"))
        lbl.grid(row=8, column=0, sticky="w")

        preview_btn = Button(self, image=self.icons["preview"], text=" Preview Chunks", compound="left", command=self.preview_chunks, bootstyle="info")
        preview_btn.grid(row=9, column=0, sticky="ew", pady=(0, 16))

        # === Export Section ===
        lbl = Label(self, text="Export Dataset")
        lbl.configure(font=("Arial", 16, "bold"))
        lbl.grid(row=10, column=0, sticky="w")

        export_txt_btn = Button(self, image=self.icons["export_txt"], text=" Export as .txt", compound="left", command=self.export_txt, bootstyle="secondary")
        export_txt_btn.grid(row=11, column=0, sticky="ew", pady=(0, 8))

        export_csv_btn = Button(self, image=self.icons["export_csv"], text=" Export as .csv", compound="left", command=self.export_csv, bootstyle="secondary")
        export_csv_btn.grid(row=12, column=0, sticky="ew")

        self.columnconfigure(0, weight=1)

    def select_file(self):
        path = filedialog.askopenfilename(title="Select Book or Document", filetypes=[("Text or Document Files", "*.txt *.pdf *.epub")])
        if path:
            self.file_path = path
            self.file_label.config(text=os.path.basename(path))
            self.chunks = []
            self.session.add_file(path)

    def handle_file_drop(self, event):
        path = event.data.strip("{}")
        if os.path.isfile(path) and path.lower().endswith((".txt", ".pdf", ".epub")):
            self.file_path = path
            self.file_label.config(text=os.path.basename(path))
            self.chunks = []
            self.session.add_file(path)
        else:
            messagebox.showerror("Invalid File", "Please drop a valid .txt, .pdf, or .epub file.")

    def process_text(self):
        if not self.file_path:
            messagebox.showerror("Missing File", "Please select a file first.")
            return

        method = self.split_method.get()
        delimiter = self.delimiter_entry.get() if method == "custom" else None

        try:
            clean_opts = {"remove_headers": True, "normalize_whitespace": True, "strip_bullets": True}
            self.chunks = process_book(self.file_path, clean_opts, method, delimiter)
            too_long = sum(1 for c in self.chunks if get_token_count(c) > TOKEN_LIMIT)

            # Store chunks in the session
            for f in self.session.files:
                if f.path == self.file_path:
                    f.chunks = self.chunks
                    break

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
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

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