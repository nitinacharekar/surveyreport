'''
Analyzes data for Question 3: "Who holds primary responsibility for API security in your organization?".

This script reads an Excel file containing survey responses about which team or role
has primary responsibility for API security. It calculates the overall distribution
of responses and performs a demographic breakdown (e.g., by country).
It uses utility functions for statistics calculation and demographic analysis.
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

def analyze_q3(file_path: str) -> dict:
    """
    Analyzes data on primary responsibility for API security (Question 3).

    The function reads data from the specified Excel file, cleans column names,
    calculates the distribution of responses regarding who holds primary responsibility,
    and adds a demographic analysis based on specified demographic columns (e.g., Country).

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary. This includes:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Statistics about response distribution (from `calculate_stats`).
              - 'demographic_analysis': Breakdown of responses by demographic groups
                (from `add_demographic_summary`).
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()

    # Define relevant column names present in the Excel file
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    answer_col = 'Answers'   # Column containing the primary answer data
    # This is the column whose values will be analyzed and broken down by demographics
    value_cols = [answer_col]

    # Total number of responses
    total_responses = len(df)

    # Calculate responsibility distribution with standard descriptive statistics
    responsibility_stats = calculate_stats(df[answer_col])

    summary = {
        'question_text': '3 Who holds primary responsibility for API security in your organization?',
        'total_responses': total_responses,
        'main_stats': responsibility_stats # Contains counts and percentages for each answer option
    }

    # Add demographic analysis (e.g., responsibility distribution per country)
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)

    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    default_data_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Section 1', '3 Who has primary responsibility.xlsx')

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q3_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        q3_results = analyze_q3(default_data_file)
    
    print(json.dumps(q3_results, indent=2)) 