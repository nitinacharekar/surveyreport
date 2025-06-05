'''
Analyzes data for Question 20: "Which stage of the API lifecycle would benefit most from the following discovery method in your organization?".

This script processes survey responses from a single 'Answers' column, which is expected
to contain categorical data indicating the API lifecycle stage (e.g., "Design", "Development",
"Testing", "Deployment", "Operations") that respondents believe would benefit most from
a specific discovery method (implied by the context of the survey, not explicitly in the data file for this question).

The script calculates:
- Overall statistics (counts, unique values, mode, etc.) for the 'Answers' column using `calculate_stats`.
- An average of the 'Answers' column *if* the data can be meaningfully converted to numeric.
  If not, this will likely result in an error or NaN, which should be interpreted accordingly.
- Demographic breakdowns of the responses based on specified demographic columns.

Note: The effectiveness of calculating an 'average' on potentially categorical data depends on the
exact nature and encoding of the 'Answers' column. If it's purely categorical (e.g., text names of stages),
the average might not be meaningful.
'''
import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path for utility imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q20(file_path: str) -> dict:
    """
    Analyzes which API lifecycle stage would benefit most from a discovery method (Question 20).

    The function reads data from the specified Excel file, expecting a primary 'Answers' column
    that contains the lifecycle stage. It calculates descriptive statistics for this column.
    An attempt is made to calculate an average from the 'Answers' column, which is only
    meaningful if the data is (or can be converted to) numeric.
    Demographic analysis is performed for the 'Answers' column.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Contains 'answer_stats' (distribution for the 'Answers' column)
                              and 'answer_average' (average of the 'Answers' column, if numeric).
              - 'demographic_analysis': Demographic breakdown for the 'Answers' column.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    answer_col = 'Answers'  # The primary column to analyze
    value_cols = [answer_col] if answer_col in df.columns else []

    # Total number of responses
    total_responses = len(df)
    
    # Calculate statistics for the answer column
    answer_stats = {}
    if answer_col in df.columns:
        answer_stats = calculate_stats(df[answer_col].dropna()) # Drop NaNs before basic stats
    else:
        answer_stats = {"error": f"Column '{answer_col}' not found in data."}
    
    # Calculate average for the answer column if it can be numeric
    # This might not be meaningful if 'Answers' is purely categorical (e.g., text names of stages)
    answer_average = None
    if answer_col in df.columns:
        numeric_series = pd.to_numeric(df[answer_col], errors='coerce').dropna()
        if not numeric_series.empty:
            answer_average = round(numeric_series.mean(), 2)
        else:
            # This case means all values were non-numeric or NaN
            answer_average = "Non-numeric or all NaN data"
    else:
        answer_average = "Column not found"

    summary = {
        'question_text': '20 Which stage of the API lifecycle would benefit most from the following discovery method in your organization?',
        'total_responses': total_responses,
        'main_stats': {
            'answer_stats': answer_stats,
            'answer_average': answer_average
        }
    }
    
    # Add demographic analysis
    if value_cols:
        # For demographic analysis, if 'Answers' is categorical, it will be treated as such.
        # If it's numeric, it will also be handled appropriately by add_demographic_summary.
        df_demo = df.copy()
        # Ensure the 'Answers' column is used for demographic analysis, converting to numeric if possible
        # but add_demographic_summary can handle categorical data too.
        if answer_col in df_demo.columns:
             df_demo[answer_col] = pd.to_numeric(df_demo[answer_col], errors='coerce')
        summary = add_demographic_summary(summary, df_demo, demo_cols, value_cols)
    else:
        summary['demographic_analysis'] = {} # Ensure key exists
        
    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    # Construct the path to the data file dynamically from the script's location.
    default_data_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'Section 3', '3.5 API Security Testing', 
        '20 Which stage of the API lifecycle would benefit most.xlsx'
    )

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q20_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q20_results = analyze_q20(default_data_file)
        except Exception as e:
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            q20_results = {"error": str(e)}
    
    print(json.dumps(q20_results, indent=2)) 