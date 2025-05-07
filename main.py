# main.py
from tkinterdnd2 import TkinterDnD  # New import
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import tkinter as tk
from ui.app_frame import AppFrame

def main():
    # Use TkinterDnD-capable root window
    root = TkinterDnD.Tk()
    style = ttkb.Style(theme="simplex")
    from ui.styles import apply_hover_style
    apply_hover_style(style)
    style.master = root  # Link ttkbootstrap theme to the root window

    root.title("Wolfscribe")
    root.geometry("700x500")
    root.minsize(700, 500)


    # Set app icon if available
    try:
        root.iconphoto(False, tk.PhotoImage(file="assets/wolfscribe-icon.png"))
    except:
        pass  # fallback silently if no icon found

    frame = AppFrame(root)
    frame.pack(fill=BOTH, expand=YES)

    root.mainloop()

if __name__ == "__main__":
    main()