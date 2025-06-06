from surveyreport.statistical_analysis.utils.survey_analysis import run_analysis_and_print

# --- User Inputs ---

# 1. The name of the Excel file in the data/<section> directory
DATA_FILE_NAME = "27 How ready is your organization in mitigating these risks.xlsx"

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
        data_file_name=DATA_FILE_NAME,
        scope_name=SCOPE_NAME,
        analysis_data_type=ANALYSIS_DATA_TYPE,
        section=SECTION
    )
