# ui/dialogs/__init__.py
"""
Wolfscribe UI Dialogs Package

This package contains specialized dialog components extracted from the main AppFrame
to reduce token consumption and improve maintainability.

Components:
- ChunkPreviewDialog: Advanced chunk preview with analytics
- AnalyticsDashboard: Premium analytics dashboard
- TokenizerComparisonDialog: Side-by-side tokenizer comparison
- PremiumUpgradeDialog: Premium upgrade and trial flows
- PremiumInfoDialog: Premium feature information
- TokenizerDisplayHelper: Helper utilities for tokenizer display
"""

from .preview_dialog import ChunkPreviewDialog
from .analytics_dialog import AnalyticsDashboard
from .premium_dialogs import (
    TokenizerComparisonDialog, 
    PremiumUpgradeDialog, 
    PremiumInfoDialog,
    TokenizerDisplayHelper
)

__all__ = [
    'ChunkPreviewDialog', 
    'AnalyticsDashboard', 
    'TokenizerComparisonDialog',
    'PremiumUpgradeDialog',
    'PremiumInfoDialog', 
    'TokenizerDisplayHelper'
]