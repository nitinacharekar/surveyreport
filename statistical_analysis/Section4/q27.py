import pandas as pd
import json
from pathlib import Path
import sys
import os
import numpy as np

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q27(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    sub_questions = [col for col in df.columns if col.startswith('API') and ':' in col]
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    value_cols = sub_questions

    # Extract the initial question text (assume it's the same for all rows)
    question_text = df['Questions'].iloc[0] if 'Questions' in df.columns else None

    stats = {}
    total_sum = 0
    for col in sub_questions:
        stats[col] = {
            'stats': calculate_stats(df[col]),
            'mean': df[col].mean(),
            'median': df[col].median(),
            'mode': int(df[col].mode().iloc[0]) if not df[col].mode().empty else None,
            'std': df[col].std(),
            'sum': df[col].sum()
        }
        total_sum += df[col].sum()
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

    # Calculate overall average across all sub_questions
    all_means = [v['mean'] for v in stats.values()]
    overall_average = round(np.mean(all_means), 2) if all_means else None

    summary = {
        'question_text': '27 How ready is your organization in mitigating these risks?',
        'main_stats': {
            'sub_question_stats': stats,
            'overall_average': overall_average
        }
    }
    
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)
    
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 4/27 How ready is your organization in mitigating these risks.xlsx'
    stats = analyze_q27(file_path)
    print(json.dumps(stats, indent=2))
