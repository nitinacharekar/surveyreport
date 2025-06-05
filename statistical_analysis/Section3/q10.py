'''
Analyzes data for Question 10: "How concerning are the following API Discovery challenges for your organization?".

This script processes survey responses where organizations rate their concern levels
for specific API Discovery challenges, such as 'Shadow/undocumented APIs', 'Zombie/dormant APIs',
etc. The ratings are assumed to be numeric.

It calculates:
- Overall statistics for each challenge using `calculate_stats`.
- Average concern ratings for each challenge.
- Demographic breakdowns of concern ratings based on specified demographic columns.
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

def analyze_q10(file_path: str) -> dict:
    """
    Analyzes concern levels for various API Discovery challenges (Question 10).

    The function reads data from the specified Excel file. For each API discovery challenge
    (defined in `concern_cols`), it calculates descriptive statistics and average concern ratings.
    The input ratings are expected to be numeric.
    Demographic analysis is performed for all specified challenges.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Contains 'concern_stats' (distribution of ratings for each challenge)
                              and 'concern_averages' (average concern rating for each challenge).
              - 'demographic_analysis': Demographic breakdown of concern ratings.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    # Columns representing different API Discovery challenges to be rated
    concern_cols = [
        'Shadow/ undocumented APIs',
        'Zombie/ dormant APIs',
        'API Usage & Visualization',
        'API Cost / Metering / Billing',
        'Identifying APIs relevant for compliance (privacy, resilience, etc.)'
    ]
    value_cols = concern_cols # These columns contain the numeric ratings to be analyzed

    # Total number of responses
    total_responses = len(df)
    
    # Calculate statistics for each concern
    concern_stats = {}
    for col in concern_cols:
        if col in df.columns:
            # Ensure data is numeric before calculating stats, coercing errors to NaN
            numeric_series = pd.to_numeric(df[col], errors='coerce').dropna()
            concern_stats[col] = calculate_stats(numeric_series) if not numeric_series.empty else {}
        else:
            concern_stats[col] = {"error": f"Column '{col}' not found in data."}
    
    # Calculate averages
    concern_averages = {}
    for col in concern_cols:
        if col in df.columns:
            # Ensure data is numeric before calculating mean, coercing errors to NaN
            numeric_series = pd.to_numeric(df[col], errors='coerce').dropna()
            concern_averages[col] = round(numeric_series.mean(), 2) if not numeric_series.empty else None
        else:
            concern_averages[col] = None

    summary = {
        'question_text': '10 How concerning are the following API Discovery challenges for your organization? ',
        'total_responses': total_responses,
        'main_stats': {
            'concern_stats': concern_stats,
            'concern_averages': concern_averages
        }
    }
    
    # Add demographic analysis
    # Ensure only valid columns present in df are passed to add_demographic_summary
    valid_value_cols_for_demo = [col for col in value_cols if col in df.columns]
    if valid_value_cols_for_demo:
        # Convert columns to numeric for demographic summary if they are not already, handling potential errors
        df_demo = df.copy()
        for col in valid_value_cols_for_demo:
            df_demo[col] = pd.to_numeric(df_demo[col], errors='coerce')
        summary = add_demographic_summary(summary, df_demo, demo_cols, valid_value_cols_for_demo)
    else:
        summary['demographic_analysis'] = {} # Ensure key exists
    
    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    # Construct the path to the data file dynamically from the script's location.
    default_data_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'Section 3', '3.1 API Discovery & Mapping', 
        '10 API Discovery & Mapping- Concerns Rating.xlsx'
    )

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q10_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q10_results = analyze_q10(default_data_file)
        except Exception as e:
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            q10_results = {"error": str(e)}
    
    print(json.dumps(q10_results, indent=2)) 