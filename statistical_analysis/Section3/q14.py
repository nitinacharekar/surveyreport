import pandas as pd
import json
from pathlib import Path
import sys
import os
# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q14(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    concern_cols = [
        'Complying with standard access control methods such as OAuth/OIDC',
        'API access control for third-party partner companies',
        'API access control for App-to-App communications',
        'API access control for external users'
    ]

    # Total responses
    total_responses = len(df)
    
    # Calculate statistics for each concern
    concern_stats = {}
    for col in concern_cols:
        concern_stats[col] = calculate_stats(df[col])
    
    # Calculate averages
    concern_averages = {col: round(df[col].mean(), 2) for col in concern_cols}

    summary = {
        'question_text': '14 How concerning are the following API Access Control challenges for your organization?',
        'total_responses': total_responses,
        'main_stats': {
            'concern_stats': concern_stats,
            'concern_averages': concern_averages
        }
    }
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, concern_cols)
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 3/3.3 API Access Control/14 API Access Control- Concern.xlsx'
    stats = analyze_q14(file_path)
    print(json.dumps(stats, indent=2)) 