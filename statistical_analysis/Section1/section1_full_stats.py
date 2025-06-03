from q1 import analyze_q1
from q2 import analyze_q2
from q3 import analyze_q3
from q4 import analyze_q4

def get_section1_stats():
    base_path = '../../data/Section 1/'
    
    stats = {
        'q1': analyze_q1(base_path + '1 Strategic Importance of API Security.xlsx'),
        'q2': analyze_q2(base_path + '2 Organizational API Security Readiness.xlsx'),
        'q3': analyze_q3(base_path + '3 Who has primary responsibility.xlsx'),
        'q4': analyze_q4(base_path + '4 Security Investment Trends.xlsx')
    }
    
    return stats

if __name__ == "__main__":
    stats = get_section1_stats()
    print(stats) 