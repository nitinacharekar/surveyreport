import os
from pathlib import Path
from .q26 import analyze_q26
from .q27 import analyze_q27
from .q28 import analyze_q28

def get_section4_stats():
    # Get the project root directory (2 levels up from this file)
    project_root = Path(__file__).parent.parent.parent
    base_path = project_root / 'data' / 'Section 4'
    
    stats = {
        'q26': analyze_q26(str(base_path / '26 Select the top 3 OWASP API security risks your organization is most concerned about.xlsx')),
        'q27': analyze_q27(str(base_path / '27 How ready is your organization in mitigating these risks.xlsx')),
        'q28': analyze_q28(str(base_path / '28 What security measures does your organization currently have in place to protect APIs.xlsx'))
    }
    
    return stats

if __name__ == "__main__":
    stats = get_section4_stats()
    print(stats) 