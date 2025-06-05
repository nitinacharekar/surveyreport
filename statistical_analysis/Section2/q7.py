"""
Analyzes data for Question 7: "How frequently does your organization use the following AI/ML APIs?".
(Note: The data file associated with this in its `__main__` block is named for Question 6 - '6 API Usage in AIML Implementations- Frequency.xlsx')

This script processes survey responses where organizations rate the frequency of use for
various AI/ML API types (e.g., 'Large Language Models (LLMs)', 'Computer Vision APIs', 'Custom ML models').
The input for each type is expected to be a numeric rating.

It calculates:
- Overall statistics for each AI/ML API type's frequency of use using `calculate_stats`.
- Average frequency rating for each AI/ML API type.
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

def analyze_q7(file_path: str) -> dict:
    """
    Analyzes the frequency of use for various AI/ML API types (Question 7).

    The function reads data from the specified Excel file. For each AI/ML API type listed
    (defined in `aiml_cols`), it calculates descriptive statistics and average frequency ratings.
    The input ratings are expected to be numeric.
    Demographic analysis is performed for all AI/ML API types.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Contains 'aiml_stats' (distribution of ratings for each type)
                              and 'aiml_averages' (average rating for each type).
              - 'demographic_analysis': Demographic breakdown of AI/ML API usage frequency ratings.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    # Columns representing different AI/ML API types whose usage frequency is rated
    aiml_cols = [
        'Large Language Models (LLMs)',
        'Computer Vision APIs',
        'Custom ML models' # Original script had 'Custom ML models', if filename implies specific naming use that.
    ]
    value_cols = aiml_cols # These columns contain the numeric ratings to be analyzed

    # Total number of responses
    total_responses = len(df)
    
    # Calculate statistics for each AI/ML type
    aiml_stats = {}
    for col in aiml_cols:
        if col in df.columns:
            # Ensure data is numeric before calculating stats, coercing errors to NaN
            numeric_series = pd.to_numeric(df[col], errors='coerce').dropna()
            aiml_stats[col] = calculate_stats(numeric_series) if not numeric_series.empty else {}
        else:
            aiml_stats[col] = {"error": f"Column '{col}' not found in data."}
    
    # Calculate averages for AI/ML API type usage frequency
    aiml_averages = {}
    for col in aiml_cols:
        if col in df.columns:
            # Ensure data is numeric before calculating mean, coercing errors to NaN
            numeric_series = pd.to_numeric(df[col], errors='coerce').dropna()
            aiml_averages[col] = round(numeric_series.mean(), 2) if not numeric_series.empty else None
        else:
            aiml_averages[col] = None

    summary = {
        'question_text': '7 How frequently does your organization use the following AI/ML APIs?',
        'total_responses': total_responses,
        'main_stats': {
            'aiml_stats': aiml_stats,
            'aiml_averages': aiml_averages
        }
    }
    
    # Add demographic analysis
    valid_value_cols_for_demo = [col for col in value_cols if col in df.columns]
    if valid_value_cols_for_demo:
        df_demo = df.copy()
        for col in valid_value_cols_for_demo:
            df_demo[col] = pd.to_numeric(df_demo[col], errors='coerce') # Convert to numeric for analysis
        summary = add_demographic_summary(summary, df_demo, demo_cols, valid_value_cols_for_demo)
    else:
        summary['demographic_analysis'] = {} # Ensure key exists
        
    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    # Note: The data file seems to be named for Question 6, but this script (q7.py) uses it for Q7 analysis.
    default_data_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'Section 2', '2.2 API Usage in AIML Implementations', 
        '6 API Usage in AIML Implementations- Frequency.xlsx'
    )

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q7_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q7_results = analyze_q7(default_data_file)
        except Exception as e:
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            q7_results = {"error": str(e)}
    
    print(json.dumps(q7_results, indent=2)) 