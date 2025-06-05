# ui/styles.py - Modern Slate Theme Enhancement
from ttkbootstrap import Style
import tkinter as tk

# Modern Slate Color Palette
MODERN_SLATE = {
    'bg_primary': '#0f172a',      # slate-900 (main background)
    'bg_secondary': '#1e293b',    # slate-800 (panels)
    'bg_cards': '#334155',        # slate-700 (cards/sections)
    'bg_hover': '#475569',        # slate-600 (hover states)
    'text_primary': '#f1f5f9',    # slate-100 (main text)
    'text_secondary': '#94a3b8',  # slate-400 (secondary text)
    'text_muted': '#64748b',      # slate-500 (muted text)
    'accent_blue': '#3b82f6',     # blue-500 (primary actions)
    'accent_cyan': '#06b6d4',     # cyan-500 (highlights)
    'success': '#22c55e',         # green-500 (success states)
    'cost_savings': '#10b981',    # emerald-500 (cost savings)
    'warning': '#f59e0b',         # amber-500 (warnings)
    'premium': '#8b5cf6',         # violet-500 (premium features)
    'border': '#475569',          # slate-600 (borders)
    'border_light': '#64748b',    # slate-500 (light borders)
}

def apply_modern_slate_theme(style: Style):
    """Apply comprehensive modern slate theme with professional styling"""
    
    # ==================== CORE FRAME STYLES ====================
    
    # Main application background
    style.configure("Modern.TFrame",
        background=MODERN_SLATE['bg_primary'],
        borderwidth=0,
        relief="flat"
    )
    
    # Secondary panels (sections)
    style.configure("Panel.TFrame",
        background=MODERN_SLATE['bg_secondary'],
        borderwidth=1,
        relief="solid",
        bordercolor=MODERN_SLATE['border']
    )
    
    # Card-style sections with subtle elevation
    style.configure("Card.TFrame",
        background=MODERN_SLATE['bg_cards'],
        borderwidth=1,
        relief="solid",
        bordercolor=MODERN_SLATE['border'],
        padding=(15, 12)
    )
    
    # Premium feature cards
    style.configure("Premium.TFrame",
        background=MODERN_SLATE['bg_cards'],
        borderwidth=2,
        relief="solid",
        bordercolor=MODERN_SLATE['premium'],
        padding=(15, 12)
    )
    
    # ==================== TEXT STYLES ====================
    
    # Primary text (headings) - Use card background for section headers
    style.configure("Heading.TLabel",
        background=MODERN_SLATE['bg_cards'],
        foreground=MODERN_SLATE['text_primary'],
        font=("Segoe UI", 16, "bold")
    )
    
    # Secondary text (descriptions) - Larger font and card background
    style.configure("Secondary.TLabel",
        background=MODERN_SLATE['bg_cards'],
        foreground=MODERN_SLATE['text_secondary'],
        font=("Segoe UI", 11)  # Increased from 10 to 11
    )
    
    # Field labels (like "Tokenizer:", "Split Method:") - Better visibility
    style.configure("FieldLabel.TLabel",
        background=MODERN_SLATE['bg_cards'],
        foreground=MODERN_SLATE['text_primary'],
        font=("Segoe UI", 12, "bold")  # Larger and bold for better readability
    )
    
    # Success text (positive indicators)
    style.configure("Success.TLabel",
        background=MODERN_SLATE['bg_primary'],
        foreground=MODERN_SLATE['success'],
        font=("Segoe UI", 10, "bold")
    )
    
    # Warning text
    style.configure("Warning.TLabel",
        background=MODERN_SLATE['bg_primary'],
        foreground=MODERN_SLATE['warning'],
        font=("Segoe UI", 10, "bold")
    )
    
    # Premium feature text
    style.configure("Premium.TLabel",
        background=MODERN_SLATE['bg_primary'],
        foreground=MODERN_SLATE['premium'],
        font=("Segoe UI", 10, "bold")
    )
    
    # Cost savings text
    style.configure("CostSavings.TLabel",
        background=MODERN_SLATE['bg_primary'],
        foreground=MODERN_SLATE['cost_savings'],
        font=("Segoe UI", 11, "bold")
    )
    
    # ==================== ENHANCED BUTTON STYLES ====================
    
    # Primary action buttons (Process, Analyze, etc.)
    style.configure("Primary.TButton",
        background=MODERN_SLATE['accent_blue'],
        foreground="white",
        borderwidth=0,
        focuscolor="none",
        padding=(16, 12),
        font=("Segoe UI", 10, "bold")
    )
    
    style.map("Primary.TButton",
        background=[
            ("active", "#2563eb"),      # blue-600 on hover
            ("pressed", "#1d4ed8"),     # blue-700 on press
            ("disabled", MODERN_SLATE['text_muted'])
        ],
        foreground=[
            ("disabled", MODERN_SLATE['text_secondary'])
        ]
    )
    
    # Secondary action buttons
    style.configure("Secondary.TButton",
        background=MODERN_SLATE['bg_cards'],
        foreground=MODERN_SLATE['text_primary'],
        borderwidth=1,
        bordercolor=MODERN_SLATE['border'],
        focuscolor="none",
        padding=(14, 10),
        font=("Segoe UI", 10)
    )
    
    style.map("Secondary.TButton",
        background=[
            ("active", MODERN_SLATE['bg_hover']),
            ("pressed", MODERN_SLATE['border'])
        ],
        bordercolor=[
            ("active", MODERN_SLATE['accent_cyan']),
            ("focus", MODERN_SLATE['accent_cyan'])
        ]
    )
    
    # Success buttons (Export, Save, etc.)
    style.configure("Success.TButton",
        background=MODERN_SLATE['success'],
        foreground="white",
        borderwidth=0,
        focuscolor="none",
        padding=(14, 10),
        font=("Segoe UI", 10, "bold")
    )
    
    style.map("Success.TButton",
        background=[
            ("active", "#16a34a"),      # green-600 on hover
            ("pressed", "#15803d")      # green-700 on press
        ]
    )
    
    # Premium feature buttons
    style.configure("Premium.TButton",
        background=MODERN_SLATE['premium'],
        foreground="white",
        borderwidth=0,
        focuscolor="none",
        padding=(16, 12),
        font=("Segoe UI", 10, "bold")
    )
    
    style.map("Premium.TButton",
        background=[
            ("active", "#7c3aed"),      # violet-600 on hover
            ("pressed", "#6d28d9")      # violet-700 on press
        ]
    )
    
    # Cost Analysis button (special highlight)
    style.configure("CostAnalysis.TButton",
        background=MODERN_SLATE['cost_savings'],
        foreground="white",
        borderwidth=0,
        focuscolor="none",
        padding=(16, 12),
        font=("Segoe UI", 10, "bold")
    )
    
    style.map("CostAnalysis.TButton",
        background=[
            ("active", "#059669"),      # emerald-600 on hover
            ("pressed", "#047857")      # emerald-700 on press
        ]
    )
    
    # Warning/Alert buttons
    style.configure("Warning.TButton",
        background=MODERN_SLATE['warning'],
        foreground="white",
        borderwidth=0,
        focuscolor="none",
        padding=(14, 10),
        font=("Segoe UI", 10, "bold")
    )
    
    style.map("Warning.TButton",
        background=[
            ("active", "#d97706"),      # amber-600 on hover
            ("pressed", "#b45309")      # amber-700 on press
        ]
    )
    
    # ==================== INPUT STYLES ====================
    
    # Entry fields
    style.configure("Modern.TEntry",
        fieldbackground=MODERN_SLATE['bg_cards'],
        background=MODERN_SLATE['bg_cards'],
        foreground=MODERN_SLATE['text_primary'],
        borderwidth=1,
        bordercolor=MODERN_SLATE['border'],
        insertcolor=MODERN_SLATE['accent_cyan'],
        padding=(12, 8),
        font=("Segoe UI", 10)
    )
    
    style.map("Modern.TEntry",
        bordercolor=[
            ("focus", MODERN_SLATE['accent_cyan']),
            ("active", MODERN_SLATE['accent_blue'])
        ],
        fieldbackground=[
            ("focus", MODERN_SLATE['bg_hover'])
        ]
    )
    
    # Combobox (dropdowns)
    style.configure("Modern.TCombobox",
        fieldbackground=MODERN_SLATE['bg_cards'],
        background=MODERN_SLATE['bg_cards'],
        foreground=MODERN_SLATE['text_primary'],
        borderwidth=1,
        bordercolor=MODERN_SLATE['border'],
        arrowcolor=MODERN_SLATE['accent_cyan'],
        padding=(12, 8),
        font=("Segoe UI", 10)
    )
    
    style.map("Modern.TCombobox",
        bordercolor=[
            ("focus", MODERN_SLATE['accent_cyan']),
            ("active", MODERN_SLATE['accent_blue'])
        ],
        fieldbackground=[
            ("focus", MODERN_SLATE['bg_hover'])
        ]
    )
    
    # ==================== SCROLLBAR STYLES ====================
    
    style.configure("Modern.Vertical.TScrollbar",
        background=MODERN_SLATE['bg_secondary'],
        troughcolor=MODERN_SLATE['bg_primary'],
        borderwidth=0,
        arrowcolor=MODERN_SLATE['text_secondary'],
        darkcolor=MODERN_SLATE['bg_cards'],
        lightcolor=MODERN_SLATE['bg_cards']
    )
    
    # ==================== SPECIAL EFFECT STYLES ====================
    
    # Gradient-like effect for premium sections
    style.configure("PremiumGradient.TFrame",
        background=MODERN_SLATE['bg_cards'],
        borderwidth=2,
        relief="solid",
        bordercolor=MODERN_SLATE['premium']
    )
    
    # Cost savings highlight
    style.configure("CostSavingsHighlight.TFrame",
        background=MODERN_SLATE['cost_savings'],
        borderwidth=0,
        padding=(8, 4)
    )

def apply_hover_style(style: Style):
    """Enhanced hover effects for modern slate theme"""
    
    # Legacy support - update existing hover style to match new theme
    style.configure("Hover.TButton",
        background=MODERN_SLATE['bg_cards'],
        foreground=MODERN_SLATE['text_primary'],
        borderwidth=1,
        bordercolor=MODERN_SLATE['border'],
        focuscolor="none",
        padding=(14, 10),
        font=("Segoe UI", 10)
    )
    
    style.map("Hover.TButton",
        background=[
            ("active", MODERN_SLATE['accent_blue']),
            ("pressed", "#2563eb")
        ],
        foreground=[
            ("active", "white"),
            ("pressed", "white")
        ],
        bordercolor=[
            ("active", MODERN_SLATE['accent_blue']),
            ("focus", MODERN_SLATE['accent_cyan'])
        ]
    )

def get_modern_colors():
    """Utility function to get color palette for other components"""
    return MODERN_SLATE

def create_gradient_effect(widget, start_color, end_color):
    """Create a subtle gradient effect (simplified version)"""
    # This is a placeholder for future gradient implementation
    # For now, we'll use solid colors with good visual hierarchy
    pass