from surveyreport.statistical_analysis.utils.survey_analysis import analyze_excel
from surveyreport.statistical_analysis.utils.question_config import QUESTION_MAP
from surveyreport.statistical_analysis.utils.scope_config import SCOPE_MAP

def analyze_q26(file_path: str, scope_name: str = "Overall"):
    question_key = "Select the top 3 OWASP API security risks your organization is most concerned about"
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
    # It uses a hardcoded path for the data file.
    # To run, execute this script directly: python -m surveyreport.statistical_analysis.Section4.q26
    import os
    import json

    current_dir = os.path.dirname(__file__)
    # Construct the path to the data file relative to this script
    data_file = os.path.abspath(os.path.join(current_dir, '..', '..', 'data', 'Section4', '26 Select the top 3 OWASP API security risks your organization is most concerned about.xlsx'))
    
    # --- Run Analysis for a specific scope ---
    scope_to_run = "Overall" 
    analysis_summary = analyze_q26(file_path=data_file, scope_name=scope_to_run)

    # --- Output Results ---
    print(f"--- Analysis for Q26: '{scope_to_run}' scope ---")
    print(json.dumps(analysis_summary, indent=2))
