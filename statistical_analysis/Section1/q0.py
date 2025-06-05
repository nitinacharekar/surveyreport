'''
Analyzes data for Question 0: "Which of the following most accurately reflects your job title and responsibilities?".

This script reads an Excel file containing survey responses for respondent roles,
calculates overall statistics for the roles, and performs a demographic breakdown
(e.g., by country). It uses utility functions for statistics calculation and
demographic analysis.
'''
import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path to enable imports from sibling directories
# (e.g., statistical_analysis.utils)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q0(file_path: str) -> dict:
    """
    Analyzes respondent roles data from the survey (Question 0).

    The function reads data from the specified Excel file, cleans column names,
    calculates the distribution of respondent roles, and adds a demographic
    analysis based on specified demographic columns (e.g., Country).

    Args:
        file_path (str): Absolute or relative path to the Excel file containing
                         the data for respondent roles.

    Returns:
        dict: A dictionary containing the analysis summary. This includes:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Statistics about role distribution (from `calculate_stats`).
              - 'demographic_analysis': Breakdown of responses by demographic groups
                (from `add_demographic_summary`).
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()

    # Define relevant column names present in the Excel file
    id_col = 'ID' # Assuming an ID column exists, though not directly used in aggregation here
    demo_cols = ['Country'] # Columns to be used for demographic breakdown
    role_col = 'Answers'     # Column containing the primary answer data (respondent roles)
    value_cols = [role_col] # Columns whose values will be analyzed against demographics

    # Total number of responses
    total_responses = len(df)

    # Calculate role distribution with standard descriptive statistics
    # calculate_stats is expected to return a dictionary of statistics (e.g., counts, percentages)
    role_stats = calculate_stats(df[role_col])

    summary = {
        'question_text': '0 Which of the following most accurately reflects your job title and responsibilities?',
        'total_responses': total_responses,
        'main_stats': role_stats
    }

    # Add demographic analysis (e.g., role distribution per country)
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)

    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    # It assumes the script is run from its own directory or a context where the relative path is valid.
    # Construct a path relative to this script's location for the default data file.
    default_data_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Section 1', '0 Resonpondent Roles.xlsx')
    
    # Check if the default file exists, otherwise prompt or use a placeholder
    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        # Provide a way to specify the file path if it's not found or use a dummy for testing structure
        # For now, this will raise an error if the file is missing when run directly.

    q0_summary_results = analyze_q0(default_data_file)
    print(json.dumps(q0_summary_results, indent=2))