import re
from baseData import get_base_data
from shiny import App, render, ui, reactive
import sys
sys.path.append('/Users/carlos-ds/dev/shiny')

baseColumns = ['SSID', 'STUDENT_NAME', 'Grade', 'School', 'Language', 'Race']
df = get_base_data().to_pandas()


def organize_columns(columns):
    organized = {
        "Assessments": {},
        "Grades": {},
        "Student Info": []
    }

    for col in columns:
        # Try to match with testing period
        match_tp = re.match(
            r"^(?P<name>.*?)\s(?P<subject>.*?)\s(?P<year>\d{4}-\d{4})\s(?P<testing_period>.*?)\s(?P<assessment_type>PL|SS)$", col)
        # Try to match without testing period
        match_no_tp = re.match(
            r"^(?P<name>.*?)\s(?P<subject>.*?)\s(?P<year>\d{4}-\d{4})\s(?P<assessment_type>PL|SS)$", col)
        # Match grades
        match_gr = re.match(r"^GR_(?P<subject>[^_]+)_(?P<period>.+)$", col)

        if match_tp:
            data = match_tp.groupdict()
            name = data['name']
            subject = data['subject']
            year = data['year']
            testing_period = data['testing_period']
            assessment_type = data['assessment_type']

            if name not in organized["Assessments"]:
                organized["Assessments"][name] = {}
            if subject not in organized["Assessments"][name]:
                organized["Assessments"][name][subject] = {}
            if year not in organized["Assessments"][name][subject]:
                organized["Assessments"][name][subject][year] = {}
            if testing_period not in organized["Assessments"][name][subject][year]:
                organized["Assessments"][name][subject][year][testing_period] = {}
            if assessment_type not in organized["Assessments"][name][subject][year][testing_period]:
                organized["Assessments"][name][subject][year][testing_period][assessment_type] = [
                ]
            organized["Assessments"][name][subject][year][testing_period][assessment_type].append(
                col)

        elif match_no_tp:
            data = match_no_tp.groupdict()
            name = data['name']
            subject = data['subject']
            year = data['year']
            testing_period = ""  # No testing period
            assessment_type = data['assessment_type']

            if name not in organized["Assessments"]:
                organized["Assessments"][name] = {}
            if subject not in organized["Assessments"][name]:
                organized["Assessments"][name][subject] = {}
            if year not in organized["Assessments"][name][subject]:
                organized["Assessments"][name][subject][year] = {}
            if testing_period not in organized["Assessments"][name][subject][year]:
                organized["Assessments"][name][subject][year][testing_period] = {}
            if assessment_type not in organized["Assessments"][name][subject][year][testing_period]:
                organized["Assessments"][name][subject][year][testing_period][assessment_type] = [
                ]
            organized["Assessments"][name][subject][year][testing_period][assessment_type].append(
                col)

        elif match_gr:
            data = match_gr.groupdict()
            subject = data['subject']
            period = data['period']

            if subject not in organized["Grades"]:
                organized["Grades"][subject] = {}
            if period not in organized["Grades"][subject]:
                organized["Grades"][subject][period] = []
            organized["Grades"][subject][period].append(col)
        else:
            organized["Student Info"].append(col)
    return organized


def create_tree_checkbox(id, label, children=None, is_leaf=False, open=False, value=False):
    """Create a tree-like checkbox structure that can be nested
    Only leaf nodes will have checkboxes"""

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


def create_assessment_menu(assessments_data):
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


def create_grades_menu(grades_data):
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


# Organize the columns
organized_cols = organize_columns(df.columns)

# Create the sidebar UI
app_sidebar = ui.sidebar(
    ui.tags.style("""
        /* Make the sidebar take up more space */
        .sidebar {
            min-width: 270px;
            width: 100%;
            max-width: 320px;
        }
        
        /* Make the Column Selection title more prominent */
        .sidebar h3 {
            font-size: 1.1rem;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
            padding-left: 8px;
        }
        
        /* Take up full height */
        .navset-card-tab {
            height: calc(100vh - 100px);
            display: flex;
            flex-direction: column;
        }
        
        /* Make tabs fill width */
        .nav-tabs {
            width: 100%;
            display: flex;
        }
        
        .nav-tabs .nav-item {
            flex-grow: 1;
            text-align: center;
        }
        
        /* Make tab panels fill available height */
        .tab-content {
            flex: 1;
            min-height: 0;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        
        .tab-pane {n            flex: 1;
            overflow-y: auto;
            position: relative;
        }
        
        .tab-pane.active {
            display: flex;
            flex-direction: column;
        }
        
        /* Tree structure styling */
        .assessment-tree {
            padding: 8px;
            height: 100%;
            overflow-y: auto;
        }
        
        .tree-node {
            margin-bottom: 2px;
        }
        
        .tree-branch {
            display: flex;
            align-items: center;
        }
        
        .tree-branch-header {
            display: flex;
            align-items: center;
            cursor: pointer;
            padding: 6px 8px;
            flex-grow: 1;
            width: 100%;
            border-radius: 0.25rem;
            transition: background-color 0.2s;
        }
        
        .tree-branch-header:hover {
            background-color: #f0f0f0;
        }
        
        .tree-icon {
            margin-right: 8px;
            color: #4b5563;
            width: 14px;
        }
        
        .tree-branch-label {
            cursor: pointer;
            margin-bottom: 0;
            font-size: 0.95rem;
            width: calc(100% - 22px);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-family: 'Poppins', sans-serif;
            font-weight: 500;
        }
        
        .tree-children {
            margin-left: 12px;
            border-left: 1px dashed #cbd5e1;
            padding-left: 8px;
            overflow: hidden;
            max-height: 2000px;
            transition: max-height 0.3s ease-out, opacity 0.3s;
        }
        
        .tree-children.collapsed {
            max-height: 0;
            opacity: 0;
            transition: max-height 0.2s ease-out, opacity 0.2s;
        }
        
        .tree-leaf {
            display: flex;
            align-items: center;
            margin: 3px 0;
            padding: 4px 6px;
            border-radius: 0.25rem;
        }
        
        .tree-leaf:hover {
            background-color: #e2e8f0;
        }
        
        /* Make the checkboxes more appealing */
        .form-check-input {
            margin-top: 0;
            margin-left: 0;
            border-radius: 0.25rem;
            border: 1px solid #cbd5e1;
        }
        
        /* Font sizes for different levels */
        .tree-node > .tree-branch .tree-branch-label {
            font-weight: 600;
            font-size: 1rem;
            color: #1e40af;
        }
    """
                  ),
    ui.h3("Column Selection", class_="text-xl font-semibold text-gray-800 mb-3"),
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
    )
)
