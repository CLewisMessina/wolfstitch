# ui/section_builders.py 
"""
UI Section Builders for Wolfscribe Premium
Extracted from app_frame.py to reduce complexity and improve maintainability
"""

import tkinter as tk
from ttkbootstrap import Frame, Label, Button, Entry, Combobox
from ttkbootstrap.tooltip import ToolTip
from ui.styles import MODERN_SLATE

class SectionBuilder:
    """Builder class for creating UI sections with consistent styling"""
    
    def __init__(self, parent, controller, icons):
        self.parent = parent
        self.controller = controller
        self.icons = icons
        # We'll need reference to the main app for some callbacks
        self.app = None  # Will be set by AppFrame
    
    def set_app_reference(self, app):
        """Set reference to main AppFrame for callbacks"""
        self.app = app
    
    def build_file_section(self):
        """Build file loader section"""
        file_section = Frame(self.parent, style="Card.TFrame")
        
        # File Loader Header with icon
        header_frame = Frame(file_section, style="Modern.TFrame")
        header_frame.pack(fill="x", pady=(0, 8))

        Label(header_frame, image=self.icons["file_header"], compound="left", 
              background=MODERN_SLATE['bg_cards']).pack(side="left")
        Label(header_frame, text=" File Loader", style="Heading.TLabel", 
              background=MODERN_SLATE['bg_cards']).pack(side="left")
        
        # File status label (will be updated by app)
        file_label = Label(file_section, text="No file selected", 
                          style="Secondary.TLabel", anchor="w")
        file_label.pack(fill="x", pady=(0, 12))
        
        # Store reference for app to update
        if self.app:
            self.app.file_label = file_label
        
        # Select file button
        Button(file_section, image=self.icons["file"], text="  Select File", 
               compound="left", command=self._get_select_file_callback(), 
               style="Secondary.TButton").pack(fill="x")
        
        return file_section
    
    def build_preprocessing_section(self):
        """Build preprocessing section with tokenizer and split options"""
        preprocess_section = Frame(self.parent, style="Card.TFrame")
        
        # Preprocessing Header with icon
        header_frame = Frame(preprocess_section, style="Modern.TFrame")
        header_frame.pack(fill="x", pady=(0, 12))

        Label(header_frame, image=self.icons["preprocessing_header"], compound="left", 
              background=MODERN_SLATE['bg_cards']).pack(side="left")
        Label(header_frame, text=" Preprocessing", style="Heading.TLabel", 
              background=MODERN_SLATE['bg_cards']).pack(side="left")

        # Split Method
        Label(preprocess_section, text="Split Method:", 
              style="FieldLabel.TLabel").pack(anchor="w", pady=(0, 6))
        
        # Create split method variable and dropdown (app will need to reference these)
        split_method = tk.StringVar(value="paragraph")
        split_dropdown = Combobox(preprocess_section, 
                                 textvariable=split_method,
                                 values=["paragraph", "sentence", "custom"], 
                                 state="readonly",
                                 style="Modern.TCombobox")
        split_dropdown.pack(fill="x", pady=(0, 12))
        split_dropdown.bind("<<ComboboxSelected>>", self._get_split_method_callback())

        # Store references for app
        if self.app:
            self.app.split_method = split_method
            self.app.split_dropdown = split_dropdown

        # Custom delimiter (hidden by default)
        delimiter_entry = Entry(preprocess_section, style="Modern.TEntry")
        delimiter_entry.insert(0, "")
        
        # Store reference for app
        if self.app:
            self.app.delimiter_entry = delimiter_entry
        
        # Tokenizer Selection
        Label(preprocess_section, text="Tokenizer:", 
              style="FieldLabel.TLabel").pack(anchor="w", pady=(8, 6))
        
        # Create tokenizer variable and dropdown (app will need to reference these)
        selected_tokenizer = tk.StringVar(value="gpt2")
        tokenizer_dropdown = Combobox(preprocess_section, 
                                     textvariable=selected_tokenizer, 
                                     state="readonly",
                                     style="Modern.TCombobox")
        tokenizer_dropdown.pack(fill="x", pady=(0, 12))
        tokenizer_dropdown.bind("<<ComboboxSelected>>", self._get_tokenizer_callback())
        
        # Store references for app
        if self.app:
            self.app.selected_tokenizer = selected_tokenizer
            self.app.tokenizer_dropdown = tokenizer_dropdown
        
        # Enhanced tooltip with modern styling
        ToolTip(tokenizer_dropdown,
                text="Choose tokenizer for accurate token counting:\n"
                     "• GPT-2: Basic estimation (Free)\n"
                     "• GPT-4/3.5: Exact OpenAI tokenization (Premium)\n"
                     "• BERT: For encoder models (Premium)\n"
                     "• Claude: Anthropic estimation (Premium)",
                delay=500)

        # License status with modern styling
        license_status_label = Label(preprocess_section, text="", 
                                   style="Secondary.TLabel", anchor="w")
        license_status_label.pack(fill="x", pady=(0, 16))
        
        # Store reference for app
        if self.app:
            self.app.license_status_label = license_status_label

        # Process button with enhanced styling
        Button(preprocess_section, image=self.icons["clean"], 
               text="  Process Text", compound="left",
               command=self._get_process_callback(), 
               style="Primary.TButton").pack(fill="x", pady=(0, 8))

        # Cost Analysis Button with comprehensive tooltip
        cost_button = Button(preprocess_section, 
                            image=self.icons["cost_analysis"],
                            text="  Analyze Training Costs", 
                            compound="left",
                            command=self._get_cost_analysis_callback(), 
                            style="CostAnalysis.TButton")
        cost_button.pack(fill="x")
        
        # Enhanced comprehensive tooltip
        cost_analysis_tooltip = """💰 Comprehensive Training Cost Analysis

Analyzes 15+ training approaches:
• Local Training: RTX 3090/4090, A100, H100
• Cloud Providers: Lambda Labs, Vast.ai, RunPod  
• Optimization: LoRA, QLoRA, Full Fine-tuning
• API Services: OpenAI, Anthropic fine-tuning

Features:
✓ Real-time cloud pricing
✓ ROI analysis with break-even calculations
✓ Cost optimization recommendations
✓ Professional export reports
✓ Hardware requirement analysis

Premium Feature - Requires active license or trial"""
        
        ToolTip(cost_button, text=cost_analysis_tooltip, delay=500)
        
        return preprocess_section
    
    def build_preview_section(self):
        """Build preview section"""
        preview_section = Frame(self.parent, style="Card.TFrame")
        
        # Preview Header with icon
        header_frame = Frame(preview_section, style="Modern.TFrame")
        header_frame.pack(fill="x", pady=(0, 12))

        Label(header_frame, image=self.icons["preview_header"], compound="left", 
              background=MODERN_SLATE['bg_cards']).pack(side="left")
        Label(header_frame, text=" Preview", style="Heading.TLabel", 
              background=MODERN_SLATE['bg_cards']).pack(side="left")
        
        Button(preview_section, image=self.icons["preview"], 
               text="  Preview Chunks", compound="left",
               command=self._get_preview_callback(), 
               style="Secondary.TButton").pack(fill="x")
        
        return preview_section
    
    def build_export_section(self):
        """Build export section"""
        export_section = Frame(self.parent, style="Card.TFrame")
        
        # Export Header with icon
        header_frame = Frame(export_section, style="Modern.TFrame")
        header_frame.pack(fill="x", pady=(0, 12))

        Label(header_frame, image=self.icons["export_header"], compound="left", 
              background=MODERN_SLATE['bg_cards']).pack(side="left")
        Label(header_frame, text=" Export Dataset", style="Heading.TLabel", 
              background=MODERN_SLATE['bg_cards']).pack(side="left")
        
        Button(export_section, image=self.icons["export_txt"], 
               text="  Export as .txt", compound="left",
               command=self._get_export_txt_callback(), 
               style="Success.TButton").pack(fill="x", pady=(0, 8))
        
        Button(export_section, image=self.icons["export_csv"], 
               text="  Export as .csv", compound="left",
               command=self._get_export_csv_callback(), 
               style="Success.TButton").pack(fill="x")
        
        return export_section
    
    def build_session_section(self):
        """Build session management section"""
        session_section = Frame(self.parent, style="Card.TFrame")
        
        # Session Header with icon
        header_frame = Frame(session_section, style="Modern.TFrame")
        header_frame.pack(fill="x", pady=(0, 12))

        Label(header_frame, image=self.icons["session_header"], compound="left", 
              background=MODERN_SLATE['bg_cards']).pack(side="left")
        Label(header_frame, text=" Session Management", style="Heading.TLabel", 
              background=MODERN_SLATE['bg_cards']).pack(side="left")
        
        Button(session_section, image=self.icons["save"], 
               text="  Save Session", compound="left",
               command=self._get_save_session_callback(), 
               style="Secondary.TButton").pack(fill="x", pady=(0, 8))
        
        Button(session_section, image=self.icons["file_up"], 
               text="  Load Session", compound="left",
               command=self._get_load_session_callback(), 
               style="Secondary.TButton").pack(fill="x")
        
        return session_section
    
    def build_premium_section(self):
        """Build premium features section"""
        premium_section = Frame(self.parent, style="Premium.TFrame")
        
        # Store reference for app to update
        if self.app:
            self.app.premium_section = premium_section
        
        return premium_section
    
    # Callback method generators - these return the actual callback functions
    def _get_select_file_callback(self):
        """Get select file callback"""
        return lambda: self.app.select_file() if self.app else None
    
    def _get_split_method_callback(self):
        """Get split method change callback"""
        return lambda event=None: self.app.on_split_method_change(event) if self.app else None
    
    def _get_tokenizer_callback(self):
        """Get tokenizer change callback"""
        return lambda event=None: self.app.on_tokenizer_change(event) if self.app else None
    
    def _get_process_callback(self):
        """Get process text callback"""
        return lambda: self.app.process_text() if self.app else None
    
    def _get_cost_analysis_callback(self):
        """Get cost analysis callback"""
        return lambda: self.app.show_cost_analysis() if self.app else None
    
    def _get_preview_callback(self):
        """Get preview callback"""
        return lambda: self.app.preview_chunks() if self.app else None
    
    def _get_export_txt_callback(self):
        """Get export TXT callback"""
        return lambda: self.app.export_txt() if self.app else None
    
    def _get_export_csv_callback(self):
        """Get export CSV callback"""
        return lambda: self.app.export_csv() if self.app else None
    
    def _get_save_session_callback(self):
        """Get save session callback"""
        return lambda: self.app.save_session() if self.app else None
    
    def _get_load_session_callback(self):
        """Get load session callback"""
        return lambda: self.app.load_session() if self.app else None