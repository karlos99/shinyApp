"""
Main module for creating the sidebar UI.
"""
from .organize import organize_columns
from shiny import ui
from baseData import get_base_data
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

# Define base columns and get base data
baseColumns = ['SSID', 'STUDENT_NAME', 'Grade', 'School', 'Language', 'Race']
df = get_base_data().to_pandas()

# Get organized columns (will be imported from __init__)
organized_cols = organize_columns(df.columns)

# Create the sidebar UI
app_sidebar = ui.sidebar(
    ui.tags.style(get_sidebar_styles()),
    ui.div(
        ui.h3("Column Selection", class_="text-xl font-semibold text-gray-800"),
        ui.tags.i(
            class_="fas fa-eye-slash toggle-button",
            id="toggle-column-btn",
            onclick="toggleColumnSelection()"
        ),
        class_="header-container"
    ),
    ui.div(
        ui.navset_card_tab(
            ui.nav_panel("Assessments", create_assessment_menu(
                organized_cols["Assessments"])),
            ui.nav_panel("Grades", create_grades_menu(
                organized_cols["Grades"])),
            ui.nav_panel("Student Info",
                         ui.div(
                             ui.input_checkbox_group(
                                 "student_info_cols", "", organized_cols["Student Info"],
                                 selected=[
                                     col for col in baseColumns if col in organized_cols["Student Info"]],
                                 inline=True
                             ),
                             class_="tree-children p-2 student-info-checkboxes"
                         )
                         )
        ),
        id="column-selection-content"
    ),
    # Divider
    ui.tags.div(class_="sidebar-divider"),
    # Filters Section
    ui.div(
        ui.h3("Filters", class_="text-xl font-semibold text-gray-800"),
        ui.tags.i(
            class_="fas fa-eye-slash toggle-button",
            id="toggle-filters-btn",
            onclick="toggleFilters()"
        ),
        class_="header-container"
    ),
    ui.div(
        ui.navset_card_tab(
            ui.nav_panel("Assessments", create_assessment_filter(
                organized_cols["Assessments"])),
            ui.nav_panel("Grades", create_grades_filter(
                organized_cols["Grades"])),
            ui.nav_panel("Student Info", create_student_info_filter(
                organized_cols["Student Info"]))
        ),
        id="filters-content",
        style="display: block;"  # Make filters visible by default
    ),
    # Divider
    ui.tags.div(class_="sidebar-divider"),
    # Column Order Section
    ui.div(
        ui.h3("Column Order", class_="text-xl font-semibold text-gray-800"),
        ui.tags.i(
            class_="fas fa-eye-slash toggle-button",
            id="toggle-order-btn",
            onclick="toggleColumnOrder()"
        ),
        class_="header-container"
    ),
    ui.div(
        get_column_order_ui(),
        id="column-order-content",
        style="display: block;"  # Make column order visible by default
    ),
    ui.tags.script(get_sidebar_javascript())
)
