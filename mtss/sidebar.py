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


def create_student_info_filter(columns):
    """Create filter controls for student info columns"""
    filter_items = []

    # Filter out any identifier columns like SSID, STUDENT_NAME, ID, etc.
    filtered_columns = [col for col in columns if col not in [
        'SSID', 'STUDENT_NAME'] and not 'ID' in col]

    for col in filtered_columns:
        # Get unique values for this column
        unique_values = df[col].dropna().unique().tolist()

        # Skip if there are too many unique values (likely an identifier)
        if len(unique_values) > 50:
            continue

        # Create select input for this column
        sanitized_col = ''.join(c if c.isalnum() else '_' for c in col)
        filter_id = f"filter_{sanitized_col}"

        # Create unique ID for the collapsible section
        collapse_id = f"collapse_{sanitized_col}"

        filter_items.append(
            ui.div(
                # Collapsible header
                ui.div(
                    ui.h4(col, class_="font-medium text-gray-700 mb-1"),
                    ui.tags.i(
                        class_="fas fa-chevron-down float-right toggle-filter-icon"),
                    class_="filter-header cursor-pointer",
                    onclick=f"toggleFilterSection('{collapse_id}')"
                ),
                # Collapsible content
                ui.div(
                    ui.input_selectize(
                        filter_id, "",
                        choices=[""] + sorted(unique_values),
                        selected="",
                        multiple=True
                    ),
                    class_="filter-content mt-2 mb-3",
                    id=collapse_id
                ),
                class_="filter-item mb-4 pb-2 border-b border-gray-200"
            )
        )

    return ui.div(
        *filter_items,
        class_="filter-section p-2"
    )


def create_assessment_filter(assessments_data):
    """Create filter controls for assessment data (PL only)"""
    assessment_filter_nodes = []

    for name, subjects in assessments_data.items():
        subject_filters = []

        for subject, years in subjects.items():
            year_filters = []

            for year, testing_periods in years.items():
                # For each assessment type, we'll create a filter for PL values only
                pl_columns = []

                for tp, assessment_types in testing_periods.items():
                    if "PL" in assessment_types:
                        for col in assessment_types["PL"]:
                            pl_columns.append(col)

                # If we have PL columns, create a filter for this year/subject
                if pl_columns:
                    # Get unique PL values across all columns
                    unique_pl_values = set()
                    for col in pl_columns:
                        if col in df.columns:
                            values = df[col].dropna().unique().tolist()
                            # Only add reasonable length string values
                            values = [v for v in values if isinstance(
                                v, str) and len(v) < 50]
                            unique_pl_values.update(values)

                    # Skip if there are no valid values
                    if not unique_pl_values:
                        continue

                    # Create a filter ID based on name, subject, year
                    # Sanitize ID: replace all non-alphanumeric characters with underscore
                    sanitized_name = ''.join(
                        c if c.isalnum() else '_' for c in name)
                    sanitized_subject = ''.join(
                        c if c.isalnum() else '_' for c in subject)
                    sanitized_year = ''.join(
                        c if c.isalnum() else '_' for c in year)
                    filter_id = f"filter_{sanitized_name}_{sanitized_subject}_{sanitized_year}"

                    year_filters.append(
                        ui.div(
                            # Collapsible header for year
                            ui.div(
                                ui.h4(
                                    f"{year}", class_="font-medium text-gray-700 mb-1"),
                                ui.tags.i(
                                    class_="fas fa-chevron-down float-right toggle-filter-icon"),
                                class_="filter-header cursor-pointer",
                                onclick=f"toggleFilterSection('collapse_{filter_id}')"
                            ),
                            # Collapsible content
                            ui.div(
                                ui.input_selectize(
                                    filter_id, "",
                                    choices=[""] +
                                    sorted(list(unique_pl_values)),
                                    selected="",
                                    multiple=True
                                ),
                                class_="filter-content mt-2 mb-3",
                                id=f"collapse_{filter_id}"
                            ),
                            class_="filter-item mb-3 pb-2 border-b border-gray-200"
                        )
                    )

            # If we have year filters, add them to subject filters
            if year_filters:
                # Create a unique ID for subject collapsible section
                subject_collapse_id = f"collapse_subject_{sanitized_name}_{sanitized_subject}"

                subject_filters.append(
                    ui.div(
                        # Collapsible header for subject
                        ui.div(
                            ui.h3(
                                subject, class_="font-semibold text-blue-800 mb-2"),
                            ui.tags.i(
                                class_="fas fa-chevron-down float-right toggle-filter-icon"),
                            class_="filter-header cursor-pointer",
                            onclick=f"toggleFilterSection('{subject_collapse_id}')"
                        ),
                        # Collapsible content
                        ui.div(
                            *year_filters,
                            class_="ml-3",
                            id=subject_collapse_id
                        ),
                        class_="mb-4"
                    )
                )

        # If we have subject filters, add them to assessment filters
        if subject_filters:
            # Create a unique ID for assessment collapsible section
            assessment_collapse_id = f"collapse_assessment_{sanitized_name}"

            assessment_filter_nodes.append(
                ui.div(
                    # Collapsible header for assessment
                    ui.div(
                        ui.h2(name, class_="text-lg font-bold text-blue-900 mb-2"),
                        ui.tags.i(
                            class_="fas fa-chevron-down float-right toggle-filter-icon"),
                        class_="filter-header cursor-pointer",
                        onclick=f"toggleFilterSection('{assessment_collapse_id}')"
                    ),
                    # Collapsible content
                    ui.div(
                        *subject_filters,
                        class_="ml-3",
                        id=assessment_collapse_id
                    ),
                    class_="mb-5 pb-3 border-b border-gray-300"
                )
            )

    return ui.div(
        *assessment_filter_nodes,
        class_="filter-section p-2"
    )


def create_grades_filter(grades_data):
    """Create filter controls for grades data"""
    subject_filter_nodes = []

    for subject, periods in grades_data.items():
        period_filters = []

        for period, cols in periods.items():
            # Get unique grade values
            unique_values = set()
            for col in cols:
                if col in df.columns:
                    values = df[col].dropna().unique().tolist()
                    # Only include grade-like values (short strings or numbers)
                    values = [v for v in values if (isinstance(
                        v, str) and len(v) < 5) or isinstance(v, (int, float))]
                    unique_values.update(values)

            # Skip if there are no valid values
            if not unique_values:
                continue

            # Create filter ID
            sanitized_subject = ''.join(
                c if c.isalnum() else '_' for c in subject)
            sanitized_period = ''.join(
                c if c.isalnum() else '_' for c in period)
            filter_id = f"filter_grades_{sanitized_subject}_{sanitized_period}"

            # Create unique ID for period collapsible section
            period_collapse_id = f"collapse_{filter_id}"

            period_filters.append(
                ui.div(
                    # Collapsible header for period
                    ui.div(
                        ui.h4(period, class_="font-medium text-gray-700 mb-1"),
                        ui.tags.i(
                            class_="fas fa-chevron-down float-right toggle-filter-icon"),
                        class_="filter-header cursor-pointer",
                        onclick=f"toggleFilterSection('{period_collapse_id}')"
                    ),
                    # Collapsible content
                    ui.div(
                        ui.input_selectize(
                            filter_id, "",
                            choices=[""] +
                            sorted(list(unique_values), key=str),
                            selected="",
                            multiple=True
                        ),
                        class_="filter-content mt-2 mb-3",
                        id=period_collapse_id
                    ),
                    class_="filter-item mb-3 pb-2 border-b border-gray-200"
                )
            )

        # If we have period filters, add them to subject filters
        if period_filters:
            # Create unique ID for subject collapsible section
            subject_collapse_id = f"collapse_grades_subject_{sanitized_subject}"

            subject_filter_nodes.append(
                ui.div(
                    # Collapsible header for subject
                    ui.div(
                        ui.h3(subject, class_="font-semibold text-blue-800 mb-2"),
                        ui.tags.i(
                            class_="fas fa-chevron-down float-right toggle-filter-icon"),
                        class_="filter-header cursor-pointer",
                        onclick=f"toggleFilterSection('{subject_collapse_id}')"
                    ),
                    # Collapsible content
                    ui.div(
                        *period_filters,
                        class_="ml-3",
                        id=subject_collapse_id
                    ),
                    class_="mb-4 pb-2 border-b border-gray-200"
                )
            )

    return ui.div(
        *subject_filter_nodes,
        class_="filter-section p-2"
    )


# Organize the columns
organized_cols = organize_columns(df.columns)

# Create the sidebar UI
app_sidebar = ui.sidebar(
    ui.tags.style("""
        /* Make the sidebar take up more space */
        .sidebar {
            min-width: 300px;
            width: 100%;
            max-width: 360px;
        }
        
        /* Make the Column Selection title more prominent */
        .sidebar h3 {
            font-size: 1.1rem;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
            padding-left: 8px;
            display: inline-block;
        }
        
        /* Toggle button styling */
        .toggle-button {
            float: right;
            margin-top: 0.5rem;
            margin-right: 0.5rem;
            cursor: pointer;
            color: #4b5563;
            transition: color 0.2s;
        }
        
        .toggle-button:hover {
            color: #1e40af;
        }
        
        /* Header container with flex layout */
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 8px;
            margin-bottom: 0.5rem;
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
        .assessment-tree, .filter-section {
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
        
        /* Filters section styling */
        .filter-section h2 {
            color: #1e40af;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 5px;
        }
        
        .filter-section h3 {
            color: #2563eb;
            font-size: 1.05rem;
        }
        
        .filter-section h4 {
            color: #4b5563;
            font-size: 0.95rem;
            display: inline-block;
        }
        
        /* Filter header styling */
        .filter-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 0;
            border-radius: 4px;
            transition: background-color 0.2s;
        }
        
        .filter-header:hover {
            background-color: #f3f4f6;
        }
        
        .toggle-filter-icon {
            color: #6b7280;
            transition: transform 0.2s;
        }
        
        /* Selectize styling */
        .selectize-control {
            width: 100%;
        }
        
        .selectize-dropdown-content {
            max-height: 200px;
        }
        
        .selectize-control.multi .selectize-input {
            padding: 6px 8px;
        }
        
        .selectize-control.multi .selectize-input > div {
            margin: 2px 3px;
            padding: 1px 5px;
            background: #e2e8f0;
            color: #4b5563;
            border-radius: 3px;
        }
        
        /* Column ordering styles */
        .column-order-container {
            border: 1px solid #e2e8f0;
            border-radius: 0.375rem;
            min-height: 50px;
            max-height: 300px;
            overflow-y: auto;
            background-color: #f8fafc;
        }
        
        .sortable-item {
            padding: 0.5rem;
            margin: 4px;
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            cursor: grab;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            transition: all 0.2s;
        }
        
        .sortable-item:hover {
            background-color: #f1f5f9;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .sortable-item.sortable-ghost {
            opacity: 0.5;
            background-color: #e2e8f0;
        }
        
        .sortable-item.sortable-chosen {
            background-color: #e2e8f0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .sortable-handle {
            color: #94a3b8;
            cursor: grab;
            margin-right: 8px;
        }
        
        /* Divider styling */
        .sidebar-divider {
            margin: 1rem 0;
            border-top: 1px solid #e2e8f0;
        }
    """
                  ),
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
        ui.div(
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
        ),
        id="column-order-content",
        style="display: block;"  # Make column order visible by default
    ),
    ui.tags.script("""
        // Add Sortable.js from CDN
        function loadScript(url, callback) {
            var script = document.createElement('script');
            script.type = 'text/javascript';
            script.src = url;
            script.onload = callback;
            document.head.appendChild(script);
        }
        
        loadScript('https://cdn.jsdelivr.net/npm/sortablejs@1.14.0/Sortable.min.js', function() {
            // Initialize Sortable on the column-order-list element
            var columnOrderList = document.getElementById('column-order-list');
            if (columnOrderList) {
                new Sortable(columnOrderList, {
                    animation: 150,
                    ghostClass: 'sortable-ghost',
                    chosenClass: 'sortable-chosen',
                    handle: '.sortable-handle',
                    onEnd: function(evt) {
                        // Get the current order and store it
                        storeColumnOrder();
                    }
                });
            }
        });
        
        // Handle custom messages from the server
        $(document).on('shiny:connected', function() {
            Shiny.addCustomMessageHandler('update_column_order_list', function(message) {
                if (message.action === 'update') {
                    updateColumnOrderList();
                }
            });
        });
        
        // Store the current column order
        function storeColumnOrder() {
            var columns = [];
            var items = document.querySelectorAll('#column-order-list .sortable-item');
            items.forEach(function(item) {
                columns.push(item.getAttribute('data-column'));
            });
            
            // Store the order in the hidden input field and trigger change event
            const orderInput = document.getElementById('column_order');
            orderInput.value = JSON.stringify(columns);
            
            // Dispatch change event to make sure Shiny detects the change
            const event = new Event('change', { bubbles: true });
            orderInput.dispatchEvent(event);
            
            // Add a visual indicator that the order has been saved
            const applyButton = document.getElementById('apply_order');
            if (applyButton) {
                applyButton.classList.add('bg-green-600');
                applyButton.textContent = 'Order Ready to Apply';
                
                // Reset the button after 2 seconds
                setTimeout(function() {
                    applyButton.classList.remove('bg-green-600');
                    applyButton.classList.add('bg-blue-600');
                    applyButton.textContent = 'Apply Order';
                }, 2000);
            }
        }
        
        // Update the column order list based on selected columns
        function updateColumnOrderList() {
            var columnOrderList = document.getElementById('column-order-list');
            
            // Clear existing items
            columnOrderList.innerHTML = '';
            
            // Get all selected columns
            var selectedColumns = [];
            
            // Process student info checkboxes
            const studentInfoCheckboxes = document.querySelectorAll('input[name="student_info_cols"]');
            studentInfoCheckboxes.forEach(function(checkbox) {
                if (checkbox.checked) {
                    selectedColumns.push({
                        id: 'student_info_' + checkbox.value,
                        name: checkbox.value,
                        originalName: checkbox.value
                    });
                }
            });
            
            // Process assessment and grade checkboxes
            const assessmentAndGradeCheckboxes = document.querySelectorAll('input[type="checkbox"][id^="col_"]');
            assessmentAndGradeCheckboxes.forEach(function(checkbox) {
                if (checkbox.checked) {
                    // Find the label associated with this checkbox
                    const label = checkbox.parentNode.querySelector('label');
                    const columnName = label ? label.textContent.trim() : checkbox.id.substring(4);
                    const originalName = checkbox.getAttribute('data-original-name') || checkbox.id.substring(4).replace(/_/g, ' ');
                    
                    selectedColumns.push({
                        id: checkbox.id,
                        name: columnName,
                        originalName: originalName
                    });
                }
            });
            
            // Add items to the sortable list
            selectedColumns.forEach(function(column) {
                var item = document.createElement('div');
                item.className = 'sortable-item';
                item.setAttribute('data-column', column.originalName);
                item.innerHTML = '<i class="fas fa-grip-lines sortable-handle"></i> ' + column.name;
                columnOrderList.appendChild(item);
            });
            
            // Update the stored order
            storeColumnOrder();
        }
        
        // Toggle column selection section
        function toggleColumnSelection() {
            const content = document.getElementById('column-selection-content');
            const toggleBtn = document.getElementById('toggle-column-btn');
            
            if (content.style.display === 'none') {
                content.style.display = 'block';
                toggleBtn.classList.remove('fa-eye');
                toggleBtn.classList.add('fa-eye-slash');
            } else {
                content.style.display = 'none';
                toggleBtn.classList.remove('fa-eye-slash');
                toggleBtn.classList.add('fa-eye');
            }
        }

        // Toggle filters section
        function toggleFilters() {
            const content = document.getElementById('filters-content');
            const toggleBtn = document.getElementById('toggle-filters-btn');
            
            if (content.style.display === 'none' || content.style.display === '') {
                content.style.display = 'block';
                toggleBtn.classList.remove('fa-eye');
                toggleBtn.classList.add('fa-eye-slash');
            } else {
                content.style.display = 'none';
                toggleBtn.classList.remove('fa-eye-slash');
                toggleBtn.classList.add('fa-eye');
            }
        }
        
        // Toggle column order section
        function toggleColumnOrder() {
            const content = document.getElementById('column-order-content');
            const toggleBtn = document.getElementById('toggle-order-btn');
            
            if (content.style.display === 'none' || content.style.display === '') {
                content.style.display = 'block';
                toggleBtn.classList.remove('fa-eye');
                toggleBtn.classList.add('fa-eye-slash');
                updateColumnOrderList(); // Update the list when showing
            } else {
                content.style.display = 'none';
                toggleBtn.classList.remove('fa-eye-slash');
                toggleBtn.classList.add('fa-eye');
            }
        }
        
        // Toggle filter section
        function toggleFilterSection(sectionId) {
            const section = document.getElementById(sectionId);
            const header = section.previousElementSibling;
            const icon = header.querySelector('.toggle-filter-icon');
            
            if (section.style.display === 'none' || section.style.display === '') {
                section.style.display = 'block';
                icon.classList.remove('fa-chevron-right');
                icon.classList.add('fa-chevron-down');
            } else {
                section.style.display = 'none';
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-right');
            }
        }
        
        // Initialize all filter sections as collapsed on page load
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize filter sections
            const filterContents = document.querySelectorAll('.filter-content');
            filterContents.forEach(function(content) {
                content.style.display = 'none';
                const header = content.previousElementSibling;
                const icon = header.querySelector('.toggle-filter-icon');
                if (icon) {
                    icon.classList.remove('fa-chevron-down');
                    icon.classList.add('fa-chevron-right');
                }
            });
            
            // Listen for changes in checkbox selections
            var checkboxes = document.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(function(checkbox) {
                checkbox.addEventListener('change', function() {
                    // Update the column order list when checkboxes change
                    updateColumnOrderList();
                });
            });
            
            // Initialize the column order list
            updateColumnOrderList();
        });
    """)
)
