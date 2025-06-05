'''
Analyzes data for Question 4: "How do you anticipate your organization's investment in API security will change over the next 12-18 months?".

This script processes survey responses from a single 'Answers' column, which is expected
to contain categorical data describing anticipated changes in API security investment
(e.g., "Increase significantly", "Increase somewhat", "Stay the same", "Decrease").

The script calculates:
- Overall statistics (counts, unique values, mode, etc.) for the 'Answers' column (referred to as `investment_col`)
  using `calculate_stats`.
- An average of the `investment_col` *if* the data could be numeric, though this is highly unlikely
  to be meaningful for this type of categorical data.
- Demographic breakdowns of responses based on specified demographic columns.

Note: The 'average' for investment trend data is generally not interpretable and will likely result in
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

def analyze_q4(file_path: str) -> dict:
    """
    Analyzes anticipated changes in API security investment (Question 4).

    The function reads data from the specified Excel file, expecting a primary 'Answers' column
    (herein `investment_col`) that contains the anticipated investment trend. It calculates
    descriptive statistics for this column. An attempt to calculate an average is made, though
    it's typically not meaningful for this categorical data. Demographic analysis for investment
    trends is performed.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Contains 'investment_stats' (distribution for `investment_col`)
                              and 'investment_average' (average of `investment_col`, if numeric).
              - 'demographic_analysis': Demographic breakdown for `investment_col`.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    investment_col = 'Answers'  # The primary column containing investment trend data
    value_cols = [investment_col] if investment_col in df.columns else []

    # Total number of responses
    total_responses = len(df)
    
    # Calculate statistics for the investment trend column
    investment_stats = {}
    if investment_col in df.columns:
        investment_stats = calculate_stats(df[investment_col].dropna())
    else:
        investment_stats = {"error": f"Column '{investment_col}' not found in data."}
    
    # Calculate average if the answers can be numeric (usually not meaningful for this question)
    investment_average = None
    if investment_col in df.columns:
        numeric_series = pd.to_numeric(df[investment_col], errors='coerce').dropna()
        if not numeric_series.empty:
            investment_average = round(numeric_series.mean(), 2)
        else:
            investment_average = "Non-numeric or all NaN data"
    else:
        investment_average = "Column not found"

    summary = {
        'question_text': '4 How do you anticipate your organization\'s investment in API security will change over the next 12-18 months?',
        'total_responses': total_responses,
        'main_stats': {
            'investment_stats': investment_stats,
            'investment_average': investment_average
        }
    }
    
    # Add demographic analysis for the investment trend column
    if value_cols:
        df_demo = df.copy()
        # For demographic analysis, investment_col will be treated as categorical.
        summary = add_demographic_summary(summary, df_demo, demo_cols, value_cols)
    else:
        summary['demographic_analysis'] = {} # Ensure key exists
        
    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    default_data_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'Section 1', 
        '4 Security Investment Trends.xlsx'
    )

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q4_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q4_results = analyze_q4(default_data_file)
        except Exception as e:
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            q4_results = {"error": str(e)}
    
    print(json.dumps(q4_results, indent=2)) 