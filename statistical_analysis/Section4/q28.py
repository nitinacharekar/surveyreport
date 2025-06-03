import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary

def analyze_q28(file_path: str):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    
    # Relevant columns
    demo_cols = ['Country']
    measure_col = 'What security measures does your organization currently have in place to protect APIs?'
    answer_col = 'Answers'

    # Filter only selected answers
    selected = df[df[answer_col] == 1]
    total_selected = len(selected)

    # Count occurrences of each security measure where Answers == 1
    measure_counts = selected[measure_col].value_counts().to_dict()
    
    # Calculate percentages
    measure_stats = {}
    for measure, count in measure_counts.items():
        measure_stats[measure] = {
            'count': int(count),
            'percentage': round((count / total_selected) * 100, 2) if total_selected else 0
        }
    # Add ranking
    sorted_measures = sorted(measure_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    for i, (measure, stats) in enumerate(sorted_measures, 1):
        measure_stats[measure]['rank'] = i

    # Calculate average count per measure
    avg_count = round(total_selected / len(measure_stats), 2) if measure_stats else 0

    summary = {
        'question_text': '28 What security measures does your organization currently have in place to protect APIs',
        'total_selected': total_selected,
        'main_stats': {
            'measure_stats': measure_stats,
            'average_count_per_measure': avg_count
        }
    }
    # Add demographic analysis (optional, if you want breakdowns by country)
    summary = add_demographic_summary(summary, df, demo_cols, [measure_col])
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 4/28 What security measures does your organization currently have in place to protect APIs.xlsx'
    stats = analyze_q28(file_path)
    print(json.dumps(stats, indent=2))
