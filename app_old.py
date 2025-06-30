# Standard library imports
import re

# Third party imports
from shiny import App, render, ui, reactive

# Local imports
from baseData import get_base_data

# --- Configuration Constants ---
assessments_prefixes = ['DIBBLES', 'ELPAC', 'CAASPP', 'IREADY']

assessment_periods = {
    'DIBBLES': ['BOY', 'MOY', 'EOY'],
    'IREADY': ['Fall', 'Winter', 'Spring']
}

assessment_subjects = {
    'DIBBLES': [
        'Composite', 'DecodingNWFWRC', 'LetterNamesLNF', 'LetterSoundsNWFCLS',
        'OralLanguage', 'PhonemicAwarenessPSF', 'RAN', 'ReadingAccuracyORFAccu',
        'ReadingComprehensionMaze', 'ReadingFluencyORF', 'WordReadingWRF'
    ],
    'IREADY': ['ELA', 'Math'],
    'ELPAC': ['Oral Language', 'Written Language', 'Overall'],
    'CAASPP': ['ELA', 'MATH']
}

score_types = ['PL', 'SS']  # Performance Level and Scale Score

grade_subject_map = {
    'E': 'English',
    'M': 'Math',
    'R': 'Reading',
    'LW': 'LanguageWriting',
    'S': 'Science',
    'SS': 'SocialStudies',
}

general_categories = {
    'Student Info': ['SSID', 'STUDENT_NAME', 'Grade', 'School'],
    'Demographics': ['Language', 'Race', 'Gender'],
    'Other': []  # Will hold any uncategorized columns
}

# Initial columns to display
initial_display_cols = ['SSID', 'STUDENT_NAME',
                        'Grade', 'School', 'Language', 'Race']

# --- Data Initialization ---
df = get_base_data()
column_names = df.columns

# Create navigation menu
nav_links = {
    "Data Explorer": "/",
    "MTSS Dashboard": "/mtss"
}

# --- Column Categorization ---
categorized_columns = {
    'Assessments': {},
    'Grades': {},
    'General': {cat: [] for cat in general_categories.keys()}
}

for col in column_names:
    is_categorized = False

    # Try to categorize as Assessment
    for prefix in assessments_prefixes:
        if col.startswith(prefix):
            assessment_name = prefix
            remaining_col_name = col[len(prefix):].strip()

            # Extract year (e.g., 2023-2024)
            year_match = re.search(r'(\d{4})(?:-(\d{4}))?', remaining_col_name)
            if year_match and year_match.group(2):
                year_formatted = f"{year_match.group(1)}-{year_match.group(2)}"
            elif year_match:
                start_year = year_match.group(1)
                year_formatted = f"{start_year}-{str(int(start_year) + 1)}"
            else:
                year_formatted = 'Unknown Year'

            # Try to find subject based on assessment type
            subject = None
            if prefix in assessment_subjects:
                for potential_subject in assessment_subjects[prefix]:
                    if potential_subject in remaining_col_name:
                        subject = potential_subject
                        break
            if not subject:
                subject = 'General'

            # Try to find period based on assessment type
            period = None
            if prefix == 'DIBBLES':
                for dibbles_period in assessment_periods['DIBBLES']:
                    if dibbles_period in remaining_col_name:
                        period = dibbles_period
                        break
            elif prefix == 'IREADY':
                for iready_period in assessment_periods['IREADY']:
                    if iready_period in remaining_col_name:
                        period = iready_period
                        break

            # Find score type (PL or SS)
            score_type = None
            for st in score_types:
                if remaining_col_name.upper().endswith(st):
                    score_type = st
                    break
            if not score_type:
                score_type = 'Score'  # Default if no specific score type found

            # Create display name
            display_name = score_type  # Just show PL, SS, or Score as the final level

            # Organize by subject -> year -> period -> score type
            if assessment_name not in categorized_columns['Assessments']:
                categorized_columns['Assessments'][assessment_name] = {}
            if subject not in categorized_columns['Assessments'][assessment_name]:
                categorized_columns['Assessments'][assessment_name][subject] = {
                }
            if year_formatted not in categorized_columns['Assessments'][assessment_name][subject]:
                categorized_columns['Assessments'][assessment_name][subject][year_formatted] = {
                }

            # Use period as category key if it exists, otherwise use 'Latest'
            category_key = period if period else 'Latest'

            if category_key not in categorized_columns['Assessments'][assessment_name][subject][year_formatted]:
                categorized_columns['Assessments'][assessment_name][subject][year_formatted][category_key] = [
                ]

            categorized_columns['Assessments'][assessment_name][subject][year_formatted][category_key].append({
                'full_name': col,
                'display_name': display_name,
                'score_type': score_type,
                'year': year_formatted,
                'period': period
            })
            is_categorized = True
            break
    if is_categorized:
        continue

    # Try to categorize as Grade
    # Columns are expected to be like 'GR_English_Q1', 'English_Q1', 'GR_Math' etc.
    # after processing by baseData.py's get_grades() function
    # Capture optional GR_, subject, and rest
    grade_match = re.match(r'^(GR_)?([A-Za-z]+)(.*)$', col)
    if grade_match:
        potential_subject_part = grade_match.group(2)
        rest_of_col = grade_match.group(3).strip('_')
        found_subject_name = None

        for original_code, subject_name in grade_subject_map.items():
            if potential_subject_part == subject_name or potential_subject_part == original_code:  # Check both full name and code
                found_subject_name = subject_name
                break

        if found_subject_name:
            if found_subject_name not in categorized_columns['Grades']:
                categorized_columns['Grades'][found_subject_name] = []

            # Create shorter display name for grades
            display_name = rest_of_col if rest_of_col else col.replace(
                f'GR_{potential_subject_part}', '').replace(potential_subject_part, '').strip('_')
            if not display_name:
                display_name = col  # Fallback

            categorized_columns['Grades'][found_subject_name].append(
                {'full_name': col, 'display_name': display_name})
            is_categorized = True

    if is_categorized:
        continue

    # If not categorized, try to add to appropriate General subcategory
    is_general_categorized = False
    for category, columns in general_categories.items():
        if col in columns:
            categorized_columns['General'][category].append(
                {'full_name': col, 'display_name': col})
            is_general_categorized = True
            break

    # If not in any predefined general category, add to Other
    if not is_general_categorized:
        categorized_columns['General']['Other'].append(
            {'full_name': col, 'display_name': col})

# --- Sorting Configuration ---
period_order = {
    'DIBBLES': {'BOY': 1, 'MOY': 2, 'EOY': 3},
    'IREADY': {'Fall': 1, 'Winter': 2, 'Spring': 3}
}


def get_period_sort_key(assessment_name, period_or_year):
    if assessment_name in period_order and period_or_year in period_order[assessment_name]:
        # Periods come first
        return (0, period_order[assessment_name][period_or_year])
    else:
        # For years, extract the first year for sorting
        year_match = re.search(r'(\d{4})', str(period_or_year))
        if year_match:
            # Years come second, negative for reverse order
            return (1, -int(year_match.group(1)))
        return (2, str(period_or_year))  # Unknown format comes last


# Sort assessments
for assessment_name, subjects_data in categorized_columns['Assessments'].items():
    for subject, years_data in subjects_data.items():
        for year, periods_data in years_data.items():
            # Sort within each period
            for period, cols_list in periods_data.items():
                cols_list.sort(key=lambda x: x['display_name'])

            # Sort periods
            categorized_columns['Assessments'][assessment_name][subject][year] = dict(
                sorted(
                    periods_data.items(),
                    key=lambda x: get_period_sort_key(assessment_name, x[0])
                )
            )

        # Sort years (most recent first)
        categorized_columns['Assessments'][assessment_name][subject] = dict(
            sorted(
                years_data.items(),
                key=lambda x: x[0],
                reverse=True
            )
        )

    # Sort subjects based on assessment-specific order
    if assessment_name in assessment_subjects:
        subject_order = {subject: idx for idx, subject in enumerate(
            assessment_subjects[assessment_name])}
        categorized_columns['Assessments'][assessment_name] = dict(
            sorted(
                subjects_data.items(),
                key=lambda x: (subject_order.get(x[0], float('inf')), x[0])
            )
        )
    else:
        categorized_columns['Assessments'][assessment_name] = dict(
            sorted(subjects_data.items()))

categorized_columns['Assessments'] = dict(
    sorted(categorized_columns['Assessments'].items()))

# Grades: Sort by quarter/term if present


def grade_sort_key(x):
    # Look for Q1, Q2, Q3, Q4 or similar patterns
    quarter_match = re.search(r'Q(\d)', x['display_name'])
    if quarter_match:
        return int(quarter_match.group(1))
    return float('inf')  # Put items without quarter at the end


for subject_name, cols_list in categorized_columns['Grades'].items():
    cols_list.sort(key=grade_sort_key)
categorized_columns['Grades'] = dict(
    sorted(categorized_columns['Grades'].items()))  # Sort subject names

# Sort general columns within each category
for category in categorized_columns['General']:
    categorized_columns['General'][category].sort(
        key=lambda x: x['display_name'])

# --- UI Definition ---
# Build Assessment Accordions (Assessment Name -> Subject -> Year -> Period -> Score Type)
assessment_name_panels = []
for assessment_name, subjects_data in categorized_columns['Assessments'].items():
    subject_panels = []
    for subject, years_data in subjects_data.items():
        if not years_data:  # Skip empty subjects
            continue

        year_panels = []
        # Sort years in reverse chronological order
        sorted_years = sorted(years_data.keys(), reverse=True)
        for year in sorted_years:
            periods_data = years_data[year]
            if not periods_data:  # Skip empty years
                continue

            period_panels = []
            for period, cols_list in periods_data.items():
                if not cols_list:  # Skip empty periods
                    continue

                # Group scores by type
                scores_by_type = {}
                for col in cols_list:
                    score_type = col['score_type']
                    if score_type not in scores_by_type:
                        scores_by_type[score_type] = []
                    scores_by_type[score_type].append(col)

                # Create panels for each score type
                score_type_items = []
                for score_type, scores in scores_by_type.items():
                    sanitized_period = period.replace(
                        '-', '_').replace(' ', '_')
                    sanitized_year = year.replace('-', '_')
                    score_type_items.append(
                        ui.input_checkbox_group(
                            f"assessments_{assessment_name.replace(' ', '_')}_{subject.replace(' ', '_')}_{sanitized_year}_{sanitized_period}_{score_type}_checkboxes",
                            f"{score_type}",  # Label the score type
                            choices={item['full_name']: item['display_name']
                                     for item in scores},
                            selected=[
                                item['full_name'] for item in scores if item['full_name'] in initial_display_cols]
                        )
                    )

                period_panels.append(
                    ui.accordion_panel(
                        period,
                        ui.div(
                            *score_type_items,
                            class_="score-types"
                        ),
                        open=False
                    )
                )

            if period_panels:  # Only add year if it has periods with data
                year_panels.append(
                    ui.accordion_panel(
                        year,  # Show the year (e.g., "2023-2024")
                        ui.accordion(
                            *period_panels,
                            open=False
                        )
                    )
                )

        if year_panels:  # Only add subject if it has years with data
            subject_panels.append(
                ui.accordion_panel(
                    f"{subject}",
                    ui.accordion(
                        *year_panels,
                        open=False
                    )
                )
            )

    if subject_panels:  # Only add assessment if it has subjects with data
        assessment_name_panels.append(
            ui.accordion_panel(
                f"{assessment_name}",
                ui.accordion(
                    *subject_panels,
                    open=False
                )
            )
        )

# Build Grades Accordions (Subject)
grades_subject_panels = []
for subject_name, cols_list in categorized_columns['Grades'].items():
    if cols_list:  # Only show subjects that have grades
        grades_subject_panels.append(
            ui.accordion_panel(
                subject_name,
                ui.input_checkbox_group(
                    f"grades_{subject_name.replace(' ', '_').replace('-', '_')}_checkboxes",
                    None,
                    choices={item['full_name']: item['display_name']
                             for item in cols_list},
                    selected=[item['full_name']
                              for item in cols_list if item['full_name'] in initial_display_cols]
                ),
                open=False
            )
        )

# Build General Accordions (Categories)
general_category_panels = []
for category, cols_list in categorized_columns['General'].items():
    if cols_list:  # Only show categories that have columns
        general_category_panels.append(
            ui.accordion_panel(
                category,
                ui.input_checkbox_group(
                    f"general_{category.lower().replace(' ', '_')}_checkboxes",
                    None,
                    choices={item['full_name']: item['display_name']
                             for item in cols_list},
                    selected=[item['full_name']
                              for item in cols_list if item['full_name'] in initial_display_cols]
                ),
                open=False  # Keep all panels closed initially
            )
        )

app_ui = ui.page_sidebar(
    ui.div(
        {"class": "nav nav-pills justify-content-end mb-3"},
        *[ui.tags.a(name, {"href": url, "class": "nav-link"}) for name, url in nav_links.items()]
    ),
    ui.h2("Student Data Explorer"),
    ui.output_data_frame("data_frame"),
    sidebar=ui.sidebar(
        ui.h4("Select Columns by Category"),
        ui.accordion(
            ui.accordion_panel(
                "General",
                ui.accordion(
                    *general_category_panels,
                    open=False  # Keep all general panels closed initially
                )
            ),
            ui.accordion_panel(
                "Assessments",
                ui.accordion(
                    *assessment_name_panels,
                    open=False
                ) if assessment_name_panels else "No assessment data available"
            ),
            ui.accordion_panel(
                "Grades",
                ui.accordion(
                    *grades_subject_panels,
                    open=False
                ) if grades_subject_panels else "No grades data available"
            ),
            id="column_categories_accordion",
            open=True  # Keep main accordion open
        ),
        ui.hr(),
        ui.h4("Selected Columns (Drag to Reorder)"),
        ui.input_selectize(
            "selected_columns",
            None,
            {col: col for col in column_names},
            multiple=True,
            selected=initial_display_cols,
            options={"plugins": ["drag_drop"]}
        )
    )
)

# --- Server Logic ---


def server(input, output, session):
    @reactive.Calc
    def get_selected_columns():
        """Get all selected columns from checkboxes in each category."""
        selected_columns = set()

        # Collect from Assessments
        for assessment_name, subjects_data in categorized_columns['Assessments'].items():
            for subject, years_data in subjects_data.items():
                for year, periods_data in years_data.items():
                    for period, cols_list in periods_data.items():
                        if not cols_list:
                            continue

                        sanitized_period = period.replace(
                            '-', '_').replace(' ', '_')
                        sanitized_year = year.replace('-', '_')

                        for col in cols_list:
                            input_id = f"assessments_{assessment_name.replace(' ', '_')}_{subject.replace(' ', '_')}_{sanitized_year}_{sanitized_period}_{col['score_type']}_checkboxes"
                            if input[input_id]():
                                selected_columns.update(input[input_id]())

        # Collect from Grades
        for subject_name, cols_list in categorized_columns['Grades'].items():
            if cols_list:
                input_id = f"grades_{subject_name.replace(' ', '_').replace('-', '_')}_checkboxes"
                if input[input_id]():
                    selected_columns.update(input[input_id]())

        # Collect from General
        for category, cols_list in categorized_columns['General'].items():
            if cols_list:
                input_id = f"general_{category.lower().replace(' ', '_')}_checkboxes"
                if input[input_id]():
                    selected_columns.update(input[input_id]())

        return list(selected_columns)

    @reactive.Effect
    def update_selectize():
        """Update selectize input when checkboxes change."""
        ui.update_selectize(
            "selected_columns",
            selected=get_selected_columns()
        )

    def get_column_groups(columns):
        """Organize columns into hierarchical groups."""
        groups = []

        for col in columns:
            # Try to identify the column type and group
            if col in general_categories['Student Info']:
                group = ('Student Info', '', '', col)
            elif col in general_categories['Demographics']:
                group = ('Demographics', '', '', col)
            # Handle assessment columns
            elif any(col.startswith(prefix) for prefix in assessments_prefixes):
                for prefix in assessments_prefixes:
                    if col.startswith(prefix):
                        # Extract components from the column name
                        remaining = col[len(prefix):].strip()

                        # Find year
                        year_match = re.search(
                            r'(\d{4})(?:-(\d{4}))?', remaining)
                        year = year_match.group(0) if year_match else ''

                        # Find subject
                        subject = 'General'
                        if prefix in assessment_subjects:
                            for potential_subject in assessment_subjects[prefix]:
                                if potential_subject in remaining:
                                    subject = potential_subject
                                    break

                        group = (prefix, subject, year, col)
                        break
            # Handle grade columns
            elif col.startswith('GR_') or any(subject in col for subject in grade_subject_map.values()):
                subject = next(
                    (subj for subj in grade_subject_map.values() if subj in col), 'Other')
                group = ('Grades', subject, '', col)
            else:
                group = ('Other', '', '', col)

            groups.append(group)

        return groups

    @render.data_frame
    def data_frame():
        """Render the data frame with organized columns."""
        selected_cols = list(input.selected_columns(
        )) if input.selected_columns() else get_selected_columns()
        if not selected_cols:
            return df.clear()

        # Get organized column groups
        column_groups = get_column_groups(selected_cols)

        # Sort groups to keep related columns together
        column_groups.sort()
        # Get original column names in sorted order
        ordered_cols = [group[3] for group in column_groups]

        # Create the multi-level column labels
        labels = {col: {
            '': col,  # Original column name
            'Category': group[0],
            'Subject': group[1] if group[1] else '',
            'Year': group[2] if group[2] else ''
        } for col, group in zip(ordered_cols, column_groups)}

        return ui.tags.div(
            {"class": "table-container"},
            render.DataGrid(
                df[ordered_cols],
                row_selection_mode="multiple",
                height="100%",
                width="100%",
                column_groups=labels
            )
        )


app = App(app_ui, server)
