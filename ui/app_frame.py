# ui/app_frame.py - FINAL OPTIMIZED VERSION with Simple Dialogs
import os
import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage
from ttkbootstrap import Frame, Label, Button, Entry, Combobox
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from controller import ProcessingController
from export.dataset_exporter import save_as_txt, save_as_csv
from tkinterdnd2 import DND_FILES
import json
from session import Session

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
        self.current_analysis = None

        # Tokenizer selection state
        self.selected_tokenizer = tk.StringVar(value="gpt2")
        self.tokenizer_options = []
        
        self._setup_icons()
        self._setup_ui()

    def _setup_icons(self):
        """Setup application icons with fallback"""
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

    def _setup_ui(self):
        """Setup main UI layout"""
        content = self.scrollable_frame

        # File Loader Section
        Label(content, text="File Loader", font=("Arial", 16, "bold")).grid(row=0, column=0, sticky="w", padx=10)
        self.file_label = Label(content, text="No file selected", anchor="w")
        self.file_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))
        Button(content, image=self.icons["file"], text=" Select File", compound="left",
               command=self.select_file, style="Hover.TButton").grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 16))
        
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_file_drop)

        # Preprocessing Section
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

        # Tokenizer Selection
        Label(content, text="Tokenizer:").grid(row=7, column=0, sticky="w", padx=10)
        self.tokenizer_dropdown = Combobox(content, textvariable=self.selected_tokenizer, state="readonly")
        self.tokenizer_dropdown.grid(row=8, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.tokenizer_dropdown.bind("<<ComboboxSelected>>", self.on_tokenizer_change)
        
        self.update_tokenizer_dropdown()
        
        ToolTip(self.tokenizer_dropdown,
                text="Choose tokenizer for accurate token counting:\n"
                     "• GPT-2: Basic estimation (Free)\n"
                     "• GPT-4/3.5: Exact OpenAI tokenization (Premium)\n"
                     "• BERT: For encoder models (Premium)\n"
                     "• Claude: Anthropic estimation (Premium)",
                delay=500)

        # License status indicator
        self.license_status_label = Label(content, text="", font=("Arial", 10), anchor="w")
        self.license_status_label.grid(row=9, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.update_license_status()

        Button(content, image=self.icons["clean"], text=" Process Text", compound="left",
               command=self.process_text, style="Hover.TButton").grid(row=10, column=0, sticky="ew", padx=10, pady=(0, 16))

        # Preview Section
        Label(content, text="Preview", font=("Arial", 16, "bold")).grid(row=11, column=0, sticky="w", padx=10)
        Button(content, image=self.icons["preview"], text=" Preview Chunks", compound="left",
               command=self.preview_chunks, style="Hover.TButton").grid(row=12, column=0, sticky="ew", padx=10, pady=(0, 16))

        # Export Section
        Label(content, text="Export Dataset", font=("Arial", 16, "bold")).grid(row=13, column=0, sticky="w", padx=10)
        Button(content, image=self.icons["export_txt"], text=" Export as .txt", compound="left",
               command=self.export_txt, style="Hover.TButton").grid(row=14, column=0, sticky="ew", padx=10, pady=(0, 8))
        Button(content, image=self.icons["export_csv"], text=" Export as .csv", compound="left",
               command=self.export_csv, style="Hover.TButton").grid(row=15, column=0, sticky="ew", padx=10)

        # Session Section
        Label(content, text="Session Management", font=("Arial", 16, "bold")).grid(row=16, column=0, sticky="w", padx=10, pady=(16, 0))
        Button(content, image=self.icons["save"], text=" Save Session", compound="left",
               command=self.save_session, style="Hover.TButton").grid(row=17, column=0, sticky="ew", padx=10, pady=(0, 8))
        Button(content, image=self.icons["file_up"], text=" Load Session", compound="left",
               command=self.load_session, style="Hover.TButton").grid(row=18, column=0, sticky="ew", padx=10, pady=(0, 8))

        # Premium Section
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
                    display_names.append(tokenizer['display_name'])
                else:
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
                self._current_tokenizer_name = available_tokenizers[0]['name']
            else:
                self.selected_tokenizer.set("GPT-2 (Free)")
                self._current_tokenizer_name = 'gpt2'
                
        except Exception as e:
            messagebox.showerror("Tokenizer Error", f"Failed to load tokenizers: {str(e)}")
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
                Label(self.premium_section, text="Premium Features", font=("Arial", 16, "bold")).pack(anchor="w")
                
                upgrade_button = Button(self.premium_section, text="🚀 Start Free Trial", 
                                      command=self.start_trial, style="Hover.TButton")
                upgrade_button.pack(fill="x", pady=(5, 0))
                
                upgrade_info_button = Button(self.premium_section, text="💎 View Premium Features", 
                                           command=self.show_upgrade_info, style="Hover.TButton")
                upgrade_info_button.pack(fill="x", pady=(5, 0))
            else:
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
        
        selected_tokenizer = None
        for tokenizer in self.tokenizer_options:
            if tokenizer['display_name'] == selected_display or f"🔒 {tokenizer['display_name']}" == selected_display:
                selected_tokenizer = tokenizer
                break
        
        if not selected_tokenizer:
            return
        
        if not selected_tokenizer['has_access']:
            self.show_premium_upgrade_dialog(selected_tokenizer['name'])
            self.update_tokenizer_dropdown()
            return
        
        self._current_tokenizer_name = selected_tokenizer['name']
        
        if self.chunks:
            self.update_chunk_analysis()

    def show_premium_upgrade_dialog(self, feature_name):
        """SIMPLIFIED: Use basic messagebox for premium upgrade"""
        try:
            upgrade_info = self.controller.get_upgrade_info()
            premium_features = upgrade_info.get('premium_features', [])
            
            feature_list = "\n".join([f"• {f['description']}" for f in premium_features[:5]])
            
            message = f"""🔒 Premium Feature: {feature_name}

Premium features include:
{feature_list}

💎 Premium: $15/month or $150/year
🆓 7-day free trial available

Would you like to start your free trial?"""
            
            result = messagebox.askyesno("Upgrade to Premium", message)
            if result:
                self.start_trial()
        except Exception as e:
            messagebox.showerror("Upgrade Error", f"Failed to show upgrade info: {str(e)}")

    def update_chunk_analysis(self):
        """Update chunk analysis with current tokenizer"""
        if not self.chunks:
            return
        
        try:
            tokenizer_name = getattr(self, '_current_tokenizer_name', 'gpt2')
            self.current_analysis = self.controller.analyze_chunks(self.chunks, tokenizer_name, TOKEN_LIMIT)
            
            if self.controller.license_manager.check_feature_access('advanced_analytics'):
                tokenizer_info = next((t for t in self.controller.get_available_tokenizers() 
                                     if t['name'] == tokenizer_name), None)
                
                if tokenizer_info and self.current_analysis:
                    enhanced_recommendations = list(self.current_analysis.get('recommendations', []))
                    
                    if tokenizer_info['accuracy'] == 'estimated' and self.current_analysis['total_tokens'] > 5000:
                        enhanced_recommendations.append("Consider upgrading to exact tokenizer for large datasets")
                    
                    if tokenizer_info['performance'] == 'slow' and len(self.chunks) > 100:
                        enhanced_recommendations.append("Large dataset detected - faster tokenizer recommended")
                    
                    self.current_analysis['recommendations'] = enhanced_recommendations
                    
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze chunks: {str(e)}")

    # File operations
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
            
            self.chunks = self.controller.process_book(self.file_path, clean_opts, method, delimiter, tokenizer_name)
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
                
            if analysis.get('advanced_analytics'):
                msg += f"\n🎯 Efficiency Score: {analysis['efficiency_score']}%"
                if analysis.get('cost_estimates'):
                    cost = analysis['cost_estimates']['estimated_api_cost']
                    msg += f"\n💰 Estimated training cost: ${cost:.4f}"
            
            messagebox.showinfo("Processing Complete", msg)
            
        except Exception as e:
            messagebox.showerror("Processing Error", str(e))

    def preview_chunks(self):
        """SIMPLIFIED: Use basic Toplevel window for chunk preview"""
        if not self.chunks:
            messagebox.showwarning("No Data", "You must process a file first.")
            return

        tokenizer_name = getattr(self, '_current_tokenizer_name', 'gpt2')
        
        try:
            # Create simple preview window
            preview_window = tk.Toplevel(self)
            preview_window.title("Chunk Preview")
            preview_window.geometry("800x600")
            preview_window.transient(self)
            
            # Create scrollable text widget
            text_frame = Frame(preview_window)
            text_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Arial", 10))
            scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side="left", fill=BOTH, expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add chunk content with basic analysis
            content = f"📊 CHUNK PREVIEW - {len(self.chunks)} chunks\n"
            content += f"Tokenizer: {tokenizer_name}\n"
            content += "=" * 60 + "\n\n"
            
            # Show first 10 chunks with token counts
            for i, chunk in enumerate(self.chunks[:10]):
                count, _ = self.controller.get_token_count(chunk, tokenizer_name)
                status = "🟢" if count <= TOKEN_LIMIT else "🔴"
                content += f"{status} Chunk {i+1} | {count} tokens\n"
                content += f"{chunk[:200]}{'...' if len(chunk) > 200 else ''}\n"
                content += "-" * 40 + "\n\n"
            
            if len(self.chunks) > 10:
                content += f"... and {len(self.chunks) - 10} more chunks\n"
            
            text_widget.insert("1.0", content)
            text_widget.config(state="disabled")
            
            # Add close button
            Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to show preview: {str(e)}")

    def create_premium_analytics_window(self):
        """SIMPLIFIED: Use messagebox for analytics summary"""
        if not self.current_analysis:
            messagebox.showwarning("No Analysis", "No analysis data available.")
            return
        
        try:
            analysis = self.current_analysis
            
            # Create analytics summary
            summary = f"""📊 ANALYTICS SUMMARY

Dataset Overview:
• Total Chunks: {analysis.get('total_chunks', 0)}
• Total Tokens: {analysis.get('total_tokens', 0):,}
• Average Tokens: {analysis.get('avg_tokens', 0)}
• Over Limit: {analysis.get('over_limit', 0)} ({analysis.get('over_limit_percentage', 0):.1f}%)

Efficiency Score: {analysis.get('efficiency_score', 0)}%"""
            
            # Add cost preview if available
            cost_preview = analysis.get('cost_preview', {})
            if cost_preview.get('available'):
                summary += f"""

💰 Cost Analysis:
• Best Approach: {cost_preview.get('best_approach', 'N/A')}
• Estimated Cost: ${cost_preview.get('estimated_cost', 0):.2f}
• Training Hours: {cost_preview.get('training_hours', 0):.1f}h"""
            else:
                summary += f"""

💰 Cost Preview:
• Estimated Range: {cost_preview.get('estimated_cost_range', 'N/A')}
• {cost_preview.get('upgrade_message', '')}"""
            
            # Add recommendations
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                summary += "\n\n💡 Recommendations:\n"
                for i, rec in enumerate(recommendations[:3], 1):
                    summary += f"{i}. {rec}\n"
            
            messagebox.showinfo("Analytics Dashboard", summary)
            
        except Exception as e:
            messagebox.showerror("Analytics Error", f"Failed to show analytics: {str(e)}")

    def show_tokenizer_comparison(self):
        """SIMPLIFIED: Use messagebox for tokenizer comparison"""
        if not self.chunks:
            messagebox.showwarning("No Data", "Process a file first to compare tokenizers.")
            return
        
        try:
            available_tokenizers = self.controller.get_available_tokenizers()
            
            # Get sample text for comparison
            sample_text = self.chunks[0][:500] if self.chunks else "Sample text for comparison"
            
            comparison = "🔍 TOKENIZER COMPARISON\n\n"
            comparison += f"Sample: {sample_text[:100]}...\n"
            comparison += "=" * 50 + "\n\n"
            
            for tokenizer in available_tokenizers[:5]:  # Limit to 5 tokenizers
                if tokenizer['available']:
                    try:
                        count, metadata = self.controller.get_token_count(sample_text, tokenizer['name'])
                        access = "✅" if tokenizer['has_access'] else "🔒"
                        comparison += f"{access} {tokenizer['display_name']}: {count} tokens\n"
                        comparison += f"   Accuracy: {tokenizer['accuracy']} | Performance: {tokenizer['performance']}\n\n"
                    except:
                        comparison += f"❌ {tokenizer['display_name']}: Error\n\n"
            
            comparison += "\n💡 Recommendation: Use exact tokenizers for production datasets"
            
            messagebox.showinfo("Tokenizer Comparison", comparison)
            
        except Exception as e:
            messagebox.showerror("Comparison Error", f"Failed to compare tokenizers: {str(e)}")

    # Export operations
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

    # Trial and premium operations - SIMPLIFIED
    def start_trial(self):
        """SIMPLIFIED: Use controller method with UI updates"""
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
        """SIMPLIFIED: Use messagebox for premium info"""
        try:
            upgrade_info = self.controller.get_upgrade_info()
            license_status = upgrade_info.get('current_status', 'free')
            
            if license_status == 'trial':
                days = upgrade_info.get('days_remaining', 0)
                message = f"""⏱️ TRIAL STATUS

You have {days} days remaining in your premium trial.

Premium Features Active:
• Exact GPT-4 & GPT-3.5 tokenization
• Advanced cost analysis with 15+ approaches
• ROI analysis and optimization recommendations
• Real-time cloud pricing integration

Upgrade to keep these features after trial expires.

💎 Premium: $15/month or $150/year"""
            
            elif license_status == 'active':
                message = """✅ PREMIUM ACTIVE

Your premium license is active with full access to:
• Exact tokenization for all major models
• Comprehensive cost analysis
• Advanced analytics with export
• Priority support

Thank you for supporting Wolfscribe!"""
            
            else:  # free
                premium_features = upgrade_info.get('premium_features', [])
                feature_list = "\n".join([f"• {f['description']}" for f in premium_features[:5]])
                
                message = f"""💎 UPGRADE TO PREMIUM

Current: Free Tier
• GPT-2 tokenization only
• Basic chunk analysis

Premium Features:
{feature_list}

💰 Pricing:
• Monthly: $15/month
• Yearly: $150/year (save $30!)

🆓 Start 7-day free trial - no credit card required"""
            
            result = messagebox.showinfo("Premium Information", message)
            
            # Offer trial if user is on free tier
            if license_status == 'free':
                trial_result = messagebox.askyesno("Start Trial?", "Would you like to start your 7-day free trial now?")
                if trial_result:
                    self.start_trial()
                    
        except Exception as e:
            messagebox.showerror("Info Error", f"Failed to show upgrade info: {str(e)}")

    # Session operations
    def save_session(self):
        """Enhanced session saving with tokenizer preferences"""
        path = filedialog.asksaveasfilename(defaultextension=".wsession", 
                                          filetypes=[("Wolfscribe Session", "*.wsession")])
        if not path:
            return
        try:
            session_data = self.session.to_dict()
            
            session_data['ui_preferences'] = {
                'selected_tokenizer': getattr(self, '_current_tokenizer_name', 'gpt2'),
                'split_method': self.split_method.get(),
                'token_limit': TOKEN_LIMIT
            }
            
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
            
            self.session = Session.from_dict(data)
            
            ui_prefs = data.get('ui_preferences', {})
            if ui_prefs:
                preferred_tokenizer = ui_prefs.get('selected_tokenizer', 'gpt2')
                if self.controller.license_manager.check_tokenizer_access(preferred_tokenizer):
                    self._current_tokenizer_name = preferred_tokenizer
                    self.update_tokenizer_dropdown()
                    
                    for tokenizer in self.tokenizer_options:
                        if tokenizer['name'] == preferred_tokenizer:
                            self.selected_tokenizer.set(tokenizer['display_name'])
                            break
                
                split_method = ui_prefs.get('split_method', 'paragraph')
                self.split_method.set(split_method)
                self.on_split_method_change()
            
            self.current_analysis = data.get('last_analysis')
            
            if self.session.files:
                first_file = self.session.files[0]
                self.file_path = first_file.path
                self.file_label.config(text=os.path.basename(self.file_path))
                self.chunks = first_file.chunks
                
                if self.chunks:
                    self.update_chunk_analysis()
            
            messagebox.showinfo("Session Loaded", f"Session loaded from {path}")
            
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

# END OF FILE - Simple Dialog Implementation Complete