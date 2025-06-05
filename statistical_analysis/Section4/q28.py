"""
Analyzes data for Question 28: "What security measures does your organization currently have in place to protect APIs?".

This script reads an Excel file where survey respondents indicate which security measures
they have in place. It calculates statistics on the prevalence of different security
measures and performs a demographic breakdown.

Note: The script uses a hardcoded string for `measure_col` which is presumed to be the
column in the Excel sheet that lists the names/types of security measures. If this is not
the actual column name, the script will fail or produce incorrect results.
The `Answers` column is assumed to indicate if a measure is selected (e.g., with a 1).
"""
import pandas as pd
import json
from pathlib import Path
import sys
import os
import traceback

# Add the project root to Python path for utility imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q28(file_path: str) -> dict:
    """
    Analyzes data on API security measures in place (Question 28).

    The function reads data from an Excel file. It expects a column (currently hardcoded
    as 'What security measures does your organization currently have in place to protect APIs?',
    which should be the actual column name listing measure types) and an 'Answers' column
    (e.g., 1 if the measure is selected).
    It calculates the distribution of selected security measures and an average selection count.
    Demographic analysis is also performed on the selected measures.

    Args:
        file_path (str): Absolute or relative path to the Excel file.

    Returns:
        dict: A dictionary containing the analysis summary, including:
              - 'question_text': The text of the survey question.
              - 'total_selected_entries': Total count of selected security measure entries.
              - 'main_stats': Contains 'measure_distribution' (distribution of selected measures)
                              and 'average_selections_per_measure_type'.
              - 'demographic_analysis': Demographic breakdown of selected measures.
    Raises:
        KeyError: If the assumed `measure_col` or `answer_col` are not in the Excel file.
    """
    df = pd.read_excel(file_path)
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()

    # Relevant columns
    demo_cols = ['Country'] # Columns for demographic breakdown
    
    # IMPORTANT: `measure_col` is currently a literal string of the question.
    # This MUST be updated to the actual column name in the Excel file that contains
    # the *names* or *types* of the security measures.
    # For example, if the column is named 'SecurityMeasureType', then use that.
    measure_col = 'What security measures does your organization currently have in place to protect APIs?'
    answer_col = 'Answers' # Column indicating if the measure is selected (e.g., value is 1)

    # Verify essential columns exist
    if measure_col not in df.columns:
        raise KeyError(f"The expected measure column '{measure_col}' was not found in the file {file_path}. Please verify the column name.")
    if answer_col not in df.columns:
        raise KeyError(f"The expected answer column '{answer_col}' was not found in the file {file_path}.")

    # Filter only rows where the measure was selected (Answers == 1)
    selected_df = df[df[answer_col] == 1].copy() # Use .copy() to avoid SettingWithCopyWarning
    total_selected_entries = len(selected_df)

    # Calculate statistics for the types of measures selected
    # `calculate_stats` will count occurrences of each unique value in `selected_df[measure_col]`
    measure_distribution_stats = calculate_stats(selected_df[measure_col]) if not selected_df.empty else {}

    # Calculate average selections per type of measure (if meaningful for the data structure)
    # This assumes `measure_distribution_stats` gives a count for each type of measure.
    # The average would be total selections divided by the number of unique measure types that were selected at least once.
    num_unique_selected_measures = len(measure_distribution_stats) # Corrected: calculate_stats returns a list of dicts
    avg_selections_per_measure_type = round(total_selected_entries / num_unique_selected_measures, 2) if num_unique_selected_measures > 0 else 0

    summary = {
        'question_text': '28 What security measures does your organization currently have in place to protect APIs',
        'total_selected_entries': total_selected_entries, # Total number of times any measure was marked as selected
        'main_stats': {
            'measure_distribution': measure_distribution_stats, # Distribution of the types of security measures selected
            'average_selections_per_measure_type': avg_selections_per_measure_type
        }
    }
    
    # Add demographic analysis: how selection of different measures breaks down by demographic groups.
    # This uses `selected_df` to only analyze demographics for measures that were actually selected.
    if not selected_df.empty:
        summary = add_demographic_summary(summary, selected_df, demo_cols, [measure_col])
    else:
        summary['demographic_analysis'] = {} # Ensure key exists even if no data
        
    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    default_data_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Section 4', '28 What security measures does your organization currently have in place to protect APIs.xlsx')

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q28_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q28_results = analyze_q28(default_data_file)
        except KeyError as e:
            print(f"Error analyzing file {default_data_file}: Missing column - {e}")
            q28_results = {"error": f"Missing column: {e}"}
        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"An unexpected error occurred while analyzing {default_data_file}: {e}")
            print(f"Full traceback:\n{error_trace}")
            q28_results = {"error": str(e), "traceback": error_trace}
    
    print(json.dumps(q28_results, indent=2))
