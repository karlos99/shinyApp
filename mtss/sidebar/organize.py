"""
Module for organizing data columns into logical categories and structures.
"""
import re
from baseData import get_base_data


def organize_columns(columns):
    """
    Organize columns into categories: Assessments, Grades, and Student Info.

    Args:
        columns: List of column names from the dataframe

    Returns:
        Dictionary with organized structure of columns
    """
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
