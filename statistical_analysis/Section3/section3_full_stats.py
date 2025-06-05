'''
Module for aggregating and providing statistical analysis results for Section 3 of the survey.

This script serves as the central point for collecting all analysis data from Section 3.
It imports analysis functions from individual question modules (e.g., `analyze_q8`,
`analyze_q10`, etc.) that are also located within this `Section3` package.

The primary function, `get_section3_stats()`, orchestrates calls to these individual
analysis functions. It constructs paths to the respective data files, which are expected
to be located in subdirectories within `data/Section 3/` (e.g., `data/Section 3/3.0 Overall/`,
`data/Section 3/3.1 API Discovery & Mapping/`, etc.), relative to the project root.
The results from all analyzed questions are compiled into a single dictionary.

Note: As of the current version, the analysis for q21 is commented out in the `stats` dictionary.
'''
import os
from pathlib import Path
import json # For pretty printing in the main block

# Import all individual question analysis functions from this package
from .q8 import analyze_q8
from .q9 import analyze_q9
from .q10 import analyze_q10
from .q11 import analyze_q11
from .q12 import analyze_q12
from .q13 import analyze_q13
from .q14 import analyze_q14
from .q15 import analyze_q15
from .q16 import analyze_q16
from .q17 import analyze_q17
from .q18 import analyze_q18
from .q19 import analyze_q19
from .q20 import analyze_q20
from .q21 import analyze_q21 # Imported, though its call is commented out below
from .q24 import analyze_q24
from .q25 import analyze_q25

def get_section3_stats() -> dict:
    """
    Retrieves and aggregates statistical analysis results for all questions in Section 3.

    This function calls individual analysis functions for each relevant question in Section 3.
    Each `analyze_qX` function is responsible for loading and processing data from a specific
    Excel file. The paths to these files are constructed relative to the project's
    `data/Section 3/` directory, with subdirectories for specific sub-sections of Section 3.

    Returns:
        dict: A dictionary where keys are question identifiers (e.g., 'q8', 'q10') and
              values are the analysis results returned by the respective `analyze_qX` functions.
    """
    # Determine the project root directory dynamically.
    # Path(__file__).parent is the current directory (Section3)
    # .parent.parent is statistical_analysis
    # .parent.parent.parent is surveyreport (project_root)
    project_root = Path(__file__).resolve().parent.parent.parent
    base_path = project_root / 'data' / 'Section 3'
    
    # Define the filename for q21 separately, as it might contain special characters or require specific handling.
    # Note: The call to analyze_q21 is currently commented out in the stats dictionary below.
    q21_filename = "21 How has code-based discovery improved your organization's API security.xlsx"
    
    stats = {
        # 3.0 Overall
        'q8': analyze_q8(str(base_path / '3.0 Overall' / '8 API Security Concerns- Rating.xlsx')),
        'q9': analyze_q9(str(base_path / '3.0 Overall' / '9 API Security Concerns- Effectiveness of Current Solutions.xlsx')),
        
        # 3.1 API Discovery & Mapping
        'q10': analyze_q10(str(base_path / '3.1 API Discovery & Mapping' / '10 API Discovery & Mapping- Concerns Rating.xlsx')),
        'q11': analyze_q11(str(base_path / '3.1 API Discovery & Mapping' / '11 API Discovery & Mapping- Effectiveness of Current Solutions.xlsx')),
        
        # 3.2 API Posture Management
        'q12': analyze_q12(str(base_path / '3.2 API Posture Management' / '12 API Posture Management- Concern.xlsx')),
        'q13': analyze_q13(str(base_path / '3.2 API Posture Management' / '13 API Posture Management- Effectiveness.xlsx')),
        
        # 3.3 API Access Control
        'q14': analyze_q14(str(base_path / '3.3 API Access Control' / '14 API Access Control- Concern.xlsx')),
        'q15': analyze_q15(str(base_path / '3.3 API Access Control' / '15 API Access Control- Effective.xlsx')),
        
        # 3.4 API Runtime
        'q16': analyze_q16(str(base_path / '3.4 API Runtime' / '16 API Runtime- Concern.xlsx')),
        'q17': analyze_q17(str(base_path / '3.4 API Runtime' / '17 API Runtime- Effectiveness.xlsx')),
        
        # 3.5 API Security Testing
        'q18': analyze_q18(str(base_path / '3.5 API Security Testing' / '18 API Security Testing- Concern.xlsx')),
        'q19': analyze_q19(str(base_path / '3.5 API Security Testing' / '19 API Security Testing- Effectiveness.xlsx')),
        'q20': analyze_q20(str(base_path / '3.5 API Security Testing' / '20 Which stage of the API lifecycle would benefit most.xlsx')),
        # 'q21': analyze_q21(str(base_path / '3.5 API Security Testing' / q21_filename)), # Currently commented out
        
        # 3.6 Regulatory Compliance
        'q24': analyze_q24(str(base_path / '3.6 Regulatory Compliance' / '24 Regulatory Compliance- Concern.xlsx')),
        'q25': analyze_q25(str(base_path / '3.6 Regulatory Compliance' / '25 Regulatory Compliance- Effectiveness.xlsx'))
    }
    
    return stats

if __name__ == "__main__":
    # This block allows direct execution of the script for testing purposes,
    # e.g., to verify that all data files are found and analyses run without error.
    section3_results = get_section3_stats()
    # Pretty print the JSON output for better readability
    print(json.dumps(section3_results, indent=2)) 