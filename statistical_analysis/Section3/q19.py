import pandas as pd
import json
from pathlib import Path
import sys
import os
# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q19(file_path: str):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    id_col = 'ID'
    demo_cols = ['Country']
    solution_cols = [
        'Code-based discovery (e.g., static/dynamic code analysis)',
        'Crawler-based discovery (e.g., scanning APIs)',
        'Traffic-based discovery (e.g., monitoring API traffic)'
    ]
    total_responses = len(df)
    solution_stats = {}
    for col in solution_cols:
        solution_stats[col] = calculate_stats(df[col])
    
    solution_averages = {col: round(df[col].mean(), 2) for col in solution_cols}
    
    summary = {
        'question_text': '19 How effective are your current solutions in identifying vulnerable and/or undocumented/shadow APIs?',
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
    file_path = '../../data/Section 3/3.5 API Security Testing/19 API Security Testing- Effectiveness.xlsx'
    stats = analyze_q19(file_path)
    print(json.dumps(stats, indent=2)) 