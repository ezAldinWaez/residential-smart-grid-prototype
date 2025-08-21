"""RSGP Raspberry pi controller main."""

from __future__ import annotations
from typing import TYPE_CHECKING
from dotenv import load_dotenv
import os
import time

if TYPE_CHECKING:
    from ..rsgp.houses_sim.simulator import HousesSimulator

from Pyro5.api import Proxy

load_dotenv()

HOST = os.getenv('RSGP_REMOTE_OBJECT_HOST', 'localhost')
PORT = int(os.getenv('RSGP_REMOTE_OBJECT_PORT', 41991))

BASE = f'PYRO:{{name}}@{HOST}:{PORT}'

rsgp_hs: 'HousesSimulator' = Proxy(BASE.format(name='houses_sim'))


try:
    while True:
        print((
            "-------------------------------------------------------------------------\n"
            f"{rsgp_hs.get_house(0).get_device('HVAC').get_envelopes()[0][2]=}\n"
            f"{rsgp_hs.get_house(0).get_device('MICROWAVE').get_envelopes()[0][2]=}\n"
            f"{rsgp_hs.get_house(0).get_device('REFRIGERATOR').get_envelopes()[0][2]=}\n"
            f"{rsgp_hs.get_house(0).get_device('WATER_HEATER').get_envelopes()[0][2]=}\n"
            "\n"
            f"{rsgp_hs.get_house(1).get_device('HVAC').get_envelopes()[0][2]=}\n"
            f"{rsgp_hs.get_house(1).get_device('MICROWAVE').get_envelopes()[0][2]=}\n"
            f"{rsgp_hs.get_house(1).get_device('REFRIGERATOR').get_envelopes()[0][2]=}\n"
            f"{rsgp_hs.get_house(1).get_device('WATER_HEATER').get_envelopes()[0][2]=}\n"
            "\n"
            f"{rsgp_hs.get_house(2).get_device('HVAC').get_envelopes()[0][2]=}\n"
            f"{rsgp_hs.get_house(2).get_device('MICROWAVE').get_envelopes()[0][2]=}\n"
            f"{rsgp_hs.get_house(2).get_device('REFRIGERATOR').get_envelopes()[0][2]=}\n"
            f"{rsgp_hs.get_house(2).get_device('WATER_HEATER').get_envelopes()[0][2]=}\n"
            "\n"
        ))

        time.sleep(.5)


except KeyboardInterrupt:
    rsgp_hs._pyroRelease()
