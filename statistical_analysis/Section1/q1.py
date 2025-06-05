"""
Analyzes data for Question 1: "How would you rate the strategic importance of API security to your organization?".

This script processes survey responses where organizations rate the strategic importance of API security
across several dimensions (e.g., 'Strategic Importance', 'Business Criticality', 'Risk Mitigation').
Ratings are expected in a format like "1 - Not Important", which are parsed by `extract_numeric_rating`.

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
        rating_str: The string containing the rating (e.g., "1 - Not Important").

    Returns:
        float: The extracted numeric rating, or None if extraction fails or input is not string-like.
    """
    try:
        # Handles cases like "1 - Not Important", "2 - Slightly Important", etc.
        # Also handles if the string is already a number (e.g., "1", "1.0").
        return float(str(rating_str).split(' - ')[0])
    except (ValueError, AttributeError, IndexError):
        # If splitting fails, conversion to float fails, or if rating_str is not processable
        return None

def analyze_q1(file_path: str) -> dict:
    """
    Analyzes ratings of API security's strategic importance (Question 1).

    The function reads data from the specified Excel file. For each importance dimension
    (defined in `rating_cols`), it calculates descriptive statistics and average ratings
    using `extract_numeric_rating` to convert string-based ratings to numbers.
    Demographic analysis is performed for all rated dimensions.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Contains 'rating_stats' (distribution of ratings for each dimension)
                              and 'rating_averages' (average rating for each dimension).
              - 'demographic_analysis': Demographic breakdown of ratings.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    # Columns representing different dimensions of strategic importance to be rated
    rating_cols = [
        'Strategic Importance',
        'Business Criticality',
        'Risk Mitigation',
        'Compliance Requirement',
        'Innovation Enablement'
    ]
    value_cols = rating_cols # These columns contain the rating values to be analyzed

    # Total number of responses
    total_responses = len(df)
    
    # Calculate statistics for each rating dimension
    rating_stats = {}
    for col in rating_cols:
        if col in df.columns:
            # Pass the raw column for calculate_stats, as it handles value counts of original strings
            rating_stats[col] = calculate_stats(df[col].dropna())
        else:
            rating_stats[col] = {"error": f"Column '{col}' not found in data."}
    
    # Calculate averages using the numeric part of the rating string
    rating_averages = {}
    for col in rating_cols:
        if col in df.columns:
            numeric_ratings = df[col].apply(extract_numeric_rating).dropna()
            rating_averages[col] = round(numeric_ratings.mean(), 2) if not numeric_ratings.empty else None
        else:
            rating_averages[col] = None # Column not found for averaging

    summary = {
        'question_text': '1 How would you rate the strategic importance of API security to your organization?',
        'total_responses': total_responses,
        'main_stats': {
            'rating_stats': rating_stats,
            'rating_averages': rating_averages
        }
    }
    
    # Add demographic analysis for all specified rating columns
    # Ensure only valid columns present in df are passed to add_demographic_summary
    valid_value_cols_for_demo = [col for col in value_cols if col in df.columns]
    if valid_value_cols_for_demo:
        # For demographic analysis, we need to pass the numeric ratings
        df_demo = df.copy()
        for col in valid_value_cols_for_demo:
            df_demo[f'{col}_numeric'] = df_demo[col].apply(extract_numeric_rating)
        
        # Update value_cols to use the new numeric columns for demographic summary
        numeric_value_cols_for_demo = [f'{col}_numeric' for col in valid_value_cols_for_demo]
        summary = add_demographic_summary(summary, df_demo, demo_cols, numeric_value_cols_for_demo, original_names=valid_value_cols_for_demo)
    else:
        summary['demographic_analysis'] = {} # Ensure key exists
        
    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    default_data_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'Section 1', 
        '1 Strategic Importance of API Security.xlsx'
    )

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q1_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q1_results = analyze_q1(default_data_file)
        except Exception as e:
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            q1_results = {"error": str(e)}
    
    print(json.dumps(q1_results, indent=2)) 