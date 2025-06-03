# ui/dialogs/__init__.py
"""
Wolfscribe UI Dialogs Package

This package contains specialized dialog components extracted from the main AppFrame
to reduce token consumption and improve maintainability.

Components:
- ChunkPreviewDialog: Advanced chunk preview with analytics
- AnalyticsDashboard: Premium analytics dashboard
- PremiumDialogs: Upgrade and trial flow dialogs (coming in A3)
"""

from .preview_dialog import ChunkPreviewDialog
from .analytics_dialog import AnalyticsDashboard

__all__ = ['ChunkPreviewDialog', 'AnalyticsDashboard']