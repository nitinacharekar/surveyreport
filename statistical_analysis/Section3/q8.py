import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary

def analyze_q8(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    concern_cols = [
        'API Discovery & Mapping',
        'API Posture Management',
        'API Access Control',
        'API Runtime Protection',
        'API Security Testing'
    ]
    value_cols = concern_cols

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
    for col in concern_cols:
        api_stats[col] = calculate_stats(df[col])
    
    # Calculate averages by extracting numeric values from the string
    def extract_numeric_rating(rating_str):
        try:
            return float(rating_str.split(' - ')[0])
        except Exception:
            return None

    api_averages = {}
    for col in concern_cols:
        numeric_ratings = df[col].apply(extract_numeric_rating)
        api_averages[col] = round(numeric_ratings.mean(), 2)

    summary = {
        'question_text': '8 For each of the following API security aspects, please rate how concerning they are for your organization?',
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
    file_path = '../../data/Section 3/3.0 Overall/8 API Security Concerns- Rating.xlsx'
    stats = analyze_q8(file_path)
    print(json.dumps(stats, indent=2)) 