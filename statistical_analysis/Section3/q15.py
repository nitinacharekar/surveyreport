"""
Analyzes data for Question 15: "How effective are your current solutions in addressing the following API Access Control challenges within your organization?".

This script processes survey responses where organizations rate the effectiveness of their
current solutions for specific API Access Control challenges (e.g., 'Complying with standard access control methods
 such as OAuth/OIDC', 'API access control for third-party partner companies'). The ratings are assumed to be numeric.

It calculates:
- Overall statistics for each solution's effectiveness using `calculate_stats`.
- Average effectiveness ratings for each solution.
- Demographic breakdowns of effectiveness ratings based on specified demographic columns.
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

def analyze_q15(file_path: str) -> dict:
    """
    Analyzes the effectiveness of current solutions for API Access Control challenges (Question 15).

    The function reads data from the specified Excel file. For each API Access Control challenge
    (defined in `solution_cols`), it calculates descriptive statistics and average effectiveness ratings.
    The input ratings are expected to be numeric.
    Demographic analysis is performed for all specified challenges.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Contains 'solution_stats' (distribution of ratings for each solution's effectiveness)
                              and 'solution_averages' (average effectiveness rating for each solution).
              - 'demographic_analysis': Demographic breakdown of effectiveness ratings.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    # Columns representing different API Access Control challenges for which solution effectiveness is rated
    solution_cols = [
        'Complying with standard access control methods such as OAuth/OIDC',
        'API access control for third-party partner companies',
        'API access control for App-to-App communications',
        'API access control for external users'
    ]
    value_cols = solution_cols # These columns contain the numeric ratings to be analyzed

    # Total number of responses
    total_responses = len(df)
    
    # Calculate statistics for each solution
    solution_stats = {}
    for col in solution_cols:
        if col in df.columns:
            # Ensure data is numeric before calculating stats, coercing errors to NaN
            numeric_series = pd.to_numeric(df[col], errors='coerce').dropna()
            solution_stats[col] = calculate_stats(numeric_series) if not numeric_series.empty else {}
        else:
            solution_stats[col] = {"error": f"Column '{col}' not found in data."}

    # Calculate averages for solution effectiveness
    solution_averages = {}
    for col in solution_cols:
        if col in df.columns:
            # Ensure data is numeric before calculating mean, coercing errors to NaN
            numeric_series = pd.to_numeric(df[col], errors='coerce').dropna()
            solution_averages[col] = round(numeric_series.mean(), 2) if not numeric_series.empty else None
        else:
            solution_averages[col] = None

    summary = {
        'question_text': '15How effective are your current solutions in addressing the following API Access Control challenges within your organization?', # Typo "15How" kept as per original, consider fixing.
        'total_responses': total_responses,
        'main_stats': {
            'solution_stats': solution_stats,
            'solution_averages': solution_averages
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
        os.path.dirname(__file__), '..', '..', 'data', 'Section 3', '3.3 API Access Control', 
        '15 API Access Control- Effective.xlsx' # Note: Filename uses "Effective" not "Effectiveness"
    )

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q15_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q15_results = analyze_q15(default_data_file)
        except Exception as e:
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            q15_results = {"error": str(e)}
    
    print(json.dumps(q15_results, indent=2)) 