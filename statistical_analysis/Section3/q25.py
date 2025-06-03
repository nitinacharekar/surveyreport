import pandas as pd
import json
from pathlib import Path

def analyze_q25(file_path: str):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    id_col = 'ID'
    demo_cols = ['Country']
    solution_cols = [
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
    solution_stats = {}
    for col in solution_cols:
        solution_stats[col] = calculate_stats(df[col])
    demo_breakdowns = {}
    for demo in demo_cols:
        if demo in df.columns:
            demo_stats = {}
            for col in solution_cols:
                demo_stats[col] = df.groupby([demo, col]).size().unstack(fill_value=0).to_dict()
            demo_breakdowns[demo] = demo_stats
    solution_averages = {col: round(df[col].mean(), 2) for col in solution_cols}
    summary = {
        'question_text': '25 Regulatory Compliance- Effectiveness',
        'total_responses': total_responses,
        'solution_stats': solution_stats,
        'demographic_breakdowns': demo_breakdowns,
        'solution_averages': solution_averages
    }
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 3/3.6 Regulatory Compliance/25 Regulatory Compliance- Effectiveness.xlsx'
    stats = analyze_q25(file_path)
    print(json.dumps(stats, indent=2)) 