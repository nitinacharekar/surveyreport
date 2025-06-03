import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary

def analyze_q8(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    aiml_cols = [
        'Large Language Models (LLMs)',
        'Computer Vision APIs',
        'Custom ML Models'
    ]
    value_cols = aiml_cols

    # Total responses
    total_responses = len(df)
    
    def calculate_stats(series):
        # Calculate value counts for categorical data
        value_counts = series.value_counts()
        total = value_counts.sum()
        
        # Create stats dictionary with counts and percentages
        stats = {
            'distribution': {
                str(k): {
                    'count': int(v),
                    'percentage': round((v / total) * 100, 2)
                } for k, v in value_counts.items()
            },
            'total_responses': int(total)
        }
        
        # Add ranking based on count
        sorted_items = sorted(stats['distribution'].items(), 
                            key=lambda x: x[1]['count'], 
                            reverse=True)
        for rank, (key, _) in enumerate(sorted_items, 1):
            stats['distribution'][key]['rank'] = rank
            
        return stats
    
    # Calculate statistics for each AIML type
    aiml_stats = {}
    for col in aiml_cols:
        aiml_stats[col] = calculate_stats(df[col])

    summary = {
        'question_text': '8 What is the deployment model for each AI/ML API your organization uses?',
        'total_responses': total_responses,
        'main_stats': aiml_stats
    }
    
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)
    
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 2/2.2 API Usage in AIML Implementations/7 API Usage in AIML Implementations- Deployment Model.xlsx'
    stats = analyze_q8(file_path)
    print(json.dumps(stats, indent=2)) 