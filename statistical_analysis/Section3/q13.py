import pandas as pd
import json
from pathlib import Path
import sys
import os
# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary

def analyze_q13(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    solution_cols = [
        'Implement API gateways',
        'Implement API Access and Authentication',
        'Authentication Discovery and Risk Scoring',
        'Rate limiting',
        'Encryption',
        'API Specification & Compliance',
        'Integration with API Lifecycle process',
        'API Risk scoring'
    ]

    # Total responses
    total_responses = len(df)
    
    def calculate_stats(series):
        stats = series.value_counts()
        stats_df = pd.DataFrame({
            'value': stats.index,
            'count': stats.values
        })
        stats_df['rank'] = range(1, len(stats_df) + 1)
        stats_df['percent_contribution'] = (stats_df['count'] / stats_df['count'].sum() * 100).round(2)
        stats_df['cumulative_percent_contribution'] = stats_df['percent_contribution'].cumsum().round(2)
        return stats_df.to_dict(orient='records')
    
    # Calculate statistics for each solution
    solution_stats = {}
    for col in solution_cols:
        solution_stats[col] = calculate_stats(df[col])

    # Calculate averages
    solution_averages = {col: round(df[col].mean(), 2) for col in solution_cols}

    summary = {
        'question_text': '13 How effective are your current solutions in implementing the following API Posture Management measures within your organization?',
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
    file_path = '../../data/Section 3/3.2 API Posture Management/13 API Posture Management- Effectiveness.xlsx'
    stats = analyze_q13(file_path)
    print(json.dumps(stats, indent=2)) 