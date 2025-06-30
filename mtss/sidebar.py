import re
from baseData import get_base_data
from shiny import App, render, ui, reactive
import sys
sys.path.append('/Users/carlos-ds/dev/shiny')

# Get the dataframe columns
# It's important to collect the LazyFrame to get the actual columns if get_base_data returns a LazyFrame
# However, df.columns works on LazyFrame, so it's fine for just getting column names.
df = get_base_data().to_pandas()


def organize_columns(columns):
    organized = {
        "Assessments": {},  # Change to dictionary for nested structure
        "Grades": [],
        "Student Info": []
    }

    for col in columns:
        # Try to match with testing period
        match_tp = re.match(
            r"^(?P<name>.*?)\s(?P<subject>.*?)\s(?P<year>\d{4}-\d{4})\s(?P<testing_period>.*?)\s(?P<assessment_type>PL|SS)$", col)
        # Try to match without testing period
        match_no_tp = re.match(
            r"^(?P<name>.*?)\s(?P<subject>.*?)\s(?P<year>\d{4}-\d{4})\s(?P<assessment_type>PL|SS)$", col)

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

        elif re.search(r"^(GR)", col):  # Added EL and SE for grades
            organized["Grades"].append(col)
        else:
            organized["Student Info"].append(col)
    return organized


def create_tree_checkbox(id, label, children=None, is_leaf=False, open=False):
    """Create a tree-like checkbox structure that can be nested
    Only leaf nodes will have checkboxes"""

    if children is None or is_leaf:
        # Leaf node - just a checkbox for the final level
        return ui.div(
            ui.input_checkbox(id, "", value=False),
            ui.tags.label(label, class_="tree-label", **{"for": id}),
            class_="tree-leaf"
        )
    else:
        # Branch node with children - no checkbox
        collapsible_id = f"{id}_content"

        # Create the expand/collapse header without checkbox
        header = ui.div(
            ui.tags.span(
                ui.tags.i(
                    class_=f"fas fa-{'minus' if open else 'plus'}-square tree-icon"),
                ui.tags.label(label, class_="tree-branch-label"),
                class_="tree-branch-header",
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
        } else {
            content.classList.add('collapsed');
            icon.classList.remove('fa-minus-square');
            icon.classList.add('fa-plus-square');
        }
    }
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
                    tp_label = tp if tp else "No Testing Period"

                    # Type nodes (PL/SS) under each testing period
                    type_nodes = []

                    for atype, cols in assessment_types.items():
                        # For each column, create a checkbox - these are leaf nodes
                        col_nodes = []
                        for col in cols:
                            # Sanitize ID: replace all non-alphanumeric characters with underscore
                            col_id = f"col_{''.join(c if c.isalnum() else '_' for c in col)}"
                            # Pass only column name without test name details - show just value
                            display_label = atype  # Just show PL or SS
                            col_nodes.append(create_tree_checkbox(
                                col_id, display_label, is_leaf=True))

                        # Group by assessment type (PL/SS)
                        # Sanitize all parts of the ID
                        sanitized_name = ''.join(
                            c if c.isalnum() else '_' for c in name)
                        sanitized_subject = ''.join(
                            c if c.isalnum() else '_' for c in subject)
                        sanitized_year = ''.join(
                            c if c.isalnum() else '_' for c in year)
                        sanitized_tp = ''.join(
                            c if c.isalnum() else '_' for c in tp) if tp else ''
                        type_id = f"type_{sanitized_name}_{sanitized_subject}_{sanitized_year}_{sanitized_tp}_{atype}"
                        type_nodes.append(create_tree_checkbox(
                            type_id, f"{tp_label} {atype}", col_nodes))

                    # Create testing period node with type nodes as children
                    # Sanitize all parts of the ID
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

                # Create year node with testing period nodes as children
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
            sanitized_name = ''.join(c if c.isalnum() else '_' for c in name)
            sanitized_subject = ''.join(
                c if c.isalnum() else '_' for c in subject)
            subject_id = f"subject_{sanitized_name}_{sanitized_subject}"
            subject_nodes.append(create_tree_checkbox(
                subject_id, subject, year_nodes))

        # Create assessment name node with subject nodes as children
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
        
        .tab-pane {
            flex: 1;
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
            cursor: pointer;
        }
        
        .tree-branch-header {
            display: flex;
            align-items: center;
            cursor: pointer;
            padding: 2px;
            flex-grow: 1;
            width: 100%;
        }
        
        .tree-branch-header:hover {
            background-color: #f0f0f0;
        }
        
        .tree-icon {
            margin-right: 5px;
            color: #666;
            width: 14px;
        }
        
        .tree-branch-label {
            cursor: pointer;
            margin-bottom: 0;
            font-size: 0.9rem;
            width: calc(100% - 20px);  /* Allow space for the icon */
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .tree-children {
            margin-left: 10px;
            border-left: 1px dashed #ddd;
            padding-left: 5px;
            overflow: hidden;
            max-height: 2000px;
            transition: max-height 0.3s ease-out;
        }
        
        .tree-children.collapsed {
            max-height: 0;
            transition: max-height 0.2s ease-out;
        }
        
        .tree-leaf {
            display: flex;
            align-items: center;
            padding: 1px 0;
            width: 100%;
        }
        
        .tree-label {
            margin-bottom: 0;
            margin-left: 4px;
            font-size: 0.85rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        /* Make the checkboxes more compact */
        .form-check-input {
            margin-top: 0;
            margin-left: 0;
        }
        
        /* Font sizes for different levels */
        .tree-node > .tree-branch .tree-branch-label {
            font-weight: bold;
            font-size: 0.95rem;
        }
    """),
    ui.h3("Column Selection"),
    ui.navset_card_tab(
        ui.nav_panel("Assessments", create_assessment_menu(
            organized_cols["Assessments"])),
        ui.nav_panel("Grades",
                     ui.div(
                         ui.input_checkbox_group(
                             "grades_cols", "", organized_cols["Grades"]),
                         class_="tree-children"
                     )
                     ),
        ui.nav_panel("Student Info",
                     ui.div(
                         ui.input_checkbox_group(
                             "student_info_cols", "", organized_cols["Student Info"]),
                         class_="tree-children"
                     )
                     )
    )
)
