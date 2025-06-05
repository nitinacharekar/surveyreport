'''
Analyzes data for Question 1: "How important is API security for your organization in the next 12 months?".

This script reads an Excel file containing survey responses related to the strategic
importance of API security. It assesses several facets: Business Impact, Digital
Transformation Priority, and Regulatory Compliance Requirement.
For each facet, it calculates overall statistics (e.g., distribution of responses,
averages) and also performs a demographic breakdown (e.g., by country).
It uses utility functions for statistics calculation and demographic analysis.
'''
import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path to enable imports from sibling directories
# (e.g., statistical_analysis.utils)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q1(file_path: str) -> dict:
    """
    Analyzes data on the strategic importance of API security (Question 1).

    The function reads data from the specified Excel file, cleans column names,
    and analyzes three key aspects: 'Business Impact', 'Digital Transformation Priority',
    and 'Regulatory compliance Requirement'. For each, it calculates descriptive
    statistics and the average score. It then adds a demographic analysis for these aspects.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary. This includes:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': A dictionary адвокатwith keys for each aspect (e.g.,
                'business_impact'), each containing its 'stats' (from `calculate_stats`)
                and 'average' score.
              - 'demographic_analysis': Breakdown of responses by demographic groups for
                the analyzed aspects (from `add_demographic_summary`).
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()

    # Define relevant column names present in the Excel file
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    impact_col = 'Business Impact'
    priority_col = 'Digital Transformation Priority'
    compliance_col = 'Regulatory compliance Requirement'
    # These are the columns whose values will be analyzed and broken down by demographics
    value_cols = [impact_col, priority_col, compliance_col]

    # Total number of responses
    total_responses = len(df)

    # Calculate statistics for each metric using the utility function
    impact_stats = calculate_stats(df[impact_col])
    priority_stats = calculate_stats(df[priority_col])
    compliance_stats = calculate_stats(df[compliance_col])

    # Calculate averages for an overall sense of importance (assuming numerical or ordinal scale)
    avg_impact = df[impact_col].mean()
    avg_priority = df[priority_col].mean()
    avg_compliance = df[compliance_col].mean()

    summary = {
        'question_text': '1 How important is API security for your organization in the next 12 months? ',
        'total_responses': total_responses,
        'main_stats': {
            'business_impact': {
                'stats': impact_stats,
                'average': round(avg_impact, 2) if pd.notnull(avg_impact) else None
            },
            'digital_transformation_priority': {
                'stats': priority_stats,
                'average': round(avg_priority, 2) if pd.notnull(avg_priority) else None
            },
            'regulatory_compliance': {
                'stats': compliance_stats,
                'average': round(avg_compliance, 2) if pd.notnull(avg_compliance) else None
            }
        }
    }

    # Add demographic analysis for the specified value columns
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)

    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    default_data_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Section 1', '1 Strategic Importance of API Security.xlsx')

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        # Fallback or error if file not found
        q1_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        q1_results = analyze_q1(default_data_file)
    
    print(json.dumps(q1_results, indent=2)) 