from surveyreport.statistical_analysis.utils.survey_analysis import run_analysis_and_print

# --- User Inputs ---

# 1. The question to analyze.
#    Provide a key from the QUESTION_MAP in 'utils/question_config.py'.
QUESTION_KEY = "How ready is your organization in mitigating these risks?"

# 2. The section where the data file is located (e.g., "Section4")
SECTION = "Section4"

# 3. The scope for the analysis.
#    Provide a key from the SCOPE_MAP in 'utils/scope_config.py'.
#    Set to "Overall" or None to analyze all countries.
SCOPE_NAME = "Asia Pacific"

# 4. The type of analysis to perform: "string", "number", or "string & number".
ANALYSIS_DATA_TYPE = "string & number"


# --- Run Analysis ---
if __name__ == "__main__":
    run_analysis_and_print(
        question_key=QUESTION_KEY,
        scope_name=SCOPE_NAME,
        analysis_data_type=ANALYSIS_DATA_TYPE,
        section=SECTION
    )
