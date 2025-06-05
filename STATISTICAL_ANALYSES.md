# Overview of Statistical Analyses

This document summarizes the statistical computations implemented throughout the repository.

## Common Workflow

Each question script inside `statistical_analysis/Section*` follows the same pattern:

1. **Load data** from the relevant Excel sheet using `pandas.read_excel`.
2. **Clean column names** and identify columns for respondent IDs, demographic categories (typically `Country`), and the answer values.
3. **Count responses** to determine the total number of entries for the question.
4. **Compute descriptive statistics** for each value column via `calculate_stats` from `statistical_analysis.utils.stats_utils`.
5. **Calculate averages** (and sometimes median, mode, or standard deviation) for numeric answers.
6. **Attach demographic analysis** using `add_demographic_summary` from `statistical_analysis.utils.demographic_analysis`.

The resulting dictionary for each question contains the question text, total responses, computed statistics, and demographic breakdowns.

## `calculate_stats`

Located in `statistical_analysis/utils/stats_utils.py`, this helper computes frequency-based statistics for a pandas `Series`.

```python
import pandas as pd

def calculate_stats(series: pd.Series):
    """Calculate statistics for a pandas Series."""
    stats = series.value_counts()
    stats_df = pd.DataFrame({
        'value': stats.index,
        'count': stats.values
    })

    # Rank order
    stats_df_rank = stats_df.sort_values(by='count', ascending=False).reset_index(drop=True)
    stats_df_rank['rank'] = range(1, len(stats_df_rank) + 1)
    stats_df_rank['percent_contribution'] = (stats_df_rank['count'] / stats_df_rank['count'].sum() * 100).round(2)
    stats_df_rank['cumulative_percent_contribution_rank'] = stats_df_rank['percent_contribution'].cumsum().round(2)
    stats_df_rank['cumulative_percent_contribution_reverse_rank'] = stats_df_rank['percent_contribution'][::-1].cumsum()[::-1].round(2).values

    # Value order
    stats_df_value = stats_df.sort_values(by='value').reset_index(drop=True)
    stats_df_value['percent_contribution'] = (stats_df_value['count'] / stats_df_value['count'].sum() * 100).round(2)
    stats_df_value['cumulative_percent_contribution_value'] = stats_df_value['percent_contribution'].cumsum().round(2)
    stats_df_value['cumulative_percent_contribution_reverse_value'] = stats_df_value['percent_contribution'][::-1].cumsum()[::-1].round(2).values

    stats_df_rank = stats_df_rank.merge(
        stats_df_value[['value', 'cumulative_percent_contribution_value', 'cumulative_percent_contribution_reverse_value']],
        on='value', how='left'
    )

    stats_df_rank = stats_df_rank.sort_values(by='value').reset_index(drop=True)
    return stats_df_rank.to_dict(orient='records')
```

This function returns a list of dictionaries with counts, ranking, percent contribution, and cumulative percentages for each unique value.

## `add_demographic_summary`

Defined in `statistical_analysis/utils/demographic_analysis.py`, this function augments a summary dictionary with demographic statistics.

```python
import pandas as pd
import numpy as np

def add_demographic_summary(summary, df, demo_cols, value_cols):
    demo_stats = calculate_demographic_stats(df, demo_cols, value_cols)
    summary['demographic_analysis'] = {
        'question_text': summary.get('question_text'),
        'total_responses_by_demo': {
            col: df[col].value_counts().to_dict()
            for col in demo_cols if col in df.columns
        },
        'statistics': demo_stats
    }
    return summary
```

The helper `calculate_demographic_stats` computes breakdowns by demographic columns. For numeric values it provides means and standard deviations per demographic group; for categorical values it generates distributions and percentage tables.

## Question-Specific Calculations

Beyond the common workflow, some questions include additional computations:

- **Section 4 – Question 27** (`statistical_analysis/Section4/q27.py`): calculates mean, median, mode, standard deviation, total sums, and ranks sub-questions by their average score while computing percent and cumulative contributions.
- **Section 4 – Question 26**: counts how many respondents selected each OWASP risk and the percentage of selections relative to total responses.
- Other questions often compute simple averages of rating scales (e.g., Section 1 questions) or parse numeric ratings from text fields (Section 3 `q8.py`, `q9.py`).

Overall, the analyses use pandas operations such as `mean`, `median`, `mode`, grouping by demographic columns, and cross-tabulation to produce detailed summary statistics.
