import os
from pathlib import Path
from .q5 import analyze_q5
from .q6 import analyze_q6
from .q7 import analyze_q7
from .q8 import analyze_q8

def get_section2_stats():
    # Get the project root directory (2 levels up from this file)
    project_root = Path(__file__).parent.parent.parent
    base_path = project_root / 'data' / 'Section 2'
    
    stats = {
        'q5': analyze_q5(str(base_path / '2.1 API Usage Classification/5 API Usage Classification- Business Purpose APIs.xlsx')),
        'q6': analyze_q6(str(base_path / '2.1 API Usage Classification/6 API Usage Classification- Technical Architecture APIs.xlsx')),
        'q7': analyze_q7(str(base_path / '2.2 API Usage in AIML Implementations/6 API Usage in AIML Implementations- Frequency.xlsx')),
        'q8': analyze_q8(str(base_path / '2.2 API Usage in AIML Implementations/7 API Usage in AIML Implementations- Deployment Model.xlsx'))
    }
    
    return stats

if __name__ == "__main__":
    stats = get_section2_stats()
    print(stats) 