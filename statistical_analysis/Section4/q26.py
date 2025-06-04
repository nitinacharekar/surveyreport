import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q26(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    answer_col = 'Answers'
    risk_col = df.columns[5]  # Assuming the 6th column is the risk name
    id_col = 'ID'
    demo_cols = ['Country']
    value_cols = [answer_col]

    # Total responses
    total_responses = len(df)
    # Total selected (Answer == 1)
    total_selected = df[answer_col].sum()
    percent_selected = (total_selected / total_responses) * 100

    # Calculate stats for each risk (where answer_col == 1)
    filtered = df[df[answer_col] == 1]
    risk_stats = calculate_stats(filtered[risk_col])

    summary = {
        'question_text': '26 Select the top 3 OWASP API security risks your organization is most concerned about',
        'total_responses': total_responses,
        'total_selected': int(total_selected),
        'percent_selected': round(percent_selected, 2),
        'main_stats': {
            'risk_stats': risk_stats,
            'average_selected': round(df[answer_col].mean(), 2)
        }
    }
    
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)
    
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 4/26 Select the top 3 OWASP API security risks your organization is most concerned about.xlsx'
    stats = analyze_q26(file_path)
    print(json.dumps(stats, indent=2)) 