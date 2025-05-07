# 📋 CHANGELOG.md

## 🐺 Wolfscribe — Changelog

---

### v1.3 – Multi-Document Foundation + Style Redesign (2025-05-07)
This version adds full session management, visual polish, and prepares for bundling multi-file datasets.

#### ✨ Added
- 💾 **Session Save/Load**: Save your progress to `.wsession` and restore it later
- 🧱 **Session Object**: Internal object tracks multiple files and their chunks
- 📂 **Multi-file support groundwork** (session structure, file queue)
- 🧑‍🎨 **Custom button styles** with hover support (`Hover.TButton`)
- 🔴 **Red-on-hover** buttons to match Wolfkit aesthetic

#### ✅ Improved
- ➕ Delimiter entry now appears **only when "custom"** is selected
- 🔽 Dropdown is now **readonly** (no free typing)
- 🖱️ **Mouse wheel support** for vertical scrolling
- 🔲 Interface layout now **scrolls vertically** and centers content

#### 🔧 Internal
- Refactored style logic into `ui/styles.py` (imported via `main.py`)
- Removed `bootstyle=...` in favor of `style="Hover.TButton"` throughout
- Code modularized for better future maintainability

---