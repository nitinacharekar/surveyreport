"""
Analyzes data for Question 8: "What is the deployment model for each AI/ML API your organization uses?".
(Note: The data file associated with this in its `__main__` block is named for Question 7 - '7 API Usage in AIML Implementations- Deployment Model.xlsx')

This script processes survey responses where organizations describe the deployment model
(e.g., "Cloud-hosted (Public)", "On-premises", "Hybrid") for various AI/ML API types
(e.g., 'Large Language Models (LLMs)', 'Computer Vision APIs', 'Custom ML Models').
The input for each type is expected to be categorical.

It calculates:
- Overall statistics (counts of each deployment model) for each AI/ML API type using `calculate_stats`.
- Demographic breakdowns of these deployment models based on specified demographic columns.

Note: Averages are not calculated for the main statistics as deployment models are categorical.
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

def analyze_q8(file_path: str) -> dict:
    """
    Analyzes the deployment models for various AI/ML API types (Question 8).

    The function reads data from the specified Excel file. For each AI/ML API type listed
    (defined in `aiml_cols`), it calculates descriptive statistics (counts) of their
    deployment models. Input data is expected to be categorical.
    Demographic analysis is performed for all AI/ML API types.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': Contains 'aiml_stats' (distribution of deployment models for each type).
              - 'demographic_analysis': Demographic breakdown of AI/ML API deployment models.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    # Columns representing different AI/ML API types whose deployment models are described
    aiml_cols = [
        'Large Language Models (LLMs)',
        'Computer Vision APIs',
        'Custom ML Models' # Note: original script had 'Custom ML Models', ensure this matches data columns
    ]
    value_cols = aiml_cols # These columns contain the categorical deployment model data

    # Total number of responses
    total_responses = len(df)
    
    # Calculate statistics for each AI/ML type (distribution of deployment models)
    aiml_stats = {}
    for col in aiml_cols:
        if col in df.columns:
            aiml_stats[col] = calculate_stats(df[col].dropna()) # Drop NaNs before calculating stats
        else:
            aiml_stats[col] = {"error": f"Column '{col}' not found in data."}

    summary = {
        'question_text': '8 What is the deployment model for each AI/ML API your organization uses?',
        'total_responses': total_responses,
        'main_stats': aiml_stats # Averages are not applicable here for categorical data
    }
    
    # Add demographic analysis
    # add_demographic_summary should be able to handle categorical data in value_cols
    valid_value_cols_for_demo = [col for col in value_cols if col in df.columns]
    if valid_value_cols_for_demo:
        summary = add_demographic_summary(summary, df, demo_cols, valid_value_cols_for_demo)
    else:
        summary['demographic_analysis'] = {} # Ensure key exists
        
    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    # Note: The data file seems to be named for Question 7, but this script (q8.py) uses it for Q8 analysis.
    default_data_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'Section 2', '2.2 API Usage in AIML Implementations', 
        '7 API Usage in AIML Implementations- Deployment Model.xlsx'
    )

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