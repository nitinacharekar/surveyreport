'''
Analyzes data for Question 9: "For each of the following API security aspects, please rate how effective your current solutions are for your organization?".

This script processes survey responses where organizations rate the effectiveness of their
current solutions for various API security aspects (e.g., API Discovery & Mapping, API Posture Management).
It calculates overall statistics and average effectiveness ratings for each aspect. The script uses
a helper function `extract_numeric_rating` to parse numeric values from rating strings
(e.g., "1 - Not Effective"). Demographic breakdowns are also performed.
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

def extract_numeric_rating(rating_str) -> float | None:
    """
    Extracts a numeric rating from a string, typically formatted like "1 - Description".

    Args:
        rating_str: The string containing the rating.

    Returns:
        float: The extracted numeric rating, or None if extraction fails.
    """
    try:
        # Handles cases like "1 - Not Effective", "2 - Slightly Effective", etc.
        # Also handles if the string is already a number (e.g., "1", "1.0").
        return float(str(rating_str).split(' - ')[0])
    except (ValueError, AttributeError, IndexError):
        # If splitting fails or conversion to float fails, or if rating_str is not string-like
        return None

def analyze_q9(file_path: str) -> dict:
    """
    Analyzes data on the effectiveness of current solutions for various API security aspects (Question 9).

    The function reads data from the specified Excel file. For each listed API security aspect
    (defined in `solution_cols`), it calculates descriptive statistics and average effectiveness ratings.
    It uses `extract_numeric_rating` to convert potentially string-based ratings to numbers before averaging.
    Demographic analysis is performed for all solution aspects.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Contains 'solution_stats' (distribution of ratings for each aspect)
                              and 'solution_averages' (average effectiveness rating for each aspect).
              - 'demographic_analysis': Demographic breakdown of effectiveness ratings.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    # Columns representing different API security aspects for which solution effectiveness is rated
    solution_cols = [
        'API Discovery & Mapping',
        'API Posture Management',
        'API Access Control',
        'API Runtime Protection',
        'API Security Testing'
    ]
    value_cols = solution_cols # These columns contain the values to be analyzed

    # Total number of responses
    total_responses = len(df)
    
    # Calculate statistics for each solution aspect
    solution_stats = {}
    for col in solution_cols:
        if col in df.columns:
            solution_stats[col] = calculate_stats(df[col].dropna()) # Drop NaNs before calculating basic stats
        else:
            solution_stats[col] = {"error": f"Column '{col}' not found in data."}
    
    # Calculate averages using the numeric part of the rating string
    solution_averages = {}
    for col in solution_cols:
        if col in df.columns:
            numeric_ratings = df[col].apply(extract_numeric_rating).dropna() # Apply extraction and drop NaNs from results
            solution_averages[col] = round(numeric_ratings.mean(), 2) if not numeric_ratings.empty else None
        else:
            solution_averages[col] = None

    summary = {
        'question_text': '9 For each of the following API security aspects, please rate how effective your current solutions are for your organization?',
        'total_responses': total_responses,
        'main_stats': {
            'solution_stats': solution_stats,
            'solution_averages': solution_averages
        }
    }
    
    # Add demographic analysis for all specified solution columns
    # Ensure only valid columns present in df are passed to add_demographic_summary
    valid_value_cols_for_demo = [col for col in value_cols if col in df.columns]
    if valid_value_cols_for_demo:
        summary = add_demographic_summary(summary, df, demo_cols, valid_value_cols_for_demo)
    else:
        summary['demographic_analysis'] = {} # Ensure key exists
        
    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    # Construct the path to the data file dynamically from the script's location.
    default_data_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'Section 3', '3.0 Overall', 
        '9 API Security Concerns- Effectiveness of Current Solutions.xlsx'
    )

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q9_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q9_results = analyze_q9(default_data_file)
        except Exception as e:
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            q9_results = {"error": str(e)}
    
    print(json.dumps(q9_results, indent=2)) 