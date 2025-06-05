'''
Analyzes data for Question 0: "What is your role in your organization?".

This script processes survey responses from a single 'Answers' column, which is expected
to contain categorical data describing the respondent's role (e.g., "Developer", "Security Analyst",
"Manager").

The script calculates:
- Overall statistics (counts, unique values, mode, etc.) for the 'Answers' column (referred to as `role_col`)
  using `calculate_stats`.
- An average of the `role_col` *if* the data can be meaningfully converted to numeric. This is
  unlikely to be meaningful for typical role descriptions but is included for consistency with
  other qX.py scripts that might handle numeric ratings.
- Demographic breakdowns of role distribution based on specified demographic columns.

Note: The 'average' calculation for roles is generally not meaningful and will likely result
in "Non-numeric or all NaN data" or similar, which is the expected behavior if roles are purely textual.
'''
import pandas as pd
import json
import os
import sys

# Add the project root to Python path for utility imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q0(file_path: str) -> dict:
    """
    Analyzes respondent roles from survey data (Question 0).

    The function reads data from the specified Excel file, expecting a primary 'Answers' column
    (herein `role_col`) that contains the respondent's role. It calculates descriptive statistics
    for this column. An attempt to calculate an average is made, though it's typically not
    meaningful for role data. Demographic analysis for roles is performed.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Contains 'role_stats' (distribution for the `role_col`)
                              and 'role_average' (average of `role_col`, if numeric).
              - 'demographic_analysis': Demographic breakdown for `role_col`.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    role_col = 'Answers'  # The primary column containing role data
    value_cols = [role_col] if role_col in df.columns else []

    # Total number of responses
    total_responses = len(df)
    
    # Calculate statistics for the role column
    role_stats = {}
    if role_col in df.columns:
        role_stats = calculate_stats(df[role_col].dropna()) # Drop NaNs before basic stats
    else:
        role_stats = {"error": f"Column '{role_col}' not found in data."}
    
    # Calculate average for the role column if it can be numeric (usually not meaningful for roles)
    role_average = None
    if role_col in df.columns:
        numeric_series = pd.to_numeric(df[role_col], errors='coerce').dropna()
        if not numeric_series.empty:
            role_average = round(numeric_series.mean(), 2)
        else:
            # This case means all values were non-numeric or NaN (expected for textual roles)
            role_average = "Non-numeric or all NaN data"
    else:
        role_average = "Column not found"

    summary = {
        'question_text': '0 What is your role in your organization?',
        'total_responses': total_responses,
        'main_stats': {
            'role_stats': role_stats,
            'role_average': role_average
        }
    }
    
    # Add demographic analysis for the role column
    if value_cols:
        df_demo = df.copy()
        # For demographic analysis, 'role_col' will be treated as categorical if non-numeric.
        # If it were numeric, it would be handled, but for roles, this is typically not the case.
        # No explicit numeric conversion needed here if add_demographic_summary handles categorical data.
        summary = add_demographic_summary(summary, df_demo, demo_cols, value_cols)
    else:
        summary['demographic_analysis'] = {} # Ensure key exists
        
    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    # Construct the path to the data file dynamically from the script's location.
    # Note: Typo in actual filename "Resonpondent" vs. expected "Respondent".
    default_data_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'Section 1', 
        '0 Resonpondent Roles.xlsx' 
    )

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q0_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q0_results = analyze_q0(default_data_file)
        except Exception as e:
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            q0_results = {"error": str(e)}
    
    print(json.dumps(q0_results, indent=2))