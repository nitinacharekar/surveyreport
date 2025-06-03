import json
from q8 import analyze_q8
from q9 import analyze_q9
from q10 import analyze_q10
from q11 import analyze_q11
from q12 import analyze_q12
from q13 import analyze_q13
from q14 import analyze_q14
from q15 import analyze_q15
from q16 import analyze_q16
from q17 import analyze_q17
from q18 import analyze_q18
from q19 import analyze_q19
from q20 import analyze_q20
from q21 import analyze_q21
from q24 import analyze_q24
from q25 import analyze_q25

def get_section3_stats():
    base = '../../data/Section 3/'
    stats = {
        'q8': analyze_q8(f'{base}3.0 Overall/8 API Security Concerns- Rating.xlsx'),
        'q9': analyze_q9(f'{base}3.0 Overall/9 API Security Concerns- Effectiveness of Current Solutions.xlsx'),
        'q10': analyze_q10(f'{base}3.1 API Discovery & Mapping/10 API Discovery & Mapping- Concerns Rating.xlsx'),
        'q11': analyze_q11(f'{base}3.1 API Discovery & Mapping/11 API Discovery & Mapping- Effectiveness of Current Solutions.xlsx'),
        'q12': analyze_q12(f'{base}3.2 API Posture Management/12 API Posture Management- Concern.xlsx'),
        'q13': analyze_q13(f'{base}3.2 API Posture Management/13 API Posture Management- Effectiveness.xlsx'),
        'q14': analyze_q14(f'{base}3.3 API Access Control/14 API Access Control- Concern.xlsx'),
        'q15': analyze_q15(f'{base}3.3 API Access Control/15 API Access Control- Effective.xlsx'),
        'q16': analyze_q16(f'{base}3.4 API Runtime/16 API Runtime- Concern.xlsx'),
        'q17': analyze_q17(f'{base}3.4 API Runtime/17 API Runtime- Effectiveness.xlsx'),
        'q18': analyze_q18(f'{base}3.5 API Security Testing/18 API Security Testing- Concern.xlsx'),
        'q19': analyze_q19(f'{base}3.5 API Security Testing/19 API Security Testing- Effectiveness.xlsx'),
        'q20': analyze_q20(f'{base}3.5 API Security Testing/20 Which stage of the API lifecycle would benefit most.xlsx'),
        #'q21': analyze_q21(f"{base}3.5 API Security Testing/21 How has code-based discovery improved your organization\'s API security.xlsx"),
        'q24': analyze_q24(f'{base}3.6 Regulatory Compliance/24 Regulatory Compliance- Concern.xlsx'),
        'q25': analyze_q25(f'{base}3.6 Regulatory Compliance/25 Regulatory Compliance- Effectiveness.xlsx'),
    }
    return stats

if __name__ == "__main__":
    stats = get_section3_stats()
    print(json.dumps(stats, indent=2)) 