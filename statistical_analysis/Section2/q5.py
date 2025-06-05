"""
Analyzes data for Question 5: "What are the predominant API styles used in your organization?".

This script processes survey responses where organizations indicate the predominance of various
API styles (e.g., 'REST', 'GraphQL', 'gRPC', 'Webhooks', 'SOAP') within their systems.
The input for each style is expected to be a numeric rating or percentage indicating its usage.

It calculates:
- Overall statistics for each API style's predominance using `calculate_stats`.
- Average predominance rating for each API style.
- Demographic breakdowns of these ratings based on specified demographic columns.
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

def analyze_q5(file_path: str) -> dict:
    """
    Analyzes the predominance of various API styles within organizations (Question 5).

    The function reads data from the specified Excel file. For each API style listed
    (defined in `api_style_cols`), it calculates descriptive statistics and average predominance ratings.
    The input ratings are expected to be numeric.
    Demographic analysis is performed for all API styles.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Contains 'style_stats' (distribution of ratings for each API style)
                              and 'style_averages' (average rating for each API style).
              - 'demographic_analysis': Demographic breakdown of API style ratings.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    # Columns representing different API styles whose predominance is rated
    api_style_cols = [
        'REST',
        'GraphQL',
        'gRPC',
        'Webhooks',
        'SOAP'
    ]
    value_cols = api_style_cols # These columns contain the numeric ratings to be analyzed

    # Total number of responses
    total_responses = len(df)
    
    # Calculate statistics for each API style
    style_stats = {}
    for col in api_style_cols:
        if col in df.columns:
            # Ensure data is numeric before calculating stats, coercing errors to NaN
            numeric_series = pd.to_numeric(df[col], errors='coerce').dropna()
            style_stats[col] = calculate_stats(numeric_series) if not numeric_series.empty else {}
        else:
            style_stats[col] = {"error": f"Column '{col}' not found in data."}
    
    # Calculate averages for API style predominance
    style_averages = {}
    for col in api_style_cols:
        if col in df.columns:
            # Ensure data is numeric before calculating mean, coercing errors to NaN
            numeric_series = pd.to_numeric(df[col], errors='coerce').dropna()
            style_averages[col] = round(numeric_series.mean(), 2) if not numeric_series.empty else None
        else:
            style_averages[col] = None

    summary = {
        'question_text': '5 What are the predominant API styles used in your organization?',
        'total_responses': total_responses,
        'main_stats': {
            'style_stats': style_stats,
            'style_averages': style_averages
        }
    }
    
    # Add demographic analysis
    valid_value_cols_for_demo = [col for col in value_cols if col in df.columns]
    if valid_value_cols_for_demo:
        df_demo = df.copy()
        for col in valid_value_cols_for_demo:
            df_demo[col] = pd.to_numeric(df_demo[col], errors='coerce')
        summary = add_demographic_summary(summary, df_demo, demo_cols, valid_value_cols_for_demo)
    else:
        summary['demographic_analysis'] = {} # Ensure key exists
        
    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    default_data_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'Section 2', 
        '5 What are the predominant API styles used in your organization.xlsx'
    )

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q5_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q5_results = analyze_q5(default_data_file)
        except Exception as e:
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            q5_results = {"error": str(e)}
    
    print(json.dumps(q5_results, indent=2)) 