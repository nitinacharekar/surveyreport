import pandas as pd
import json
from pathlib import Path

def analyze_q6(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country', 'Gender', 'Age']
    expected_api_cols = [
        'REST APIs',
        'GraphQL APIs',
        'gRPC/RPC APIs',
        'Event-driven APIs',
        'Streaming APIs',
    ]
    # Only use columns that exist in the DataFrame
    api_cols = [col for col in expected_api_cols if col in df.columns]
    missing_cols = [col for col in expected_api_cols if col not in df.columns]
    if missing_cols:
        print(f"Warning: The following columns are missing in the file and will be skipped: {missing_cols}")

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
    
    # Calculate statistics for each API type
    api_stats = {}
    for col in api_cols:
        api_stats[col] = calculate_stats(df[col])
    
    # Calculate averages
    api_averages = {col: round(df[col].mean(), 2) for col in api_cols}

    summary = {
        'question_text': '6 API Usage Classification- Technical Architecture APIs',
        'total_responses': total_responses,
        'api_stats': api_stats,
        'api_averages': api_averages,
    }
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 2/2.1 API Usage Classification/6 API Usage Classification- Technical Architecture APIs.xlsx'
    stats = analyze_q6(file_path)
    print(json.dumps(stats, indent=2)) 