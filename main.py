# main.py - Enhanced with Modern Slate Theme
from tkinterdnd2 import TkinterDnD
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import tkinter as tk
from ui.app_frame import AppFrame

def main():
    # Use TkinterDnD-capable root window
    root = TkinterDnD.Tk()
    
    # Apply modern dark theme as base (darkly is a good dark theme in ttkbootstrap)
    style = ttkb.Style(theme="darkly")  # Using darkly as base for dark theme
    
    # Apply our custom modern slate styling
    from ui.styles import apply_modern_slate_theme, apply_hover_style, MODERN_SLATE
    apply_modern_slate_theme(style)
    apply_hover_style(style)
    
    # Link style to root window
    style.master = root

    # Configure main window with modern styling
    root.title("Wolfscribe Premium - AI Training Cost Optimizer")
    root.geometry("750x600")  # Slightly larger for better visual breathing room
    root.minsize(750, 600)
    
    # Set modern dark background
    root.configure(bg=MODERN_SLATE['bg_primary'])

    # Set app icon if available
    try:
        root.iconphoto(False, tk.PhotoImage(file="assets/wolfscribe-icon.png"))
    except:
        pass  # Fallback silently if no icon found

    # Create main application frame
    frame = AppFrame(root)
    frame.pack(fill=BOTH, expand=YES)

    # Set window-level dark theme properties
    root.option_add('*TCombobox*Listbox.selectBackground', MODERN_SLATE['accent_blue'])
    root.option_add('*TCombobox*Listbox.background', MODERN_SLATE['bg_cards'])
    root.option_add('*TCombobox*Listbox.foreground', MODERN_SLATE['text_primary'])

    root.mainloop()

if __name__ == "__main__":
    main()