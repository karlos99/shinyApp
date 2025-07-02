"""
Main module to assemble and expose the sidebar UI components.
This file re-exports all necessary components for the app.py file.
"""
from .organize import organize_columns
from .components import create_tree_checkbox
from .assessment_menu import create_assessment_menu
from .grades_menu import create_grades_menu
from .filters import (
    create_student_info_filter,
    create_assessment_filter,
    create_grades_filter
)
from .javascript import get_sidebar_javascript
from .styles import get_sidebar_styles
from .column_order import get_column_order_ui
from .main import app_sidebar, baseColumns

# Export all necessary components for app.py
__all__ = ['app_sidebar', 'organized_cols', 'baseColumns']

# Re-import and process data
from baseData import get_base_data
import re

# Get base data
df = get_base_data().to_pandas()

# Organize the columns
organized_cols = organize_columns(df.columns)
