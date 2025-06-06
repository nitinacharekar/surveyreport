# A configurable mapping of questions to their corresponding data file names and analysis columns.
# Users can add or modify questions in this dictionary.
# Each question should have a "file_name" and a list of "data_columns" to be analyzed.

QUESTION_MAP = {
    "Select the top 3 OWASP API security risks your organization is most concerned about": {
        "file_name": "26 Select the top 3 OWASP API security risks your organization is most concerned about.xlsx",
        "data_columns": [
            "API1:2023 - Broken Object Level Authorization",
            "API2:2023 - Broken Authentication",
            "API3:2023 - Broken Object Property Level Authorization",
            "API4:2023 - Unrestricted Resource Consumption",
            "API5:2023 - Broken Function Level Authorization",
            "API6:2023 - Unrestricted Access to Sensitive Business Flows",
            "API7:2023 - Server-Side Request Forgery",
            "API8:2023 - Security Misconfiguration",
            "API9:2023 - Improper Inventory Management",
            "API10:2023 - Unsafe Consumption of APIs"
        ]
    },
    "How ready is your organization in mitigating these risks?": {
        "file_name": "27 How ready is your organization in mitigating these risks.xlsx",
        "data_columns": [
            "API1:2023 - Broken Object Level Authorization",
            "API2:2023 - Broken Authentication",
            "API3:2023 - Broken Object Property Level Authorization",
            "API4:2023 - Unrestricted Resource Consumption",
            "API5:2023 - Broken Function Level Authorization",
            "API6:2023 - Unrestricted Access to Sensitive Business Flows",
            "API7:2023 - Server-Side Request Forgery",
            "API8:2023 - Security Misconfiguration",
            "API9:2023 - Improper Inventory Management",
            "API10:2023 - Unsafe Consumption of APIs"
        ]
    },
    "What security measures does your organization currently have in place to protect APIs?": {
        "file_name": "28 What security measures does your organization currently have in place to protect APIs.xlsx",
        # This question uses a different analysis script (q28.py) and data structure.
        # The 'data_columns' concept does not directly apply in the same way.
        # This entry is a placeholder for future refactoring.
        "data_columns": []
    }
} 