'''
Analyzes data for Question 2: "How mature are your organization's API security capabilities?".

This script reads an Excel file containing survey responses related to the maturity of an
organization's API security capabilities. It assesses three key areas: Technical Expertise,
Tool Maturity, and Process Maturity.
For each area, it calculates overall statistics (e.g., distribution of responses,
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

def analyze_q2(file_path: str) -> dict:
    """
    Analyzes data on the maturity of organizational API security capabilities (Question 2).

    The function reads data from the specified Excel file, cleans column names,
    and analyzes three key aspects: 'Technical Expertise', 'Tool Maturity',
    and 'Process Maturity'. For each, it calculates descriptive
    statistics and the average score. It then adds a demographic analysis for these aspects.

    Args:
        file_path (str): Absolute or relative path to the Excel file containing the data.

    Returns:
        dict: A dictionary containing the analysis summary. This includes:
              - 'question_text': The text of the survey question.
              - 'total_responses': The total number of responses.
              - 'main_stats': A dictionary with keys for each aspect (e.g.,
                'technical_expertise'), each containing its 'stats' (from `calculate_stats`)
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
    expertise_col = 'Technical Expertise'
    tool_col = 'Tool Maturity'
    process_col = 'Process Maturity'
    # These are the columns whose values will be analyzed and broken down by demographics
    value_cols = [expertise_col, tool_col, process_col]

    # Total number of responses
    total_responses = len(df)

    # Calculate statistics for each metric using the utility function
    expertise_stats = calculate_stats(df[expertise_col])
    tool_stats = calculate_stats(df[tool_col])
    process_stats = calculate_stats(df[process_col])

    # Calculate averages for an overall sense of maturity (assuming numerical or ordinal scale)
    avg_expertise = df[expertise_col].mean()
    avg_tool = df[tool_col].mean()
    avg_process = df[process_col].mean()

    summary = {
        'question_text': '2 How mature are your organization\'s API security capabilities?',
        'total_responses': total_responses,
        'main_stats': {
            'technical_expertise': {
                'stats': expertise_stats,
                'average': round(avg_expertise, 2) if pd.notnull(avg_expertise) else None
            },
            'tool_maturity': {
                'stats': tool_stats,
                'average': round(avg_tool, 2) if pd.notnull(avg_tool) else None
            },
            'process_maturity': {
                'stats': process_stats,
                'average': round(avg_process, 2) if pd.notnull(avg_process) else None
            }
        }
    }

    # Add demographic analysis for the specified value columns
    summary = add_demographic_summary(summary, df, demo_cols, value_cols)

    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    default_data_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Section 1', '2 Organizational API Security Readiness.xlsx')

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        # Fallback or error if file not found
        q2_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        q2_results = analyze_q2(default_data_file)
    
    print(json.dumps(q2_results, indent=2)) 