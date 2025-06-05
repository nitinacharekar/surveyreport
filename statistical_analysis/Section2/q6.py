'''
Analyzes data for Question 6: "How is your organization currently using APIs in its AI/ML implementations?".

This script processes survey responses where organizations indicate their usage of APIs
for various AI/ML implementation purposes (e.g., 'Data Ingestion', 'Model Training', 'Inference').
The input for each purpose is expected to be a numeric rating or percentage indicating usage level.

It calculates:
- Overall statistics for each AI/ML API usage purpose using `calculate_stats`.
- Average usage rating for each purpose.
- Demographic breakdowns of these ratings based on specified demographic columns.
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

def analyze_q6(file_path: str) -> dict:
    """
    Analyzes how organizations are using APIs in their AI/ML implementations (Question 6).

    The function reads data from the specified Excel file. For each AI/ML API usage purpose
    (defined in `aiml_usage_cols`), it calculates descriptive statistics and average usage ratings.
    The input ratings are expected to be numeric.
    Demographic analysis is performed for all usage purposes.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Contains 'usage_stats' (distribution of ratings for each purpose)
                              and 'usage_averages' (average rating for each purpose).
              - 'demographic_analysis': Demographic breakdown of usage ratings.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    # Columns representing different AI/ML API usage purposes to be rated
    aiml_usage_cols = [
        'Data Ingestion for AI/ML models',
        'Model Training APIs',
        'Inference APIs (for consuming AI/ML models)',
        'AI-powered APIs (APIs that expose AI/ML capabilities)',
        'APIs for MLOps (e.g., model deployment, monitoring)'
    ]
    value_cols = aiml_usage_cols # These columns contain the numeric ratings to be analyzed

    # Total number of responses
    total_responses = len(df)
    
    # Calculate statistics for each AI/ML API usage purpose
    usage_stats = {}
    for col in aiml_usage_cols:
        if col in df.columns:
            # Ensure data is numeric before calculating stats, coercing errors to NaN
            numeric_series = pd.to_numeric(df[col], errors='coerce').dropna()
            usage_stats[col] = calculate_stats(numeric_series) if not numeric_series.empty else {}
        else:
            usage_stats[col] = {"error": f"Column '{col}' not found in data."}
    
    # Calculate averages for AI/ML API usage purposes
    usage_averages = {}
    for col in aiml_usage_cols:
        if col in df.columns:
            # Ensure data is numeric before calculating mean, coercing errors to NaN
            numeric_series = pd.to_numeric(df[col], errors='coerce').dropna()
            usage_averages[col] = round(numeric_series.mean(), 2) if not numeric_series.empty else None
        else:
            usage_averages[col] = None

    summary = {
        'question_text': '6 How is your organization currently using APIs in its AI/ML implementations?',
        'total_responses': total_responses,
        'main_stats': {
            'usage_stats': usage_stats,
            'usage_averages': usage_averages
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
    default_data_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'Section 2', 
        '6 How is your organization currently using APIs in its AI_ML implementations.xlsx'
    )

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q6_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q6_results = analyze_q6(default_data_file)
        except Exception as e:
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            q6_results = {"error": str(e)}
    
    print(json.dumps(q6_results, indent=2)) 