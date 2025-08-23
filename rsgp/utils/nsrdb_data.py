"""NSRDB data handlers."""

# TODO: Use `pvlib.iotools` instead.

from datetime import datetime, timedelta, timezone
from typing import Any

from ..config.settings import settings

from timezonefinder import TimezoneFinder
import pandas as pd


def get_nsrdb_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read NSRDB dataset, manipulate it, and returen it as DataFrames.

    Returns:
        tuple[DataFrame, DataFrame]: NSRDB metadata, and NSRDB data.

    """
    nsrdb_meta = pd.read_csv(settings.NSRDB_PATH, nrows=1)
    nsrdb_data = pd.read_csv(settings.NSRDB_PATH, header=2)

    if nsrdb_data is None:
        raise Exception("Error: Couldn't initialize NSRDB data!")

    tz_offset = int(
        nsrdb_meta["Local Time Zone"][0] - nsrdb_meta["Time Zone"][0]
    )

    nsrdb_data.insert(0, 'Timestamp', pd.to_datetime({
        'year': nsrdb_data['Year'],
        'month': nsrdb_data['Month'],
        'day': nsrdb_data['Day'],
        'hour': nsrdb_data['Hour'],
        'minute': nsrdb_data['Minute'],
    }, utc=True).dt.tz_convert(timezone(timedelta(hours=tz_offset))))

    nsrdb_data.drop(
        columns=['Year', 'Month', 'Day', 'Hour', 'Minute'],
        inplace=True
    )

    nsrdb_data.insert(
        loc=1,
        column='Time of Day',
        value=[
            'Day' if val < 90 else 'Night'
            for val in nsrdb_data['Solar Zenith Angle']
        ]
    )

    return nsrdb_meta, nsrdb_data


def get_nsrdb_location(nsrdb_meta: pd.DataFrame) -> dict[str, Any]:
    """Get location basic info based on NSRDB dataset metadata.

    Args:
        nsrdb_meta (DataFrame): `nsrdb_meta` from :func:`get_nsrdb_data`.

    Returns:
        dict[str, Any]: A dictionary of location info (`latitude`, `longitude`, `timezone`).

    """
    lat = float(nsrdb_meta["Latitude"][0])
    lng = float(nsrdb_meta["Longitude"][0])
    tz_offset = timedelta(hours=int(nsrdb_meta["Local Time Zone"][0] - nsrdb_meta["Time Zone"][0]))
    tz_name = TimezoneFinder().timezone_at(lat=lat, lng=lng)
    tz = timezone(tz_offset, name=tz_name)

    return {'latitude': lat, 'longitude': lng, 'timezone': tz}


nsrdb_meta, nsrdb_data = get_nsrdb_data()  #: tuple[DataFrame, DataFrame]: NSRDB meta data and data.
nsrdb_location = get_nsrdb_location(nsrdb_meta)  #: dict[str, Any]: NSRDB location.
nsrdb_start_point: datetime = nsrdb_data["Timestamp"].min()  #: datetime: NSRDB start point.
