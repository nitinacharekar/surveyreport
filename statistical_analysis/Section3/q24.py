import pandas as pd
import json
from pathlib import Path

def analyze_q24(file_path: str):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    id_col = 'ID'
    demo_cols = ['Country']
    concern_cols = [
        'Data residency requirements',
        'Cross-border data transfer restrictions',
        'Privacy law compliance',
        'Industry-specific regulations',
        'Unclear or rapidly evolving regulatory landscape'
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
        'question_text': '24 Regulatory Compliance- Concern',
        'total_responses': total_responses,
        'concern_stats': concern_stats,
        'concern_averages': concern_averages
    }
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 3/3.6 Regulatory Compliance/24 Regulatory Compliance- Concern.xlsx'
    stats = analyze_q24(file_path)
    print(json.dumps(stats, indent=2)) 