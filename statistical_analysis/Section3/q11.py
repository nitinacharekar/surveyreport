import pandas as pd
import json
from pathlib import Path
import sys
import os
# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

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
    
    # Calculate statistics for each solution
    solution_stats = {}
    for col in solution_cols:
        solution_stats[col] = calculate_stats(df[col])
    

    summary = {
        'question_text': '11 How effective are your current solutions in addressing the following API Discovery challenges within your organization?',
        'total_responses': total_responses,
        'main_stats': {
            'concern_stats': solution_stats,
            'concern_averages': solution_stats
        }
    }
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, solution_cols)
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 3/3.1 API Discovery & Mapping/11 API Discovery & Mapping- Effectiveness of Current Solutions.xlsx'
    stats = analyze_q11(file_path)
    print(json.dumps(stats, indent=2)) 