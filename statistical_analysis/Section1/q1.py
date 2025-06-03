import pandas as pd
import json
from pathlib import Path

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
    impact_stats = calculate_stats(df[impact_col])
    priority_stats = calculate_stats(df[priority_col])
    compliance_stats = calculate_stats(df[compliance_col])
    
    # Calculate averages
    avg_impact = df[impact_col].mean()
    avg_priority = df[priority_col].mean()
    avg_compliance = df[compliance_col].mean()

    summary = {
        'question_text': '1 Strategic Importance of API Security',
        'total_responses': total_responses,
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
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 1/1 Strategic Importance of API Security.xlsx'
    stats = analyze_q1(file_path)
    print(json.dumps(stats, indent=2)) 