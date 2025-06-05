# ui/app_frame.py - FINAL OPTIMIZED VERSION with Enhanced Cost Analysis
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
               command=self.process_text, style="Hover.TButton").grid(row=10, column=0, sticky="ew", padx=10, pady=(0, 8))

        # *** STAGE 1 ADDITION: Cost Analysis Button ***
        cost_button = Button(content, text="💰 Analyze Training Costs", 
                            command=self.show_cost_analysis, style="Hover.TButton")
        cost_button.grid(row=11, column=0, sticky="ew", padx=10, pady=(0, 16))
        
        ToolTip(cost_button, 
                text="Analyze comprehensive training costs across 15+ approaches:\n"
                     "• Local training (RTX 3090/4090/A100)\n"
                     "• Cloud providers (Lambda Labs, Vast.ai, RunPod)\n"
                     "• API fine-tuning costs\n"
                     "• LoRA/QLoRA optimization\n"
                     "• ROI analysis with break-even calculations",
                delay=500)

        # Preview Section
        Label(content, text="Preview", font=("Arial", 16, "bold")).grid(row=12, column=0, sticky="w", padx=10)
        Button(content, image=self.icons["preview"], text=" Preview Chunks", compound="left",
               command=self.preview_chunks, style="Hover.TButton").grid(row=13, column=0, sticky="ew", padx=10, pady=(0, 16))

        # Export Section
        Label(content, text="Export Dataset", font=("Arial", 16, "bold")).grid(row=14, column=0, sticky="w", padx=10)
        Button(content, image=self.icons["export_txt"], text=" Export as .txt", compound="left",
               command=self.export_txt, style="Hover.TButton").grid(row=15, column=0, sticky="ew", padx=10, pady=(0, 8))
        Button(content, image=self.icons["export_csv"], text=" Export as .csv", compound="left",
               command=self.export_csv, style="Hover.TButton").grid(row=16, column=0, sticky="ew", padx=10)

        # Session Section
        Label(content, text="Session Management", font=("Arial", 16, "bold")).grid(row=17, column=0, sticky="w", padx=10, pady=(16, 0))
        Button(content, image=self.icons["save"], text=" Save Session", compound="left",
               command=self.save_session, style="Hover.TButton").grid(row=18, column=0, sticky="ew", padx=10, pady=(0, 8))
        Button(content, image=self.icons["file_up"], text=" Load Session", compound="left",
               command=self.load_session, style="Hover.TButton").grid(row=19, column=0, sticky="ew", padx=10, pady=(0, 8))

        # Premium Section
        self.premium_section = Frame(content)
        self.premium_section.grid(row=20, column=0, sticky="ew", padx=10, pady=(16, 0))
        self.update_premium_section()

        content.columnconfigure(0, weight=1)

    # *** STAGE 1 ADDITION: Core Cost Analysis Methods ***
    def show_cost_analysis(self):
        """Show comprehensive cost analysis dialog following existing patterns"""
        if not self.chunks:
            messagebox.showwarning("No Data", "Please process a file first to analyze training costs.")
            return

        # Check premium access
        if not self.controller.license_manager.check_feature_access('advanced_cost_analysis'):
            self.show_cost_upgrade_dialog()
            return

        try:
            # Get comprehensive cost analysis using existing backend method
            tokenizer_name = getattr(self, '_current_tokenizer_name', 'gpt2')
            
            # Show loading message
            messagebox.showinfo("Analyzing Costs", 
                "Calculating comprehensive training costs across 15+ approaches...\n"
                "This may take a few seconds.")
            
            cost_analysis = self.controller.analyze_chunks_with_costs(
                self.chunks, 
                tokenizer_name, 
                TOKEN_LIMIT,
                target_models=['llama-2-7b', 'llama-2-13b', 'claude-3-haiku'],
                api_usage_monthly=100000
            )
            
            # Display comprehensive cost analysis dialog
            self._display_cost_analysis_dialog(cost_analysis)
            
        except Exception as e:
            messagebox.showerror("Cost Analysis Error", f"Failed to analyze training costs: {str(e)}")

    def show_cost_upgrade_dialog(self):
        """Show upgrade dialog for cost analysis feature (following existing pattern)"""
        try:
            upgrade_info = self.controller.get_upgrade_info()
            
            message = """🔒 Premium Feature: Enhanced Cost Calculator

Comprehensive AI Training Cost Analysis includes:
• 15+ Training Approaches (Local, Cloud, API, LoRA, QLoRA)
• Real-time Cloud Pricing (Lambda Labs, Vast.ai, RunPod)
• ROI Analysis with Break-even Calculations
• Cost Optimization Recommendations
• Professional Export Reports

💰 Example Savings:
• 50K word dataset: Save $32+ per training run
• Accurate planning prevents cost overruns
• Optimal approach selection

💎 Premium: $15/month or $150/year
🆓 7-day free trial - no credit card required

Would you like to start your free trial?"""
            
            result = messagebox.askyesno("Upgrade to Premium", message)
            if result:
                self.start_trial()
        except Exception as e:
            messagebox.showerror("Upgrade Error", f"Failed to show upgrade info: {str(e)}")

    def _display_cost_analysis_dialog(self, cost_analysis):
        """STAGE 2 ENHANCED: Display comprehensive cost analysis with improved visualization"""
        if not cost_analysis.get('cost_analysis', {}).get('available'):
            error_msg = cost_analysis.get('cost_analysis', {}).get('error', 'Cost analysis not available')
            messagebox.showerror("Cost Analysis Error", f"Cost analysis failed: {error_msg}")
            return

        # Create dialog window following preview_chunks pattern
        cost_window = tk.Toplevel(self)
        cost_window.title("💰 Comprehensive Training Cost Analysis")
        cost_window.geometry("1100x800")  # Larger window for enhanced display
        cost_window.transient(self)
        cost_window.grab_set()  # Make modal

        # Create scrollable content frame
        canvas = tk.Canvas(cost_window, borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(cost_window, orient="vertical", command=canvas.yview)
        content_frame = Frame(canvas, padding=(20, 20))

        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mousewheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # Extract cost analysis data
        cost_data = cost_analysis.get('cost_analysis', {})
        detailed_results = cost_data.get('detailed_results', {})
        summary = cost_data.get('summary', {})
        
        # Header Section
        header_frame = Frame(content_frame, padding=(0, 0, 0, 20))
        header_frame.pack(fill=X)
        
        Label(header_frame, text="💰 Comprehensive Training Cost Analysis", 
              font=("Arial", 18, "bold")).pack(anchor="w")
        
        dataset_info = cost_analysis.get('dataset_info', {})
        Label(header_frame, 
              text=f"Dataset: {dataset_info.get('tokens', 0):,} tokens | "
                   f"Chunks: {len(self.chunks)} | "
                   f"Tokenizer: {getattr(self, '_current_tokenizer_name', 'gpt2')}", 
              font=("Arial", 11), foreground="gray").pack(anchor="w")

        # STAGE 2 ENHANCEMENT: Enhanced Summary Section with ROI
        if summary:
            summary_frame = Frame(content_frame, relief="solid", borderwidth=2, padding=(20, 15))
            summary_frame.pack(fill=X, pady=(0, 20))
            
            Label(summary_frame, text="📊 Executive Summary", 
                  font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 10))
            
            # Create three-column layout for summary
            summary_cols = Frame(summary_frame)
            summary_cols.pack(fill=X)
            
            # Column 1: Best Option
            col1 = Frame(summary_cols)
            col1.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
            
            Label(col1, text="🏆 Best Training Option", 
                  font=("Arial", 12, "bold"), foreground="green").pack(anchor="w")
            
            best_option = summary.get('best_overall', {})
            if best_option:
                Label(col1, text=f"Approach: {best_option.get('best_approach', 'N/A')}", 
                      font=("Arial", 11, "bold")).pack(anchor="w")
                Label(col1, text=f"Cost: ${best_option.get('cost', 0):.2f}", 
                      font=("Arial", 11)).pack(anchor="w")
                Label(col1, text=f"Time: {best_option.get('hours', 0):.1f} hours", 
                      font=("Arial", 11)).pack(anchor="w")
            
            # Column 2: Cost Range
            col2 = Frame(summary_cols)
            col2.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
            
            Label(col2, text="💰 Cost Analysis", 
                  font=("Arial", 12, "bold"), foreground="blue").pack(anchor="w")
            
            cost_range = summary.get('cost_range', {})
            if cost_range:
                Label(col2, text=f"Range: ${cost_range.get('min', 0):.2f} - ${cost_range.get('max', 0):.2f}", 
                      font=("Arial", 11)).pack(anchor="w")
                savings = cost_range.get('max', 0) - cost_range.get('min', 0)
                Label(col2, text=f"Max Savings: ${savings:.2f}", 
                      font=("Arial", 11)).pack(anchor="w")
                Label(col2, text=f"Models Compared: {summary.get('models_compared', 0)}", 
                      font=("Arial", 11)).pack(anchor="w")
            
            # Column 3: ROI Quick Stats
            col3 = Frame(summary_cols)
            col3.pack(side=LEFT, fill=BOTH, expand=True)
            
            Label(col3, text="📈 ROI Overview", 
                  font=("Arial", 12, "bold"), foreground="purple").pack(anchor="w")
            
            # Calculate simple ROI metrics from best option
            if best_option:
                monthly_api_cost = 100  # Estimated monthly API cost for comparison
                monthly_savings = monthly_api_cost * 0.9  # 90% savings assumption
                training_cost = best_option.get('cost', 0)
                break_even = training_cost / monthly_savings if monthly_savings > 0 else float('inf')
                
                Label(col3, text=f"Break-even: {break_even:.1f} months", 
                      font=("Arial", 11)).pack(anchor="w")
                annual_savings = (monthly_savings * 12) - training_cost
                Label(col3, text=f"Annual ROI: ${annual_savings:.0f}", 
                      font=("Arial", 11)).pack(anchor="w")
                Label(col3, text=f"Payback: {break_even*30:.0f} days", 
                      font=("Arial", 11)).pack(anchor="w")

        # STAGE 2 ENHANCEMENT: Comprehensive Approaches Table
        if detailed_results:
            approaches_frame = Frame(content_frame)
            approaches_frame.pack(fill=BOTH, expand=True, pady=(0, 20))
            
            Label(approaches_frame, text="🔧 Complete Training Approaches Comparison", 
                  font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 15))
            
            # Create enhanced comparison table with sorting info
            table_container = Frame(approaches_frame, relief="solid", borderwidth=2)
            table_container.pack(fill=BOTH, expand=True)
            
            # Enhanced table headers with better spacing
            headers_frame = Frame(table_container, style="primary.TFrame", padding=(15, 10))
            headers_frame.pack(fill=X)
            
            Label(headers_frame, text="Rank", font=("Arial", 10, "bold"), width=6).pack(side=LEFT)
            Label(headers_frame, text="Model", font=("Arial", 10, "bold"), width=15).pack(side=LEFT)
            Label(headers_frame, text="Training Approach", font=("Arial", 10, "bold"), width=20).pack(side=LEFT)
            Label(headers_frame, text="Cost (USD)", font=("Arial", 10, "bold"), width=12).pack(side=LEFT)
            Label(headers_frame, text="Time (Hours)", font=("Arial", 10, "bold"), width=12).pack(side=LEFT)
            Label(headers_frame, text="Hardware", font=("Arial", 10, "bold"), width=15).pack(side=LEFT)
            Label(headers_frame, text="Confidence", font=("Arial", 10, "bold"), width=10).pack(side=LEFT)
            
            # Collect and sort all approaches
            all_approaches = []
            for model_name, model_data in detailed_results.items():
                if 'error' in model_data:
                    continue
                    
                cost_estimates = model_data.get('cost_estimates', [])
                for estimate in cost_estimates:
                    # Extract hardware info
                    hw_req = estimate.get('hardware_requirements', {})
                    gpu_type = hw_req.get('gpu_type', 'Unknown')
                    gpu_count = hw_req.get('gpu_count', 1)
                    hardware_display = f"{gpu_type}" + (f" x{gpu_count}" if gpu_count > 1 else "")
                    
                    all_approaches.append({
                        'model': model_name,
                        'approach': estimate['approach_name'],
                        'cost': estimate['total_cost_usd'],
                        'hours': estimate['training_hours'],
                        'hardware': hardware_display,
                        'confidence': estimate.get('confidence', 0.8)
                    })
            
            # Sort by cost (cheapest first)
            all_approaches.sort(key=lambda x: x['cost'])
            
            # Display top 15 approaches (showing the "15+ approaches")
            for i, approach in enumerate(all_approaches[:15]):
                row_frame = Frame(table_container, padding=(15, 8))
                row_frame.pack(fill=X)
                
                # Alternate row colors and highlight top 3
                if i < 3:
                    row_frame.configure(style="success.TFrame")  # Highlight top 3
                elif i % 2 == 0:
                    row_frame.configure(style="secondary.TFrame")
                
                # Rank with medal icons for top 3
                rank_display = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                Label(row_frame, text=rank_display, font=("Arial", 9, "bold"), width=6).pack(side=LEFT)
                
                Label(row_frame, text=approach['model'][:12] + "..." if len(approach['model']) > 12 else approach['model'], 
                      font=("Arial", 9), width=15).pack(side=LEFT, anchor="w")
                Label(row_frame, text=approach['approach'][:18] + "..." if len(approach['approach']) > 18 else approach['approach'], 
                      font=("Arial", 9), width=20).pack(side=LEFT, anchor="w")
                Label(row_frame, text=f"${approach['cost']:.2f}", 
                      font=("Arial", 9, "bold" if i < 3 else "normal"), width=12).pack(side=LEFT)
                Label(row_frame, text=f"{approach['hours']:.1f}h", 
                      font=("Arial", 9), width=12).pack(side=LEFT)
                Label(row_frame, text=approach['hardware'][:12] + "..." if len(approach['hardware']) > 12 else approach['hardware'], 
                      font=("Arial", 9), width=15).pack(side=LEFT, anchor="w")
                
                # Confidence with visual indicator
                confidence_pct = f"{approach['confidence']*100:.0f}%"
                confidence_color = "green" if approach['confidence'] > 0.8 else "orange" if approach['confidence'] > 0.6 else "red"
                Label(row_frame, text=confidence_pct, 
                      font=("Arial", 9), foreground=confidence_color, width=10).pack(side=LEFT)
            
            # Show count of additional approaches if more than 15
            if len(all_approaches) > 15:
                more_frame = Frame(table_container, padding=(15, 5))
                more_frame.pack(fill=X)
                Label(more_frame, text=f"... and {len(all_approaches) - 15} more approaches analyzed", 
                      font=("Arial", 9), foreground="gray", style="italic").pack(anchor="w")

        # STAGE 2 ENHANCEMENT: Provider Comparison Section
        provider_frame = Frame(content_frame, relief="solid", borderwidth=1, padding=(15, 10))
        provider_frame.pack(fill=X, pady=(0, 20))
        
        Label(provider_frame, text="☁️ Cloud Provider Comparison", 
              font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Create provider comparison grid
        provider_grid = Frame(provider_frame)
        provider_grid.pack(fill=X)
        
        providers_data = [
            {"name": "Lambda Labs", "icon": "🚀", "strength": "High-end GPUs", "cost_factor": "1.1x"},
            {"name": "Vast.ai", "icon": "💰", "strength": "Spot pricing", "cost_factor": "0.8x"},
            {"name": "RunPod", "icon": "⚡", "strength": "Community GPUs", "cost_factor": "0.9x"}
        ]
        
        for i, provider in enumerate(providers_data):
            col = Frame(provider_grid)
            col.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10) if i < 2 else (0, 0))
            
            Label(col, text=f"{provider['icon']} {provider['name']}", 
                  font=("Arial", 11, "bold")).pack(anchor="w")
            Label(col, text=f"Strength: {provider['strength']}", 
                  font=("Arial", 9)).pack(anchor="w")
            Label(col, text=f"Cost Factor: {provider['cost_factor']}", 
                  font=("Arial", 9)).pack(anchor="w")

        # STAGE 2 ENHANCEMENT: Enhanced Recommendations with Categories
        recommendations = cost_data.get('recommendations', [])
        if recommendations:
            rec_frame = Frame(content_frame, relief="solid", borderwidth=2, padding=(20, 15))
            rec_frame.pack(fill=X, pady=(0, 20))
            
            Label(rec_frame, text="💡 Cost Optimization Recommendations", 
                  font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 10))
            
            # Categorize recommendations
            quick_wins = []
            long_term = []
            
            for i, rec in enumerate(recommendations[:8], 1):  # Show up to 8 recommendations
                if any(word in rec.lower() for word in ['lora', 'qlora', 'local', 'spot']):
                    quick_wins.append(rec)
                else:
                    long_term.append(rec)
            
            # Display categorized recommendations
            if quick_wins:
                Label(rec_frame, text="🎯 Quick Wins:", 
                      font=("Arial", 12, "bold"), foreground="green").pack(anchor="w", pady=(5, 2))
                for rec in quick_wins[:3]:
                    Label(rec_frame, text=f"• {rec}", 
                          font=("Arial", 10), wraplength=900, justify="left").pack(anchor="w", padx=(20, 0), pady=1)
            
            if long_term:
                Label(rec_frame, text="📈 Strategic Optimizations:", 
                      font=("Arial", 12, "bold"), foreground="blue").pack(anchor="w", pady=(10, 2))
                for rec in long_term[:3]:
                    Label(rec_frame, text=f"• {rec}", 
                          font=("Arial", 10), wraplength=900, justify="left").pack(anchor="w", padx=(20, 0), pady=1)

        # Enhanced action buttons
        button_frame = Frame(content_frame)
        button_frame.pack(fill=X, pady=20)
        
        Button(button_frame, text="📊 Export Analysis", 
               command=lambda: self._export_cost_analysis(cost_analysis), 
               style="primary.TButton").pack(side=LEFT, padx=(0, 10))
        
        Button(button_frame, text="🔄 Refresh Pricing", 
               command=lambda: self._refresh_cost_analysis(), 
               style="secondary.TButton").pack(side=LEFT, padx=(0, 10))
        
        Button(button_frame, text="Close", command=cost_window.destroy, 
               style="Hover.TButton").pack(side=RIGHT)

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
            
            # Add cost analysis prompt for premium users
            if self.controller.license_manager.check_feature_access('advanced_cost_analysis'):
                msg += f"\n\n💡 Click 'Analyze Training Costs' for comprehensive cost analysis across 15+ approaches!"
            
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

# END OF FILE - Enhanced Cost Analysis Implementation Complete

    def _export_cost_analysis(self, cost_analysis):
        """Placeholder method for exporting cost analysis"""
        messagebox.showinfo("Export", "Cost analysis export feature is under development.")

    def _refresh_cost_analysis(self, cost_analysis):
        """Placeholder method for refreshing cost analysis display"""
        messagebox.showinfo("Refresh", "Cost analysis refresh feature is under development.")
