# ui/app_frame.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Toplevel, PhotoImage
from ttkbootstrap import Frame, Label, Button, Entry, Combobox
from ttkbootstrap.constants import *
from controller import process_book, get_token_count
from export.dataset_exporter import save_as_txt, save_as_csv
from tkinterdnd2 import DND_FILES
import json
from session import Session

TOKEN_LIMIT = 512

class AppFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = Frame(self.canvas, padding=(20, 10))

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=650)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Enable mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        self.file_path = None
        self.chunks = []
        self.session = Session()

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
            "export_csv": self.icon("icon-export-csv.png"),
            "save": self.icon("icon-save.png"),
            "file_up": self.icon("icon-file-up.png")
        }

        content = self.scrollable_frame

        # === File Loader Section ===
        Label(content, text="File Loader", font=("Arial", 16, "bold")).grid(row=0, column=0, sticky="w", padx=10)

        self.file_label = Label(content, text="No file selected", anchor="w")
        self.file_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))

        Button(content, image=self.icons["file"], text=" Select File", compound="left",
               command=self.select_file, style="Hover.TButton").grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 16))

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_file_drop)

        # === Preprocessing Section ===
        Label(content, text="Preprocessing", font=("Arial", 16, "bold")).grid(row=3, column=0, sticky="w", padx=10)

        Label(content, text="Split Method:").grid(row=4, column=0, sticky="w", padx=10)
        self.split_method = tk.StringVar(value="paragraph")
        self.split_dropdown = Combobox(content, textvariable=self.split_method,
                                       values=["paragraph", "sentence", "custom"], state="readonly")
        self.split_dropdown.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.split_dropdown.bind("<<ComboboxSelected>>", self.on_split_method_change)

        self.delimiter_entry = Entry(content)
        self.delimiter_entry.insert(0, "")
        self.delimiter_entry.grid(row=6, column=0, sticky="ew", padx=10, pady=(0, 16))
        self.delimiter_entry.grid_remove()

        Button(content, image=self.icons["clean"], text=" Process Text", compound="left",
               command=self.process_text, style="Hover.TButton").grid(row=7, column=0, sticky="ew", padx=10, pady=(0, 16))

        # === Preview Section ===
        Label(content, text="Preview", font=("Arial", 16, "bold")).grid(row=8, column=0, sticky="w", padx=10)

        Button(content, image=self.icons["preview"], text=" Preview Chunks", compound="left",
               command=self.preview_chunks, style="Hover.TButton").grid(row=9, column=0, sticky="ew", padx=10, pady=(0, 16))

        # === Export Section ===
        Label(content, text="Export Dataset", font=("Arial", 16, "bold")).grid(row=10, column=0, sticky="w", padx=10)

        Button(content, image=self.icons["export_txt"], text=" Export as .txt", compound="left",
               command=self.export_txt, style="Hover.TButton").grid(row=11, column=0, sticky="ew", padx=10, pady=(0, 8))

        Button(content, image=self.icons["export_csv"], text=" Export as .csv", compound="left",
               command=self.export_csv, style="Hover.TButton").grid(row=12, column=0, sticky="ew", padx=10)

        # === Session Section ===
        Label(content, text="Session Management", font=("Arial", 16, "bold")).grid(row=13, column=0, sticky="w", padx=10, pady=(16, 0))

        Button(content, image=self.icons["save"], text=" Save Session", compound="left",
               command=self.save_session, style="Hover.TButton").grid(row=14, column=0, sticky="ew", padx=10, pady=(0, 8))

        Button(content, image=self.icons["file_up"], text=" Load Session", compound="left",
               command=self.load_session, style="Hover.TButton").grid(row=15, column=0, sticky="ew", padx=10, pady=(0, 8))

        content.columnconfigure(0, weight=1)

    def select_file(self):
        path = filedialog.askopenfilename(title="Select Book or Document",
                                          filetypes=[("Text or Document Files", "*.txt *.pdf *.epub")])
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


    def on_split_method_change(self, event=None):
        selected = self.split_method.get()
        if selected == "custom":
            self.delimiter_entry.grid()
        else:
            self.delimiter_entry.grid_remove()

    def save_session(self):
        path = filedialog.asksaveasfilename(defaultextension=".wsession", filetypes=[("Wolfscribe Session", "*.wsession")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.session.to_dict(), f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Session Saved", f"Session saved to {path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def load_session(self):
        path = filedialog.askopenfilename(filetypes=[("Wolfscribe Session", "*.wsession")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.session = Session.from_dict(data)
            if self.session.files:
                first_file = self.session.files[0]
                self.file_path = first_file.path
                self.file_label.config(text=os.path.basename(self.file_path))
                self.chunks = first_file.chunks
            messagebox.showinfo("Session Loaded", f"Loaded session from {path}")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))