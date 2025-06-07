import pandas as pd
from typing import Dict, List
import numpy as np
import os
import json
from .scope_config import SCOPE_MAP
from .question_config import QUESTION_MAP

# Helper function to convert NumPy types to native Python types for JSON serialization
def convert_to_py_types(obj):
    if isinstance(obj, dict):
        return {k: convert_to_py_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_py_types(elem) for elem in obj]
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif pd.isna(obj): # Handles pd.NA, np.nan, pd.NaT if they were to appear
        return None
    return obj

def analyze_excel(
    file_path: str,
    analysis_data_type: str = "string & number",
    data_columns: list = None,
    data_sheet: str = "Data",
    legend_sheet: str = "Legend",
    country_scope: list = None
) -> dict:
    """
    Generalized analysis function for survey-style Excel sheets.
    Performs string and/or numeric analysis on data filtered by a scope.
    The scope is defined by a list of values (e.g., countries) in the 'Country' column.
    """

    # Load sheets
    df = pd.read_excel(file_path, sheet_name=data_sheet)
    legend_df = pd.read_excel(file_path, sheet_name=legend_sheet)

    # Clean column names
    df.columns = df.columns.str.strip()
    legend_df.columns = legend_df.columns[:2]
    legend_df.columns = ["Value", "Label"]
    
    # Determine scope before filtering
    final_scope = country_scope
    if not final_scope:
        final_scope = df["Country"].dropna().unique().tolist()

    # Filter data based on country_scope if provided
    if country_scope:
        df = df[df["Country"].isin(country_scope)].copy()

    # Set defaults if not provided
    if data_columns is None:
        data_columns = ["Answer"]
        
    # Build legend mapping
    legend_map = dict(zip(legend_df["Value"], legend_df["Label"]))
    
    summary = {
        "data_columns": data_columns,
        "scope": final_scope,
        "analysis_data_type": analysis_data_type
    }

    # Perform analyses using utility functions
    summary["analysis_by_data_column"] = analyze_by_data_column(df, data_columns, legend_map, analysis_data_type)
    summary["analysis_by_legend"] = analyze_by_legend_label(df, data_columns, legend_map)

    return summary

def analyze_by_data_column(df: pd.DataFrame, data_columns: List[str], legend_map: Dict, analysis_data_type: str) -> Dict:
    """
    Performs analysis on a DataFrame, grouping results by data columns.
    """
    analysis_results = {}
    for col in data_columns:
        series = df[col].dropna() 
        col_summary = {}

        # Perform string analysis if applicable
        if analysis_data_type in ["string", "string & number"] and pd.api.types.is_numeric_dtype(series):
            string_series_scope = series.map(legend_map).dropna()

            if not string_series_scope.empty:
                counts_scope = string_series_scope.value_counts()
                sorted_top_scope = counts_scope.sort_values(ascending=False)
                
                valid_sorted_legend_keys = sorted([k for k in legend_map.keys() if pd.notna(k)])
                list_of_ordered_labels = [legend_map.get(key, "Unknown") for key in valid_sorted_legend_keys]
                list_of_ordered_labels = pd.Series(list_of_ordered_labels).unique().tolist()

                ordered_counts_scope = counts_scope.reindex(list_of_ordered_labels).fillna(0)

                total_count = counts_scope.sum()
                cumulative_top_percent = (sorted_top_scope.cumsum() / total_count * 100).round(2)
                cumulative_sequential_top_percent = (ordered_counts_scope.cumsum() / total_count * 100).round(2)

                col_summary["string_analysis"] = {
                    "counts": counts_scope.to_dict(),
                    "rank_top": sorted_top_scope.index.tolist(),
                    "cumulative_top": cumulative_top_percent.to_dict(),
                    "cumulative_sequential_top": cumulative_sequential_top_percent.to_dict()
                }
            else:
                 col_summary["string_analysis"] = {
                    "counts": {}, "rank_top": [], "cumulative_top": {}, "cumulative_sequential_top": {}
                }
        
        # Perform number analysis if applicable
        if analysis_data_type in ["number", "string & number"] and pd.api.types.is_numeric_dtype(series):
            if not series.empty:
                col_summary["number_analysis"] = {
                    "mean": round(series.mean(), 2),
                    "median": round(series.median(), 2),
                    "std_dev": round(series.std(), 2)
                }
            else:
                 col_summary["number_analysis"] = {
                    "mean": None, "median": None, "std_dev": None
                }
        
        if col_summary:
            analysis_results[col] = col_summary
    
    return analysis_results

def analyze_by_legend_label(df: pd.DataFrame, data_columns: List[str], legend_map: Dict) -> Dict:
    """
    Performs analysis on a DataFrame, grouping results by legend labels.
    """
    analysis_by_legend = {}
    unique_labels = sorted(list(set(legend_map.values())))

    for label in unique_labels:
        label_analysis = {}
        counts_per_column = {}
        
        for data_col in data_columns:
            if pd.api.types.is_numeric_dtype(df[data_col]):
                mapped_series = df[data_col].map(legend_map)
                count = int((mapped_series == label).sum())
                counts_per_column[data_col] = count
            else:
                counts_per_column[data_col] = 0
                
        counts_series = pd.Series(counts_per_column)
        sorted_top = counts_series.sort_values(ascending=False)
        
        # Ensure a consistent, predictable order for the sequential analysis
        sequential_order = sorted(data_columns)
        ordered_counts = counts_series.reindex(sequential_order).fillna(0)

        total_count = counts_series.sum()
        cumulative_top_percent = (sorted_top.cumsum() / total_count * 100).round(2) if total_count > 0 else sorted_top.cumsum()
        cumulative_sequential_top_percent = (ordered_counts.cumsum() / total_count * 100).round(2) if total_count > 0 else ordered_counts.cumsum()

        label_analysis["string_analysis_of_data_columns"] = {
            "counts": counts_series.to_dict(),
            "rank_top": sorted_top.index.tolist(),
            "cumulative_top": cumulative_top_percent.to_dict(),
            "cumulative_sequential_top": cumulative_sequential_top_percent.to_dict()
        }
        
        analysis_by_legend[label] = label_analysis

    return analysis_by_legend 

def run_analysis_and_print(question_key: str, scope_name: str, analysis_data_type: str, section: str):
    """
    Runs the survey analysis for a given question and scope, and prints the output.
    Assumes a standard project directory structure.
    """
    # --- Look up question configuration ---
    question_config = QUESTION_MAP.get(question_key)
    if not question_config:
        print(f"Error: Question key '{question_key}' not found in configuration. Aborting analysis.")
        return
        
    data_file_name = question_config.get("file_name")
    data_columns = question_config.get("data_columns")

    if not data_file_name or data_columns is None:
        print(f"Error: 'file_name' or 'data_columns' not configured for question key '{question_key}'. Aborting analysis.")
        return

    # --- Look up scope ---
    # If scope_name is None or "Overall", scope_of_analysis will be None, triggering analysis on all countries.
    # Otherwise, get the list of countries from the config map.
    scope_of_analysis = None
    if scope_name and scope_name.lower() != 'overall':
        scope_of_analysis = SCOPE_MAP.get(scope_name)
        if scope_of_analysis is None:
            print(f"Warning: Scope name '{scope_name}' not found in configuration. Running for all countries.")

    # --- Path Construction ---
    current_dir = os.path.dirname(__file__)
    surveyreport_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
    data_path = os.path.join(surveyreport_dir, "data", section, data_file_name)

    print(f"Attempting to load data from: {data_path}")
    print(f"\n--- Analyzing scope: {scope_name if scope_name else 'All Countries'} ---")

    # --- Run Analysis ---
    analysis_summary = analyze_excel(
        file_path=data_path,
        analysis_data_type=analysis_data_type,
        data_columns=data_columns,
        country_scope=scope_of_analysis
    )
    
    json_compatible_summary = convert_to_py_types(analysis_summary)

    # Separate and print the two main analysis sections
    print("\n\n--- Analysis by Data Column ---")
    print(json.dumps(json_compatible_summary.get("analysis_by_data_column", {}), indent=2))

    print("\n\n--- Analysis by Legend Label ---")
    print(json.dumps(json_compatible_summary.get("analysis_by_legend", {}), indent=2)) 