import os
import json
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary

# Get the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
base_path = os.path.join(project_root, 'data', 'Section 1')

# Import all question analysis functions
from .q1 import analyze_q1
from .q2 import analyze_q2
from .q3 import analyze_q3
from .q4 import analyze_q4

def get_section1_stats():
    # Define file paths
    stats = {
        'q1': analyze_q1(base_path + '/1 Strategic Importance of API Security.xlsx'),
        'q2': analyze_q2(base_path + '/2 Organizational API Security Readiness.xlsx'),
        'q3': analyze_q3(base_path + '/3 Who has primary responsibility.xlsx'),
        'q4': analyze_q4(base_path + '/4 Security Investment Trends.xlsx')
    }
    
    return stats

if __name__ == "__main__":
    stats = get_section1_stats()
    print(json.dumps(stats, indent=2)) 