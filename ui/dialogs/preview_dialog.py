# ui/dialogs/preview_dialog.py
import tkinter as tk
from tkinter import Text, Toplevel
from ttkbootstrap import Frame, Label, Button
from ttkbootstrap.constants import *
from typing import List, Dict, Any, Optional

TOKEN_LIMIT = 512

class ChunkPreviewDialog:
    """Enhanced chunk preview dialog with advanced tokenizer information and analytics"""
    
    def __init__(self, parent, chunks: List[str], controller, tokenizer_name: str = 'gpt2', current_analysis: Optional[Dict[str, Any]] = None):
        self.parent = parent
        self.chunks = chunks
        self.controller = controller
        self.tokenizer_name = tokenizer_name
        self.current_analysis = current_analysis
        self.window = None
        
    def show(self):
        """Display the preview dialog"""
        if not self.chunks:
            from tkinter import messagebox
            messagebox.showwarning("No Data", "You must process a file first.")
            return

        # Update analysis if needed
        if not self.current_analysis:
            self._update_chunk_analysis()
        
        # Create enhanced preview window
        self.window = Toplevel(self.parent)
        self.window.title("🔍 Advanced Chunk Preview")
        self.window.geometry("900x700")

        # Create main container
        main_container = Frame(self.window)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Build UI sections
        self._create_header_section(main_container)
        self._create_analytics_summary(main_container)
        self._create_compatibility_warnings(main_container)
        self._create_chunks_preview(main_container)
        self._create_action_buttons(main_container)

    def _update_chunk_analysis(self):
        """Update chunk analysis with current tokenizer"""
        if not self.chunks:
            return
        
        try:
            self.current_analysis = self.controller.analyze_chunks(self.chunks, self.tokenizer_name, TOKEN_LIMIT)
            
            # Add enhanced analysis for premium users
            if self.controller.license_manager.check_feature_access('advanced_analytics'):
                # Add tokenizer-specific recommendations
                tokenizer_info = next((t for t in self.controller.get_available_tokenizers() 
                                     if t['name'] == self.tokenizer_name), None)
                
                if tokenizer_info and self.current_analysis:
                    # Enhance recommendations based on tokenizer type
                    enhanced_recommendations = list(self.current_analysis.get('recommendations', []))
                    
                    if tokenizer_info['accuracy'] == 'estimated' and self.current_analysis['total_tokens'] > 5000:
                        enhanced_recommendations.append("Consider upgrading to exact tokenizer for large datasets")
                    
                    if tokenizer_info['performance'] == 'slow' and len(self.chunks) > 100:
                        enhanced_recommendations.append("Large dataset detected - faster tokenizer recommended")
                    
                    self.current_analysis['recommendations'] = enhanced_recommendations
                    
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Analysis Error", f"Failed to analyze chunks: {str(e)}")

    def _create_header_section(self, parent):
        """Create header section with tokenizer info"""
        header_frame = Frame(parent, relief="solid", borderwidth=1)
        header_frame.pack(fill="x", pady=(0, 15))
        
        # Title with tokenizer info
        title_frame = Frame(header_frame)
        title_frame.pack(fill="x", padx=20, pady=15)
        
        Label(title_frame, text="📊 Advanced Chunk Analysis", 
              font=("Arial", 16, "bold")).pack(anchor="w")
        
        # Tokenizer status line
        tokenizer_info = self.controller.get_available_tokenizers()
        current_tokenizer_info = next((t for t in tokenizer_info if t['name'] == self.tokenizer_name), None)
        
        if current_tokenizer_info:
            accuracy_badge = "🎯 Exact" if current_tokenizer_info['accuracy'] == 'exact' else "📊 Estimated"
            performance_badge = f"⚡ {current_tokenizer_info['performance'].title()}"
            premium_badge = "💎 Premium" if current_tokenizer_info['is_premium'] else "🆓 Free"
            
            tokenizer_status = f"Tokenizer: {current_tokenizer_info['display_name']} | {accuracy_badge} | {performance_badge} | {premium_badge}"
        else:
            tokenizer_status = f"Tokenizer: {self.tokenizer_name} | Status: Unknown"
        
        Label(title_frame, text=tokenizer_status, 
              font=("Arial", 11)).pack(anchor="w", pady=(5, 0))

    def _create_analytics_summary(self, parent):
        """Create analytics summary panel"""
        if not self.current_analysis:
            return
            
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
            ("📊 Total Chunks", f"{self.current_analysis['total_chunks']:,}"),
            ("🔢 Total Tokens", f"{self.current_analysis['total_tokens']:,}"),
            ("📏 Average Tokens", f"{self.current_analysis['avg_tokens']}"),
            ("⚠️ Over Limit", f"{self.current_analysis['over_limit']} ({self.current_analysis['over_limit_percentage']:.1f}%)")
        ]
        
        # Display basic stats in 2x2 grid
        for i, (label, value) in enumerate(basic_stats):
            row = i // 2
            col = i % 2
            
            stat_frame = Frame(stats_container, relief="solid", borderwidth=1)
            stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            Label(stat_frame, text=label, font=("Arial", 10, "bold")).pack(pady=(8, 2))
            Label(stat_frame, text=value, font=("Arial", 12)).pack(pady=(0, 8))
        
        # Configure grid weights
        stats_container.columnconfigure(0, weight=1)
        stats_container.columnconfigure(1, weight=1)
        
        # Premium stats (if available)
        if self.current_analysis.get('advanced_analytics'):
            premium_frame = Frame(analytics_frame, relief="solid", borderwidth=1)
            premium_frame.pack(fill="x", padx=20, pady=(10, 15))
            
            Label(premium_frame, text="💎 Premium Analytics", 
                  font=("Arial", 12, "bold"), foreground="blue").pack(anchor="w", padx=15, pady=(10, 5))
            
            premium_stats_text = []
            
            if 'efficiency_score' in self.current_analysis:
                premium_stats_text.append(f"🎯 Efficiency Score: {self.current_analysis['efficiency_score']}%")
            
            if self.current_analysis.get('cost_estimates'):
                cost = self.current_analysis['cost_estimates']['estimated_api_cost']
                premium_stats_text.append(f"💰 Estimated Training Cost: ${cost:.4f}")
            
            if self.current_analysis.get('token_distribution'):
                dist = self.current_analysis['token_distribution']
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

    def _create_compatibility_warnings(self, parent):
        """Create compatibility warnings section"""
        try:
            # Check for compatibility issues
            warnings = self.controller.tokenizer_manager.get_compatibility_warnings(self.tokenizer_name)
            
            if warnings or not self.controller.license_manager.check_tokenizer_access(self.tokenizer_name):
                warning_frame = Frame(parent, relief="solid", borderwidth=1)
                warning_frame.pack(fill="x", pady=(0, 15))
                
                Label(warning_frame, text="⚠️ Compatibility Notices", 
                      font=("Arial", 12, "bold"), foreground="red").pack(anchor="w", padx=15, pady=(10, 5))
                
                # Show access warnings
                if not self.controller.license_manager.check_tokenizer_access(self.tokenizer_name):
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

    def _create_chunks_preview(self, parent):
        """Create the main chunks preview section"""
        preview_frame = Frame(parent, relief="solid", borderwidth=1)
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
        
        # Use regular tkinter Text widget
        text_widget = Text(text_frame, wrap="word", font=("Consolas", 10), relief="flat", bd=0)
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add chunks with enhanced formatting
        self._populate_enhanced_chunks(text_widget)

    def _populate_enhanced_chunks(self, text_widget):
        """Populate text widget with enhanced chunk information"""
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
                count, metadata = self.controller.get_token_count(chunk_for_tokenization, self.tokenizer_name)
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

    def _create_action_buttons(self, parent):
        """Create action buttons section"""
        button_frame = Frame(parent)
        button_frame.pack(fill="x", pady=(15, 0))
        
        # Advanced analytics button (premium feature)
        if self.controller.license_manager.check_feature_access('advanced_analytics'):
            analytics_btn = Button(button_frame, text="📊 Advanced Analytics Dashboard", 
                                  command=self._show_analytics_dashboard,
                                  style="Hover.TButton")
            analytics_btn.pack(side="left", padx=(0, 10))
        else:
            upgrade_btn = Button(button_frame, text="💎 Upgrade for Advanced Analytics", 
                               command=self._show_premium_upgrade,
                               style="Hover.TButton")
            upgrade_btn.pack(side="left", padx=(0, 10))
        
        # Tokenizer comparison button (premium feature) 
        if self.controller.license_manager.check_feature_access('advanced_analytics'):
            compare_btn = Button(button_frame, text="🔍 Compare Tokenizers", 
                               command=self._show_tokenizer_comparison,
                               style="Hover.TButton")
            compare_btn.pack(side="left", padx=(0, 10))
        
        # Close button
        close_btn = Button(button_frame, text="Close", command=self.window.destroy)
        close_btn.pack(side="right")

    def _show_analytics_dashboard(self):
        """Show analytics dashboard using extracted AnalyticsDashboard"""
        from .analytics_dialog import AnalyticsDashboard
        
        analytics_dashboard = AnalyticsDashboard(
            parent=self.parent,
            controller=self.controller,
            current_analysis=self.current_analysis,
            file_path=getattr(self.parent, 'file_path', 'Unknown'),
            tokenizer_name=self.tokenizer_name,
            chunks=self.chunks
        )
        analytics_dashboard.show()

    def _show_premium_upgrade(self):
        """Show premium upgrade dialog (to be implemented)"""
        # This will be implemented when premium dialogs are extracted
        from tkinter import messagebox
        messagebox.showinfo("Premium Required", "Premium upgrade dialog will be available after next extraction.")

    def _show_tokenizer_comparison(self):
        """Show tokenizer comparison (to be implemented)"""
        # This will be implemented when premium dialogs are extracted
        from tkinter import messagebox
        messagebox.showinfo("Coming Soon", "Tokenizer comparison will be available after next extraction.")