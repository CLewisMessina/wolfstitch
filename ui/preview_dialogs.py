# ui/preview_dialogs.py - Preview & Dialog System (Stage 2)

import os
import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Frame, Label, Button
from ttkbootstrap.constants import *
from ui.styles import MODERN_SLATE

TOKEN_LIMIT = 512

class PreviewDialogs:
    """Handles all preview and dialog functionality for Wolfscribe"""
    
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        
    def preview_chunks(self, chunks):
        """Enhanced preview with modern dark styling and proper scrolling"""
        if not chunks:
            messagebox.showwarning("No Data", "You must process a file first.")
            return

        tokenizer_name = getattr(self.parent, '_current_tokenizer_name', 'gpt2')
        
        try:
            # Create preview window
            preview_window = tk.Toplevel(self.parent)
            preview_window.title("👁️ Chunk Preview")
            preview_window.geometry("900x650")
            preview_window.transient(self.parent)
            preview_window.grab_set()
            preview_window.configure(bg=MODERN_SLATE['bg_primary'])
            
            # Center the window
            preview_window.geometry("+%d+%d" % (
                preview_window.winfo_screenwidth()//2 - 450,
                preview_window.winfo_screenheight()//2 - 325
            ))
            
            # Create content frame
            content_frame = Frame(preview_window, style="Card.TFrame", padding=(20, 20))
            content_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)
            
            # Add chunk content with enhanced analysis
            content = f"📊 CHUNK PREVIEW - {len(chunks)} chunks processed\n"
            content += f"🔧 Tokenizer: {tokenizer_name}\n"
            content += f"📏 Token Limit: {TOKEN_LIMIT}\n"
            content += "=" * 70 + "\n\n"
            
            # Show first 10 chunks with detailed token analysis
            for i, chunk in enumerate(chunks[:10]):
                count, metadata = self.controller.get_token_count(chunk, tokenizer_name)
                
                # Color-coded status indicators
                if count <= TOKEN_LIMIT * 0.8:
                    status = "🟢 OPTIMAL"
                elif count <= TOKEN_LIMIT:
                    status = "🟡 GOOD"
                else:
                    status = "🔴 OVER LIMIT"
                
                efficiency = (min(count, TOKEN_LIMIT) / TOKEN_LIMIT) * 100
                
                content += f"{status} | Chunk {i+1:2d} | {count:4d} tokens | {efficiency:5.1f}% efficiency\n"
                content += f"{'─' * 70}\n"
                
                # Truncate chunk content for preview
                preview_text = chunk[:300] + "..." if len(chunk) > 300 else chunk
                content += f"{preview_text}\n\n"
            
            if len(chunks) > 10:
                content += f"{'═' * 70}\n"
                content += f"... and {len(chunks) - 10} more chunks (showing first 10)\n\n"
                
                # Add summary statistics
                if self.parent.current_analysis:
                    analysis = self.parent.current_analysis
                    content += f"📈 SUMMARY STATISTICS:\n"
                    content += f"• Total Chunks: {analysis['total_chunks']}\n"
                    content += f"• Total Tokens: {analysis['total_tokens']:,}\n"
                    content += f"• Average Tokens: {analysis['avg_tokens']:.1f}\n"
                    content += f"• Over Limit: {analysis['over_limit']} ({analysis['over_limit_percentage']:.1f}%)\n"
                    if analysis.get('efficiency_score'):
                        content += f"• Efficiency Score: {analysis['efficiency_score']}%\n"
            
            # Use Text widget with proper scrolling
            text_widget = tk.Text(content_frame, 
                                 wrap=tk.WORD, 
                                 font=("Consolas", 10),
                                 bg=MODERN_SLATE['bg_cards'],
                                 fg=MODERN_SLATE['text_primary'],
                                 insertbackground=MODERN_SLATE['accent_cyan'],
                                 selectbackground=MODERN_SLATE['accent_blue'],
                                 selectforeground="white",
                                 borderwidth=1,
                                 relief="solid",
                                 height=25)
            text_widget.pack(fill=BOTH, expand=True, pady=(0, 15))
            
            text_widget.insert("1.0", content)
            text_widget.config(state="disabled")
            
            # Add close button
            Button(content_frame, text="Close Preview", 
                   command=preview_window.destroy,
                   style="Secondary.TButton").pack()
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to show preview: {str(e)}")

    def create_premium_analytics_window(self, analysis=None):
        """Enhanced analytics with modern styling"""
        if not analysis and not self.parent.current_analysis:
            messagebox.showwarning("No Analysis", "No analysis data available.")
            return
        
        analysis = analysis or self.parent.current_analysis
        
        try:
            # Create analytics summary with modern dark theme
            summary = f"""📊 ADVANCED ANALYTICS DASHBOARD

Dataset Overview:
• Total Chunks: {analysis.get('total_chunks', 0):,}
• Total Tokens: {analysis.get('total_tokens', 0):,}
• Average Tokens: {analysis.get('avg_tokens', 0):.1f}
• Token Range: {analysis.get('min_tokens', 0)} - {analysis.get('max_tokens', 0)}
• Over Limit: {analysis.get('over_limit', 0)} chunks ({analysis.get('over_limit_percentage', 0):.1f}%)

Performance Metrics:
• Efficiency Score: {analysis.get('efficiency_score', 0)}% 
• Tokenizer: {getattr(self.parent, '_current_tokenizer_name', 'gpt2')}
• Processing Method: {self.parent.split_method.get()}"""
            
            # Add cost preview if available
            cost_preview = analysis.get('cost_preview', {})
            if cost_preview.get('available'):
                summary += f"""

💰 Cost Analysis Preview:
• Best Approach: {cost_preview.get('best_approach', 'N/A')}
• Estimated Cost: ${cost_preview.get('estimated_cost', 0):.2f}
• Training Hours: {cost_preview.get('training_hours', 0):.1f}h
• Confidence: {cost_preview.get('confidence', 'Unknown')}"""
            else:
                summary += f"""

💰 Cost Estimation:
• Estimated Range: {cost_preview.get('estimated_cost_range', 'N/A')}
• Accuracy: {cost_preview.get('accuracy', '±50%')}
• {cost_preview.get('upgrade_message', '')}"""
            
            # Add optimization recommendations
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                summary += "\n\n💡 Optimization Recommendations:\n"
                for i, rec in enumerate(recommendations[:3], 1):
                    summary += f"{i}. {rec}\n"
            
            # Enhanced token distribution (if available)
            if analysis.get('token_distribution'):
                dist = analysis['token_distribution']
                summary += f"""

📊 Token Distribution:
• Under 50 tokens: {dist.get('under_50', 0)} chunks
• 50-200 tokens: {dist.get('50_200', 0)} chunks  
• 200-400 tokens: {dist.get('200_400', 0)} chunks
• 400-{TOKEN_LIMIT} tokens: {dist.get('400_512', 0)} chunks
• Over limit: {dist.get('over_limit', 0)} chunks"""
            
            messagebox.showinfo("📊 Advanced Analytics Dashboard", summary)
            
        except Exception as e:
            messagebox.showerror("Analytics Error", f"Failed to show analytics: {str(e)}")

    def show_tokenizer_comparison(self, chunks=None):
        """Enhanced tokenizer comparison with modern presentation"""
        chunks = chunks or self.parent.chunks
        
        if not chunks:
            messagebox.showwarning("No Data", "Process a file first to compare tokenizers.")
            return
        
        try:
            available_tokenizers = self.controller.get_available_tokenizers()
            
            # Get sample text for comparison
            sample_text = chunks[0][:500] if chunks else "Sample text for comparison"
            
            comparison = "🔍 TOKENIZER PERFORMANCE COMPARISON\n\n"
            comparison += f"Sample Text: {sample_text[:100]}...\n"
            comparison += f"Text Length: {len(sample_text)} characters\n"
            comparison += "=" * 60 + "\n\n"
            
            results = []
            for tokenizer in available_tokenizers[:5]:  # Limit to 5 tokenizers
                if tokenizer['available']:
                    try:
                        count, metadata = self.controller.get_token_count(sample_text, tokenizer['name'])
                        access_icon = "✅" if tokenizer['has_access'] else "🔒"
                        premium_indicator = " (Premium)" if tokenizer['is_premium'] else " (Free)"
                        
                        results.append({
                            'name': tokenizer['display_name'],
                            'tokens': count,
                            'access': access_icon,
                            'premium': premium_indicator,
                            'accuracy': tokenizer['accuracy'],
                            'performance': tokenizer['performance']
                        })
                        
                    except Exception as e:
                        results.append({
                            'name': tokenizer['display_name'],
                            'tokens': 'Error',
                            'access': "❌",
                            'premium': "",
                            'accuracy': 'N/A',
                            'performance': 'N/A'
                        })
            
            # Sort by token count for comparison
            valid_results = [r for r in results if isinstance(r['tokens'], int)]
            error_results = [r for r in results if not isinstance(r['tokens'], int)]
            valid_results.sort(key=lambda x: x['tokens'])
            
            # Display results
            for result in valid_results + error_results:
                comparison += f"{result['access']} {result['name']}{result['premium']}\n"
                if isinstance(result['tokens'], int):
                    comparison += f"   📊 Tokens: {result['tokens']}\n"
                    comparison += f"   🎯 Accuracy: {result['accuracy']} | ⚡ Performance: {result['performance']}\n"
                else:
                    comparison += f"   ❌ Status: {result['tokens']}\n"
                comparison += "\n"
            
            comparison += "\n💡 Professional Recommendation:\n"
            comparison += "• Use exact tokenizers (GPT-4, GPT-3.5) for production datasets\n"
            comparison += "• GPT-2 suitable for development and estimation\n"
            comparison += "• BERT tokenizers best for encoder/classification models\n"
            comparison += "• Claude estimator optimized for Anthropic models"
            
            messagebox.showinfo("🔍 Tokenizer Comparison", comparison)
            
        except Exception as e:
            messagebox.showerror("Comparison Error", f"Failed to compare tokenizers: {str(e)}")

    def show_premium_upgrade_dialog(self, feature_name):
        """Enhanced premium upgrade dialog with modern presentation"""
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

    def show_upgrade_info(self):
        """Enhanced upgrade info with modern presentation"""
        try:
            upgrade_info = self.controller.get_upgrade_info()
            license_status = upgrade_info.get('current_status', 'free')
            
            if license_status == 'trial':
                days = upgrade_info.get('days_remaining', 0)
                message = f"""⏱️ PREMIUM TRIAL STATUS

You have {days} days remaining in your premium trial.

🚀 Premium Features Currently Active:
• 🎯 Exact GPT-4 & GPT-3.5 tokenization
• 💰 Comprehensive cost analysis (15+ approaches)
• 📊 ROI analysis and optimization recommendations
• ⚡ Real-time cloud pricing integration
• 📈 Advanced analytics with export capabilities
• 🛡️ Priority support

💎 Continue with Premium: $15/month or $150/year
💰 Save $30 with annual subscription!

Upgrade now to keep these powerful features after your trial expires."""
            
            elif license_status == 'active':
                message = """✅ PREMIUM LICENSE ACTIVE

Your premium license is active with full access to:

🎯 Professional Tokenization:
• Exact GPT-4 & GPT-3.5 tokenization
• Claude estimator for Anthropic models  
• BERT tokenizers for encoder models

💰 Advanced Cost Analysis:
• 15+ training approaches comparison
• Real-time cloud pricing integration
• ROI analysis with break-even calculations
• Cost optimization recommendations

📊 Premium Analytics:
• Advanced efficiency scoring
• Professional export capabilities
• Detailed token distribution analysis

Thank you for supporting Wolfscribe Premium! 🎉"""
            
            else:  # free
                premium_features = upgrade_info.get('premium_features', [])
                feature_list = "\n".join([f"• {f['description']}" for f in premium_features[:6]])
                
                message = f"""💎 UPGRADE TO WOLFSCRIBE PREMIUM

🆓 Current: Free Tier
• GPT-2 tokenization only
• Basic chunk analysis
• Limited export options

🚀 Premium Features:
{feature_list}

💰 Transparent Pricing:
• Monthly: $15/month
• Yearly: $150/year (save $30!)
• Cancel anytime

🆓 Risk-Free Trial:
• 7-day free trial
• No credit card required
• Full feature access

💡 Average User Saves $32+ per training run through optimal approach selection!"""
            
            messagebox.showinfo("💎 Premium Information", message)
            
            # Offer trial if user is on free tier
            if license_status == 'free':
                trial_result = messagebox.askyesno("Start Free Trial?", 
                    "🚀 Ready to experience Wolfscribe Premium?\n\n"
                    "Start your 7-day free trial now to access:\n"
                    "• Comprehensive cost analysis\n"
                    "• Exact tokenization for all major models\n"
                    "• Advanced analytics and optimization\n\n"
                    "No credit card required!")
                if trial_result:
                    self.start_trial()
                    
        except Exception as e:
            messagebox.showerror("Info Error", f"Failed to show upgrade info: {str(e)}")

    def start_trial(self):
        """Enhanced trial start with modern UI feedback"""
        try:
            if self.controller.start_trial():
                messagebox.showinfo("🎉 Trial Started", 
                    "Your 7-day premium trial has started!\n\n"
                    "✅ All premium features are now available:\n"
                    "• Exact GPT-4 & GPT-3.5 tokenization\n"
                    "• Comprehensive cost analysis\n"
                    "• Advanced analytics with export\n"
                    "• Priority support\n\n"
                    "Enjoy exploring Wolfscribe Premium!")
                
                # Update parent UI elements
                self.parent.update_tokenizer_dropdown()
                self.parent.update_license_status()
                self.parent.update_premium_section()
            else:
                messagebox.showwarning("Trial Unavailable", 
                    "❌ Trial is not available.\n\n"
                    "You may have already used your trial period.\n"
                    "Contact support if you believe this is an error.")
        except Exception as e:
            messagebox.showerror("Trial Error", f"Failed to start trial: {str(e)}")




