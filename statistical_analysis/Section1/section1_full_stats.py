'''
Module for aggregating and providing statistical analysis results for Section 1 of the survey.

This script serves as the central point for collecting all analysis data from Section 1.
It imports analysis functions from individual question modules (e.g., `analyze_q0`,
`analyze_q1`, etc.) that are also located within this `Section1` package.

The primary function, `get_section1_stats()`, orchestrates calls to these individual
analysis functions. It constructs paths to the respective data files, which are expected
to be located in the `data/Section 1/` directory relative to the project root.
The results from all analyzed questions are compiled into a single dictionary.
'''
import os
import json
from pathlib import Path # Pathlib is imported but not used; os.path is used instead.
import sys

# Add the project root to Python path to enable imports from sibling directories
# (e.g., statistical_analysis.utils)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Individual question analysis functions are expected to handle their own utils imports if needed.
# from statistical_analysis.utils.demographic_analysis import add_demographic_summary # Not directly used here

# Import all question-specific analysis functions from .qX.py files in the current directory.
from .q0 import analyze_q0
from .q1 import analyze_q1
from .q2 import analyze_q2
from .q3 import analyze_q3
from .q4 import analyze_q4

def get_section1_stats() -> dict:
    """
    Retrieves and aggregates statistical analysis results for all questions in Section 1.

    This function calls individual analysis functions for each relevant question in Section 1
    (Q0 to Q4). Each `analyze_qX` function is responsible for loading and processing data
    from a specific Excel file. The paths to these files are constructed relative to the
    project's `data/Section 1/` directory.

    Returns:
        dict: A dictionary where keys are question identifiers (e.g., 'q0', 'q1') and
              values are the analysis results returned by the respective `analyze_qX` functions.
    """
    # Get the project root directory. This is used to construct absolute paths to data files.
    # Path(__file__).resolve().parent.parent would be the statistical_analysis directory.
    # Path(__file__).resolve().parent.parent.parent would be the surveyreport (project_root).
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    base_path = os.path.join(project_root, 'data', 'Section 1')
    
    stats = {
        'q0': analyze_q0(os.path.join(base_path, '0 Resonpondent Roles.xlsx')), # Note: Typo in "Resonpondent"
        'q1': analyze_q1(os.path.join(base_path, '1 Strategic Importance of API Security.xlsx')),
        'q2': analyze_q2(os.path.join(base_path, '2 Organizational API Security Readiness.xlsx')),
        'q3': analyze_q3(os.path.join(base_path, '3 Who has primary responsibility.xlsx')),
        'q4': analyze_q4(os.path.join(base_path, '4 Security Investment Trends.xlsx'))
    }
    
    return stats

if __name__ == "__main__":
    # This block allows direct execution of the script for testing purposes,
    # e.g., to verify that all data files are found and analyses run without error.
    section1_results = get_section1_stats()
    # Pretty print the JSON output for better readability
    print(json.dumps(section1_results, indent=2)) 