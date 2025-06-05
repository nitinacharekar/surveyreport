print("Script q26.py is starting...")
"""
Analyzes data for Question 26: "Select the top 3 OWASP API security risks your organization is most concerned about".

This script reads an Excel file where each row might represent a selection of a specific
OWASP API security risk by a respondent. It calculates statistics on which risks are most
selected and performs a demographic breakdown.

Note: The script identifies the column containing the risk names by its index (df.columns[5]),
which could be fragile if the Excel sheet structure changes.
"""
import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path for utility imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q26(file_path: str) -> dict:
    """
    Analyzes data on the top 3 OWASP API security risks (Question 26).

    The function reads data from the specified Excel file. It assumes one column ('Answers')
    indicates if a risk was selected (e.g., with a 1) and another column (identified by index)
    contains the name of the risk.
    It calculates the total selections, percentage selected, and statistics for the distribution
    of selected risks. Demographic analysis is also performed.

    Args:
        file_path (str): Absolute or relative path to the Excel file.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': Total rows in the input file (may not be unique respondents
                                   if data is structured one row per risk selection per respondent).
              - 'total_selected': Count of rows where 'Answers' column is 1.
              - 'percent_selected': Percentage of 'Answers' being 1.
              - 'main_stats': Contains 'risk_stats' (distribution of selected risks) and
                              'average_selected_value' (mean of the 'Answers' column).
              - 'demographic_analysis': Demographic breakdown.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()

    # Identify relevant columns
    answer_col = 'Answers'  # Column indicating selection (e.g., 1 if selected, 0 or NaN otherwise)
    # IMPORTANT: risk_col is identified by index (6th column). This is fragile.
    # Consider using a more robust method if column order might change, e.g., by name.
    try:
        risk_col = df.columns[5]
    except IndexError:
        # Handle error if the 6th column doesn't exist
        raise ValueError(f"The Excel file at {file_path} does not have at least 6 columns to identify the risk column.")

    id_col = 'ID' # Assuming an ID column exists, though not directly used in aggregation here
    demo_cols = ['Country'] # Columns for demographic breakdown
    # value_cols for demographic summary should reflect what is being analyzed.
    # Here, 'Answers' (selection status) is used, demographic breakdown will show selection rate by country.
    value_cols = [answer_col]

    # Total number of rows (might represent individual selections rather than unique respondents)
    total_responses = len(df)

    # Total selected (where 'Answers' column == 1)
    total_selected = df[answer_col].sum()
    percent_selected = (total_selected / total_responses) * 100 if total_responses else 0

    # Calculate statistics for each risk (based on rows where answer_col == 1)
    filtered_df = df[df[answer_col] == 1]
    risk_stats = calculate_stats(filtered_df[risk_col]) if not filtered_df.empty else {}

    summary = {
        'question_text': '26 Select the top 3 OWASP API security risks your organization is most concerned about',
        'total_responses': total_responses,
        'total_selected': int(total_selected),
        'percent_selected': round(percent_selected, 2),
        'main_stats': {
            'risk_stats': risk_stats, # Distribution of selected risks
            'average_selected_value': round(df[answer_col].mean(), 2) if total_responses and pd.notna(df[answer_col].mean()) else 0
        }
    }

    # Add demographic analysis (e.g., selection rate of risks per country)
    # The demographic analysis here is on the 'Answers' column, showing how selection varies by demographic.
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)

    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    default_data_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Section 4', '26 Select the top 3 OWASP API security risks your organization is most concerned about.xlsx')

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q26_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q26_results = analyze_q26(default_data_file)
        except ValueError as e:
            print(f"Error analyzing file: {e}")
            q26_results = {"error": str(e)}
    
    print(json.dumps(q26_results, indent=2)) 