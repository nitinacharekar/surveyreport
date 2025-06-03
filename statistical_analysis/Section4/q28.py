import pandas as pd
import json
from pathlib import Path

def analyze_q28(file_path: str):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    demo_cols = ['Country', 'Gender', 'Age']
    measure_col = 'What security measures does your organization currently have in place to protect APIs?'
    answer_col = 'Answers'

    # Extract the initial question text (assume it's the same for all rows)
    question_text = measure_col

    # Only consider selected measures (Answers == 1)
    selected = df[df[answer_col] == 1]

    # Count and percent for each security measure
    measure_counts = selected[measure_col].value_counts().to_dict()
    total_respondents = df['ID'].nunique() if 'ID' in df.columns else None
    total_selected = sum(measure_counts.values())
    percent_selected = {k: round(v / total_respondents * 100, 2) if total_respondents else None for k, v in measure_counts.items()}

    # Ranking and % contribution
    measure_df = pd.DataFrame(list(measure_counts.items()), columns=['measure', 'count'])
    measure_df = measure_df.sort_values('count', ascending=False)
    measure_df['rank'] = range(1, len(measure_df) + 1)
    measure_df['percent_contribution'] = (measure_df['count'] / total_selected * 100).round(2)
    measure_df['cumulative_percent_contribution'] = measure_df['percent_contribution'].cumsum().round(2)
    measure_stats = measure_df.to_dict(orient='records')

    # Demographic breakdowns
    #demo_breakdowns = {}
    #for demo in demo_cols:
    #    if demo in df.columns:
   #         demo_breakdowns[demo] = {}
   #         for val in df[demo].dropna().unique():
   #             demo_df = selected[selected[demo] == val]
   #             demo_breakdowns[demo][str(val)] = demo_df[measure_col].value_counts().to_dict()

    summary = {
        'question_text': question_text,
        'measure_stats': measure_stats,
        'percent_selected': percent_selected,
        #'demographic_breakdowns': demo_breakdowns
    }
    return summary

if __name__ == "__main__":
    file_path = '../../data/Section 4/28 What security measures does your organization currently have in place to protect APIs.xlsx'
    stats = analyze_q28(file_path)
    print(json.dumps(stats, indent=2))
