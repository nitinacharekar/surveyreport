import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary

def analyze_q5(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    api_cols = [
        'Customer-facing public APIs',
        'Partner integration APIs',
        'Internal system APIs',
        'B2B marketplace APIs',
        'Mobile app backend APIs'
    ]
    value_cols = api_cols

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
    
    # Calculate statistics for each API type
    api_stats = {}
    for col in api_cols:
        api_stats[col] = calculate_stats(df[col])
    
    # Calculate averages
    api_averages = {col: round(df[col].mean(), 2) for col in api_cols}

    summary = {
        'question_text': '5 How frequently does your organization use the following types of APIs?',
        'total_responses': total_responses,
        'main_stats': {
            'api_stats': api_stats,
            'api_averages': api_averages
        }
    }
    
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)
    
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 2/2.1 API Usage Classification/5 API Usage Classification- Business Purpose APIs.xlsx'
    stats = analyze_q5(file_path)
    print(json.dumps(stats, indent=2)) 