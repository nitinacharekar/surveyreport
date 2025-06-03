import pandas as pd
import json
from pathlib import Path
import numpy as np

def analyze_q27(file_path: str):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    sub_questions = [col for col in df.columns if col.startswith('API') and ':' in col]
    demo_cols = ['Country']

    # Extract the initial question text (assume it's the same for all rows)
    question_text = df['Questions'].iloc[0] if 'Questions' in df.columns else None

    stats = {}
    total_sum = 0
    for col in sub_questions:
        col_sum = df[col].sum()
        total_sum += col_sum
        stats[col] = {
            'mean': df[col].mean(),
            'median': df[col].median(),
            'mode': int(df[col].mode().iloc[0]) if not df[col].mode().empty else None,
            'std': df[col].std(),
            'distribution': {str(k): int(v) for k, v in df[col].value_counts().sort_index().to_dict().items()},
            'sum': col_sum
        }
    # Ranking and % contribution
    means = {k: v['mean'] for k, v in stats.items()}
    contributions = {k: stats[k]['sum'] / total_sum * 100 if total_sum else 0 for k in stats.keys()}
    sorted_keys = sorted(means, key=means.get, reverse=True)
    cumulative = 0
    for i, k in enumerate(sorted_keys):
        stats[k]['rank'] = i + 1
        stats[k]['percent_contribution'] = round(contributions[k], 2)
        cumulative += contributions[k]
        stats[k]['cumulative_percent_contribution'] = round(cumulative, 2)

    # Convert all numpy types to Python native types for JSON serialization
    def to_py_type(val):
        if isinstance(val, (np.integer,)):
            return int(val)
        if isinstance(val, (np.floating,)):
            return float(val)
        return val
    for k in stats:
        for field in stats[k]:
            stats[k][field] = to_py_type(stats[k][field])

    # Demographic breakdowns (optional)
    demo_breakdowns = {}
    for demo in demo_cols:
        if demo in df.columns:
            demo_breakdowns[demo] = {}
            for val in df[demo].dropna().unique():
                demo_df = df[df[demo] == val]
                demo_breakdowns[demo][str(val)] = {
                    col: {str(k): int(v) for k, v in demo_df[col].value_counts().sort_index().to_dict().items()} for col in sub_questions
                }

    summary = {
        'question_text': question_text,
        'sub_question_stats': stats,
        'demographic_breakdowns': demo_breakdowns
    }
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 4/27 How ready is your organization in mitigating these risks.xlsx'
    stats = analyze_q27(file_path)
    print(json.dumps(stats, indent=2))
