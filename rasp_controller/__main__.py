"""RSGP Raspberry pi controller main."""

from __future__ import annotations
from typing import TYPE_CHECKING
from dotenv import load_dotenv
import os

if TYPE_CHECKING:
    from ..rsgp.houses_sim.simulator import HousesSimulator

from Pyro5.api import Proxy
from .gpio_controller import GPIOController

load_dotenv()

HOST = os.getenv('RSGP_REMOTE_OBJECT_HOST', 'localhost')
PORT = int(os.getenv('RSGP_REMOTE_OBJECT_PORT', 41991))

BASE = f'PYRO:{{name}}@{HOST}:{PORT}'

rsgp_hs: 'HousesSimulator' = Proxy(BASE.format(name='houses_sim'))

gpio_controller = GPIOController(rsgp_hs)

try:
    print("Starting Raspberry Pi GPIO controller...")
    print("Hardware mapping:")
    print("  House 1: Buttons 2-5,  LEDs 15-18")
    print("  House 2: Buttons 6-9,  LEDs 19-22") 
    print("  House 3: Buttons 10-13, LEDs 23-26")
    print("  Utility: Button 14,     LED 27")
    print("Press Ctrl+C to exit")
    
    gpio_controller.start()
    
    while True:
        try:
            gpio_controller._update_thread.join(timeout=1.0)
            if not gpio_controller._update_thread.is_alive():
                break
        except KeyboardInterrupt:
            break

except KeyboardInterrupt:
    print("\nShutting down GPIO controller...")
finally:
    gpio_controller.stop()
    rsgp_hs._pyroRelease()
