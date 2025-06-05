'''
Analyzes data for Question 3: "Who has primary responsibility for API security in your organization?".

This script processes survey responses from a single 'Answers' column, which is expected
to contain categorical data identifying the team or role with primary responsibility for API security
(e.g., "Dedicated Security Team", "Development Team", "Shared Responsibility").

The script calculates:
- Overall statistics (counts, unique values, mode, etc.) for the 'Answers' column (referred to as `responsibility_col`)
  using `calculate_stats`.
- An average of the `responsibility_col` *if* the data could be numeric, though this is highly unlikely
  to be meaningful for this type of categorical data.
- Demographic breakdowns of responses based on specified demographic columns.

Note: The 'average' for responsibility data is generally not interpretable and will likely result in
"Non-numeric or all NaN data", which is expected.
'''
import pandas as pd
import json
import os
import sys

# Add the project root to Python path for utility imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q3(file_path: str) -> dict:
    """
    Analyzes who has primary responsibility for API security (Question 3).

    The function reads data from the specified Excel file, expecting a primary 'Answers' column
    (herein `responsibility_col`) that contains the responsible party. It calculates descriptive
    statistics for this column. An attempt to calculate an average is made, though it's typically
    not meaningful for this categorical data. Demographic analysis for responsibility is performed.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Contains 'responsibility_stats' (distribution for `responsibility_col`)
                              and 'responsibility_average' (average of `responsibility_col`, if numeric).
              - 'demographic_analysis': Demographic breakdown for `responsibility_col`.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    responsibility_col = 'Answers'  # The primary column containing responsibility data
    value_cols = [responsibility_col] if responsibility_col in df.columns else []

    # Total number of responses
    total_responses = len(df)
    
    # Calculate statistics for the responsibility column
    responsibility_stats = {}
    if responsibility_col in df.columns:
        responsibility_stats = calculate_stats(df[responsibility_col].dropna())
    else:
        responsibility_stats = {"error": f"Column '{responsibility_col}' not found in data."}
    
    # Calculate average if the answers can be numeric (usually not meaningful for this question)
    responsibility_average = None
    if responsibility_col in df.columns:
        numeric_series = pd.to_numeric(df[responsibility_col], errors='coerce').dropna()
        if not numeric_series.empty:
            responsibility_average = round(numeric_series.mean(), 2)
        else:
            responsibility_average = "Non-numeric or all NaN data"
    else:
        responsibility_average = "Column not found"

    summary = {
        'question_text': '3 Who has primary responsibility for API security in your organization?',
        'total_responses': total_responses,
        'main_stats': {
            'responsibility_stats': responsibility_stats,
            'responsibility_average': responsibility_average
        }
    }
    
    # Add demographic analysis for the responsibility column
    if value_cols:
        df_demo = df.copy()
        # For demographic analysis, responsibility_col will be treated as categorical.
        summary = add_demographic_summary(summary, df_demo, demo_cols, value_cols)
    else:
        summary['demographic_analysis'] = {} # Ensure key exists
        
    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    default_data_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'Section 1', 
        '3 Who has primary responsibility.xlsx'
    )

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q3_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q3_results = analyze_q3(default_data_file)
        except Exception as e:
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            q3_results = {"error": str(e)}
    
    print(json.dumps(q3_results, indent=2)) 