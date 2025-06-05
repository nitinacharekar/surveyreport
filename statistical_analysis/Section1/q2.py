"""
Analyzes data for Question 2: "How would you characterize your organization's current API security readiness/maturity?".

This script processes survey responses where organizations rate their API security readiness/maturity
across several dimensions (e.g., 'Overall API Security Posture', 'API Discovery & Inventory',
'API Data Security & Classification'). Ratings are expected in a format like "1 - Low Maturity",
which are parsed by `extract_numeric_rating`.

It calculates:
- Overall statistics for each rated dimension using `calculate_stats`.
- Average numeric ratings for each dimension.
- Demographic breakdowns of ratings based on specified demographic columns.
"""
import pandas as pd
import json
import os
import sys

# Add the project root to Python path for utility imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def extract_numeric_rating(rating_str) -> float | None:
    """
    Extracts a numeric rating from a string, typically formatted like "1 - Description".

    Args:
        rating_str: The string containing the rating (e.g., "1 - Low Maturity").

    Returns:
        float: The extracted numeric rating, or None if extraction fails or input is not string-like.
    """
    try:
        # Handles cases like "1 - Low Maturity", "2 - Developing Maturity", etc.
        # Also handles if the string is already a number (e.g., "1", "1.0").
        return float(str(rating_str).split(' - ')[0])
    except (ValueError, AttributeError, IndexError):
        # If splitting fails, conversion to float fails, or if rating_str is not processable
        return None

def analyze_q2(file_path: str) -> dict:
    """
    Analyzes ratings of API security readiness/maturity (Question 2).

    The function reads data from the specified Excel file. For each readiness/maturity dimension
    (defined in `readiness_cols`), it calculates descriptive statistics and average ratings
    using `extract_numeric_rating` to convert string-based ratings to numbers.
    Demographic analysis is performed for all rated dimensions.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Contains 'readiness_stats' (distribution of ratings for each dimension)
                              and 'readiness_averages' (average rating for each dimension).
              - 'demographic_analysis': Demographic breakdown of ratings.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    # Columns representing different dimensions of API security readiness/maturity to be rated
    readiness_cols = [
        'Overall API Security Posture',
        'API Discovery & Inventory',
        'API Data Security & Classification',
        'API Access Control & Authentication',
        'API Threat Protection & Monitoring',
        'API Security Testing & Validation',
        'API Security Governance & Compliance'
    ]
    value_cols = readiness_cols # These columns contain the rating values to be analyzed

    # Total number of responses
    total_responses = len(df)
    
    # Calculate statistics for each readiness dimension
    readiness_stats = {}
    for col in readiness_cols:
        if col in df.columns:
            # Pass the raw column for calculate_stats for value counts of original strings
            readiness_stats[col] = calculate_stats(df[col].dropna())
        else:
            readiness_stats[col] = {"error": f"Column '{col}' not found in data."}
    
    # Calculate averages using the numeric part of the rating string
    readiness_averages = {}
    for col in readiness_cols:
        if col in df.columns:
            numeric_ratings = df[col].apply(extract_numeric_rating).dropna()
            readiness_averages[col] = round(numeric_ratings.mean(), 2) if not numeric_ratings.empty else None
        else:
            readiness_averages[col] = None # Column not found for averaging

    summary = {
        'question_text': '2 How would you characterize your organization\'s current API security readiness/maturity?',
        'total_responses': total_responses,
        'main_stats': {
            'readiness_stats': readiness_stats,
            'readiness_averages': readiness_averages
        }
    }
    
    # Add demographic analysis for all specified readiness columns
    valid_value_cols_for_demo = [col for col in value_cols if col in df.columns]
    if valid_value_cols_for_demo:
        df_demo = df.copy()
        numeric_value_cols_for_demo = []
        for col in valid_value_cols_for_demo:
            df_demo[f'{col}_numeric'] = df_demo[col].apply(extract_numeric_rating)
            numeric_value_cols_for_demo.append(f'{col}_numeric')
        
        summary = add_demographic_summary(summary, df_demo, demo_cols, numeric_value_cols_for_demo, original_names=valid_value_cols_for_demo)
    else:
        summary['demographic_analysis'] = {} # Ensure key exists
        
    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    default_data_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'Section 1', 
        '2 Organizational API Security Readiness.xlsx'
    )

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q2_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q2_results = analyze_q2(default_data_file)
        except Exception as e:
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            q2_results = {"error": str(e)}
    
    print(json.dumps(q2_results, indent=2)) 