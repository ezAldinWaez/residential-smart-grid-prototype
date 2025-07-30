"""Solar system simulated panels."""

from datetime import datetime

from .data import PanelsConf
from ..utils.nsrdb_data import nsrdb_data, nsrdb_location
from ..utils.helpers import find_nearest_timestamp_row
from ..config.settings import settings

from pvlib.location import Location
from pvlib.irradiance import get_total_irradiance
import pandas as pd
from ..remote_object import expose


@expose
class Panels:
    conf: PanelsConf  #: PanelsConf: The panels configuration
    pv_loc: Location  #: Location: The `pvlib` location info from the NSRDB meta data
    # TODO: make that as data type in .data; an interface between panels and nsrdb data
    pv_data: pd.Series  #: Series: The data row from the NSRDB for the current timestamp
    total_power: float  #: float: The theoretical total power produced by the panels [Watt]

    def __init__(self):
        self.conf = PanelsConf(
            num_panels=settings.PANELS_NUM,
            panel_area=settings.PANEL_AREA,
            panel_efficiency=settings.PANEL_EFFICIENCY,
        )

        self.pv_loc = Location(
            latitude=nsrdb_location['latitude'],
            longitude=nsrdb_location['longitude'],
            tz=nsrdb_location['timezone'],
        )

        self.pv_data = None

        self.total_power = 0.0

    def calc_total_power(self, timestamp: datetime):
        """
        Calculate and return the total power that could be produced by the panels.

        Args:
            - timestamp (datetime): The current timestamp in the same timezone as the NSRDB data
        """

        self.pv_data = find_nearest_timestamp_row(nsrdb_data, timestamp)
        solar_pos = self.pv_loc.get_solarposition(timestamp)

        if self.pv_data['Solar Zenith Angle'] > 90:
            poa_irradiance = 0
        else:
            poa_irradiance = get_total_irradiance(
                surface_tilt=35,
                surface_azimuth=180,
                solar_zenith=self.pv_data['Solar Zenith Angle'],
                solar_azimuth=solar_pos['azimuth'],
                dni=self.pv_data['DNI'],
                ghi=self.pv_data['GHI'],
                dhi=self.pv_data['DHI'],
            )['poa_global'].iloc[0]

        self.total_power = poa_irradiance * self.conf.panel_area * \
            self.conf.panel_efficiency * self.conf.num_panels

        return self.total_power

    def __str__(self):
        return f"Panels(total_power={self.total_power:.2f})"
