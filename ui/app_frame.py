# ui/app_frame.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Toplevel, PhotoImage
from ttkbootstrap import Frame, Label, Button, Entry, Combobox
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from controller import ProcessingController
from export.dataset_exporter import save_as_txt, save_as_csv
from tkinterdnd2 import DND_FILES
import json
from session import Session
from datetime import datetime

TOKEN_LIMIT = 512

class AppFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Initialize the enhanced controller
        self.controller = ProcessingController()
        
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
        self.current_analysis = None  # Store chunk analysis results

        # Tokenizer selection state
        self.selected_tokenizer = tk.StringVar(value="gpt2")  # Default to free tokenizer
        self.tokenizer_options = []
        
        self.icon = lambda name: PhotoImage(file=f"assets/icons/{name}")
        try:
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
        except:
            # Fallback if icons not available
            self.icons = {key: None for key in ["file", "text", "clean", "split_paragraph", 
                                               "split_sentence", "split_custom", "preview", 
                                               "export_txt", "export_csv", "save", "file_up"]}

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
        self.delimiter_entry.grid(row=6, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.delimiter_entry.grid_remove()

        # === NEW: Tokenizer Selection ===
        Label(content, text="Tokenizer:").grid(row=7, column=0, sticky="w", padx=10)
        
        self.tokenizer_dropdown = Combobox(content, textvariable=self.selected_tokenizer, state="readonly")
        self.tokenizer_dropdown.grid(row=8, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.tokenizer_dropdown.bind("<<ComboboxSelected>>", self.on_tokenizer_change)
        
        # Initialize tokenizer dropdown
        self.update_tokenizer_dropdown()
        
        # Add tooltip for tokenizer explanation
        tokenizer_tooltip = ToolTip(
            self.tokenizer_dropdown,
            text="Choose tokenizer for accurate token counting:\n"
                 "• GPT-2: Basic estimation (Free)\n"
                 "• GPT-4/3.5: Exact OpenAI tokenization (Premium)\n"
                 "• BERT: For encoder models (Premium)\n"
                 "• Claude: Anthropic estimation (Premium)",
            delay=500
        )

        # License status indicator
        self.license_status_label = Label(content, text="", font=("Arial", 10), anchor="w")
        self.license_status_label.grid(row=9, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.update_license_status()

        Button(content, image=self.icons["clean"], text=" Process Text", compound="left",
               command=self.process_text, style="Hover.TButton").grid(row=10, column=0, sticky="ew", padx=10, pady=(0, 16))

        # === Preview Section ===
        Label(content, text="Preview", font=("Arial", 16, "bold")).grid(row=11, column=0, sticky="w", padx=10)

        Button(content, image=self.icons["preview"], text=" Preview Chunks", compound="left",
               command=self.preview_chunks, style="Hover.TButton").grid(row=12, column=0, sticky="ew", padx=10, pady=(0, 16))

        # === Export Section ===
        Label(content, text="Export Dataset", font=("Arial", 16, "bold")).grid(row=13, column=0, sticky="w", padx=10)

        Button(content, image=self.icons["export_txt"], text=" Export as .txt", compound="left",
               command=self.export_txt, style="Hover.TButton").grid(row=14, column=0, sticky="ew", padx=10, pady=(0, 8))

        Button(content, image=self.icons["export_csv"], text=" Export as .csv", compound="left",
               command=self.export_csv, style="Hover.TButton").grid(row=15, column=0, sticky="ew", padx=10)

        # === Session Section ===
        Label(content, text="Session Management", font=("Arial", 16, "bold")).grid(row=16, column=0, sticky="w", padx=10, pady=(16, 0))

        Button(content, image=self.icons["save"], text=" Save Session", compound="left",
               command=self.save_session, style="Hover.TButton").grid(row=17, column=0, sticky="ew", padx=10, pady=(0, 8))

        Button(content, image=self.icons["file_up"], text=" Load Session", compound="left",
               command=self.load_session, style="Hover.TButton").grid(row=18, column=0, sticky="ew", padx=10, pady=(0, 8))

        # === Premium Section (if applicable) ===
        self.premium_section = Frame(content)
        self.premium_section.grid(row=19, column=0, sticky="ew", padx=10, pady=(16, 0))
        self.update_premium_section()

        content.columnconfigure(0, weight=1)

    def update_tokenizer_dropdown(self):
        """Update tokenizer dropdown with available options"""
        try:
            tokenizers = self.controller.get_available_tokenizers()
            self.tokenizer_options = []
            display_names = []
            
            for tokenizer in tokenizers:
                self.tokenizer_options.append(tokenizer)
                
                if tokenizer['has_access']:
                    # User has access - show normally
                    display_names.append(tokenizer['display_name'])
                else:
                    # User doesn't have access - show with lock
                    if not tokenizer['display_name'].startswith('🔒'):
                        display_names.append(f"🔒 {tokenizer['display_name']}")
                    else:
                        display_names.append(tokenizer['display_name'])
            
            self.tokenizer_dropdown['values'] = display_names
            
            # Set default to first available tokenizer
            available_tokenizers = [t for t in tokenizers if t['has_access'] and t['available']]
            if available_tokenizers:
                default_name = available_tokenizers[0]['display_name']
                self.selected_tokenizer.set(default_name)
                # Store the actual tokenizer name for processing
                self._current_tokenizer_name = available_tokenizers[0]['name']
            else:
                self.selected_tokenizer.set("GPT-2 (Free)")
                self._current_tokenizer_name = 'gpt2'
                
        except Exception as e:
            messagebox.showerror("Tokenizer Error", f"Failed to load tokenizers: {str(e)}")
            # Fallback
            self.tokenizer_dropdown['values'] = ["GPT-2 (Free)"]
            self.selected_tokenizer.set("GPT-2 (Free)")
            self._current_tokenizer_name = 'gpt2'

    def update_license_status(self):
        """Update license status display"""
        try:
            license_info = self.controller.get_licensing_info()
            status = license_info['license_status']
            
            if status['status'] == 'demo':
                self.license_status_label.config(text="🧑‍💻 Demo Mode - All Premium Features Enabled", foreground="blue")
            elif status['status'] == 'trial':
                days = status.get('days_remaining', 0)
                self.license_status_label.config(text=f"⏱️ Trial: {days} days remaining", foreground="orange")
            elif status['status'] == 'active':
                self.license_status_label.config(text="✅ Premium License Active", foreground="green")
            elif status['status'] == 'expired':
                self.license_status_label.config(text="❌ License Expired", foreground="red")
            else:
                self.license_status_label.config(text="ℹ️ Free Tier - Upgrade for Premium Features", foreground="gray")
                
        except Exception as e:
            self.license_status_label.config(text="⚠️ License Status Unknown", foreground="gray")

    def update_premium_section(self):
        """Update premium section based on license status"""
        try:
            license_info = self.controller.get_licensing_info()
            
            # Clear existing premium section
            for widget in self.premium_section.winfo_children():
                widget.destroy()
            
            if not license_info['premium_licensed']:
                # Show upgrade options
                Label(self.premium_section, text="Premium Features", font=("Arial", 16, "bold")).pack(anchor="w")
                
                upgrade_button = Button(self.premium_section, text="🚀 Start Free Trial", 
                                      command=self.start_trial, style="Hover.TButton")
                upgrade_button.pack(fill="x", pady=(5, 0))
                
                upgrade_info_button = Button(self.premium_section, text="💎 View Premium Features", 
                                           command=self.show_upgrade_info, style="Hover.TButton")
                upgrade_info_button.pack(fill="x", pady=(5, 0))
            else:
                # Show premium status
                status = license_info['license_status']
                if status['status'] == 'trial' and status.get('days_remaining'):
                    Label(self.premium_section, text="Premium Features", font=("Arial", 16, "bold")).pack(anchor="w")
                    Label(self.premium_section, text=f"Trial expires in {status['days_remaining']} days", 
                          foreground="orange").pack(anchor="w")
                    
                    upgrade_button = Button(self.premium_section, text="💎 Upgrade to Full License", 
                                          command=self.show_upgrade_info, style="Hover.TButton")
                    upgrade_button.pack(fill="x", pady=(5, 0))
                    
        except Exception as e:
            pass  # Silently fail for premium section

    def on_tokenizer_change(self, event=None):
        """Handle tokenizer selection change"""
        selected_display = self.selected_tokenizer.get()
        
        # Find the actual tokenizer info
        selected_tokenizer = None
        for tokenizer in self.tokenizer_options:
            if tokenizer['display_name'] == selected_display or f"🔒 {tokenizer['display_name']}" == selected_display:
                selected_tokenizer = tokenizer
                break
        
        if not selected_tokenizer:
            return
        
        # Check if user has access
        if not selected_tokenizer['has_access']:
            self.show_premium_upgrade_dialog(selected_tokenizer['name'])
            # Revert to previous selection
            self.update_tokenizer_dropdown()
            return
        
        # Store current tokenizer
        self._current_tokenizer_name = selected_tokenizer['name']
        
        # Update any existing analysis if chunks are available
        if self.chunks:
            self.update_chunk_analysis()

    def show_premium_upgrade_dialog(self, feature_name):
        """Show premium upgrade dialog for specific feature"""
        try:
            upgrade_info = self.controller.get_upgrade_info()
            
            dialog = Toplevel(self)
            dialog.title("Premium Feature Required")
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            
            # Center the dialog
            dialog.transient(self)
            dialog.grab_set()
            
            main_frame = Frame(dialog, padding=20)
            main_frame.pack(fill="both", expand=True)
            
            Label(main_frame, text="🔒 Premium Feature", font=("Arial", 18, "bold")).pack(pady=(0, 10))
            
            feature_info = f"Advanced tokenizers require a premium license."
            Label(main_frame, text=feature_info, wraplength=450, justify="left").pack(pady=(0, 10))
            
            # Show premium features
            Label(main_frame, text="Premium Features Include:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
            
            features_text = "• Exact GPT-4 and GPT-3.5 tokenization\n• Claude tokenizer estimation\n• BERT/RoBERTa tokenizers\n• Advanced analytics and cost estimation\n• Smart chunking optimization\n• Batch processing capabilities"
            Label(main_frame, text=features_text, justify="left", wraplength=450).pack(anchor="w", pady=(0, 15))
            
            # Pricing info
            Label(main_frame, text="Pricing:", font=("Arial", 12, "bold")).pack(anchor="w")
            pricing_text = f"Monthly: {upgrade_info['pricing']['monthly']}\nYearly: {upgrade_info['pricing']['yearly']}"
            Label(main_frame, text=pricing_text, justify="left").pack(anchor="w", pady=(0, 15))
            
            # Buttons
            button_frame = Frame(main_frame)
            button_frame.pack(fill="x", pady=(10, 0))
            
            if upgrade_info['trial_available']:
                trial_button = Button(button_frame, text="🆓 Start Free Trial", 
                                    command=lambda: self.start_trial_from_dialog(dialog), 
                                    style="Hover.TButton")
                trial_button.pack(side="left", padx=(0, 10))
            
            upgrade_button = Button(button_frame, text="💎 Upgrade Now", 
                                  command=lambda: self.open_upgrade_url(dialog), 
                                  style="Hover.TButton")
            upgrade_button.pack(side="left", padx=(0, 10))
            
            close_button = Button(button_frame, text="Close", command=dialog.destroy)
            close_button.pack(side="right")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show upgrade dialog: {str(e)}")

    def start_trial_from_dialog(self, dialog):
        """Start trial from upgrade dialog"""
        if self.controller.start_trial():
            dialog.destroy()
            messagebox.showinfo("Trial Started", "🎉 Your 7-day premium trial has started!\nAll premium features are now available.")
            self.update_tokenizer_dropdown()
            self.update_license_status()
            self.update_premium_section()
        else:
            messagebox.showerror("Trial Error", "Failed to start trial. You may have already used your trial period.")

    def open_upgrade_url(self, dialog):
        """Open upgrade URL in browser"""
        import webbrowser
        webbrowser.open("https://wolflow.ai/upgrade")
        dialog.destroy()

    def update_chunk_analysis(self):
        """Update chunk analysis with current tokenizer (enhanced version)"""
        if not self.chunks:
            return
        
        try:
            tokenizer_name = getattr(self, '_current_tokenizer_name', 'gpt2')
            self.current_analysis = self.controller.analyze_chunks(self.chunks, tokenizer_name, TOKEN_LIMIT)
            
            # Add enhanced analysis for premium users
            if self.controller.license_manager.check_feature_access('advanced_analytics'):
                # Add tokenizer-specific recommendations
                tokenizer_info = next((t for t in self.controller.get_available_tokenizers() 
                                     if t['name'] == tokenizer_name), None)
                
                if tokenizer_info and self.current_analysis:
                    # Enhance recommendations based on tokenizer type
                    enhanced_recommendations = list(self.current_analysis.get('recommendations', []))
                    
                    if tokenizer_info['accuracy'] == 'estimated' and self.current_analysis['total_tokens'] > 5000:
                        enhanced_recommendations.append("Consider upgrading to exact tokenizer for large datasets")
                    
                    if tokenizer_info['performance'] == 'slow' and len(self.chunks) > 100:
                        enhanced_recommendations.append("Large dataset detected - faster tokenizer recommended")
                    
                    self.current_analysis['recommendations'] = enhanced_recommendations
                    
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze chunks: {str(e)}")

    def select_file(self):
        path = filedialog.askopenfilename(title="Select Book or Document",
                                          filetypes=[("Text or Document Files", "*.txt *.pdf *.epub")])
        if path:
            self.file_path = path
            self.file_label.config(text=os.path.basename(path))
            self.chunks = []
            self.current_analysis = None
            self.session.add_file(path)

    def handle_file_drop(self, event):
        path = event.data.strip("{}")
        if os.path.isfile(path) and path.lower().endswith((".txt", ".pdf", ".epub")):
            self.file_path = path
            self.file_label.config(text=os.path.basename(path))
            self.chunks = []
            self.current_analysis = None
            self.session.add_file(path)
        else:
            messagebox.showerror("Invalid File", "Please drop a valid .txt, .pdf, or .epub file.")

# END OF PART 1

# ui/app_frame.py - Complete Enhanced Version Part 2 (FIXED)
# Continue from Part 1...

    def process_text(self):
        if not self.file_path:
            messagebox.showerror("Missing File", "Please select a file first.")
            return

        method = self.split_method.get()
        delimiter = self.delimiter_entry.get() if method == "custom" else None
        tokenizer_name = getattr(self, '_current_tokenizer_name', 'gpt2')

        try:
            clean_opts = {"remove_headers": True, "normalize_whitespace": True, "strip_bullets": True}
            
            # Use enhanced controller
            self.chunks = self.controller.process_book(self.file_path, clean_opts, method, delimiter, tokenizer_name)
            
            # Analyze chunks with current tokenizer
            self.current_analysis = self.controller.analyze_chunks(self.chunks, tokenizer_name, TOKEN_LIMIT)
            
            # Update session
            for f in self.session.files:
                if f.path == self.file_path:
                    f.chunks = self.chunks
                    f.config['tokenizer'] = tokenizer_name
                    break

            # Create enhanced success message
            analysis = self.current_analysis
            msg = f"✅ Processed {analysis['total_chunks']} chunks using {tokenizer_name}\n"
            msg += f"📊 Total tokens: {analysis['total_tokens']:,} | Average: {analysis['avg_tokens']}\n"
            
            if analysis['over_limit'] > 0:
                msg += f"⚠️ {analysis['over_limit']} chunks exceed {TOKEN_LIMIT} tokens ({analysis['over_limit_percentage']:.1f}%)"
            else:
                msg += "✨ All chunks within token limit!"
                
            # Add premium analytics if available
            if analysis.get('advanced_analytics'):
                msg += f"\n🎯 Efficiency Score: {analysis['efficiency_score']}%"
                if analysis.get('cost_estimates'):
                    cost = analysis['cost_estimates']['estimated_api_cost']
                    msg += f"\n💰 Estimated training cost: ${cost:.4f}"
            
            messagebox.showinfo("Processing Complete", msg)
            
        except Exception as e:
            messagebox.showerror("Processing Error", str(e))

    def preview_chunks(self):
        """Enhanced chunk preview with advanced tokenizer information and analytics - FIXED"""
        if not self.chunks:
            messagebox.showwarning("No Data", "You must process a file first.")
            return

        # Get current tokenizer and analysis
        tokenizer_name = getattr(self, '_current_tokenizer_name', 'gpt2')
        
        # Update analysis if needed
        if not self.current_analysis:
            self.update_chunk_analysis()
        
        # Create enhanced preview window
        window = Toplevel()
        window.title("🔍 Advanced Chunk Preview")
        window.geometry("900x700")

        # Create main container - REMOVED bg parameter for ttkbootstrap compatibility
        main_container = Frame(window)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # === HEADER SECTION ===
        header_frame = Frame(main_container, relief="solid", borderwidth=1)
        header_frame.pack(fill="x", pady=(0, 15))
        
        # Title with tokenizer info
        title_frame = Frame(header_frame)
        title_frame.pack(fill="x", padx=20, pady=15)
        
        Label(title_frame, text="📊 Advanced Chunk Analysis", 
              font=("Arial", 16, "bold")).pack(anchor="w")
        
        # Tokenizer status line
        tokenizer_info = self.controller.get_available_tokenizers()
        current_tokenizer_info = next((t for t in tokenizer_info if t['name'] == tokenizer_name), None)
        
        if current_tokenizer_info:
            accuracy_badge = "🎯 Exact" if current_tokenizer_info['accuracy'] == 'exact' else "📊 Estimated"
            performance_badge = f"⚡ {current_tokenizer_info['performance'].title()}"
            premium_badge = "💎 Premium" if current_tokenizer_info['is_premium'] else "🆓 Free"
            
            tokenizer_status = f"Tokenizer: {current_tokenizer_info['display_name']} | {accuracy_badge} | {performance_badge} | {premium_badge}"
        else:
            tokenizer_status = f"Tokenizer: {tokenizer_name} | Status: Unknown"
        
        Label(title_frame, text=tokenizer_status, 
              font=("Arial", 11)).pack(anchor="w", pady=(5, 0))

        # === ANALYTICS SUMMARY SECTION ===
        if self.current_analysis:
            self._create_analytics_summary(main_container, self.current_analysis, tokenizer_name)

        # === COMPATIBILITY WARNING SECTION ===
        self._create_compatibility_warnings(main_container, tokenizer_name)

        # === CHUNKS PREVIEW SECTION ===
        preview_frame = Frame(main_container, relief="solid", borderwidth=1)
        preview_frame.pack(fill="both", expand=True, pady=(15, 0))
        
        # Preview header
        preview_header = Frame(preview_frame)
        preview_header.pack(fill="x", padx=20, pady=(15, 10))
        
        Label(preview_header, text="📋 Chunk Preview (First 10)", 
              font=("Arial", 14, "bold")).pack(anchor="w")
        
        Label(preview_header, text="Color coding: 🟢 Optimal | 🟡 Close to limit | 🔴 Over limit", 
              font=("Arial", 10)).pack(anchor="w", pady=(5, 0))

        # Scrollable text widget for chunks
        text_frame = Frame(preview_frame)
        text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Use regular tkinter Text widget (not ttkbootstrap) - REMOVED bg parameter
        text_widget = Text(text_frame, wrap="word", font=("Consolas", 10), relief="flat", bd=0)
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add chunks with enhanced formatting
        self._populate_enhanced_chunks(text_widget, tokenizer_name)

        # === ACTION BUTTONS ===
        button_frame = Frame(main_container)
        button_frame.pack(fill="x", pady=(15, 0))
        
        # Advanced analytics button (premium feature)
        if self.controller.license_manager.check_feature_access('advanced_analytics'):
            analytics_btn = Button(button_frame, text="📊 Advanced Analytics Dashboard", 
                                  command=self.create_premium_analytics_window,
                                  style="Hover.TButton")
            analytics_btn.pack(side="left", padx=(0, 10))
        else:
            upgrade_btn = Button(button_frame, text="💎 Upgrade for Advanced Analytics", 
                               command=lambda: self.show_premium_upgrade_dialog('advanced_analytics'),
                               style="Hover.TButton")
            upgrade_btn.pack(side="left", padx=(0, 10))
        
        # Tokenizer comparison button (premium feature) 
        if self.controller.license_manager.check_feature_access('advanced_analytics'):
            compare_btn = Button(button_frame, text="🔍 Compare Tokenizers", 
                               command=self.show_tokenizer_comparison,
                               style="Hover.TButton")
            compare_btn.pack(side="left", padx=(0, 10))
        
        # Close button
        close_btn = Button(button_frame, text="Close", command=window.destroy)
        close_btn.pack(side="right")

    def _create_analytics_summary(self, parent, analysis, tokenizer_name):
        """Create analytics summary panel - FIXED for ttkbootstrap"""
        analytics_frame = Frame(parent, relief="solid", borderwidth=1)
        analytics_frame.pack(fill="x", pady=(0, 15))
        
        # Header
        header = Frame(analytics_frame)
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        Label(header, text="📈 Summary Statistics", 
              font=("Arial", 14, "bold")).pack(anchor="w")

        # Create stats grid
        stats_container = Frame(analytics_frame)
        stats_container.pack(fill="x", padx=20, pady=(0, 15))
        
        # Basic stats (always available)
        basic_stats = [
            ("📊 Total Chunks", f"{analysis['total_chunks']:,}"),
            ("🔢 Total Tokens", f"{analysis['total_tokens']:,}"),
            ("📏 Average Tokens", f"{analysis['avg_tokens']}"),
            ("⚠️ Over Limit", f"{analysis['over_limit']} ({analysis['over_limit_percentage']:.1f}%)")
        ]
        
        # Display basic stats in 2x2 grid using ttkbootstrap Frame - REMOVED bg parameters
        for i, (label, value) in enumerate(basic_stats):
            row = i // 2
            col = i % 2
            
            # Use ttkbootstrap Frame without bg parameter
            stat_frame = Frame(stats_container, relief="solid", borderwidth=1)
            stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            Label(stat_frame, text=label, font=("Arial", 10, "bold")).pack(pady=(8, 2))
            Label(stat_frame, text=value, font=("Arial", 12)).pack(pady=(0, 8))
        
        # Configure grid weights
        stats_container.columnconfigure(0, weight=1)
        stats_container.columnconfigure(1, weight=1)
        
        # Premium stats (if available)
        if analysis.get('advanced_analytics'):
            premium_frame = Frame(analytics_frame, relief="solid", borderwidth=1)
            premium_frame.pack(fill="x", padx=20, pady=(10, 15))
            
            Label(premium_frame, text="💎 Premium Analytics", 
                  font=("Arial", 12, "bold"), foreground="blue").pack(anchor="w", padx=15, pady=(10, 5))
            
            premium_stats_text = []
            
            if 'efficiency_score' in analysis:
                premium_stats_text.append(f"🎯 Efficiency Score: {analysis['efficiency_score']}%")
            
            if analysis.get('cost_estimates'):
                cost = analysis['cost_estimates']['estimated_api_cost']
                premium_stats_text.append(f"💰 Estimated Training Cost: ${cost:.4f}")
            
            if analysis.get('token_distribution'):
                dist = analysis['token_distribution']
                premium_stats_text.append(f"📊 Distribution: {dist['under_50']} small | {dist['50_200']} medium | {dist['200_400']} large | {dist['over_limit']} oversized")
            
            for stat in premium_stats_text:
                Label(premium_frame, text=stat, font=("Arial", 10)).pack(anchor="w", padx=15, pady=1)
            
            # Add padding at bottom
            Label(premium_frame, text="").pack(pady=5)
        
        else:
            # Show premium preview
            preview_frame = Frame(analytics_frame, relief="solid", borderwidth=1)
            preview_frame.pack(fill="x", padx=20, pady=(10, 15))
            
            Label(preview_frame, text="💡 Upgrade for Advanced Analytics", 
                  font=("Arial", 12, "bold"), foreground="orange").pack(anchor="w", padx=15, pady=(10, 5))
            
            preview_features = [
                "🎯 Efficiency scoring and optimization suggestions",
                "💰 Training cost estimation by provider", 
                "📊 Detailed token distribution analysis",
                "🔍 Model compatibility recommendations"
            ]
            
            for feature in preview_features:
                Label(preview_frame, text=feature, font=("Arial", 10)).pack(anchor="w", padx=15, pady=1)
            
            Label(preview_frame, text="").pack(pady=5)

# END OF PART 2

# ui/app_frame.py - Complete Enhanced Version Part 3 (FIXED)
# Continue from Part 2...

    def _create_compatibility_warnings(self, parent, tokenizer_name):
        """Create compatibility warnings section - FIXED for ttkbootstrap"""
        try:
            # Check for compatibility issues
            warnings = self.controller.tokenizer_manager.get_compatibility_warnings(tokenizer_name)
            
            if warnings or not self.controller.license_manager.check_tokenizer_access(tokenizer_name):
                warning_frame = Frame(parent, relief="solid", borderwidth=1)
                warning_frame.pack(fill="x", pady=(0, 15))
                
                Label(warning_frame, text="⚠️ Compatibility Notices", 
                      font=("Arial", 12, "bold"), foreground="red").pack(anchor="w", padx=15, pady=(10, 5))
                
                # Show access warnings
                if not self.controller.license_manager.check_tokenizer_access(tokenizer_name):
                    Label(warning_frame, text="🔒 Using fallback tokenizer - premium tokenizer access required", 
                          font=("Arial", 10), foreground="red").pack(anchor="w", padx=15, pady=1)
                
                # Show compatibility warnings
                for warning in warnings:
                    Label(warning_frame, text=f"• {warning}", font=("Arial", 10), 
                          foreground="red").pack(anchor="w", padx=15, pady=1)
                
                Label(warning_frame, text="").pack(pady=5)
        
        except Exception as e:
            # Silently handle any compatibility checking errors
            pass

    def _populate_enhanced_chunks(self, text_widget, tokenizer_name):
        """Populate text widget with enhanced chunk information - FIXED token length handling"""
        # Configure color tags
        text_widget.tag_config("chunk_header_optimal", foreground="#059669", font=("Arial", 10, "bold"))
        text_widget.tag_config("chunk_header_close", foreground="#d97706", font=("Arial", 10, "bold"))
        text_widget.tag_config("chunk_header_over", foreground="#dc2626", font=("Arial", 10, "bold"))
        text_widget.tag_config("chunk_content", foreground="#374151", font=("Consolas", 9))
        text_widget.tag_config("metadata", foreground="#6b7280", font=("Arial", 9))
        text_widget.tag_config("separator", foreground="#d1d5db")
        
        chunks_to_show = min(10, len(self.chunks))
        
        for i in range(chunks_to_show):
            chunk = self.chunks[i]
            
            # Truncate very long chunks before tokenization to avoid sequence length errors
            chunk_for_tokenization = chunk if len(chunk) <= 2000 else chunk[:2000]
            
            # Get token count and metadata with error handling
            try:
                count, metadata = self.controller.get_token_count(chunk_for_tokenization, tokenizer_name)
                # If chunk was truncated, add approximate adjustment
                if len(chunk) > 2000:
                    count = int(count * (len(chunk) / 2000))
                    metadata['truncated'] = True
            except Exception as e:
                # Fallback to word-based estimation
                count = int(len(chunk.split()) * 1.3)
                metadata = {'accuracy': 'estimated', 'error': f'Tokenization error: {str(e)[:50]}...'}
            
            # Determine color coding and status
            if count > TOKEN_LIMIT:
                header_tag = "chunk_header_over"
                status_icon = "🔴"
                efficiency = "Over limit"
            elif count > TOKEN_LIMIT * 0.9:
                header_tag = "chunk_header_close"
                status_icon = "🟡"
                efficiency = "Close to limit"
            else:
                header_tag = "chunk_header_optimal"
                status_icon = "🟢"
                efficiency = "Optimal"
            
            # Create chunk header
            header_text = f"{status_icon} Chunk {i+1} | {int(count)} tokens | {efficiency}"
            
            # Add accuracy and performance info if available
            if metadata.get('accuracy'):
                accuracy_icon = "🎯" if metadata['accuracy'] == 'exact' else "📊"
                header_text += f" | {accuracy_icon} {metadata['accuracy'].title()}"
            
            if metadata.get('performance'):
                perf_icon = {"fast": "⚡", "medium": "⚖️", "slow": "🐌"}.get(metadata['performance'], "")
                header_text += f" {perf_icon}"
            
            # Add premium features info
            if self.controller.license_manager.check_feature_access('advanced_analytics'):
                # Calculate efficiency percentage
                efficiency_pct = min(100, int((min(count, TOKEN_LIMIT) / (TOKEN_LIMIT * 0.9)) * 100))
                header_text += f" | Efficiency: {efficiency_pct}%"
            
            text_widget.insert("end", header_text + "\n", header_tag)
            
            # Add metadata line
            metadata_line = f"Length: {len(chunk)} chars"
            if metadata.get('error'):
                metadata_line += f" | Error: {metadata['error']}"
            elif metadata.get('access_denied'):
                metadata_line += f" | 🔒 Premium tokenizer access required"
            elif metadata.get('truncated'):
                metadata_line += f" | ⚠️ Chunk truncated for tokenization"
            
            text_widget.insert("end", metadata_line + "\n", "metadata")
            
            # Add chunk content (truncated if very long for display)
            chunk_preview = chunk if len(chunk) <= 500 else chunk[:500] + "..."
            text_widget.insert("end", chunk_preview + "\n", "chunk_content")
            
            # Add separator (except for last chunk)
            if i < chunks_to_show - 1:
                text_widget.insert("end", "─" * 80 + "\n\n", "separator")
        
        # Add summary if showing partial chunks
        if len(self.chunks) > 10:
            summary_text = f"\n... and {len(self.chunks) - 10} more chunks\n"
            text_widget.insert("end", summary_text, "metadata")
        
        # Disable editing
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

    def start_trial(self):
        """Start premium trial"""
        try:
            if self.controller.start_trial():
                messagebox.showinfo("Trial Started", "🎉 Your 7-day premium trial has started!\nAll premium features are now available.")
                self.update_tokenizer_dropdown()
                self.update_license_status()
                self.update_premium_section()
            else:
                messagebox.showwarning("Trial Unavailable", "Trial is not available. You may have already used your trial period.")
        except Exception as e:
            messagebox.showerror("Trial Error", f"Failed to start trial: {str(e)}")

    def show_upgrade_info(self):
        """Show premium upgrade information"""
        try:
            upgrade_info = self.controller.get_upgrade_info()
            
            dialog = Toplevel(self)
            dialog.title("Premium Features")
            dialog.geometry("600x500")
            dialog.resizable(False, False)
            
            dialog.transient(self)
            dialog.grab_set()
            
            main_frame = Frame(dialog, padding=20)
            main_frame.pack(fill="both", expand=True)
            
            Label(main_frame, text="💎 Wolfscribe Premium", font=("Arial", 20, "bold")).pack(pady=(0, 15))
            
            # Feature list
            Label(main_frame, text="Premium Features:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
            
            features = [
                "🎯 Exact GPT-4 & GPT-3.5 Tokenization",
                "🤖 Claude & BERT Tokenizer Support", 
                "📊 Advanced Analytics & Cost Estimation",
                "⚡ Smart Chunking Optimization",
                "📁 Batch Processing Capabilities",
                "💾 Enhanced Export with Metadata"
            ]
            
            for feature in features:
                Label(main_frame, text=f"  {feature}", font=("Arial", 11)).pack(anchor="w", pady=1)
            
            # Pricing
            pricing_frame = Frame(main_frame, relief="solid", padding=15)
            pricing_frame.pack(fill="x", pady=(20, 15))
            
            Label(pricing_frame, text="💰 Pricing", font=("Arial", 14, "bold")).pack(anchor="w")
            Label(pricing_frame, text=f"Monthly: {upgrade_info['pricing']['monthly']}", font=("Arial", 12)).pack(anchor="w")
            Label(pricing_frame, text=f"Yearly: {upgrade_info['pricing']['yearly']}", font=("Arial", 12)).pack(anchor="w")
            
            # Buttons
            button_frame = Frame(main_frame)
            button_frame.pack(fill="x", pady=(15, 0))
            
            if upgrade_info['trial_available']:
                trial_button = Button(button_frame, text="🆓 Start Free Trial (7 Days)", 
                                    command=lambda: self.start_trial_from_upgrade_dialog(dialog), 
                                    style="Hover.TButton")
                trial_button.pack(side="left", padx=(0, 10))
            
            upgrade_button = Button(button_frame, text="💎 Upgrade Now", 
                                  command=lambda: self.open_upgrade_url(dialog), 
                                  style="Hover.TButton")
            upgrade_button.pack(side="left", padx=(0, 10))
            
            close_button = Button(button_frame, text="Maybe Later", command=dialog.destroy)
            close_button.pack(side="right")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show upgrade information: {str(e)}")

    def start_trial_from_upgrade_dialog(self, dialog):
        """Start trial from upgrade info dialog"""
        if self.controller.start_trial():
            dialog.destroy()
            messagebox.showinfo("Trial Started", 
                              "🎉 Welcome to Wolfscribe Premium!\n\n"
                              "Your 7-day trial includes:\n"
                              "• All premium tokenizers\n"
                              "• Advanced analytics\n"
                              "• Smart chunking features\n\n"
                              "Enjoy exploring the premium features!")
            self.update_tokenizer_dropdown()
            self.update_license_status()
            self.update_premium_section()
        else:
            messagebox.showerror("Trial Error", 
                               "Trial could not be started.\n"
                               "You may have already used your trial period.")

# END OF PART 3

# ui/app_frame.py - Complete Enhanced Version Part 4 (FIXED)
# Continue from Part 3...

    def save_session(self):
        """Enhanced session saving with tokenizer preferences"""
        path = filedialog.asksaveasfilename(defaultextension=".wsession", 
                                          filetypes=[("Wolfscribe Session", "*.wsession")])
        if not path:
            return
        try:
            # Include tokenizer preferences in session
            session_data = self.session.to_dict()
            
            # Add current UI state
            session_data['ui_preferences'] = {
                'selected_tokenizer': getattr(self, '_current_tokenizer_name', 'gpt2'),
                'split_method': self.split_method.get(),
                'token_limit': TOKEN_LIMIT
            }
            
            # Add analysis data if available
            if self.current_analysis:
                session_data['last_analysis'] = self.current_analysis
                
            with open(path, "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Session Saved", f"Session saved to {path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def load_session(self):
        """Enhanced session loading with tokenizer preferences"""
        path = filedialog.askopenfilename(filetypes=[("Wolfscribe Session", "*.wsession")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Load session data
            self.session = Session.from_dict(data)
            
            # Restore UI preferences if available
            ui_prefs = data.get('ui_preferences', {})
            if ui_prefs:
                # Restore tokenizer selection (if user has access)
                preferred_tokenizer = ui_prefs.get('selected_tokenizer', 'gpt2')
                if self.controller.license_manager.check_tokenizer_access(preferred_tokenizer):
                    self._current_tokenizer_name = preferred_tokenizer
                    self.update_tokenizer_dropdown()
                    
                    # Find and set the display name
                    for tokenizer in self.tokenizer_options:
                        if tokenizer['name'] == preferred_tokenizer:
                            self.selected_tokenizer.set(tokenizer['display_name'])
                            break
                
                # Restore split method
                split_method = ui_prefs.get('split_method', 'paragraph')
                self.split_method.set(split_method)
                self.on_split_method_change()
            
            # Restore analysis data
            self.current_analysis = data.get('last_analysis')
            
            # Load first file if available
            if self.session.files:
                first_file = self.session.files[0]
                self.file_path = first_file.path
                self.file_label.config(text=os.path.basename(self.file_path))
                self.chunks = first_file.chunks
                
                # Update analysis if chunks exist
                if self.chunks:
                    self.update_chunk_analysis()
            
            messagebox.showinfo("Session Loaded", f"Session loaded from {path}")
            
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def create_premium_analytics_window(self):
        """Create dedicated analytics window for premium users"""
        if not self.current_analysis:
            messagebox.showwarning("No Analysis", "Please process a file first to see analytics.")
            return
            
        if not self.controller.license_manager.check_feature_access('advanced_analytics'):
            self.show_premium_upgrade_dialog('advanced_analytics')
            return
            
        window = Toplevel()
        window.title("Advanced Analytics Dashboard")
        window.geometry("700x800")
        
        main_frame = Frame(window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        Label(main_frame, text="📊 Advanced Analytics Dashboard", 
              font=("Arial", 18, "bold")).pack(pady=(0, 20))
        
        analysis = self.current_analysis
        tokenizer_name = getattr(self, '_current_tokenizer_name', 'gpt2')
        
        # Overview section
        overview_frame = Frame(main_frame, relief="solid", padding=15)
        overview_frame.pack(fill="x", pady=(0, 15))
        
        Label(overview_frame, text="📋 Overview", font=("Arial", 14, "bold")).pack(anchor="w")
        
        overview_stats = [
            f"Dataset: {os.path.basename(self.file_path) if self.file_path else 'Unknown'}",
            f"Tokenizer: {tokenizer_name}",
            f"Total Chunks: {analysis['total_chunks']:,}",
            f"Total Tokens: {analysis['total_tokens']:,}",
            f"Average Tokens/Chunk: {analysis['avg_tokens']}",
            f"Token Range: {analysis['min_tokens']} - {analysis['max_tokens']}",
            f"Efficiency Score: {analysis.get('efficiency_score', 0)}%"
        ]
        
        for stat in overview_stats:
            Label(overview_frame, text=f"• {stat}", font=("Arial", 10)).pack(anchor="w", pady=1)
        
        # Token distribution section
        if analysis.get('token_distribution'):
            dist_frame = Frame(main_frame, relief="solid", padding=15)
            dist_frame.pack(fill="x", pady=(0, 15))
            
            Label(dist_frame, text="📈 Token Distribution", font=("Arial", 14, "bold")).pack(anchor="w")
            
            dist = analysis['token_distribution']
            total_chunks = analysis['total_chunks']
            
            dist_stats = [
                f"Under 50 tokens: {dist['under_50']} ({dist['under_50']/total_chunks*100:.1f}%)",
                f"50-200 tokens: {dist['50_200']} ({dist['50_200']/total_chunks*100:.1f}%)",
                f"200-400 tokens: {dist['200_400']} ({dist['200_400']/total_chunks*100:.1f}%)",
                f"400-512 tokens: {dist['400_512']} ({dist['400_512']/total_chunks*100:.1f}%)",
                f"Over limit: {dist['over_limit']} ({dist['over_limit']/total_chunks*100:.1f}%)"
            ]
            
            for stat in dist_stats:
                Label(dist_frame, text=f"• {stat}", font=("Arial", 10)).pack(anchor="w", pady=1)
        
        # Cost estimation section
        if analysis.get('cost_estimates'):
            cost_frame = Frame(main_frame, relief="solid", padding=15)
            cost_frame.pack(fill="x", pady=(0, 15))
            
            Label(cost_frame, text="💰 Cost Estimation", font=("Arial", 14, "bold")).pack(anchor="w")
            
            cost = analysis['cost_estimates']
            cost_stats = [
                f"Tokenizer: {cost['tokenizer']}",
                f"Total Tokens: {cost['total_tokens']:,}",
                f"Cost per 1K tokens: ${cost['cost_per_1k_tokens']:.4f}",
                f"Estimated API Cost: ${cost['estimated_api_cost']:.4f}",
                f"Note: {cost['note']}"
            ]
            
            for stat in cost_stats:
                Label(cost_frame, text=f"• {stat}", font=("Arial", 10)).pack(anchor="w", pady=1)
        
        # Recommendations section
        if analysis.get('recommendations'):
            rec_frame = Frame(main_frame, relief="solid", padding=15)
            rec_frame.pack(fill="x", pady=(0, 15))
            
            Label(rec_frame, text="💡 Optimization Recommendations", font=("Arial", 14, "bold")).pack(anchor="w")
            
            for rec in analysis['recommendations']:
                Label(rec_frame, text=f"• {rec}", wraplength=650, font=("Arial", 10)).pack(anchor="w", pady=2)
        
        # Action buttons
        button_frame = Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        export_analytics_btn = Button(button_frame, text="📊 Export Analytics Report", 
                                    command=lambda: self.export_analytics_report(analysis))
        export_analytics_btn.pack(side="left", padx=(0, 10))
        
        close_btn = Button(button_frame, text="Close", command=window.destroy)
        close_btn.pack(side="right")

    def export_analytics_report(self, analysis):
        """Export detailed analytics report"""
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Report", "*.json"), ("Text Report", "*.txt")]
        )
        
        if not path:
            return
            
        try:
            if path.endswith('.json'):
                # Export as JSON
                report_data = {
                    'file_info': {
                        'filename': os.path.basename(self.file_path) if self.file_path else 'Unknown',
                        'processed_at': str(datetime.now()),
                        'tokenizer_used': getattr(self, '_current_tokenizer_name', 'gpt2')
                    },
                    'analysis': analysis,
                    'chunks_sample': self.chunks[:5] if len(self.chunks) > 5 else self.chunks
                }
                
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
                    
            else:
                # Export as text report
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("WOLFSCRIBE ANALYTICS REPORT\n")
                    f.write("=" * 50 + "\n\n")
                    
                    f.write(f"File: {os.path.basename(self.file_path) if self.file_path else 'Unknown'}\n")
                    f.write(f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Tokenizer: {getattr(self, '_current_tokenizer_name', 'gpt2')}\n\n")
                    
                    f.write("OVERVIEW\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"Total Chunks: {analysis['total_chunks']:,}\n")
                    f.write(f"Total Tokens: {analysis['total_tokens']:,}\n")
                    f.write(f"Average Tokens: {analysis['avg_tokens']}\n")
                    f.write(f"Min/Max Tokens: {analysis['min_tokens']} / {analysis['max_tokens']}\n")
                    f.write(f"Over Limit: {analysis['over_limit']} ({analysis['over_limit_percentage']:.1f}%)\n")
                    
                    if analysis.get('efficiency_score'):
                        f.write(f"Efficiency Score: {analysis['efficiency_score']}%\n")
                    
                    if analysis.get('recommendations'):
                        f.write("\nRECOMMENDATIONS\n")
                        f.write("-" * 20 + "\n")
                        for i, rec in enumerate(analysis['recommendations'], 1):
                            f.write(f"{i}. {rec}\n")
            
            messagebox.showinfo("Report Exported", f"Analytics report saved to {path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")

# END OF PART 4

# ui/app_frame.py - Complete Enhanced Version Part 5 (FIXED)
# Continue from Part 4...

    def show_tokenizer_comparison(self):
        """Show comparison of different tokenizers for current text (premium feature)"""
        if not self.chunks:
            messagebox.showwarning("No Data", "Please process a file first.")
            return
            
        if not self.controller.license_manager.check_feature_access('advanced_analytics'):
            self.show_premium_upgrade_dialog('advanced_analytics')
            return
        
        # Sample some text for comparison - FIXED to avoid token length errors
        sample_text = "\n\n".join(self.chunks[:3]) if len(self.chunks) >= 3 else "\n\n".join(self.chunks)
        if len(sample_text) > 2000:  # Limit for comparison to avoid tokenization errors
            sample_text = sample_text[:2000] + "..."
        
        window = Toplevel()
        window.title("Tokenizer Comparison")
        window.geometry("800x600")
        
        main_frame = Frame(window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        Label(main_frame, text="🔍 Tokenizer Comparison", font=("Arial", 16, "bold")).pack(pady=(0, 15))
        
        # Create comparison table
        comparison_frame = Frame(main_frame, relief="solid", padding=10)
        comparison_frame.pack(fill="both", expand=True)
        
        # Headers
        headers = ["Tokenizer", "Token Count", "Accuracy", "Performance", "Access"]
        for i, header in enumerate(headers):
            Label(comparison_frame, text=header, font=("Arial", 10, "bold")).grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        # Compare all tokenizers with enhanced error handling
        available_tokenizers = self.controller.get_available_tokenizers()
        for row, tokenizer in enumerate(available_tokenizers, 1):
            # Tokenizer name
            Label(comparison_frame, text=tokenizer['display_name']).grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            if tokenizer['has_access'] and tokenizer['available']:
                try:
                    # Use the same truncation logic as in chunk processing
                    test_text = sample_text if len(sample_text) <= 1500 else sample_text[:1500]
                    count, metadata = self.controller.get_token_count(test_text, tokenizer['name'])
                    
                    # Adjust count if text was truncated
                    if len(sample_text) > 1500:
                        count = int(count * (len(sample_text) / 1500))
                    
                    Label(comparison_frame, text=str(count)).grid(row=row, column=1, padx=5, pady=2)
                    Label(comparison_frame, text=metadata.get('accuracy', 'unknown')).grid(row=row, column=2, padx=5, pady=2)
                    Label(comparison_frame, text=metadata.get('performance', 'unknown')).grid(row=row, column=3, padx=5, pady=2)
                    Label(comparison_frame, text="✅", foreground="green").grid(row=row, column=4, padx=5, pady=2)
                    
                except Exception as e:
                    # Fallback for tokenization errors
                    fallback_count = int(len(sample_text.split()) * 1.3)
                    Label(comparison_frame, text=f"~{fallback_count}", foreground="orange").grid(row=row, column=1, padx=5, pady=2)
                    Label(comparison_frame, text="estimated").grid(row=row, column=2, padx=5, pady=2)
                    Label(comparison_frame, text="error").grid(row=row, column=3, padx=5, pady=2)
                    Label(comparison_frame, text="⚠️", foreground="orange").grid(row=row, column=4, padx=5, pady=2)
            else:
                Label(comparison_frame, text="N/A").grid(row=row, column=1, padx=5, pady=2)
                Label(comparison_frame, text=tokenizer['accuracy']).grid(row=row, column=2, padx=5, pady=2)
                Label(comparison_frame, text=tokenizer['performance']).grid(row=row, column=3, padx=5, pady=2)
                access_text = "🔒" if tokenizer['is_premium'] and not tokenizer['has_access'] else "❌"
                access_color = "orange" if access_text == "🔒" else "red"
                Label(comparison_frame, text=access_text, foreground=access_color).grid(row=row, column=4, padx=5, pady=2)
        
        # Sample text display
        Label(main_frame, text="Sample Text Used for Comparison:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(15, 5))
        
        sample_display = Text(main_frame, height=8, wrap="word")
        sample_display.pack(fill="x", pady=(0, 15))
        sample_display.insert("1.0", sample_text)
        sample_display.config(state="disabled")
        
        # Close button
        Button(main_frame, text="Close", command=window.destroy).pack(pady=(10, 0))

    def get_tokenizer_display_info(self, tokenizer_name):
        """Get formatted display information for a tokenizer"""
        try:
            tokenizer_info = next((t for t in self.controller.get_available_tokenizers() 
                                 if t['name'] == tokenizer_name), None)
            
            if not tokenizer_info:
                return {
                    'display_name': tokenizer_name,
                    'accuracy_badge': '📊 Estimated',
                    'performance_badge': '❓ Unknown',
                    'premium_badge': '❓ Unknown',
                    'status': 'Unknown tokenizer'
                }
            
            accuracy_badge = "🎯 Exact" if tokenizer_info['accuracy'] == 'exact' else "📊 Estimated"
            performance_badge = f"⚡ {tokenizer_info['performance'].title()}"
            premium_badge = "💎 Premium" if tokenizer_info['is_premium'] else "🆓 Free"
            
            status = "Available" if tokenizer_info['available'] else "Unavailable"
            if not tokenizer_info['has_access']:
                status += " (Premium Required)"
            
            return {
                'display_name': tokenizer_info['display_name'],
                'accuracy_badge': accuracy_badge,
                'performance_badge': performance_badge, 
                'premium_badge': premium_badge,
                'status': status
            }
            
        except Exception as e:
            return {
                'display_name': tokenizer_name,
                'accuracy_badge': '📊 Estimated',
                'performance_badge': '❓ Unknown', 
                'premium_badge': '❓ Unknown',
                'status': 'Error loading info'
            }

    def open_upgrade_url(self, dialog=None):
        """Open upgrade URL in browser"""
        try:
            import webbrowser
            webbrowser.open("https://wolflow.ai/upgrade")
            if dialog:
                dialog.destroy()
        except Exception as e:
            messagebox.showerror("Browser Error", f"Could not open browser: {str(e)}")
            if dialog:
                dialog.destroy()

# End of AppFrame class