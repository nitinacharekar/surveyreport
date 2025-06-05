print("Script q26.py is starting...")
"""
Analyzes data for Question 26: "Select the top 3 OWASP API security risks your organization is most concerned about".

This script reads an Excel file where each row might represent a selection of a specific
OWASP API security risk by a respondent. It calculates statistics on which risks are most
selected and performs a demographic breakdown.

Note: The script identifies the column containing the risk names by its index (df.columns[5]),
which could be fragile if the Excel sheet structure changes.
"""
import pandas as pd
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path for utility imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from statistical_analysis.utils.demographic_analysis import add_demographic_summary
from statistical_analysis.utils.stats_utils import calculate_stats

def analyze_q26(file_path: str) -> dict:
    """
    Analyzes data for Question 26: "Select the top 3 OWASP API security risks 
    your organization is most concerned about" from an Excel file.

    The function reads data from a sheet named "Data" in the specified Excel 
    file. It assumes that each row represents a unique respondent and that the file 
    contains metadata columns (like 'ID', 'Country', 'Age', 'Gender', 'Category') 
    and several other columns, each representing a specific OWASP API security risk. 
    The values in these risk columns (e.g., 1 or 0) indicate whether a respondent 
    selected that particular risk.

    The analysis calculates:
    - The total number of responses (respondents).
    - The overall frequency of selection for each identified OWASP API security risk.
    - A matrix of risk selections grouped by country, showing the sum of selections 
      for each risk within each country.
    - A matrix of risk selections grouped by risk, showing the total selections for 
      each risk and a further breakdown of these selections by country.

    Args:
        file_path (str): Absolute or relative path to the Excel file 
                         containing the survey data.

    Returns:
        dict: A dictionary containing the analysis summary, with the following structure:
              - 'question_text' (str): The text of the survey question.
              - 'total_responses' (int): The total number of respondents.
              - 'main_stats' (dict): Contains the core statistical outputs:
                  - 'risk_stats_asia_pacific' (dict): A dictionary where keys are 
                    risk column names (representing specific OWASP risks) and values 
                    are the total number of times each risk was selected across all 
                    respondents, sorted in descending order of selection count. 
                    Example: {'API1_Risk': 150, 'API2_Risk': 120, ...}
                  - 'risk_matrix_by_country' (dict): A nested dictionary where outer 
                    keys are country names. Inner keys are risk column names, and 
                    inner values are the total selections for that risk in that country.
                    Example: {'CountryA': {'API1_Risk': 50, 'API2_Risk': 40}, ...}
                  - 'risk_matrix_by_risk' (dict): A nested dictionary where outer keys 
                    are risk column names. Inner values are dictionaries containing a 
                    'total' count of selections for that risk and a 'by_country' 
                    dictionary detailing selections per country for that risk.
                    Example: {'API1_Risk': {'total': 150, 
                                          'by_country': {'CountryA': 50, 'CountryB': 100}}, 
                              ...}
    """
    df = pd.read_excel(file_path, sheet_name="Data")

    # Clean column names by stripping leading/trailing whitespace
    df.columns = df.columns.str.strip()

    # Identify metadata and risk columns
    metadata_cols = ['ID', 'Country', 'Age', 'Gender', 'Category']
    risk_cols = [col for col in df.columns if col not in metadata_cols]

    # Total responses = number of rows (respondents)
    total_responses = len(df)

    # Total selected = sum of all 1s in all risk columns
    total_selected = df[risk_cols].sum().sum()

    # Percent selected = total 1s / (total cells checked = total_responses * num_risks)
    percent_selected = (total_selected / (total_responses * len(risk_cols))) * 100 if total_responses else 0

    # Calculate frequency of selection for each risk
    risk_stats = df[risk_cols].sum().sort_values(ascending=False).to_dict()
    risk_matrix_by_country = (
        df.groupby('Country')[risk_cols]
        .sum()
        .round(0)
        .astype(int)
        .to_dict(orient='index')  # current structure: Country → Risk
    )

    grouped = df.groupby('Country')[risk_cols].sum().round(0).astype(int)
    risk_matrix_by_risk = {}

    for risk in risk_cols:
        total = grouped[risk].sum()
        by_country = grouped[risk].to_dict()
        risk_matrix_by_risk[risk] = {
            'total': int(total),
            'by_country': by_country
        }

    summary = {
        'question_text': '26 Select the top 3 OWASP API security risks your organization is most concerned about',
        'total_responses': total_responses,
        'main_stats': {
            'risk_stats_asia_pacific': risk_stats,
            'risk_matrix_by_country': risk_matrix_by_country,
            'risk_matrix_by_risk': risk_matrix_by_risk,
            }
        }

    return summary

if __name__ == "__main__":
    # This block allows direct execution of the script for testing or individual analysis.
    default_data_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Section 4', '26 Select the top 3 OWASP API security risks your organization is most concerned about.xlsx')

    if not os.path.exists(default_data_file):
        print(f"Warning: Default data file not found at {default_data_file}")
        q26_results = {"error": f"Data file not found: {default_data_file}"}
    else:
        try:
            q26_results = analyze_q26(default_data_file)
        except ValueError as e:
            print(f"Error analyzing file: {e}")
            q26_results = {"error": str(e)}
    
    print(json.dumps(q26_results, indent=2)) 