"""
Module for creating the filters section in the sidebar.
"""
from shiny import ui
from baseData import get_base_data

# Get base data
df = get_base_data().to_pandas()


def create_student_info_filter(columns):
    """
    Create filter controls for student info columns.

    Args:
        columns: List of student info column names

    Returns:
        UI element representing the student info filters
    """
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
    """
    Create filter controls for assessment data (PL only).

    Args:
        assessments_data: Dictionary with organized assessment data

    Returns:
        UI element representing the assessment filters
    """
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
    """
    Create filter controls for grades data.

    Args:
        grades_data: Dictionary with organized grades data

    Returns:
        UI element representing the grades filters
    """
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
