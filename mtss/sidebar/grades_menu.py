"""
Module for creating the grades menu in the sidebar.
"""
from shiny import ui
from baseData import get_base_data
from .components import create_tree_checkbox

# Get base data
df = get_base_data().to_pandas()
baseColumns = ['SSID', 'STUDENT_NAME', 'Grade', 'School', 'Language', 'Race']


def create_grades_menu(grades_data):
    """
    Create the grades menu tree structure for the sidebar.

    Args:
        grades_data: Dictionary with organized grades data

    Returns:
        UI element representing the grades menu
    """
    subject_nodes = []
    for subject, periods in grades_data.items():
        period_nodes = []
        for period, cols in periods.items():
            for col in cols:
                col_id = f"col_{''.join(c if c.isalnum() else '_' for c in col)}"
                is_checked = col in baseColumns
                period_nodes.append(create_tree_checkbox(
                    col_id, period, is_leaf=True, value=is_checked))

        if period_nodes:
            sanitized_subject = ''.join(
                c if c.isalnum() else '_' for c in subject)
            subject_id = f"subject_grades_{sanitized_subject}"
            subject_nodes.append(create_tree_checkbox(
                subject_id, subject, period_nodes))

    return ui.div(
        *subject_nodes,
        class_="assessment-tree"
    )
