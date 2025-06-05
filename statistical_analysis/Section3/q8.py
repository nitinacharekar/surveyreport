"""
Analyzes data for Question 8: "For each of the following API security aspects, please rate how concerning they are for your organization?".

This script reads an Excel file containing survey responses where organizations rate their
concern levels for various API security aspects (e.g., API Discovery & Mapping, API Posture Management).
It calculates overall statistics and average concern ratings for each aspect. The script includes
a helper function `extract_numeric_rating` to parse numeric values from rating strings
(e.g., "1 - Not Concerning"). Demographic breakdowns are also performed.
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

def extract_numeric_rating(rating_str) -> float | None:
    """
    Extracts a numeric rating from a string, typically formatted like "1 - Description".

    Args:
        rating_str: The string containing the rating.

    Returns:
        float: The extracted numeric rating, or None if extraction fails.
    """
    try:
        # Handles cases like "1 - Not Concerning", "2 - Slightly Concerning", etc.
        # Also handles if the string is already a number (e.g., "1", "1.0").
        return float(str(rating_str).split(' - ')[0])
    except (ValueError, AttributeError, IndexError):
        # If splitting fails or conversion to float fails, or if rating_str is not string-like
        return None

def analyze_q8(file_path: str) -> dict:
    """
    Analyzes data on concern levels for various API security aspects (Question 8).

    The function reads data from the specified Excel file. For each listed API security aspect
    (defined in `concern_cols`), it calculates descriptive statistics and average concern ratings.
    It uses `extract_numeric_rating` to convert potentially string-based ratings to numbers before averaging.
    Demographic analysis is performed for all concern aspects.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Contains 'api_stats' (distribution of ratings for each aspect)
                              and 'api_averages' (average concern rating for each aspect).
              - 'demographic_analysis': Demographic breakdown of concern ratings.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    # Columns representing different API security aspects to be rated
    concern_cols = [
        'API Discovery & Mapping',
        'API Posture Management',
        'API Access Control',
        'API Runtime Protection',
        'API Security Testing'
    ]
    value_cols = concern_cols # These columns contain the values to be analyzed

    # Total number of responses
    total_responses = len(df)
    
    # Calculate statistics for each API security aspect
    api_stats = {}
    for col in concern_cols:
        if col in df.columns:
            api_stats[col] = calculate_stats(df[col].dropna()) # Drop NaNs before calculating basic stats
        else:
            api_stats[col] = {"error": f"Column '{col}' not found in data."}
    
    # Calculate averages using the numeric part of the rating string
    api_averages = {}
    for col in concern_cols:
        if col in df.columns:
            numeric_ratings = df[col].apply(extract_numeric_rating).dropna() # Apply extraction and drop NaNs from results
            api_averages[col] = round(numeric_ratings.mean(), 2) if not numeric_ratings.empty else None
        else:
            api_averages[col] = None

    summary = {
        'question_text': '8 For each of the following API security aspects, please rate how concerning they are for your organization?',
        'total_responses': total_responses,
        'main_stats': {
            'api_stats': api_stats,
            'api_averages': api_averages
        }
    }
    
    # Add demographic analysis for all specified concern columns
    # Ensure only valid columns present in df are passed to add_demographic_summary
    valid_value_cols_for_demo = [col for col in value_cols if col in df.columns]
    if valid_value_cols_for_demo:
        summary = add_demographic_summary(summary, df, demo_cols, valid_value_cols_for_demo)
    else:
        summary['demographic_analysis'] = {} # Ensure key exists
    
    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    default_data_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Section 3', '3.0 Overall', '8 API Security Concerns- Rating.xlsx')

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q8_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q8_results = analyze_q8(default_data_file)
        except Exception as e:
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            q8_results = {"error": str(e)}
    
    print(json.dumps(q8_results, indent=2)) 