from shiny import App, render, ui, reactive
from baseData import get_base_data
from mtss.sidebar import app_sidebar, organized_cols, baseColumns


df = get_base_data().to_pandas()

# Define head content for external CSS and fonts
head_content = ui.tags.head(
    # Tailwind CSS from CDN
    ui.tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"
    ),
    # Google Fonts - Roboto and Poppins
    ui.tags.link(
        rel="stylesheet",
        href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Poppins:wght@400;500;600;700&display=swap"
    ),
    # Font Awesome for icons
    ui.tags.link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ),
    # Custom CSS
    ui.tags.link(
        rel="stylesheet",
        href="custom.css"
    ),
    ui.tags.style("""
        body, html {
            font-family: 'Roboto', sans-serif;
            background-color: #f9fafb;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Poppins', sans-serif;
        }
        .sidebar {
            background-color: #f8fafc;
            border-right: 1px solid #e2e8f0;
        }
        /* Enhanced table styles with horizontal scrolling */
        .data-table-container {
            overflow-x: auto;
            max-width: 100%;
            margin-bottom: 1rem;
        }
        .data-table-container table {
            min-width: 100%;
            border-collapse: collapse;
            white-space: nowrap;
            width: 100%;
        }
        .data-table-container th {
            position: sticky;
            top: 0;
            background-color: #f1f5f9;
            z-index: 10;
            padding: 0.75rem;
            font-weight: 600;
            text-align: left;
            border-bottom: 2px solid #e2e8f0;
            white-space: nowrap;
        }
        .data-table-container td {
            padding: 0.75rem;
            border-bottom: 1px solid #e2e8f0;
        }
        .data-table-container tr:hover {
            background-color: #f1f5f9;
        }
        /* Adding Bootstrap-like table styling */
        .table-responsive {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        .data-table-container table {
            border-collapse: collapse;
            margin-bottom: 1rem;
            color: #212529;
        }
        .data-table-container table th,
        .data-table-container table td {
            padding: 0.75rem;
            vertical-align: top;
            border-top: 1px solid #dee2e6;
        }
        .data-table-container table thead th {
            vertical-align: bottom;
            border-bottom: 2px solid #dee2e6;
            background-color: #f8f9fa;
        }
        .data-table-container table tbody tr:nth-of-type(odd) {
            background-color: rgba(0, 0, 0, 0.05);
        }
        .data-table-container table tbody tr:hover {
            background-color: rgba(0, 0, 0, 0.075);
        }
    """)
)

app_ui = ui.page_fluid(
    head_content,
    ui.div(
        ui.div(
            ui.tags.i(class_="fas fa-chart-bar text-blue-600 mr-2"),
            ui.h2("DATA DASHBOARD", class_="text-3xl font-bold text-gray-800"),
            class_="flex items-center mb-6 p-4 bg-white rounded-lg shadow-sm"
        ),
        ui.layout_sidebar(
            app_sidebar,
            ui.div(
                ui.div(
                    ui.h3("Selected Data",
                          class_="text-xl font-semibold text-gray-700 mb-3"),
                    ui.div(
                        ui.output_data_frame("data_table"),
                        class_="overflow-x-auto w-full table-responsive shiny-data-frame-container"
                    ),
                    class_="bg-white rounded-lg shadow-lg p-5"
                ),
                class_="data-table-container"
            ),
            sidebar_class="sidebar p-4 bg-white rounded-lg shadow-sm",
            main_class="p-4 bg-gray-50"
        ),
        class_="container mx-auto px-4"
    ),
    class_="bg-gray-50 min-h-screen py-6"
)


def server(input, output, session):
    @reactive.Calc
    def selected_columns_list():
        cols = set()

        # Add selected student info columns (these are direct checkbox group values)
        if input.student_info_cols():
            cols.update(input.student_info_cols())

        # Collect all original assessment column names
        all_assessment_original_cols = []
        for name, subjects in organized_cols["Assessments"].items():
            for subject, years in subjects.items():
                for year, testing_periods in years.items():
                    for tp, assessment_types in testing_periods.items():
                        for atype, assessment_column_names in assessment_types.items():
                            all_assessment_original_cols.extend(
                                assessment_column_names)

        # Check each original assessment column name if its corresponding checkbox is selected
        for original_col in all_assessment_original_cols:
            sanitized_id = f"col_{''.join(c if c.isalnum() else '_' for c in original_col)}"
            if sanitized_id in input and input[sanitized_id]():
                cols.add(original_col)

        # Collect all original grades column names
        all_grades_original_cols = []
        for subject, periods in organized_cols["Grades"].items():
            for period, grade_column_names in periods.items():
                all_grades_original_cols.extend(grade_column_names)

        # Check each original grade column name if its corresponding checkbox is selected
        for original_col in all_grades_original_cols:
            sanitized_id = f"col_{''.join(c if c.isalnum() else '_' for c in original_col)}"
            if sanitized_id in input and input[sanitized_id]():
                cols.add(original_col)

        return list(cols)

    @reactive.Calc
    def get_active_filters():
        """Collect all active filters from the UI"""
        filters = {
            "assessments": {},
            "grades": {},
            "student_info": {}
        }

        # Collect assessment filters
        for name, subjects in organized_cols["Assessments"].items():
            for subject, years in subjects.items():
                for year, _ in years.items():
                    # Sanitize filter ID
                    sanitized_name = ''.join(
                        c if c.isalnum() else '_' for c in name)
                    sanitized_subject = ''.join(
                        c if c.isalnum() else '_' for c in subject)
                    sanitized_year = ''.join(
                        c if c.isalnum() else '_' for c in year)
                    filter_id = f"filter_{sanitized_name}_{sanitized_subject}_{sanitized_year}"

                    if filter_id in input and input[filter_id]():
                        if name not in filters["assessments"]:
                            filters["assessments"][name] = {}
                        if subject not in filters["assessments"][name]:
                            filters["assessments"][name][subject] = {}
                        filters["assessments"][name][subject][year] = input[filter_id]()

        # Collect grades filters
        for subject, periods in organized_cols["Grades"].items():
            for period in periods.keys():
                # Sanitize filter ID
                sanitized_subject = ''.join(
                    c if c.isalnum() else '_' for c in subject)
                sanitized_period = ''.join(
                    c if c.isalnum() else '_' for c in period)
                filter_id = f"filter_grades_{sanitized_subject}_{sanitized_period}"

                if filter_id in input and input[filter_id]():
                    if subject not in filters["grades"]:
                        filters["grades"][subject] = {}
                    filters["grades"][subject][period] = input[filter_id]()

        # Collect student info filters
        for col in organized_cols["Student Info"]:
            if col not in ['SSID', 'STUDENT_NAME'] and not 'ID' in col:
                # Sanitize filter ID
                sanitized_col = ''.join(c if c.isalnum() else '_' for c in col)
                filter_id = f"filter_{sanitized_col}"

                if filter_id in input and input[filter_id]():
                    filters["student_info"][col] = input[filter_id]()

        return filters

    @output
    @render.data_frame
    def data_table():
        # Ensure all selected columns exist in the DataFrame
        valid_cols = [col for col in selected_columns_list()
                      if col in df.columns]

        # If no columns are selected, return an empty DataFrame with a message
        if not valid_cols:
            return df.head(0)

        # Get active filters
        filters = get_active_filters()

        # Start with the original dataframe
        filtered_df = df.copy()

        # Apply student info filters
        for col, values in filters["student_info"].items():
            if values and col in filtered_df.columns:
                # Filter out empty string values that might come from selectize
                valid_values = [v for v in values if v != ""]
                if valid_values:
                    filtered_df = filtered_df[filtered_df[col].isin(
                        valid_values)]

        # Apply assessment filters
        for name, subjects in filters["assessments"].items():
            for subject, years in subjects.items():
                for year, values in years.items():
                    if not values:
                        continue

                    # Filter out empty string values that might come from selectize
                    valid_values = [v for v in values if v != ""]
                    if not valid_values:
                        continue

                    # Find all PL columns for this assessment/subject/year
                    matching_columns = []
                    for col in filtered_df.columns:
                        if name in col and subject in col and year in col and "PL" in col:
                            matching_columns.append(col)

                    # Apply filter to any matching columns
                    if matching_columns:
                        # Create a condition that checks if ANY of the columns has ANY of the values
                        condition = None
                        for col in matching_columns:
                            col_condition = filtered_df[col].isin(values)
                            if condition is None:
                                condition = col_condition
                            else:
                                condition = condition | col_condition

                        if condition is not None:
                            filtered_df = filtered_df[condition]

        # Apply grades filters
        for subject, periods in filters["grades"].items():
            for period, values in periods.items():
                if not values:
                    continue

                # Filter out empty string values that might come from selectize
                valid_values = [v for v in values if v != ""]
                if not valid_values:
                    continue

                # Find matching grade columns
                matching_columns = []
                for col in filtered_df.columns:
                    if col.startswith(f"GR_{subject}_{period}"):
                        matching_columns.append(col)

                # Apply filter to any matching columns
                if matching_columns:
                    # Create a condition that checks if ANY of the columns has ANY of the values
                    condition = None
                    for col in matching_columns:
                        # Convert values to the same type as the column data
                        typed_values = []
                        for val in values:
                            try:
                                if filtered_df[col].dtype == 'int64':
                                    typed_values.append(int(val))
                                elif filtered_df[col].dtype == 'float64':
                                    typed_values.append(float(val))
                                else:
                                    typed_values.append(val)
                            except (ValueError, TypeError):
                                typed_values.append(val)

                        col_condition = filtered_df[col].isin(typed_values)
                        if condition is None:
                            condition = col_condition
                        else:
                            condition = condition | col_condition

                    if condition is not None:
                        filtered_df = filtered_df[condition]

        # Return the filtered DataFrame with selected columns
        return filtered_df[valid_cols]


app = App(app_ui, server)
