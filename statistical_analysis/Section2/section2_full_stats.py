'''
Module for aggregating and providing statistical analysis results for Section 2 of the survey.

This script serves as the central point for collecting all analysis data from Section 2.
It imports analysis functions from individual question modules: `analyze_q5` (API Styles),
`analyze_q6` (API Usage in AI/ML), `analyze_q7` (Frequency of AI/ML API Usage),
and `analyze_q8` (Deployment Model of AI/ML APIs).

The primary function, `get_section2_stats()`, orchestrates calls to these individual
analysis functions. It constructs paths to the respective data files, which are expected
to be located in subdirectories within `data/Section 2/`, relative to the project root.
The results from all analyzed questions are compiled into a single dictionary.
'''
import os
import json
import sys

# Add the project root to Python path to enable imports if this script were to be called from elsewhere
# and to allow its qX.py modules to import from statistical_analysis.utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import all question-specific analysis functions from .qX.py files in the current directory.
from .q5 import analyze_q5
from .q6 import analyze_q6
from .q7 import analyze_q7 # Corresponds to "Frequency of AI/ML API Usage"
from .q8 import analyze_q8 # Corresponds to "Deployment Model of AI/ML APIs"

def get_section2_stats() -> dict:
    """
    Retrieves and aggregates statistical analysis results for all questions in Section 2.

    This function calls individual analysis functions for each relevant question in Section 2
    (Q5, Q6, Q7, Q8). Each `analyze_qX` function is responsible for loading and processing
    data from a specific Excel file. The paths to these files are constructed relative to
    the project's `data/Section 2/` directory, using specific subdirectories as needed.

    Returns:
        dict: A dictionary where keys are question identifiers (e.g., 'q5', 'q7') and
              values are the analysis results returned by the respective `analyze_qX` functions.
    """
    # Get the project root directory. This is used to construct absolute paths to data files.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    base_path_section2 = os.path.join(project_root, 'data', 'Section 2')

    # Define file paths based on the actual files used by q5, q6, q7, q8
    q5_file = os.path.join(base_path_section2, '5 What are the predominant API styles used in your organization.xlsx')
    q6_file = os.path.join(base_path_section2, '6 How is your organization currently using APIs in its AI_ML implementations.xlsx')
    # Based on q7.py's __main__ block:
    q7_file = os.path.join(base_path_section2, '2.2 API Usage in AIML Implementations', '6 API Usage in AIML Implementations- Frequency.xlsx')
    # Based on q8.py's __main__ block:
    q8_file = os.path.join(base_path_section2, '2.2 API Usage in AIML Implementations', '7 API Usage in AIML Implementations- Deployment Model.xlsx')
    
    stats = {
        'q5': analyze_q5(q5_file),
        'q6': analyze_q6(q6_file),
        'q7': analyze_q7(q7_file), # analyze_q7 processes Frequency data
        'q8': analyze_q8(q8_file)  # analyze_q8 processes Deployment Model data
    }
    
    return stats

if __name__ == "__main__":
    # This block allows direct execution of the script for testing purposes,
    # e.g., to verify that all data files are found and analyses run without error.
    section2_results = get_section2_stats()
    # Pretty print the JSON output for better readability
    print(json.dumps(section2_results, indent=2)) 