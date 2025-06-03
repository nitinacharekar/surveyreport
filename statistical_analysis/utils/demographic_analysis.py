import pandas as pd
import numpy as np
from typing import Dict, List, Union, Any

def calculate_demographic_stats(df: pd.DataFrame, 
                              demo_cols: List[str], 
                              value_cols: List[str]) -> Dict[str, Any]:
    """
    Calculate demographic statistics for given columns.
    
    Args:
        df: DataFrame containing the data
        demo_cols: List of demographic column names (e.g., ['Country'])
        value_cols: List of value columns to analyze
        
    Returns:
        Dictionary containing demographic breakdowns and statistics
    """
    demo_stats = {}
    
    for demo_col in demo_cols:
        if demo_col not in df.columns:
            continue
            
        demo_stats[demo_col] = {
            'overall_distribution': df[demo_col].value_counts().to_dict(),
            'breakdowns': {}
        }
        
        # Calculate breakdowns for each value column
        for value_col in value_cols:
            if value_col not in df.columns:
                continue
                
            # For numeric columns, calculate mean by demographic
            if pd.api.types.is_numeric_dtype(df[value_col]):
                demo_stats[demo_col]['breakdowns'][value_col] = {
                    'mean_by_demo': df.groupby(demo_col)[value_col].mean().round(2).to_dict(),
                    'std_by_demo': df.groupby(demo_col)[value_col].std().round(2).to_dict(),
                    'count_by_demo': df.groupby(demo_col)[value_col].count().to_dict()
                }
            # For categorical columns, calculate cross-tabulation
            else:
                cross_tab = pd.crosstab(df[demo_col], df[value_col])
                demo_stats[demo_col]['breakdowns'][value_col] = {
                    'distribution': cross_tab.to_dict(),
                    'percentages': (cross_tab.div(cross_tab.sum(axis=1), axis=0) * 100).round(2).to_dict()
                }
    
    return demo_stats

def add_demographic_summary(summary: Dict[str, Any], 
                          df: pd.DataFrame, 
                          demo_cols: List[str], 
                          value_cols: List[str]) -> Dict[str, Any]:
    """
    Add demographic analysis to an existing summary dictionary.
    
    Args:
        summary: Existing summary dictionary
        df: DataFrame containing the data
        demo_cols: List of demographic column names
        value_cols: List of value columns to analyze
        
    Returns:
        Updated summary dictionary with demographic analysis
    """
    demo_stats = calculate_demographic_stats(df, demo_cols, value_cols)
    
    # Add demographic analysis to summary
    summary['demographic_analysis'] = {
        'question_text': summary.get('question_text', None),
        'total_responses_by_demo': {
            col: df[col].value_counts().to_dict()
            for col in demo_cols if col in df.columns
        },
        'statistics': demo_stats
    }
    
    return summary 