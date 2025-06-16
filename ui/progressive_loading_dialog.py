# progressive_loading_dialog.py - Progressive Loading UI Component
import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Frame, Label, Button
from ttkbootstrap.constants import *
import threading
import time
from ui.styles import MODERN_SLATE

class ProgressiveLoadingDialog:
    """
    Progressive loading dialog that matches existing loading UI style
    Shows tokenizer and premium feature loading progress
    """
    
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.loading_window = None
        self.progress_bars = {}
        self.status_labels = {}
        self.overall_progress = None
        self.is_showing = False
        self.auto_close_timer = None
        
        # Register for loading updates
        if hasattr(controller, 'register_loading_callback'):
            controller.register_loading_callback(self._on_loading_update)

    def show_progressive_loading(self, show_immediately=True):
        """
        Show progressive loading dialog
        
        Args:
            show_immediately: If True, show dialog immediately. If False, wait for loading to start.
        """
        if self.is_showing:
            return
            
        # Check if we need to show loading dialog
        loading_status = self.controller.get_loading_status()
        
        # Don't show if everything is already loaded
        if (loading_status['premium_features']['loaded'] and 
            loading_status['tokenizers']['loading_complete']):
            return
        
        if show_immediately or self._has_active_loading(loading_status):
            self._create_loading_dialog()

    def _has_active_loading(self, loading_status):
        """Check if there's any active loading happening"""
        return (loading_status['premium_features']['loading'] or 
                loading_status['tokenizers']['loading_premium_tokenizers'] > 0 or
                loading_status['tokenizers']['loading_progress_percent'] < 100)

    def _create_loading_dialog(self):
        """Create the progressive loading dialog with existing UI style"""
        if self.is_showing:
            return
            
        self.is_showing = True
        
        # Create modal dialog (matches existing _show_loading_dialog style)
        self.loading_window = tk.Toplevel(self.parent)
        self.loading_window.title("Loading Premium Features")
        self.loading_window.geometry("450x400")
        self.loading_window.transient(self.parent)
        self.loading_window.grab_set()
        self.loading_window.configure(bg=MODERN_SLATE['bg_primary'])
        
        # Center the window (matches existing style)
        self.loading_window.geometry("+%d+%d" % (
            self.loading_window.winfo_screenwidth()//2 - 225,
            self.loading_window.winfo_screenheight()//2 - 140
        ))
        
        # Create content frame with modern styling (matches existing)
        content_frame = Frame(self.loading_window, style="Card.TFrame", padding=(30, 20))
        content_frame.pack(fill=BOTH, expand=True)
        
        # Header message (matches existing style)
        header_label = Label(content_frame, 
                           text="🚀 Loading Premium Features", 
                           style="Secondary.TLabel", 
                           font=("Segoe UI", 12, "bold"),
                           justify="center")
        header_label.pack(pady=(0, 5))
        
        # Description (matches existing style)
        desc_label = Label(content_frame, 
                          text="Enhancing your experience with advanced tokenizers...", 
                          style="Secondary.TLabel", 
                          font=("Segoe UI", 9),
                          justify="center")
        desc_label.pack(pady=(0, 15))
        
        # Overall progress section
        overall_frame = Frame(content_frame, style="Modern.TFrame")
        overall_frame.pack(fill=X, pady=(0, 15))
        
        Label(overall_frame, text="Overall Progress:", 
              style="Modern.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor=W)
        
        # Overall progress bar (matches existing style)
        self.overall_progress = ttk.Progressbar(overall_frame, 
                                              mode='determinate',
                                              style="Modern.Horizontal.TProgressbar")
        self.overall_progress.pack(fill=X, pady=(5, 0))
        
        # Tokenizer loading section
        tokenizer_frame = Frame(content_frame, style="Modern.TFrame")
        tokenizer_frame.pack(fill=X, pady=(0, 10))
        
        Label(tokenizer_frame, text="🔧 Premium Tokenizers:", 
              style="Modern.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor=W)
        
        self.progress_bars['tokenizers'] = ttk.Progressbar(tokenizer_frame, 
                                                          mode='determinate',
                                                          style="Modern.Horizontal.TProgressbar")
        self.progress_bars['tokenizers'].pack(fill=X, pady=(5, 0))
        
        self.status_labels['tokenizers'] = Label(tokenizer_frame, 
                                                text="Loading exact tokenizers...", 
                                                style="Secondary.TLabel", 
                                                font=("Segoe UI", 9))
        self.status_labels['tokenizers'].pack(anchor=W, pady=(2, 0))
        
        # Premium features section
        features_frame = Frame(content_frame, style="Modern.TFrame")
        features_frame.pack(fill=X, pady=(0, 10))
        
        Label(features_frame, text="💎 Premium Features:", 
              style="Modern.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor=W)
        
        self.progress_bars['features'] = ttk.Progressbar(features_frame, 
                                                       mode='determinate',
                                                       style="Success.Horizontal.TProgressbar")
        self.progress_bars['features'].pack(fill=X, pady=(5, 0))
        
        self.status_labels['features'] = Label(features_frame, 
                                             text="Loading cost analysis...", 
                                             style="Secondary.TLabel", 
                                             font=("Segoe UI", 9))
        self.status_labels['features'].pack(anchor=W, pady=(2, 0))
        
        # Action buttons frame
        button_frame = Frame(content_frame, style="Modern.TFrame")
        button_frame.pack(fill=X, pady=(15, 0))
        
        # Continue in background button
        bg_button = Button(button_frame, 
                          text="Continue in Background", 
                          style="Modern.TButton",
                          command=self._continue_in_background)
        bg_button.pack(side=LEFT)
        
        # Status info
        info_label = Label(button_frame, 
                          text="• App is fully functional now\n• Premium features will activate automatically", 
                          style="Secondary.TLabel", 
                          font=("Segoe UI", 8),
                          justify="left")
        info_label.pack(side=RIGHT, padx=(10, 0))
        
        # Handle window close
        self.loading_window.protocol("WM_DELETE_WINDOW", self._continue_in_background)
        
        # Start periodic updates
        self._update_progress()
        
        # Auto-close after loading completes (with delay for user to see completion)
        self._schedule_auto_close_check()

    def _on_loading_update(self, component_type, component_name, status):
        """Handle loading status updates from controller"""
        if not self.is_showing or not self.loading_window:
            return
            
        try:
            # Update based on component type
            if component_type == 'tokenizer':
                self._update_tokenizer_status(component_name, status)
            elif component_type == 'premium_features':
                self._update_premium_status(component_name, status)
            
            # Update overall progress
            self._update_overall_progress()
            
        except tk.TclError:
            # Dialog might be destroyed
            self.is_showing = False

    def _update_tokenizer_status(self, tokenizer_name, status):
        """Update tokenizer loading status"""
        if 'tokenizers' not in self.status_labels:
            return
            
        status_messages = {
            'loading': f"Loading {tokenizer_name}...",
            'loaded': f"✅ {tokenizer_name} ready",
            'failed': f"⚠️ {tokenizer_name} failed"
        }
        
        message = status_messages.get(status, f"{tokenizer_name}: {status}")
        self.status_labels['tokenizers'].config(text=message)

    def _update_premium_status(self, feature_name, status):
        """Update premium features loading status"""
        if 'features' not in self.status_labels:
            return
            
        if status == 'loaded':
            self.status_labels['features'].config(text="✅ Premium features ready")
            self.progress_bars['features']['value'] = 100

    def _update_progress(self):
        """Update progress bars based on current loading status"""
        if not self.is_showing or not self.loading_window:
            return
            
        try:
            loading_status = self.controller.get_loading_status()
            
            # Update tokenizer progress
            tokenizer_progress = loading_status['tokenizers']['loading_progress_percent']
            if 'tokenizers' in self.progress_bars:
                self.progress_bars['tokenizers']['value'] = tokenizer_progress
            
            # Update premium features progress
            premium_progress = loading_status['overall_progress']['premium_features']
            if 'features' in self.progress_bars:
                self.progress_bars['features']['value'] = premium_progress
            
            # Update overall progress
            self._update_overall_progress()
            
            # Continue updating if still loading
            if self._has_active_loading(loading_status):
                self.loading_window.after(500, self._update_progress)
            else:
                # Everything loaded - show completion
                self._show_completion_state()
                
        except tk.TclError:
            # Dialog destroyed
            self.is_showing = False
        except Exception as e:
            # Any other error - continue updating
            if self.is_showing:
                self.loading_window.after(1000, self._update_progress)

    def _update_overall_progress(self):
        """Update overall progress bar"""
        if not self.overall_progress:
            return
            
        try:
            loading_status = self.controller.get_loading_status()
            
            # Calculate weighted overall progress
            tokenizer_weight = 0.6  # 60% of progress
            features_weight = 0.4   # 40% of progress
            
            tokenizer_progress = loading_status['tokenizers']['loading_progress_percent']
            features_progress = loading_status['overall_progress']['premium_features']
            
            overall = (tokenizer_progress * tokenizer_weight + 
                      features_progress * features_weight)
            
            self.overall_progress['value'] = overall
            
        except (tk.TclError, KeyError):
            pass

    def _show_completion_state(self):
        """Show completion state with success styling"""
        if not self.is_showing:
            return
            
        try:
            # Update status labels to show completion
            if 'tokenizers' in self.status_labels:
                self.status_labels['tokenizers'].config(text="✅ All tokenizers loaded successfully")
            if 'features' in self.status_labels:
                self.status_labels['features'].config(text="✅ Premium features activated")
            
            # Update progress bars to 100%
            for progress_bar in self.progress_bars.values():
                progress_bar['value'] = 100
            if self.overall_progress:
                self.overall_progress['value'] = 100
            
            # Schedule auto-close
            self.auto_close_timer = self.loading_window.after(2000, self._auto_close)
            
        except tk.TclError:
            self.is_showing = False

    def _schedule_auto_close_check(self):
        """Schedule periodic checks for auto-close"""
        if self.is_showing and self.loading_window:
            try:
                loading_status = self.controller.get_loading_status()
                if not self._has_active_loading(loading_status):
                    # Start auto-close timer
                    self.auto_close_timer = self.loading_window.after(3000, self._auto_close)
                else:
                    # Check again later
                    self.loading_window.after(2000, self._schedule_auto_close_check)
            except tk.TclError:
                self.is_showing = False

    def _auto_close(self):
        """Auto-close the dialog after loading completes"""
        self._continue_in_background()

    def _continue_in_background(self):
        """Close dialog and continue loading in background"""
        if self.auto_close_timer:
            try:
                self.loading_window.after_cancel(self.auto_close_timer)
            except:
                pass
            
        self._close_dialog()

    def _close_dialog(self):
        """Close the loading dialog safely"""
        if not self.is_showing:
            return
            
        try:
            if self.loading_window:
                self.loading_window.grab_release()
                self.loading_window.destroy()
        except tk.TclError:
            pass
        finally:
            self.is_showing = False
            self.loading_window = None

    def is_loading_active(self):
        """Check if loading dialog is currently showing"""
        return self.is_showing

    def force_show(self):
        """Force show the loading dialog regardless of status"""
        if not self.is_showing:
            self.show_progressive_loading(show_immediately=True)