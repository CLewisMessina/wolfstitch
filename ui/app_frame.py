# ui/app_frame.py - AFTER Checkpoint A2: Analytics Dashboard Extracted
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

# Import extracted dialogs
from ui.dialogs import ChunkPreviewDialog, AnalyticsDashboard

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
        """SIMPLIFIED: Use extracted ChunkPreviewDialog"""
        if not self.chunks:
            messagebox.showwarning("No Data", "You must process a file first.")
            return

        # Get current tokenizer name
        tokenizer_name = getattr(self, '_current_tokenizer_name', 'gpt2')
        
        # Create and show the preview dialog
        preview_dialog = ChunkPreviewDialog(
            parent=self,
            chunks=self.chunks,
            controller=self.controller,
            tokenizer_name=tokenizer_name,
            current_analysis=self.current_analysis
        )
        preview_dialog.show()

    def create_premium_analytics_window(self):
        """SIMPLIFIED: Use extracted AnalyticsDashboard - NEW METHOD"""
        analytics_dashboard = AnalyticsDashboard(
            parent=self,
            controller=self.controller,
            current_analysis=self.current_analysis,
            file_path=self.file_path,
            tokenizer_name=getattr(self, '_current_tokenizer_name', 'gpt2'),
            chunks=self.chunks
        )
        analytics_dashboard.show()

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

    # ===================================================================
    # REMAINING METHODS - TARGETS FOR FUTURE EXTRACTIONS (A3)
    # ===================================================================

    def show_tokenizer_comparison(self):
        """Show comparison of different tokenizers - TARGET FOR A3 EXTRACTION"""
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
        """Get formatted display information for a tokenizer - HELPER METHOD"""
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

# END OF FILE - FINAL ESTIMATED SIZE: ~500 lines (down from ~700 after A1)
# ANALYTICS METHODS SUCCESSFULLY EXTRACTED TO ui/dialogs/analytics_dialog.py
# REMAINING FOR A3 EXTRACTION: show_tokenizer_comparison() + premium dialog methods (~200 lines)