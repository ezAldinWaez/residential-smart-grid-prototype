"""RSGP Raspberry pi controller main."""

from __future__ import annotations
from typing import TYPE_CHECKING
from dotenv import load_dotenv
import os

from .gpio_controller import GPIOController

from Pyro5.api import Proxy

load_dotenv()

HOST = os.getenv('RSGP_REMOTE_OBJECT_HOST', '0.0.0.0')
PORT = int(os.getenv('RSGP_REMOTE_OBJECT_PORT', 41991))
BASE = f'PYRO:{{name}}@{HOST}:{PORT}'

rsgp_hs = Proxy(BASE.format(name='houses_sim'))

gpio_controller = GPIOController(rsgp_hs)

try:
    print("Starting Raspberry Pi GPIO controller...")
    gpio_controller.mainloop(0.1)

except KeyboardInterrupt:
    print("\nShutting down GPIO controller...")

finally:
    gpio_controller.stop()
    rsgp_hs._pyroRelease()
