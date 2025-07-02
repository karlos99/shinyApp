"""
Module for creating the assessment menu in the sidebar.
"""
from shiny import ui
from baseData import get_base_data
from .components import create_tree_checkbox

# Get base data
df = get_base_data().to_pandas()
baseColumns = ['SSID', 'STUDENT_NAME', 'Grade', 'School', 'Language', 'Race']


def create_assessment_menu(assessments_data):
    """
    Create the assessment menu tree structure for the sidebar.

    Args:
        assessments_data: Dictionary with organized assessment data

    Returns:
        UI element representing the assessment menu
    """
    # Create the JavaScript for toggling tree nodes
    js_code = """
    function toggleTreeNode(contentId, headerEl) {
        const content = document.getElementById(contentId);
        const icon = headerEl.querySelector('.tree-icon');
        
        if (content.classList.contains('collapsed')) {
            content.classList.remove('collapsed');
            icon.classList.remove('fa-plus-square');
            icon.classList.add('fa-minus-square');
            
            // Add a smooth animation
            setTimeout(function() {
                content.style.opacity = '1';
            }, 50);
        } else {
            content.style.opacity = '0';
            
            // Wait for opacity transition before collapsing
            setTimeout(function() {
                content.classList.add('collapsed');
                icon.classList.remove('fa-minus-square');
                icon.classList.add('fa-plus-square');
            }, 200);
        }
    }
    
    // Add hover effect to tree elements
    document.addEventListener('DOMContentLoaded', function() {
        const treeItems = document.querySelectorAll('.tree-branch-header, .tree-leaf');
        treeItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                this.classList.add('bg-gray-100');
            });
            item.addEventListener('mouseleave', function() {
                this.classList.remove('bg-gray-100');
            });
        });
    });
    """

    # Top-level assessment names
    assessment_nodes = []

    for name, subjects in assessments_data.items():
        # Subject-level nodes under each assessment
        subject_nodes = []

        for subject, years in subjects.items():
            # Year-level nodes under each subject
            year_nodes = []

            for year, testing_periods in years.items():
                # Testing period nodes under each year
                tp_nodes = []

                for tp, assessment_types in testing_periods.items():
                    # Check if this is ELPAC or CAASPP which have no test date
                    is_no_date_assessment = name in ["ELPAC", "CAASPP"]

                    # For assessments with no test date, don't show "No Testing Period"
                    tp_label = "" if (not tp and is_no_date_assessment) else (
                        tp if tp else "No Testing Period")

                    # For assessments with test dates, we'll only show the latest PL or SS
                    # For ELPAC and CAASPP (no test dates), we show both PL and SS
                    if is_no_date_assessment:
                        # Type nodes (PL/SS) under each testing period
                        type_nodes = []

                        for atype, cols in assessment_types.items():
                            # For each column, create a checkbox - these are leaf nodes
                            col_nodes = []
                            for col in cols:
                                # Sanitize ID: replace all non-alphanumeric characters with underscore
                                col_id = f"col_{''.join(c if c.isalnum() else '_' for c in col)}"
                                is_checked = col in baseColumns
                                # Pass only column name without test name details - show just value
                                display_label = atype  # Just show PL or SS
                                col_nodes.append(create_tree_checkbox(
                                    col_id, display_label, is_leaf=True, value=is_checked))

                            # Group by assessment type (PL/SS)
                            sanitized_name = ''.join(
                                c if c.isalnum() else '_' for c in name)
                            sanitized_subject = ''.join(
                                c if c.isalnum() else '_' for c in subject)
                            sanitized_year = ''.join(
                                c if c.isalnum() else '_' for c in year)
                            sanitized_tp = ''.join(
                                c if c.isalnum() else '_' for c in tp) if tp else ''
                            type_id = f"type_{sanitized_name}_{sanitized_subject}_{sanitized_year}_{sanitized_tp}_{atype}"

                            # If there's no testing period label, just show the assessment type (PL/SS)
                            type_label = atype if not tp_label else f"{tp_label} {atype}"
                            type_nodes.append(create_tree_checkbox(
                                type_id, type_label, col_nodes))

                        # Create testing period node with type nodes as children
                        sanitized_name = ''.join(
                            c if c.isalnum() else '_' for c in name)
                        sanitized_subject = ''.join(
                            c if c.isalnum() else '_' for c in subject)
                        sanitized_year = ''.join(
                            c if c.isalnum() else '_' for c in year)
                        sanitized_tp = ''.join(
                            c if c.isalnum() else '_' for c in tp) if tp else ''

                        # Skip creating a separate testing period level if there's only one type
                        if len(type_nodes) <= 1:
                            # Add type nodes directly to tp_nodes
                            tp_nodes.extend(type_nodes)
                        else:
                            tp_id = f"tp_{sanitized_name}_{sanitized_subject}_{sanitized_year}_{sanitized_tp}"
                            tp_nodes.append(create_tree_checkbox(
                                tp_id, tp_label, type_nodes))
                    else:
                        # For assessments with test dates, show only the latest PL and SS for each testing period
                        # Find the most recent PL and SS (if available)
                        latest_pl_col = None
                        latest_ss_col = None

                        # Get PL and SS columns if they exist
                        pl_cols = assessment_types.get("PL", [])
                        ss_cols = assessment_types.get("SS", [])

                        # Only take the first one of each type (the data is already sorted by date in baseData.py)
                        if pl_cols:
                            latest_pl_col = pl_cols[0]
                        if ss_cols:
                            latest_ss_col = ss_cols[0]

                        # Create leaf nodes for the latest PL and SS
                        leaf_nodes = []

                        if latest_pl_col:
                            col_id = f"col_{''.join(c if c.isalnum() else '_' for c in latest_pl_col)}"
                            is_checked = latest_pl_col in baseColumns
                            leaf_nodes.append(create_tree_checkbox(
                                col_id, "PL", is_leaf=True, value=is_checked))

                        if latest_ss_col:
                            col_id = f"col_{''.join(c if c.isalnum() else '_' for c in latest_ss_col)}"
                            is_checked = latest_ss_col in baseColumns
                            leaf_nodes.append(create_tree_checkbox(
                                col_id, "SS", is_leaf=True, value=is_checked))

                        # Add the testing period node with just the latest PL/SS as children
                        if leaf_nodes:
                            sanitized_name = ''.join(
                                c if c.isalnum() else '_' for c in name)
                            sanitized_subject = ''.join(
                                c if c.isalnum() else '_' for c in subject)
                            sanitized_year = ''.join(
                                c if c.isalnum() else '_' for c in year)
                            sanitized_tp = ''.join(
                                c if c.isalnum() else '_' for c in tp) if tp else ''

                            # Skip creating a separate testing period level if there's only one leaf node
                            if len(leaf_nodes) <= 1:
                                tp_nodes.extend(leaf_nodes)
                            else:
                                tp_id = f"tp_{sanitized_name}_{sanitized_subject}_{sanitized_year}_{sanitized_tp}"
                                # If there's no testing period label, just show the year
                                node_label = year if not tp_label else tp_label
                                tp_nodes.append(create_tree_checkbox(
                                    tp_id, node_label, leaf_nodes))

                # Create year node with testing period nodes as children
                if tp_nodes:
                    sanitized_name = ''.join(
                        c if c.isalnum() else '_' for c in name)
                    sanitized_subject = ''.join(
                        c if c.isalnum() else '_' for c in subject)
                    sanitized_year = ''.join(
                        c if c.isalnum() else '_' for c in year)
                    year_id = f"year_{sanitized_name}_{sanitized_subject}_{sanitized_year}"
                    year_nodes.append(create_tree_checkbox(
                        year_id, year, tp_nodes))

            # Create subject node with year nodes as children
            if year_nodes:
                sanitized_name = ''.join(
                    c if c.isalnum() else '_' for c in name)
                sanitized_subject = ''.join(
                    c if c.isalnum() else '_' for c in subject)
                subject_id = f"subject_{sanitized_name}_{sanitized_subject}"
                subject_nodes.append(create_tree_checkbox(
                    subject_id, subject, year_nodes))

        # Create assessment name node with subject nodes as children
        if subject_nodes:
            sanitized_name = ''.join(c if c.isalnum() else '_' for c in name)
            name_id = f"assessment_{sanitized_name}"
            assessment_nodes.append(
                create_tree_checkbox(name_id, name, subject_nodes))

    # Return the complete tree with JavaScript
    return ui.div(
        ui.tags.script(js_code),
        *assessment_nodes,
        class_="assessment-tree"
    )
