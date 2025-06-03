import pandas as pd
import json
from pathlib import Path

def analyze_q21(file_path: str):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    id_col = 'ID'
    demo_cols = ['Country']
    answer_col = 'Answers'
    total_responses = len(df)
    def calculate_stats(series):
        stats = series.value_counts().sort_values(ascending=False)
        stats_df = pd.DataFrame({
            'value': stats.index,
            'count': stats.values
        })
        stats_df['rank'] = range(1, len(stats_df) + 1)
        stats_df['percent_contribution'] = (stats_df['count'] / stats_df['count'].sum() * 100).round(2)
        stats_df['cumulative_percent_contribution'] = stats_df['percent_contribution'].cumsum().round(2)
        return stats_df.to_dict(orient='records')
    answer_stats = calculate_stats(df[answer_col])
    demo_breakdowns = {}
    for demo in demo_cols:
        if demo in df.columns:
            demo_stats = df.groupby([demo, answer_col]).size().unstack(fill_value=0)
            demo_stats = (demo_stats.div(demo_stats.sum(axis=1), axis=0) * 100).round(2)
            demo_breakdowns[demo] = demo_stats.to_dict()
    summary = {
        'question_text': "21 How has code-based discovery improved your organization's API security",
        'total_responses': total_responses,
        'answer_stats': answer_stats,
        'demographic_breakdowns': demo_breakdowns
    }
    return summary

if __name__ == "__main__":
    file_path = "../../data/Section 3/3.5 API Security Testing/21 How has code-based discovery improved your organization's API security.xlsx"
    stats = analyze_q21(file_path)
    print(json.dumps(stats, indent=2)) 