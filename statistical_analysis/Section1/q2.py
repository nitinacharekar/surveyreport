import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary

def analyze_q2(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    expertise_col = 'Technical Expertise'
    tool_col = 'Tool Maturity'
    process_col = 'Process Maturity'
    value_cols = [expertise_col, tool_col, process_col]

    # Total responses
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
    
    # Calculate statistics for each metric
    expertise_stats = calculate_stats(df[expertise_col])
    tool_stats = calculate_stats(df[tool_col])
    process_stats = calculate_stats(df[process_col])
    
    # Calculate averages
    avg_expertise = df[expertise_col].mean()
    avg_tool = df[tool_col].mean()
    avg_process = df[process_col].mean()

    summary = {
        'question_text': '2 How mature are your organization\'s API security capabilities?',
        'total_responses': total_responses,
        'main_stats': {
            'technical_expertise': {
                'stats': expertise_stats,
                'average': round(avg_expertise, 2)
            },
            'tool_maturity': {
                'stats': tool_stats,
                'average': round(avg_tool, 2)
            },
            'process_maturity': {
                'stats': process_stats,
                'average': round(avg_process, 2)
            }
        }
    }
    
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)
    
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 1/2 Organizational API Security Readiness.xlsx'
    stats = analyze_q2(file_path)
    print(json.dumps(stats, indent=2)) 