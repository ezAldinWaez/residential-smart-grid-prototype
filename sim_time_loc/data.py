from enum import Enum
from dataclasses import dataclass


@dataclass
class LocationInfo:
    """
    Attributes
    ----------
    - lat : latitude
    - lng : longitude
    - alt : altitude
    - tz_name : timezone name
    """
    lat: float
    lng: float
    alt: float
    tz_name: str

    def __post_init__(self):
        assert (True)


class Location(Enum):
    """
    Location Info for some places on Earth
    """
    ALEPPO = LocationInfo(
        lat=36.2022,
        lng=37.1343,
        alt=380,
        tz_name='Asia/Damascus',
    )
    MEXICO = LocationInfo(
        lat=19.4326,
        lng=-99.1332,
        alt=2250,
        tz_name='America/Mexico_City',
    )
    NEW_YORK = LocationInfo(
        lat=40.7128,
        lng=-74.0060,
        alt=10,
        tz_name='America/New_York',
    )
    ANTARCTICA = LocationInfo(
        lat=-90,
        lng=0,
        alt=0,
        tz_name='Antarctica',
    )
    SAHARA_DESERT = LocationInfo(
        lat=23.4162,
        lng=25.6628,
        alt=500,
        tz_name='Africa/Khartoum',
    )
