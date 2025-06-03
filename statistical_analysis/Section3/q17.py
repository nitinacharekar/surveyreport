import pandas as pd
import json
from pathlib import Path

def analyze_q17(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    solution_cols = [
        'Data Leakage',
        'Data Tampering',
        'Data Policy Violations',
        'Sensitive Data Detection and Masking',
        'API Security Attacks',
        'ML-based Traffic Monitoring',
        'Automated Policy Generation',
        'Suspicious Behaviour',
        'Open API Specification/Swagger enforcement',
        'Malicious user detection'
    ]

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
    
    # Calculate statistics for each solution
    solution_stats = {}
    for col in solution_cols:
        solution_stats[col] = calculate_stats(df[col])
    
    # Calculate breakdown by demographic factors
    demo_breakdowns = {}
    for demo in demo_cols:
        if demo in df.columns:
            demo_stats = {}
            for col in solution_cols:
                # Convert DataFrame to dictionary for JSON serialization
                demo_stats[col] = df.groupby([demo, col]).size().unstack(fill_value=0).to_dict()
            demo_breakdowns[demo] = demo_stats

    # Calculate averages by extracting numeric values
    def extract_numeric_rating(rating_str):
        try:
            return float(rating_str.split(' - ')[0])
        except:
            return None
    
    solution_averages = {col: round(df[col].mean(), 2) for col in solution_cols}

    summary = {
        'question_text': '17 API Runtime- Effectiveness',
        'total_responses': total_responses,
        'solution_stats': solution_stats,
        'demographic_breakdowns': demo_breakdowns,
        'solution_averages': solution_averages
    }
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 3/3.4 API Runtime/17 API Runtime- Effectiveness.xlsx'
    stats = analyze_q17(file_path)
    print(json.dumps(stats, indent=2)) 