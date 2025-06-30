from shiny import App, render, ui, reactive
from baseData import get_base_data
from mtss.sidebar import app_sidebar, organized_cols, baseColumns


df = get_base_data().to_pandas()

app_ui = ui.page_fluid(
    ui.h2("DATA DASHBOARD"),
    ui.layout_sidebar(
        app_sidebar,
        ui.output_data_frame("data_table")
    )
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
                            all_assessment_original_cols.extend(assessment_column_names)

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

    @output
    @render.data_frame
    def data_table():
        # Ensure all selected columns exist in the DataFrame
        valid_cols = [col for col in selected_columns_list() if col in df.columns]
        return df[valid_cols]


app = App(app_ui, server)