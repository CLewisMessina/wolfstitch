# ui/dialogs/premium_dialogs.py
import tkinter as tk
from tkinter import Text, Toplevel, messagebox
from ttkbootstrap import Frame, Label, Button
from ttkbootstrap.constants import *
from typing import List, Dict, Any, Optional
import webbrowser

class TokenizerComparisonDialog:
    """Premium tokenizer comparison dialog for side-by-side analysis"""
    
    def __init__(self, parent, controller, chunks: List[str]):
        self.parent = parent
        self.controller = controller
        self.chunks = chunks
        self.window = None
        
    def show(self):
        """Display the tokenizer comparison dialog"""
        if not self.chunks:
            messagebox.showwarning("No Data", "Please process a file first.")
            return
            
        if not self.controller.license_manager.check_feature_access('advanced_analytics'):
            PremiumUpgradeDialog(self.parent, self.controller, 'advanced_analytics').show()
            return
        
        # Sample some text for comparison - avoid token length errors
        sample_text = "\n\n".join(self.chunks[:3]) if len(self.chunks) >= 3 else "\n\n".join(self.chunks)
        if len(sample_text) > 2000:  # Limit for comparison to avoid tokenization errors
            sample_text = sample_text[:2000] + "..."
        
        self.window = Toplevel(self.parent)
        self.window.title("Tokenizer Comparison")
        self.window.geometry("800x600")
        
        main_frame = Frame(self.window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Build UI sections
        self._create_header(main_frame)
        self._create_comparison_table(main_frame, sample_text)
        self._create_sample_display(main_frame, sample_text)
        self._create_close_button(main_frame)

    def _create_header(self, parent):
        """Create dialog header"""
        Label(parent, text="🔍 Tokenizer Comparison", font=("Arial", 16, "bold")).pack(pady=(0, 15))

    def _create_comparison_table(self, parent, sample_text):
        """Create the tokenizer comparison table"""
        comparison_frame = Frame(parent, relief="solid", padding=10)
        comparison_frame.pack(fill="both", expand=True)
        
        # Headers
        headers = ["Tokenizer", "Token Count", "Accuracy", "Performance", "Access"]
        for i, header in enumerate(headers):
            Label(comparison_frame, text=header, font=("Arial", 10, "bold")).grid(
                row=0, column=i, padx=5, pady=5, sticky="w"
            )
        
        # Compare all tokenizers with enhanced error handling
        available_tokenizers = self.controller.get_available_tokenizers()
        for row, tokenizer in enumerate(available_tokenizers, 1):
            # Tokenizer name
            Label(comparison_frame, text=tokenizer['display_name']).grid(
                row=row, column=0, padx=5, pady=2, sticky="w"
            )
            
            if tokenizer['has_access'] and tokenizer['available']:
                try:
                    # Use truncation logic to avoid tokenization errors
                    test_text = sample_text if len(sample_text) <= 1500 else sample_text[:1500]
                    count, metadata = self.controller.get_token_count(test_text, tokenizer['name'])
                    
                    # Adjust count if text was truncated
                    if len(sample_text) > 1500:
                        count = int(count * (len(sample_text) / 1500))
                    
                    Label(comparison_frame, text=str(count)).grid(
                        row=row, column=1, padx=5, pady=2
                    )
                    Label(comparison_frame, text=metadata.get('accuracy', 'unknown')).grid(
                        row=row, column=2, padx=5, pady=2
                    )
                    Label(comparison_frame, text=metadata.get('performance', 'unknown')).grid(
                        row=row, column=3, padx=5, pady=2
                    )
                    Label(comparison_frame, text="✅", foreground="green").grid(
                        row=row, column=4, padx=5, pady=2
                    )
                    
                except Exception as e:
                    # Fallback for tokenization errors
                    fallback_count = int(len(sample_text.split()) * 1.3)
                    Label(comparison_frame, text=f"~{fallback_count}", foreground="orange").grid(
                        row=row, column=1, padx=5, pady=2
                    )
                    Label(comparison_frame, text="estimated").grid(
                        row=row, column=2, padx=5, pady=2
                    )
                    Label(comparison_frame, text="error").grid(
                        row=row, column=3, padx=5, pady=2
                    )
                    Label(comparison_frame, text="⚠️", foreground="orange").grid(
                        row=row, column=4, padx=5, pady=2
                    )
            else:
                Label(comparison_frame, text="N/A").grid(
                    row=row, column=1, padx=5, pady=2
                )
                Label(comparison_frame, text=tokenizer['accuracy']).grid(
                    row=row, column=2, padx=5, pady=2
                )
                Label(comparison_frame, text=tokenizer['performance']).grid(
                    row=row, column=3, padx=5, pady=2
                )
                access_text = "🔒" if tokenizer['is_premium'] and not tokenizer['has_access'] else "❌"
                access_color = "orange" if access_text == "🔒" else "red"
                Label(comparison_frame, text=access_text, foreground=access_color).grid(
                    row=row, column=4, padx=5, pady=2
                )

    def _create_sample_display(self, parent, sample_text):
        """Create sample text display section"""
        Label(parent, text="Sample Text Used for Comparison:", 
              font=("Arial", 10, "bold")).pack(anchor="w", pady=(15, 5))
        
        sample_display = Text(parent, height=8, wrap="word")
        sample_display.pack(fill="x", pady=(0, 15))
        sample_display.insert("1.0", sample_text)
        sample_display.config(state="disabled")

    def _create_close_button(self, parent):
        """Create close button"""
        Button(parent, text="Close", command=self.window.destroy).pack(pady=(10, 0))


class PremiumUpgradeDialog:
    """Comprehensive premium upgrade dialog with trial and purchase options"""
    
    def __init__(self, parent, controller, feature_name: str = None):
        self.parent = parent
        self.controller = controller
        self.feature_name = feature_name
        self.window = None
        
    def show(self):
        """Display the premium upgrade dialog"""
        try:
            upgrade_info = self.controller.get_upgrade_info()
            
            self.window = Toplevel(self.parent)
            self.window.title("Premium Feature Required")
            self.window.geometry("500x400")
            self.window.resizable(False, False)
            
            # Center the dialog
            self.window.transient(self.parent)
            self.window.grab_set()
            
            main_frame = Frame(self.window, padding=20)
            main_frame.pack(fill="both", expand=True)
            
            # Build UI sections
            self._create_header(main_frame)
            self._create_feature_info(main_frame)
            self._create_features_list(main_frame)
            self._create_pricing_info(main_frame, upgrade_info)
            self._create_action_buttons(main_frame, upgrade_info)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show upgrade dialog: {str(e)}")

    def _create_header(self, parent):
        """Create dialog header"""
        Label(parent, text="🔒 Premium Feature", font=("Arial", 18, "bold")).pack(pady=(0, 10))

    def _create_feature_info(self, parent):
        """Create feature-specific information"""
        if self.feature_name:
            feature_info = f"This feature requires a premium license."
        else:
            feature_info = f"Advanced features require a premium license."
            
        Label(parent, text=feature_info, wraplength=450, justify="left").pack(pady=(0, 10))

    def _create_features_list(self, parent):
        """Create premium features list"""
        Label(parent, text="Premium Features Include:", 
              font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        features_text = ("• Exact GPT-4 and GPT-3.5 tokenization\n"
                        "• Claude tokenizer estimation\n"
                        "• BERT/RoBERTa tokenizers\n"
                        "• Advanced analytics and cost estimation\n"
                        "• Smart chunking optimization\n"
                        "• Batch processing capabilities")
        
        Label(parent, text=features_text, justify="left", wraplength=450).pack(anchor="w", pady=(0, 15))

    def _create_pricing_info(self, parent, upgrade_info):
        """Create pricing information section"""
        Label(parent, text="Pricing:", font=("Arial", 12, "bold")).pack(anchor="w")
        pricing_text = (f"Monthly: {upgrade_info['pricing']['monthly']}\n"
                       f"Yearly: {upgrade_info['pricing']['yearly']}")
        Label(parent, text=pricing_text, justify="left").pack(anchor="w", pady=(0, 15))

    def _create_action_buttons(self, parent, upgrade_info):
        """Create action buttons section"""
        button_frame = Frame(parent)
        button_frame.pack(fill="x", pady=(10, 0))
        
        if upgrade_info['trial_available']:
            trial_button = Button(button_frame, text="🆓 Start Free Trial", 
                                command=self._start_trial, 
                                style="Hover.TButton")
            trial_button.pack(side="left", padx=(0, 10))
        
        upgrade_button = Button(button_frame, text="💎 Upgrade Now", 
                              command=self._open_upgrade_url, 
                              style="Hover.TButton")
        upgrade_button.pack(side="left", padx=(0, 10))
        
        close_button = Button(button_frame, text="Close", command=self.window.destroy)
        close_button.pack(side="right")

    def _start_trial(self):
        """Start premium trial"""
        if self.controller.start_trial():
            self.window.destroy()
            messagebox.showinfo("Trial Started", 
                              "🎉 Your 7-day premium trial has started!\n"
                              "All premium features are now available.")
            # Refresh parent UI if possible
            if hasattr(self.parent, 'update_tokenizer_dropdown'):
                self.parent.update_tokenizer_dropdown()
            if hasattr(self.parent, 'update_license_status'):
                self.parent.update_license_status()
            if hasattr(self.parent, 'update_premium_section'):
                self.parent.update_premium_section()
        else:
            messagebox.showerror("Trial Error", 
                               "Failed to start trial. You may have already used your trial period.")

    def _open_upgrade_url(self):
        """Open upgrade URL in browser"""
        try:
            webbrowser.open("https://wolflow.ai/upgrade")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Browser Error", f"Could not open browser: {str(e)}")


class PremiumInfoDialog:
    """Premium features information dialog"""
    
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.window = None
        
    def show(self):
        """Display the premium info dialog"""
        try:
            upgrade_info = self.controller.get_upgrade_info()
            
            self.window = Toplevel(self.parent)
            self.window.title("Premium Features")
            self.window.geometry("600x500")
            self.window.resizable(False, False)
            
            self.window.transient(self.parent)
            self.window.grab_set()
            
            main_frame = Frame(self.window, padding=20)
            main_frame.pack(fill="both", expand=True)
            
            # Build UI sections
            self._create_title(main_frame)
            self._create_features_list(main_frame)
            self._create_pricing_section(main_frame, upgrade_info)
            self._create_action_buttons(main_frame, upgrade_info)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show upgrade information: {str(e)}")

    def _create_title(self, parent):
        """Create dialog title"""
        Label(parent, text="💎 Wolfscribe Premium", font=("Arial", 20, "bold")).pack(pady=(0, 15))

    def _create_features_list(self, parent):
        """Create detailed features list"""
        Label(parent, text="Premium Features:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
        
        features = [
            "🎯 Exact GPT-4 & GPT-3.5 Tokenization",
            "🤖 Claude & BERT Tokenizer Support", 
            "📊 Advanced Analytics & Cost Estimation",
            "⚡ Smart Chunking Optimization",
            "📁 Batch Processing Capabilities",
            "💾 Enhanced Export with Metadata"
        ]
        
        for feature in features:
            Label(parent, text=f"  {feature}", font=("Arial", 11)).pack(anchor="w", pady=1)

    def _create_pricing_section(self, parent, upgrade_info):
        """Create pricing section"""
        pricing_frame = Frame(parent, relief="solid", padding=15)
        pricing_frame.pack(fill="x", pady=(20, 15))
        
        Label(pricing_frame, text="💰 Pricing", font=("Arial", 14, "bold")).pack(anchor="w")
        Label(pricing_frame, text=f"Monthly: {upgrade_info['pricing']['monthly']}", 
              font=("Arial", 12)).pack(anchor="w")
        Label(pricing_frame, text=f"Yearly: {upgrade_info['pricing']['yearly']}", 
              font=("Arial", 12)).pack(anchor="w")

    def _create_action_buttons(self, parent, upgrade_info):
        """Create action buttons"""
        button_frame = Frame(parent)
        button_frame.pack(fill="x", pady=(10, 0))
        
        if upgrade_info['trial_available']:
            trial_button = Button(button_frame, text="🆓 Start Free Trial", 
                                command=self._start_trial, 
                                style="Hover.TButton")
            trial_button.pack(side="left", padx=(0, 10))
        
        upgrade_button = Button(button_frame, text="💎 Upgrade Now", 
                              command=self._open_upgrade_url, 
                              style="Hover.TButton")
        upgrade_button.pack(side="left", padx=(0, 10))
        
        close_button = Button(button_frame, text="Maybe Later", command=self.window.destroy)
        close_button.pack(side="right")

    def _start_trial(self):
        """Start trial from info dialog"""
        if self.controller.start_trial():
            self.window.destroy()
            messagebox.showinfo("Trial Started", 
                              "🎉 Welcome to Wolfscribe Premium!\n\n"
                              "Your 7-day trial includes:\n"
                              "• All premium tokenizers\n"
                              "• Advanced analytics\n"
                              "• Smart chunking features\n\n"
                              "Enjoy exploring the premium features!")
            # Refresh parent UI if possible
            if hasattr(self.parent, 'update_tokenizer_dropdown'):
                self.parent.update_tokenizer_dropdown()
            if hasattr(self.parent, 'update_license_status'):
                self.parent.update_license_status()
            if hasattr(self.parent, 'update_premium_section'):
                self.parent.update_premium_section()
        else:
            messagebox.showerror("Trial Error", 
                               "Trial could not be started.\n"
                               "You may have already used your trial period.")

    def _open_upgrade_url(self):
        """Open upgrade URL in browser"""
        try:
            webbrowser.open("https://wolflow.ai/upgrade")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Browser Error", f"Could not open browser: {str(e)}")


class TokenizerDisplayHelper:
    """Helper class for tokenizer display information"""
    
    @staticmethod
    def get_tokenizer_display_info(controller, tokenizer_name: str) -> Dict[str, str]:
        """Get formatted display information for a tokenizer"""
        try:
            tokenizer_info = next((t for t in controller.get_available_tokenizers() 
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