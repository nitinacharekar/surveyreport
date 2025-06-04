import pandas as pd
import json
from pathlib import Path
import sys
import os
# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q15(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    solution_cols = [
        'Complying with standard access control methods such as OAuth/OIDC',
        'API access control for third-party partner companies',
        'API access control for App-to-App communications',
        'API access control for external users'
    ]

    # Total responses
    total_responses = len(df)
    
    # Calculate statistics for each solution
    solution_stats = {}
    for col in solution_cols:
        solution_stats[col] = calculate_stats(df[col])

    # Calculate averages
    solution_averages = {col: round(df[col].mean(), 2) for col in solution_cols}

    summary = {
        'question_text': '15How effective are your current solutions in addressing the following API Access Control challenges within your organization?',
        'total_responses': total_responses,
        'main_stats': {
            'solution_stats': solution_stats,
            'solution_averages': solution_averages
        }
    }
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, solution_cols)
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 3/3.3 API Access Control/15 API Access Control- Effective.xlsx'
    stats = analyze_q15(file_path)
    print(json.dumps(stats, indent=2)) 