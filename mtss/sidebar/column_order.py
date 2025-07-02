"""
Module for the column order UI in the sidebar.
"""
from shiny import ui


def get_column_order_ui():
    """
    Get the UI for the column order section in the sidebar.

    Returns:
        UI element representing the column order section
    """
    return ui.div(
        ui.p("Drag and drop columns to reorder them:",
             class_="text-sm text-gray-600 mb-2"),
        ui.div(
            id="column-order-list",
            class_="column-order-container"
        ),
        # Hidden input to store the column order
        ui.input_text("column_order", "", value="[]"),
        ui.tags.style("#column_order { display: none; }"),
        ui.div(
            ui.input_action_button(
                "apply_order", "Apply Order",
                class_="mt-3 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            ),
            class_="text-right mt-2"
        ),
        class_="p-2"
    )
