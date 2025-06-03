import pandas as pd
import json
from pathlib import Path

def analyze_q3(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country', 'Gender', 'Age']
    answer_col = 'Answers'

    # Total responses
    total_responses = len(df)
    
    # Calculate responsibility distribution with standard stats
    responsibility_stats = df[answer_col].value_counts()
    stats_df = pd.DataFrame({
        'value': responsibility_stats.index,
        'count': responsibility_stats.values
    })
    stats_df['rank'] = range(1, len(stats_df) + 1)
    stats_df['percent_contribution'] = (stats_df['count'] / stats_df['count'].sum() * 100).round(2)
    stats_df['cumulative_percent_contribution'] = stats_df['percent_contribution'].cumsum().round(2)
    responsibility_stats = stats_df.to_dict(orient='records')
    
    # Calculate breakdown by demographic factors
    demo_breakdowns = {}
    for demo in demo_cols:
        if demo in df.columns:
            demo_stats = df.groupby([demo, answer_col]).size().unstack(fill_value=0)
            demo_stats = (demo_stats.div(demo_stats.sum(axis=1), axis=0) * 100).round(2)
            demo_breakdowns[demo] = demo_stats.to_dict()

    summary = {
        'question_text': '3 Who has primary responsibility',
        'total_responses': total_responses,
        'responsibility_stats': responsibility_stats,
        'demographic_breakdowns': demo_breakdowns
    }
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 1/3 Who has primary responsibility.xlsx'
    stats = analyze_q3(file_path)
    print(json.dumps(stats, indent=2)) 