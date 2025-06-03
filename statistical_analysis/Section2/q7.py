import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary

def analyze_q7(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    aiml_cols = [
        'Large Language Models (LLMs)',
        'Computer Vision APIs',
        'Custom ML models'
    ]
    value_cols = aiml_cols

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
    
    # Calculate statistics for each AIML type
    aiml_stats = {}
    for col in aiml_cols:
        aiml_stats[col] = calculate_stats(df[col])
    
    # Calculate averages
    aiml_averages = {col: round(df[col].mean(), 2) for col in aiml_cols}

    summary = {
        'question_text': '7 How frequently does your organization use the following AI/ML APIs?',
        'total_responses': total_responses,
        'main_stats': {
            'aiml_stats': aiml_stats,
            'aiml_averages': aiml_averages
        }
    }
    
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)
    
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 2/2.2 API Usage in AIML Implementations/6 API Usage in AIML Implementations- Frequency.xlsx'
    stats = analyze_q7(file_path)
    print(json.dumps(stats, indent=2)) 