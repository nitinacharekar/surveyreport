import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary

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
    investment_stats = df[answer_col].value_counts()
    stats_df = pd.DataFrame({
        'value': investment_stats.index,
        'count': investment_stats.values
    })
    stats_df['rank'] = range(1, len(stats_df) + 1)
    stats_df['percent_contribution'] = (stats_df['count'] / stats_df['count'].sum() * 100).round(2)
    stats_df['cumulative_percent_contribution'] = stats_df['percent_contribution'].cumsum().round(2)
    investment_stats = stats_df.to_dict(orient='records')
    

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