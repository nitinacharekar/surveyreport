from surveyreport.statistical_analysis.utils.survey_analysis import analyze_excel
from surveyreport.statistical_analysis.utils.question_config import QUESTION_MAP
from surveyreport.statistical_analysis.utils.scope_config import SCOPE_MAP

def analyze_q28(file_path: str, scope_name: str = "Overall"):
    question_key = "What security measures does your organization currently have in place to protect APIs?"
    question_config = QUESTION_MAP.get(question_key)
    data_columns = question_config.get("data_columns")
    analysis_data_type = "string & number"
    
    scope_of_analysis = None
    if scope_name and scope_name.lower() != 'overall':
        scope_of_analysis = SCOPE_MAP.get(scope_name)

    return analyze_excel(
        file_path=file_path,
        analysis_data_type=analysis_data_type,
        data_columns=data_columns,
        country_scope=scope_of_analysis
    )

if __name__ == '__main__':
    # This block is for independent testing of this question's analysis.
    import os
    import json

    current_dir = os.path.dirname(__file__)
    data_file = os.path.abspath(os.path.join(current_dir, '..', '..', 'data', 'Section4', '28 What security measures does your organization currently have in place to protect APIs.xlsx'))
    
    scope_to_run = "Overall" 
    analysis_summary = analyze_q28(file_path=data_file, scope_name=scope_to_run)

    print(f"--- Analysis for Q28: '{scope_to_run}' scope ---")
    print(json.dumps(analysis_summary, indent=2))
