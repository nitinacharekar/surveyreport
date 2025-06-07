"""
Module for aggregating and providing statistical analysis results for Section 4 of the survey.

This script coordinates the analysis of individual questions within Section 4
(OWASP API security risks, mitigation readiness, and current security measures)
by calling specific analysis functions (`analyze_q26`, `analyze_q27`, `analyze_q28`)
from their respective modules.

The `get_section4_stats()` function orchestrates these calls using `pathlib.Path`
for robust path construction to data files located in `data/Section 4/`.
"""
import os
import json # Added for pretty printing in main
from pathlib import Path
from .q26 import analyze_q26
from .q27 import analyze_q27
from .q28 import analyze_q28

def get_section4_stats() -> dict:
    """
    Retrieves and aggregates statistical analysis results for all questions in Section 4.

    This function calls individual analysis functions for each question in Section 4 (q26, q27, q28).
    Each analysis function loads and processes data from a specific Excel file
    located in the `data/Section 4/` directory, relative to the project root.
    File paths are constructed using `pathlib.Path` for cross-platform compatibility.

    Returns:
        dict: A dictionary where keys are question identifiers (e.g., 'q26') and
              values are the analysis results from the respective `analyze_qX` functions.
    """
    # Get the project root directory (assumed to be 3 levels up: Section4 -> statistical_analysis -> surveyreport)
    # Path(__file__).parent is the current dir (Section4)
    # .parent.parent is statistical_analysis
    # .parent.parent.parent is surveyreport (project_root)
    project_root = Path(__file__).resolve().parent.parent.parent
    base_path = project_root / 'data' / 'Section4'
    
    stats = {
        'q26': analyze_q26(str(base_path / '26 Select the top 3 OWASP API security risks your organization is most concerned about.xlsx')),
        'q27': analyze_q27(str(base_path / '27 How ready is your organization in mitigating these risks.xlsx')),
        'q28': analyze_q28(str(base_path / '28 What security measures does your organization currently have in place to protect APIs.xlsx'))
    }
    
    return stats

if __name__ == "__main__":
    # This block allows direct execution for testing Section 4 statistics aggregation.
    section4_results = get_section4_stats()
    # Pretty print the JSON output
    print(json.dumps(section4_results, indent=2)) 