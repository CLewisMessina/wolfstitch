# ui/dialogs/analytics_dialog.py
import os
import json
from tkinter import filedialog, messagebox, Toplevel
from ttkbootstrap import Frame, Label, Button
from ttkbootstrap.constants import *
from datetime import datetime
from typing import Dict, Any, Optional

class AnalyticsDashboard:
    """Premium analytics dashboard for detailed tokenization insights"""
    
    def __init__(self, parent, controller, current_analysis: Dict[str, Any], file_path: str, tokenizer_name: str, chunks: list):
        self.parent = parent
        self.controller = controller
        self.current_analysis = current_analysis
        self.file_path = file_path
        self.tokenizer_name = tokenizer_name
        self.chunks = chunks
        self.window = None
        
    def show(self):
        """Display the analytics dashboard"""
        if not self.current_analysis:
            messagebox.showwarning("No Analysis", "Please process a file first to see analytics.")
            return
            
        if not self.controller.license_manager.check_feature_access('advanced_analytics'):
            self._show_premium_upgrade_dialog()
            return
            
        self.window = Toplevel(self.parent)
        self.window.title("Advanced Analytics Dashboard")
        self.window.geometry("700x800")
        
        main_frame = Frame(self.window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Build UI sections
        self._create_title(main_frame)
        self._create_overview_section(main_frame)
        self._create_token_distribution_section(main_frame)
        self._create_cost_estimation_section(main_frame)
        self._create_recommendations_section(main_frame)
        self._create_action_buttons(main_frame)

    def _create_title(self, parent):
        """Create dashboard title"""
        Label(parent, text="📊 Advanced Analytics Dashboard", 
              font=("Arial", 18, "bold")).pack(pady=(0, 20))

    def _create_overview_section(self, parent):
        """Create overview statistics section"""
        overview_frame = Frame(parent, relief="solid", padding=15)
        overview_frame.pack(fill="x", pady=(0, 15))
        
        Label(overview_frame, text="📋 Overview", font=("Arial", 14, "bold")).pack(anchor="w")
        
        overview_stats = [
            f"Dataset: {os.path.basename(self.file_path) if self.file_path else 'Unknown'}",
            f"Tokenizer: {self.tokenizer_name}",
            f"Total Chunks: {self.current_analysis['total_chunks']:,}",
            f"Total Tokens: {self.current_analysis['total_tokens']:,}",
            f"Average Tokens/Chunk: {self.current_analysis['avg_tokens']}",
            f"Token Range: {self.current_analysis['min_tokens']} - {self.current_analysis['max_tokens']}",
            f"Efficiency Score: {self.current_analysis.get('efficiency_score', 0)}%"
        ]
        
        for stat in overview_stats:
            Label(overview_frame, text=f"• {stat}", font=("Arial", 10)).pack(anchor="w", pady=1)

    def _create_token_distribution_section(self, parent):
        """Create token distribution analysis section"""
        if not self.current_analysis.get('token_distribution'):
            return
            
        dist_frame = Frame(parent, relief="solid", padding=15)
        dist_frame.pack(fill="x", pady=(0, 15))
        
        Label(dist_frame, text="📈 Token Distribution", font=("Arial", 14, "bold")).pack(anchor="w")
        
        dist = self.current_analysis['token_distribution']
        total_chunks = self.current_analysis['total_chunks']
        
        dist_stats = [
            f"Under 50 tokens: {dist['under_50']} ({dist['under_50']/total_chunks*100:.1f}%)",
            f"50-200 tokens: {dist['50_200']} ({dist['50_200']/total_chunks*100:.1f}%)",
            f"200-400 tokens: {dist['200_400']} ({dist['200_400']/total_chunks*100:.1f}%)",
            f"400-512 tokens: {dist['400_512']} ({dist['400_512']/total_chunks*100:.1f}%)",
            f"Over limit: {dist['over_limit']} ({dist['over_limit']/total_chunks*100:.1f}%)"
        ]
        
        for stat in dist_stats:
            Label(dist_frame, text=f"• {stat}", font=("Arial", 10)).pack(anchor="w", pady=1)

    def _create_cost_estimation_section(self, parent):
        """Create cost estimation section"""
        if not self.current_analysis.get('cost_estimates'):
            return
            
        cost_frame = Frame(parent, relief="solid", padding=15)
        cost_frame.pack(fill="x", pady=(0, 15))
        
        Label(cost_frame, text="💰 Cost Estimation", font=("Arial", 14, "bold")).pack(anchor="w")
        
        cost = self.current_analysis['cost_estimates']
        cost_stats = [
            f"Tokenizer: {cost['tokenizer']}",
            f"Total Tokens: {cost['total_tokens']:,}",
            f"Cost per 1K tokens: ${cost['cost_per_1k_tokens']:.4f}",
            f"Estimated API Cost: ${cost['estimated_api_cost']:.4f}",
            f"Note: {cost['note']}"
        ]
        
        for stat in cost_stats:
            Label(cost_frame, text=f"• {stat}", font=("Arial", 10)).pack(anchor="w", pady=1)

    def _create_recommendations_section(self, parent):
        """Create optimization recommendations section"""
        if not self.current_analysis.get('recommendations'):
            return
            
        rec_frame = Frame(parent, relief="solid", padding=15)
        rec_frame.pack(fill="x", pady=(0, 15))
        
        Label(rec_frame, text="💡 Optimization Recommendations", font=("Arial", 14, "bold")).pack(anchor="w")
        
        for rec in self.current_analysis['recommendations']:
            Label(rec_frame, text=f"• {rec}", wraplength=650, font=("Arial", 10)).pack(anchor="w", pady=2)

    def _create_action_buttons(self, parent):
        """Create action buttons section"""
        button_frame = Frame(parent)
        button_frame.pack(fill="x", pady=(20, 0))
        
        export_analytics_btn = Button(button_frame, text="📊 Export Analytics Report", 
                                    command=self.export_analytics_report,
                                    style="Hover.TButton")
        export_analytics_btn.pack(side="left", padx=(0, 10))
        
        close_btn = Button(button_frame, text="Close", command=self.window.destroy)
        close_btn.pack(side="right")

    def export_analytics_report(self):
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
                        'tokenizer_used': self.tokenizer_name
                    },
                    'analysis': self.current_analysis,
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
                    f.write(f"Tokenizer: {self.tokenizer_name}\n\n")
                    
                    f.write("OVERVIEW\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"Total Chunks: {self.current_analysis['total_chunks']:,}\n")
                    f.write(f"Total Tokens: {self.current_analysis['total_tokens']:,}\n")
                    f.write(f"Average Tokens: {self.current_analysis['avg_tokens']}\n")
                    f.write(f"Min/Max Tokens: {self.current_analysis['min_tokens']} / {self.current_analysis['max_tokens']}\n")
                    f.write(f"Over Limit: {self.current_analysis['over_limit']} ({self.current_analysis['over_limit_percentage']:.1f}%)\n")
                    
                    if self.current_analysis.get('efficiency_score'):
                        f.write(f"Efficiency Score: {self.current_analysis['efficiency_score']}%\n")
                    
                    if self.current_analysis.get('recommendations'):
                        f.write("\nRECOMMENDATIONS\n")
                        f.write("-" * 20 + "\n")
                        for i, rec in enumerate(self.current_analysis['recommendations'], 1):
                            f.write(f"{i}. {rec}\n")
            
            messagebox.showinfo("Report Exported", f"Analytics report saved to {path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")

    def _show_premium_upgrade_dialog(self):
        """Show premium upgrade dialog for analytics feature"""
        # This is a simplified version - will be enhanced when premium dialogs are extracted in A3
        messagebox.showinfo("Premium Required", 
                          "Advanced analytics require a premium license.\n\n"
                          "Premium features include:\n"
                          "• Detailed token distribution analysis\n"
                          "• Training cost estimation\n"
                          "• Efficiency scoring\n"
                          "• Optimization recommendations\n\n"
                          "Upgrade to access these features.")
