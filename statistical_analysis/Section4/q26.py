import pandas as pd
import json
from pathlib import Path

def analyze_q26(file_path: str):
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    # Identify relevant columns
    answer_col = 'Answers'
    risk_col = df.columns[5]  # Assuming the 6th column is the risk name
    id_col = 'ID'
    demo_cols = ['Country', 'Gender', 'Age']

    # Total responses
    total_responses = len(df)
    # Total selected (Answer == 1)
    total_selected = df[answer_col].sum()
    percent_selected = (total_selected / total_responses) * 100

    # Breakdown by risk
    risk_stats = df.groupby(risk_col)[answer_col].agg(['sum', 'count', 'mean'])
    risk_stats = risk_stats.rename(columns={'sum': 'selected_count', 'count': 'total', 'mean': 'average'})
    risk_stats = risk_stats.sort_values('selected_count', ascending=False)
    risk_stats['rank'] = range(1, len(risk_stats) + 1)
    risk_stats['percent_contribution'] = (risk_stats['selected_count'] / risk_stats['selected_count'].sum() * 100).round(2)
    risk_stats['cumulative_percent_contribution'] = risk_stats['percent_contribution'].cumsum().round(2)
    risk_stats = risk_stats.reset_index().to_dict(orient='records')

    # Had to comment these or else token limit was consistently exceeded
    # Demographic breakdowns
    #demo_breakdowns = {}
    #for demo in demo_cols:
   #     if demo in df.columns:
    #        demo_breakdowns[demo] = df.groupby([demo, risk_col])[answer_col].agg(['sum', 'count', 'mean'])
    #        demo_breakdowns[demo] = demo_breakdowns[demo].rename(columns={'sum': 'selected_count', 'count': 'total', 'mean': 'percent_selected'})
    #        demo_breakdowns[demo]['percent_selected'] = (demo_breakdowns[demo]['percent_selected'] * 100).round(2)

    # Per-respondent stats: how many risks did each respondent select?
    if id_col in df.columns:
        risks_selected_per_id = df[df[answer_col] == 1].groupby(id_col).size()
        # Distribution: how many respondents selected 1, 2, 3, ... risks
        selection_distribution = risks_selected_per_id.value_counts().sort_index().to_dict()
        avg_selected_per_respondent = risks_selected_per_id.mean()
    else:
        selection_distribution = {}
        avg_selected_per_respondent = None

    summary = {
        'question_text': '26 Select the top 3 OWASP API security risks your organization is most concerned about',
        'total_responses': total_responses,
        'total_selected': int(total_selected),
        'percent_selected': round(percent_selected, 2),
        'risk_stats': risk_stats,
        #'demographic_breakdowns': {k: v.reset_index().to_dict(orient='records') for k, v in demo_breakdowns.items()},
        'respondent_selection_distribution': selection_distribution,
        'avg_selected_per_respondent': avg_selected_per_respondent
    }
    return summary

if __name__ == "__main__":
    # Use the correct path for the file in 'statistical_analysis/Section4/'
    file_path = '../../data/Section 4/26 Select the top 3 OWASP API security risks your organization is most concerned about.xlsx'
    stats = analyze_q26(file_path)
    print(json.dumps(stats, indent=2)) 