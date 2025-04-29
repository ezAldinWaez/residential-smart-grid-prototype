"""RSGP helpers."""

from datetime import datetime
import pandas as pd


def find_nearest_timestamp_row(
    dataframe: pd.DataFrame,
    target_timestamp: datetime,
) -> pd.Series:
    """Find datetime row with timestamp closest to the target timestamp.

    Args:
        dataframe (DataFrame): pandas dataframe with `Timestamp` column.
        target_timestamp (Timestamp): Timestamp to search for.

    Returns:
        Series: The row from df with nearest timestamp.
    """
    time_diffs = (dataframe['Timestamp'] - target_timestamp).abs()
    nearest_idx = time_diffs.idxmin()
    return dataframe.loc[nearest_idx]
