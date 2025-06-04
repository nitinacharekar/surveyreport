import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q1(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Identify relevant columns
    id_col = 'ID'
    demo_cols = ['Country']
    impact_col = 'Business Impact'
    priority_col = 'Digital Transformation Priority'
    compliance_col = 'Regulatory compliance Requirement'
    value_cols = [impact_col, priority_col, compliance_col]

    # Total responses
    total_responses = len(df)
    
    # Calculate statistics for each metric
    impact_stats = calculate_stats(df[impact_col])
    priority_stats = calculate_stats(df[priority_col])
    compliance_stats = calculate_stats(df[compliance_col])
    
    # Calculate averages
    avg_impact = df[impact_col].mean()
    avg_priority = df[priority_col].mean()
    avg_compliance = df[compliance_col].mean()

    summary = {
        'question_text': '1 How important is API security for your organization in the next 12 months? ',
        'total_responses': total_responses,
        'main_stats': {
            'business_impact': {
                'stats': impact_stats,
                'average': round(avg_impact, 2)
            },
            'digital_transformation_priority': {
                'stats': priority_stats,
                'average': round(avg_priority, 2)
            },
            'regulatory_compliance': {
                'stats': compliance_stats,
                'average': round(avg_compliance, 2)
            }
        }
    }
    
    # Add demographic analysis
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)
    
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 1/1 Strategic Importance of API Security.xlsx'
    stats = analyze_q1(file_path)
    print(json.dumps(stats, indent=2)) 