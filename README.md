# Survey Report Agent

## Overview

The Survey Report Agent is a Python-based system designed to automate the analysis and summarization of survey data. It leverages a multi-agent architecture built with LangGraph and powered by Large Language Models (LLMs) like OpenAI's GPT series. The system processes survey data through a defined workflow, including section-wise analysis, combined summaries, country-specific insights, and persona-based analysis, along with validation checks.

## Project Structure

```
Survey Report Agent/
├── surveyreport/
│   ├── .git/
│   ├── .gitignore
│   ├── archive/                  # (Purpose to be confirmed - likely for old versions or backups)
│   ├── data/                     # Input survey data, organized by sections
│   │   ├── Section 1/
│   │   ├── Section 2/
│   │   └── ...
│   ├── myenv/                    # Python virtual environment
│   ├── output/                   # Generated reports and analysis outputs
│   ├── statistical_analysis/     # Python modules for data processing and statistics
│   │   ├── Section1/             # Code for Section 1 analysis (e.g., section1_full_stats.py)
│   │   ├── Section2/             # Code for Section 2 analysis
│   │   ├── Section3/             # Code for Section 3 analysis
│   │   ├── Section4/             # Code for Section 4 analysis
│   │   ├── utils/                # Utility functions for analysis
│   │   └── __init__.py
│   ├── summary_final_updated.py  # Main script orchestrating the agent workflow
│   ├── test.py                   # (Purpose to be confirmed - likely unit tests)
│   ├── test_country_analysis.py  # (Purpose to be confirmed - likely tests for country analysis)
│   ├── requirements.txt          # Project dependencies
│   └── summary_agent.log         # Log file for the summary agent
└── (other workspace files)
```

## Setup

1.  **Clone the Repository (if applicable)**
    ```bash
    # git clone <repository_url>
    # cd Survey Report Agent
    ```

2.  **Create and Activate Python Virtual Environment**
    It's recommended to use a virtual environment (like `myenv` provided or create a new one):
    ```bash
    python -m venv myenv
    # On Windows
    myenv\Scripts\activate
    # On macOS/Linux
    source myenv/bin/activate
    ```

3.  **Install Dependencies**
    Navigate to the `surveyreport` directory and install the required packages:
    ```bash
    cd surveyreport
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**
    The system requires API keys for LLM services. Create a `.env` file in the `surveyreport` directory and add your keys:
    ```
    OPENAI_API_KEY="your_openai_api_key_here"
    # Add other keys if required by different models or services
    ```
    The `summary_final_updated.py` script loads these variables using `python-dotenv`.

## Input Data

Place your survey data into the respective subdirectories within `surveyreport/data/`. The exact format and structure of these data files are determined by the processing scripts in `surveyreport/statistical_analysis/Section*/`. (Further details on data format to be added once the stats scripts are analyzed).

## Running the Analysis

To run the main analysis and report generation process, execute the `summary_final_updated.py` script from within the `surveyreport` directory:

```bash
python summary_final_updated.py
```

This will trigger the LangGraph workflow, process the data through the various agents, and generate outputs, likely saved in the `surveyreport/output/` directory. Check the `summary_agent.log` file for detailed logging of the process.

## Key Components

*   **`summary_final_updated.py`**: The core script that defines the agent states, workflow (using LangGraph), and orchestrates the different analysis agents (OpenAI-based). It handles:
    *   Processing questions for each survey section.
    *   Generating summaries for each section.
    *   Creating a combined summary from all sections.
    *   Performing country-specific analysis.
    *   Conducting persona-based analysis.
    *   Validating outputs with a feedback and retry mechanism.
*   **`statistical_analysis/`**: This directory contains Python modules responsible for loading, processing, and calculating statistics for each section of the survey. Each `SectionX` subdirectory typically has a script like `sectionX_full_stats.py` that provides the data inputs for the LLM agents.
*   **`OpenAIAgent` (in `summary_final_updated.py`)**: A custom agent class that interfaces with OpenAI's LLMs to generate analytical text based on prompts and provided data.
*   **`AgentState` (in `summary_final_updated.py`)**: A TypedDict that manages and passes the state (data, summaries, feedback) between different nodes in the LangGraph workflow.

## How it Works

The system uses a graph-based approach (LangGraph) to manage a sequence of tasks performed by different AI agents.
1.  **Data Ingestion**: Statistical data is loaded by modules in `statistical_analysis/`.
2.  **Section Analysis**: For each section, questions are processed, and an LLM agent generates an analysis for each question's statistics. These are then summarized for the section.
3.  **Combined Analysis**: Section summaries are combined into an overall report.
4.  **Specialized Analyses**: Country-specific and persona-based analyses are performed.
5.  **Validation**: Outputs are validated, and if issues are found, feedback can be incorporated for a retry of the relevant step.

(Further details on specific algorithms or methodologies will be added by examining the code in more depth). 