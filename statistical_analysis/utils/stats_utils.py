import pandas as pd

def calculate_stats(series: pd.Series):
    """
    Calculate statistics for a pandas Series, including:
    - Rank order (by count descending)
    - Value order (ascending)
    - Reverse orders
    - Percent and cumulative percent contributions
    Returns a list of dicts, one per unique value.
    """
    stats = series.value_counts()
    stats_df = pd.DataFrame({
        'value': stats.index,
        'count': stats.values
    })

    # Rank order (by count descending)
    stats_df_rank = stats_df.sort_values(by='count', ascending=False).reset_index(drop=True)
    stats_df_rank['rank'] = range(1, len(stats_df_rank) + 1)
    stats_df_rank['percent_contribution'] = (stats_df_rank['count'] / stats_df_rank['count'].sum() * 100).round(2)
    stats_df_rank['cumulative_percent_contribution_rank'] = stats_df_rank['percent_contribution'].cumsum().round(2)
    stats_df_rank['cumulative_percent_contribution_reverse_rank'] = stats_df_rank['percent_contribution'][::-1].cumsum()[::-1].round(2).values

    # Value order (ascending)
    stats_df_value = stats_df.sort_values(by='value').reset_index(drop=True)
    stats_df_value['percent_contribution'] = (stats_df_value['count'] / stats_df_value['count'].sum() * 100).round(2)
    stats_df_value['cumulative_percent_contribution_value'] = stats_df_value['percent_contribution'].cumsum().round(2)
    stats_df_value['cumulative_percent_contribution_reverse_value'] = stats_df_value['percent_contribution'][::-1].cumsum()[::-1].round(2).values

    # Merge all cumulative columns into the rank-ordered DataFrame for output
    stats_df_rank = stats_df_rank.merge(
        stats_df_value[['value', 'cumulative_percent_contribution_value', 'cumulative_percent_contribution_reverse_value']],
        on='value',
        how='left'
    )

    # Ensure final output is ordered by value
    stats_df_rank = stats_df_rank.sort_values(by='value').reset_index(drop=True)

    return stats_df_rank.to_dict(orient='records') 