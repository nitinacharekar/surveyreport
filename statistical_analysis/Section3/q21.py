"""
Analyzes data for Question 21: "How has code-based discovery improved your organization's API security?".

This script processes survey responses from a single 'Answers' column. The data in this column
likely reflects the perceived improvement in API security due to code-based discovery,
which could be categorical (e.g., "Significant improvement", "Moderate improvement", "No improvement")
or a numeric rating.

The script calculates:
- Overall statistics (counts, unique values, mode, etc.) for the 'Answers' column using `calculate_stats`.
- An average of the 'Answers' column *if* the data can be meaningfully converted to numeric.
  This is particularly relevant if the answers are on a rating scale.
- Demographic breakdowns of the responses based on specified demographic columns.

Note: The meaningfulness of an 'average' depends on the nature of the 'Answers' column. If it contains
qualitative text, the average may not be directly interpretable unless the text represents an ordinal scale
that has been numerically encoded.
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

def analyze_q21(file_path: str) -> dict:
    """
    Analyzes responses on how code-based discovery improved API security (Question 21).

    The function reads data from the specified Excel file, expecting a primary 'Answers' column.
    It calculates descriptive statistics for this column. An attempt is made to calculate an
    average from the 'Answers' column, which is most relevant if the data is numeric or
    represents an ordinal scale. Demographic analysis is performed for the 'Answers' column.

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
    answer_average = None
    if answer_col in df.columns:
        numeric_series = pd.to_numeric(df[answer_col], errors='coerce').dropna()
        if not numeric_series.empty:
            answer_average = round(numeric_series.mean(), 2)
        else:
            answer_average = "Non-numeric or all NaN data"
    else:
        answer_average = "Column not found"

    summary = {
        'question_text': '21 How has code-based discovery improved your organization\'s API security?',
        'total_responses': total_responses,
        'main_stats': {
            'answer_stats': answer_stats,
            'answer_average': answer_average
        }
    }
    
    # Add demographic analysis
    if value_cols:
        df_demo = df.copy()
        if answer_col in df_demo.columns: # Ensure column exists before trying to convert
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
        "21 How has code-based discovery improved your organization's API security.xlsx"
    )

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q21_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q21_results = analyze_q21(default_data_file)
        except Exception as e:
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            q21_results = {"error": str(e)}
    
    print(json.dumps(q21_results, indent=2)) 