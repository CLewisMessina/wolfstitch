# 📋 CHANGELOG.md

## 🐺 Wolfscribe — Changelog

---

### v1.2 – UI Layout Upgrade (2025-04-30)
This update transforms the interface into a visually structured, icon-enhanced layout using `grid()` for better UX and future scalability.

#### ✨ Added
- 🖼️ PNG-based icons from the Lucide set
- 📐 Grid layout for all interface components
- 🔤 Section headers styled using Arial font with manual font config

#### ✅ Improved
- No more emoji-only buttons — replaced with compound icon + label buttons
- Default window size now starts at `700x500` for a tighter, cleaner launch
- Layout spacing and sectioning aligned to Wolflow’s brand standards

#### 🔧 Internal
- Removed `.qss` loading (not compatible with Tkinter)
- Replaced `class_="section-title"` with manual `font=("Arial", 16, "bold")` styling
- Confirmed compatibility with ttkbootstrap v1.10+

---

### v1.1 – Drag-and-Drop Release (2025-04-30)
**This update adds a major UX upgrade:** drag-and-drop file loading!

#### ✨ Added
- 📥 Drag-and-drop support for `.txt`, `.pdf`, and `.epub` files
- Auto-updates file label when file is dropped
- Full support for Windows; fallback-friendly on macOS/Linux

#### ✅ Improved
- Confirmed compatibility with Wolfkit staging workflow
- Updated `README.md` and `requirements.txt` to reflect changes

#### 🔧 Internal
- Replaced `ttkb.Window` with `TkinterDnD.Tk` in `main.py`
- Registered `DND_FILES` on `AppFrame` and bound `<<Drop>>` event
- Added `tkinterdnd2` as a new dependency

---

### v1.0 – Initial Launch (2025-04-XX)
The first working version of Wolfscribe — a local app that converts long-form books into clean, token-counted `.txt` or `.csv` datasets.

#### 🚀 Core Features
- Import `.epub`, `.pdf`, and `.txt` files
- Clean and chunk text by paragraph, sentence, or custom delimiter
- View preview chunks with token count warnings
- Export as `.txt` or `.csv`
- Fully local: no tracking, no cloud

---

_You write the story. Wolfscribe makes it trainable._
