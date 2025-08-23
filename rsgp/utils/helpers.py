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
    nearest_idx = (dataframe['Timestamp'] - target_timestamp).abs().idxmin()
    return dataframe.loc[nearest_idx]


def log_record_into_csv(csv_file_path, /, **record: dict[str, str]) -> None:
    """Log a record into a CSV file.

    Args:
        csv_file_path (str): Path to the CSV file.
        record (dict[str, Any]): The record to log. The keys are the column names and the values
            are the record values.

    """
    with open(csv_file_path, mode="a", encoding="utf-8") as f:
        if f.tell() == 0:
            f.write(",".join(record.keys()) + "\n")
        f.write(",".join(record.values()) + "\n")
        f.close()
