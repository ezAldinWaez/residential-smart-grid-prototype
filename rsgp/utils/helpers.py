"""RSGP Helpers."""

from datetime import datetime
import pandas as pd


def find_nearest_timestamp_row(df: pd.DataFrame, target_timestamp: datetime) -> pd.Series:
    """Find df row with timestamp closest to the target timestamp.

    Args:
        df (DataFrame): pandas data frame with 'Timestamp' column.
        target_timestamp (Timestamp): Timestamp to search for.

    Returns:
        Series: The row from df with nearest timestamp.
    """

    time_diffs = (df['Timestamp'] - target_timestamp).abs()
    nearest_idx = time_diffs.idxmin()
    return df.loc[nearest_idx]
