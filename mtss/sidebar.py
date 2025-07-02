"""
Redirect module to re-export sidebar components from the sidebar package.
This maintains backward compatibility with existing code.
"""
from mtss.sidebar.main import app_sidebar, baseColumns
from mtss.sidebar import organized_cols

# Re-export all necessary components
__all__ = ['app_sidebar', 'organized_cols', 'baseColumns']
