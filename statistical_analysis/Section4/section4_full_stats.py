import json
from q26 import analyze_q26
from q27 import analyze_q27
from q28 import analyze_q28

def get_section4_stats():
    base = '../../data/Section 4/'
    q26_stats = analyze_q26(base + '26 Select the top 3 OWASP API security risks your organization is most concerned about.xlsx')
    q27_stats = analyze_q27(base + '27 How ready is your organization in mitigating these risks.xlsx')
    q28_stats = analyze_q28(base + '28 What security measures does your organization currently have in place to protect APIs.xlsx')
    return {"Q26": q26_stats, "Q27": q27_stats, "Q28": q28_stats}

if __name__ == "__main__":
    stats = get_section4_stats()
    print("Section 4 full statistics loaded.") 