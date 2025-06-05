"""Analyzes data for Question 27: \"How ready is your organization in mitigating these risks?\".\n\nThis script processes an Excel file where multiple columns represent sub-questions\n(identified by starting with \'API\' and containing \':\') related to organizational\nreadiness in mitigating various API security risks. For each sub-question, it calculates\na suite of statistics including mean, median, mode, sum, standard deviation, rank,\nand percentage contribution to a total sum.\n\nIt includes logic to convert NumPy data types to native Python types for JSON\nserialization and performs a demographic breakdown for all sub-questions.\n"""
import pandas as pd
import json
from pathlib import Path
import sys
import os
import numpy as np
import traceback

# Add the project root to Python path for utility imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q27(file_path: str) -> dict:
    """
    Analyzes organizational readiness in mitigating API security risks (Question 27).\n\n    The function reads data from an Excel file, identifies sub-questions based on column\n    name patterns (\'API*\':\'), and for each, calculates:\n    - Basic descriptive statistics (via `calculate_stats`).\n    - Mean, median, mode, standard deviation, and sum.\n    - Rank (based on mean) and percentage contribution to the total sum of all sub-question responses.\n\n    It also attempts to extract a general question text from a \'Questions\' column if present.\n    NumPy data types are converted to Python native types for JSON compatibility.\n    Finally, it adds a demographic analysis for all identified sub-questions.\n\n    Args:\n        file_path (str): Absolute or relative path to the Excel file.\n\n    Returns:\n        dict: A dictionary containing the analysis summary, including:\n              - \'question_text\': The text of the survey question (or a fallback).\n              - \'main_stats\': Contains \'sub_question_stats\' (a dictionary where each key\n                is a sub-question and value is its detailed statistics) and \'overall_average\'.\n              - \'demographic_analysis\': Demographic breakdown for all sub-questions.\n    """
    df = pd.read_excel(file_path, sheet_name="Data")
    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()
    
    # Identify metadata and risk columns
    metadata_cols = ['ID', 'Country', 'Age', 'Gender', 'Category']
    risk_cols = [col for col in df.columns if col not in metadata_cols]

    # Total responses = number of rows (respondents)
    total_responses = len(df)

    # Identify sub-question columns (e.g.,Likert scale responses for different risk mitigations)
    sub_questions = [col for col in df.columns if col.startswith('API') and ':' in col]

    if not sub_questions:
        # Handle case where no sub-question columns are found
        return {
            'question_text': '27 How ready is your organization in mitigating these risks? (No data columns found)',
            'main_stats': {'sub_question_stats': {}, 'overall_average': None},
            'demographic_analysis': {},
            'error': 'No sub-question columns found matching the pattern.'
        }

    # Identify other relevant columns
    id_col = 'ID' # Assuming an ID column exists
    demo_cols = ['Country'] # Columns for demographic breakdown
    value_cols = sub_questions # These are the columns whose values will be analyzed by demographics

    # Attempt to extract the initial question text. This is somewhat fragile.
    # It assumes a 'Questions' column exists and the first row is representative.
    question_text_from_file = df['Questions'].iloc[0] if 'Questions' in df.columns and not df.empty and not df['Questions'].empty else None

    sub_q_stats = {}
    total_sum_of_responses = 0
    for col in sub_questions:
        # Get the data for the column, ensuring it's a Series
        # (in case of duplicate column names in Excel, df[col] would be a DataFrame)
        data_series = df[col]
        if isinstance(data_series, pd.DataFrame):
            # Duplicate column name found. Using the data from the first instance.
            # A warning could be logged here in a more production-oriented script.
            data_series = data_series.iloc[:, 0]

        # Ensure data is numeric, coercing errors to NaN. Otherwise, .mean() etc. might fail.
        data_series = pd.to_numeric(data_series, errors='coerce')
        
        col_mean = data_series.mean()
        col_median = data_series.median()
        col_mode_series = data_series.mode()
        col_mode = int(col_mode_series.iloc[0]) if not col_mode_series.empty and pd.notna(col_mode_series.iloc[0]) else None
        col_std = data_series.std()
        col_sum = data_series.sum()

        sub_q_stats[col] = {
            'stats': calculate_stats(data_series.dropna()), # calculate_stats usually expects a Series without NaNs for some ops
            'mean': col_mean if pd.notna(col_mean) else None,
            'median': col_median if pd.notna(col_median) else None,
            'mode': col_mode,
            'std': col_std if pd.notna(col_std) else None,
            'sum': col_sum if pd.notna(col_sum) else 0 # Default sum to 0 if all are NaN
        }
        if pd.notna(col_sum):
            total_sum_of_responses += col_sum
           
    # Ranking and % contribution based on mean values
    # Filter out items with None means before sorting to avoid errors
    valid_means = {k: v['mean'] for k, v in sub_q_stats.items() if v['mean'] is not None}
    sorted_keys_by_mean = sorted(valid_means, key=valid_means.get, reverse=True)
    
    # Add items with None means at the end, or handle them as unranked
    for k_unranked in [k_item for k_item in sub_q_stats if k_item not in valid_means]:
        sorted_keys_by_mean.append(k_unranked)

    cumulative_percentage = 0
    for i, key_col in enumerate(sorted_keys_by_mean):
        if sub_q_stats[key_col]['mean'] is not None: # Only rank valid means
            sub_q_stats[key_col]['rank'] = i + 1
            contribution = (sub_q_stats[key_col]['sum'] / total_sum_of_responses * 100) if total_sum_of_responses else 0
            sub_q_stats[key_col]['percent_contribution'] = round(contribution, 2)
            cumulative_percentage += contribution
            sub_q_stats[key_col]['cumulative_percent_contribution'] = round(cumulative_percentage, 2)
        else:
            sub_q_stats[key_col]['rank'] = None # Unranked
            sub_q_stats[key_col]['percent_contribution'] = 0
            sub_q_stats[key_col]['cumulative_percent_contribution'] = round(cumulative_percentage, 2) # Keep last cumulative

    # Convert all numpy types to Python native types for JSON serialization
    def to_py_type(value_to_convert):
        if isinstance(value_to_convert, (np.integer, np.int64)): # Note: np.integer is deprecated, np.integral is current
            return int(value_to_convert)
        if isinstance(value_to_convert, (np.floating, np.float64)): # Note: np.floating is deprecated
            return float(value_to_convert)
        if pd.isna(value_to_convert):
            return None
        return value_to_convert

    for outer_key, inner_dict in sub_q_stats.items():
        for field_key, field_val in inner_dict.items():
            if field_key == 'stats': # field_val is the list of dicts from calculate_stats
                processed_stats_list = []
                if isinstance(field_val, list): # Ensure it's a list before iterating
                    for stat_item_dict in field_val:
                        processed_item_dict = {}
                        if isinstance(stat_item_dict, dict): # Ensure item in list is a dict
                            for sub_k, sub_v in stat_item_dict.items():
                                processed_item_dict[sub_k] = to_py_type(sub_v)
                        else: # Handle case where item in list is not a dict (e.g. if calculate_stats changes)
                            processed_item_dict = to_py_type(stat_item_dict) # Try to convert it directly
                        processed_stats_list.append(processed_item_dict)
                else: # Handle case where 'stats' field is not a list (e.g. if calculate_stats changes)
                    processed_stats_list = to_py_type(field_val) # Try to convert it directly
                sub_q_stats[outer_key][field_key] = processed_stats_list
            else: # For 'mean', 'median', etc. field_val should be scalar or None
                sub_q_stats[outer_key][field_key] = to_py_type(field_val)

    # Calculate overall average across all sub_questions' means
    all_valid_means = [item_v['mean'] for item_v in sub_q_stats.values() if item_v['mean'] is not None]
    overall_avg = round(np.mean(all_valid_means), 2) if all_valid_means else None

    summary_output = {
        'question_text': question_text_from_file if question_text_from_file else '27 How ready is your organization in mitigating these risks?',
        'total_responses': len(df), # Total number of respondents
        'main_stats': {
            'sub_question_stats': sub_q_stats,
            'overall_average_readiness': overall_avg
        }
    }
    
    # Add demographic analysis. This will create a breakdown for each sub_question in value_cols.
    summary_output = add_demographic_summary(summary_output, df, demo_cols, value_cols)
    
    return summary_output

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    default_data_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Section 4', '27 How ready is your organization in mitigating these risks.xlsx')

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q27_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q27_results = analyze_q27(default_data_file)
        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"Error analyzing file {default_data_file}: {e}")
            print(f"Full traceback:\n{error_trace}")
            q27_results = {"error": str(e), "traceback": error_trace}
    
    print(json.dumps(q27_results, indent=2))
