import pandas as pd
import json
from pathlib import Path
import sys
import os
# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary

def analyze_q12(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    concern_cols = [
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
        stats = series.value_counts().sort_index()
        stats_df = pd.DataFrame({
            'value': stats.index,
            'count': stats.values
        })
        stats_df['rank'] = range(1, len(stats_df) + 1)
        stats_df['percent_contribution'] = (stats_df['count'] / stats_df['count'].sum() * 100).round(2)
        stats_df['cumulative_percent_contribution'] = stats_df['percent_contribution'].cumsum().round(2)
        return stats_df.to_dict(orient='records')
    
    # Calculate statistics for each concern
    concern_stats = {}
    for col in concern_cols:
        concern_stats[col] = calculate_stats(df[col])
    
    # Calculate averages
    concern_averages = {col: round(df[col].mean(), 2) for col in concern_cols}

    summary = {
        'question_text': '12 How concerning are the following API Posture Management measures for your organization?',
        'total_responses': total_responses,
        'concern_stats': concern_stats,
        'concern_averages': concern_averages
    }
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, concern_cols)
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 3/3.2 API Posture Management/12 API Posture Management- Concern.xlsx'
    stats = analyze_q12(file_path)
    print(json.dumps(stats, indent=2)) 