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
    concern_cols = [
        'API Discovery & Mapping',
        'API Posture Management',
        'API Access Control',
        'API Runtime Protection',
        'API Security Testing'
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
    
    # Calculate averages by extracting numeric values
    def extract_numeric_rating(rating_str):
        try:
            return float(rating_str.split(' - ')[0])
        except:
            return None
    
    concern_averages = {}
    for col in concern_cols:
        numeric_ratings = df[col].apply(extract_numeric_rating)
        concern_averages[col] = round(numeric_ratings.mean(), 2)

    summary = {
        'question_text': '8 API Security Concerns- Rating',
        'total_responses': total_responses,
        'concern_stats': concern_stats,
        'concern_averages': concern_averages
    }
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 3/3.0 Overall/8 API Security Concerns- Rating.xlsx'
    stats = analyze_q8(file_path)
    print(json.dumps(stats, indent=2)) 