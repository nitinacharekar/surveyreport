import pandas as pd
import json
from pathlib import Path

def analyze_q11(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    solution_cols = [
        'Shadow/ undocumented APIs',
        'Zombie/ dormant APIs',
        'API Usage & Visualization',
        'API Cost / Metering / Billing',
        'Identifying APIs relevant for compliance (privacy, resilience, etc.)'
    ]

    # Total responses
    total_responses = len(df)
    
    def calculate_stats(series):
        stats = series.value_counts()
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

    summary = {
        'question_text': '11 API Discovery & Mapping- Effectiveness of Current Solutions',
        'total_responses': total_responses,
        'solution_stats': solution_stats,
        'demographic_breakdowns': demo_breakdowns
    }
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 3/3.1 API Discovery & Mapping/11 API Discovery & Mapping- Effectiveness of Current Solutions.xlsx'
    stats = analyze_q11(file_path)
    print(json.dumps(stats, indent=2)) 