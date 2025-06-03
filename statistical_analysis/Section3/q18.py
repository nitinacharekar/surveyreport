import pandas as pd
import json
from pathlib import Path

def analyze_q18(file_path: str):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    id_col = 'ID'
    demo_cols = ['Country']
    concern_cols = [
        'Code-based discovery (e.g., static/dynamic code analysis)',
        'Crawler-based discovery (e.g., scanning APIs)',
        'Traffic-based discovery (e.g., monitoring API traffic)'
    ]
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
    concern_stats = {}
    for col in concern_cols:
        concern_stats[col] = calculate_stats(df[col])
    concern_averages = {col: round(df[col].mean(), 2) for col in concern_cols}
    summary = {
        'question_text': '18 API Security Testing- Concern',
        'total_responses': total_responses,
        'concern_stats': concern_stats,
        'concern_averages': concern_averages
    }
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 3/3.5 API Security Testing/18 API Security Testing- Concern.xlsx'
    stats = analyze_q18(file_path)
    print(json.dumps(stats, indent=2)) 