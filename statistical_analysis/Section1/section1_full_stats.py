'''
Module for aggregating and providing statistical analysis results for Section 1 of the survey.

This script coordinates the analysis of individual questions within Section 1 by calling
specific analysis functions (e.g., `analyze_q1`, `analyze_q2`) from their respective
modules (e.g., `q1.py`, `q2.py`). Each analysis function is responsible for processing
the data from a specific Excel file related to its question.

The primary function `get_section1_stats()` orchestrates these calls and returns a
consolidated dictionary of results for all analyzed questions in Section 1.
It assumes that the data files are located in the `data/Section 1/` directory relative
to the project root.
'''
import os
import json
from pathlib import Path
import sys

# Add the project root to Python path to allow for absolute-like imports from statistical_analysis.utils
# This approach might be refactorable if the project is structured as a package.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Assuming add_demographic_summary is used by the individual qX.py analysis functions
from statistical_analysis.utils.demographic_analysis import add_demographic_summary

# Get the project root directory. This is used to construct absolute paths to data files.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
# Define the base path for data files specific to Section 1.
base_path = os.path.join(project_root, 'data', 'Section 1')

# Import all question-specific analysis functions from local qX.py files.
from .q0 import analyze_q0 # Assuming q0.py and analyze_q0 exist as per file listing
from .q1 import analyze_q1
from .q2 import analyze_q2
from .q3 import analyze_q3
from .q4 import analyze_q4

def get_section1_stats() -> dict:
    '''
    Retrieves and aggregates statistical analysis results for all questions in Section 1.

    This function calls individual analysis functions for each question in Section 1.
    Each analysis function is expected to load and process data from a specific
    Excel file located in the `data/Section 1/` directory.

    The file names are hardcoded in this function.

    Returns:
        dict: A dictionary where keys are question identifiers (e.g., 'q1', 'q2') and
              values are the analysis results returned by the respective
              `analyze_qX` functions.
    '''
    # Define file paths and call the respective analysis functions.
    # It is assumed that q0.py exists and contains analyze_q0 as per the directory listing.
    # If q0 is not meant to be included, it should be removed here.
    stats = {
        'q0': analyze_q0(os.path.join(base_path, '0 Resonpondent Roles.xlsx')), # Corrected filename for q0
        'q1': analyze_q1(os.path.join(base_path, '1 Strategic Importance of API Security.xlsx')),
        'q2': analyze_q2(os.path.join(base_path, '2 Organizational API Security Readiness.xlsx')),
        'q3': analyze_q3(os.path.join(base_path, '3 Who has primary responsibility.xlsx')),
        'q4': analyze_q4(os.path.join(base_path, '4 Security Investment Trends.xlsx'))
    }
    
    return stats

if __name__ == "__main__":
    # This block allows the script to be run directly, for example, to test
    # the statistics generation for Section 1 and print the results.
    section1_results = get_section1_stats()
    print(json.dumps(section1_results, indent=2)) 