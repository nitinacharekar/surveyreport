import pandas as pd
import json
from pathlib import Path
import sys
import os
# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q20(file_path: str):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    id_col = 'ID'
    demo_cols = ['Country']
    answer_col = 'Answers'
    total_responses = len(df)
    answer_stats = calculate_stats(df[answer_col])
    
    # Calculate average if the answers are numeric or can be converted
    try:
        answer_numeric = pd.to_numeric(df[answer_col], errors='coerce')
        answer_average = round(answer_numeric.mean(), 2)
    except Exception:
        answer_average = None

    summary = {
        'question_text': '20 Which stage of the API lifecycle would benefit most from the following discovery method in your organization?',
        'total_responses': total_responses,
        'main_stats': {
            'answer_stats': answer_stats,
            'answer_average': answer_average
        },

    }
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, [answer_col])
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 3/3.5 API Security Testing/20 Which stage of the API lifecycle would benefit most.xlsx'
    stats = analyze_q20(file_path)
    print(json.dumps(stats, indent=2)) 