import pandas as pd
import json
from pathlib import Path

def analyze_q8(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    aiml_cols = [
        'Large Language Models (LLMs)',
        'Computer Vision APIs',
        'Custom ML Models'
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
    
    # Calculate statistics for each AIML type
    aiml_stats = {}
    for col in aiml_cols:
        aiml_stats[col] = calculate_stats(df[col])
    
    # Calculate breakdown by demographic factors
    demo_breakdowns = {}
    for demo in demo_cols:
        if demo in df.columns:
            demo_stats = {}
            for col in aiml_cols:
                # Convert DataFrame to dictionary for JSON serialization
                demo_stats[col] = df.groupby([demo, col]).size().unstack(fill_value=0).to_dict()
            demo_breakdowns[demo] = demo_stats

    summary = {
        'question_text': '8 API Usage in AIML Implementations- Deployment Model',
        'total_responses': total_responses,
        'aiml_stats': aiml_stats,
        'demographic_breakdowns': demo_breakdowns
    }
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 2/2.2 API Usage in AIML Implementations/7 API Usage in AIML Implementations- Deployment Model.xlsx'
    stats = analyze_q8(file_path)
    print(json.dumps(stats, indent=2)) 