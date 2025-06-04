import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q9(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    solution_cols = [
        'API Discovery & Mapping',
        'API Posture Management',
        'API Access Control',
        'API Runtime Protection',
        'API Security Testing'
    ]
    value_cols = solution_cols

    # Total responses
    total_responses = len(df)
    
    # Calculate statistics for each solution
    solution_stats = {}
    for col in solution_cols:
        solution_stats[col] = calculate_stats(df[col])
    
    # Calculate averages by extracting numeric values from the string
    def extract_numeric_rating(rating_str):
        try:
            return float(rating_str.split(' - ')[0])
        except Exception:
            return None

    solution_averages = {}
    for col in solution_cols:
        numeric_ratings = df[col].apply(extract_numeric_rating)
        solution_averages[col] = round(numeric_ratings.mean(), 2)

    summary = {
        'question_text': '9 For each of the following API security aspects, please rate how concerning they are for your organization?',
        'total_responses': total_responses,
        'main_stats': {
            'solution_stats': solution_stats,
            'solution_averages': solution_averages
        }
    }
    
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)
    
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 3/3.0 Overall/9 API Security Concerns- Effectiveness of Current Solutions.xlsx'
    stats = analyze_q9(file_path)
    print(json.dumps(stats, indent=2)) 