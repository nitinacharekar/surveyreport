import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q4(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    answer_col = 'Answers'
    value_cols = [answer_col]

    # Total responses
    total_responses = len(df)
    
    # Calculate investment trend distribution with standard stats
    investment_stats = calculate_stats(df[answer_col])
    
    summary = {
        'question_text': '4 How do you expect your API security investment to change in the next 12 months?',
        'total_responses': total_responses,
        'main_stats': investment_stats,
    }
    
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)
    
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 1/4 Security Investment Trends.xlsx'
    stats = analyze_q4(file_path)
    print(json.dumps(stats, indent=2)) 