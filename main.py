# main.py
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import tkinter as tk
from ui.app_frame import AppFrame

def main():
    app = ttkb.Window(themename="simplex")
    app.title("Wolfscribe")
    app.geometry("900x600")
    app.minsize(700, 500)

    # Set app icon if available
    try:
        app.iconphoto(False, tk.PhotoImage(file="assets/wolfscribe-icon.png"))
    except:
        pass  # fallback silently if no icon found

    frame = AppFrame(app)
    frame.pack(fill=BOTH, expand=YES)

    app.mainloop()

if __name__ == "__main__":
    main()
