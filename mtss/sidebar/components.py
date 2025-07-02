"""
Module for reusable UI components used in the sidebar.
"""
from shiny import ui


def create_tree_checkbox(id, label, children=None, is_leaf=False, open=False, value=False):
    """
    Create a tree-like checkbox structure that can be nested.
    Only leaf nodes will have checkboxes.

    Args:
        id: ID for the checkbox or tree node
        label: Label text to display
        children: List of child nodes (if not a leaf)
        is_leaf: Whether this is a leaf node (has a checkbox)
        open: Whether the node should be open by default
        value: Default value for the checkbox (if leaf)

    Returns:
        UI element representing a tree node
    """
    if children is None or is_leaf:
        # Leaf node - just a checkbox for the final level
        return ui.div(
            ui.div(
                ui.input_checkbox(id, "", value=value),
                ui.tags.label(
                    label, class_="tree-label text-gray-700 ml-1", **{"for": id}),
                class_="flex items-center"
            ),
            class_="tree-leaf hover:bg-gray-100 rounded py-1 px-2"
        )
    else:
        # Branch node with children - no checkbox
        collapsible_id = f"{id}_content"

        # Create the expand/collapse header without checkbox
        header = ui.div(
            ui.tags.span(
                ui.tags.i(
                    class_=f"fas fa-{'minus' if open else 'plus'}-square tree-icon text-blue-600"),
                ui.tags.label(label, class_="tree-branch-label font-medium"),
                class_="tree-branch-header hover:bg-gray-100 rounded",
                id=f"{id}_header",
                onclick=f"toggleTreeNode('{collapsible_id}', this)"
            ),
            class_="tree-branch"
        )

        # Create the container for children, initially hidden if not open
        children_container = ui.div(
            *children,
            id=collapsible_id,
            class_="tree-children" + ("" if open else " collapsed"),
        )

        # Return the branch with its children
        return ui.div(
            header,
            children_container,
            class_="tree-node"
        )
