import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q0(file_path: str):
    """
    Analyze respondent roles data from the survey.
    
    Args:
        file_path: Path to the Excel file containing respondent roles data
        
    Returns:
        Dictionary containing analysis results
    """
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    role_col = 'Answers'
    value_cols = [role_col]

    # Total responses
    total_responses = len(df)
    
    # Calculate role distribution with standard stats
    role_stats = calculate_stats(df[role_col])

    summary = {
        'question_text': '0 Which of the following most accurately reflects your job title and responsibilities?',
        'total_responses': total_responses,
        'main_stats': role_stats
    }
    
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)
    
    return summary

if __name__ == "__main__":
    file_path = "../../data/Section 1/0 Resonpondent Roles.xlsx"
    summary = analyze_q0(file_path)
    print(json.dumps(summary, indent=2))