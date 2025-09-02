"""GPIO controller for Raspberry Pi hardware interface."""

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Callable
import threading
import time

from .hardware_config import HardwareConfig, GPIOMapping, DeviceType
if TYPE_CHECKING:
    from ..rsgp.houses_sim.simulator import HousesSimulator

from Pyro5.api import Proxy
try:
    import lgpio
except ImportError:
    print("No GPIO library available. Exiting...")
    exit(1)


class GPIOController:
    """GPIO controller for Raspberry Pi hardware interface.

    Manages physical buttons and LEDs for controlling the smart grid simulation.
    Synchronizes hardware state with RSGP simulation components.

    Args:
        rsgp_hs (HousesSimulator): Houses simulator instance for remote control.

    """

    def __init__(self, rsgp_hs: 'HousesSimulator') -> None:
        self._rsgp_hs = rsgp_hs
        self._running = False
        self._update_thread: threading.Thread = None
        self._button_states: Dict[int, bool] = {}
        self._led_states: Dict[int, bool] = {}
        self._button_callbacks: Dict[int, Callable] = {}
        self._gpio_chip = None
        self._setup_gpio()
        self._setup_callbacks()

    def _setup_gpio(self) -> None:
        self._gpio_chip = lgpio.gpiochip_open(0)
        for pin in HardwareConfig.get_button_pins():
            lgpio.gpio_claim_input(self._gpio_chip, pin, lgpio.SET_PULL_UP)
            self._button_states[pin] = bool(lgpio.gpio_read(self._gpio_chip, pin))
        for pin in HardwareConfig.get_led_pins():
            lgpio.gpio_claim_output(self._gpio_chip, pin, 0)
            self._led_states[pin] = False

    def _setup_callbacks(self) -> None:
        for mapping in HardwareConfig.GPIO_MAPPINGS:
            if mapping.device_type == DeviceType.UTILITY_LINE:
                self._button_callbacks[mapping.button_gpio] = self._toggle_utility_line
            elif mapping.device_type == DeviceType.LOAD_LINE:
                self._button_callbacks[mapping.button_gpio] = lambda m=mapping: self._toggle_load_line(m)
            else:
                self._button_callbacks[mapping.button_gpio] = lambda m=mapping: self._toggle_device(m)

    def _toggle_utility_line(self) -> None:
        try:
            for house_idx in range(self._rsgp_hs.get_num_houses()):
                house = self._rsgp_hs.get_house(house_idx)
                house.toggle_utility_line()
        except Exception as e:
            print(f"Error toggling utility line: {e}")

    def _toggle_load_line(self, mapping: GPIOMapping) -> None:
        try:
            house = self._rsgp_hs.get_house(mapping.house_id - 1)
            house.toggle_load_line()
        except Exception as e:
            print(f"Error toggling load line for house {mapping.house_id}: {e}")

    def _toggle_device(self, mapping: GPIOMapping) -> None:
        try:
            house = self._rsgp_hs.get_house(mapping.house_id - 1)
            device = house.get_device(mapping.device_type.value)
            elapsed = self._rsgp_hs.get_time_sim_elapsed()
            device.toggle_envelope_state(idx=0, elapsed=elapsed)
        except Exception as e:
            print(f"Error toggling {mapping.device_type.value} for house {mapping.house_id}: {e}")

    def _read_buttons(self) -> None:
        for pin in HardwareConfig.get_button_pins():
            current_state = bool(lgpio.gpio_read(self._gpio_chip, pin))
            if self._button_states[pin] and not current_state:
                mapping = HardwareConfig.get_mapping_by_button(pin)
                print(f"Button pressed: {mapping.control_name}")
                if pin in self._button_callbacks:
                    try:
                        self._button_callbacks[pin]()
                    except Exception as e:
                        print(f"Error executing callback for button {pin}: {e}")
            self._button_states[pin] = current_state

    def _update_leds(self) -> None:
        try:
            for mapping in HardwareConfig.GPIO_MAPPINGS:
                led_state = self._get_simulation_state(mapping)
                self._set_led(mapping.led_gpio, led_state)
        except Exception as e:
            print(f"Error updating LEDs: {e}")

    def _get_simulation_state(self, mapping: GPIOMapping) -> bool:
        try:
            if mapping.device_type == DeviceType.UTILITY_LINE:
                return any(
                    self._rsgp_hs.get_house(i).get_utility_line()
                    for i in range(self._rsgp_hs.get_num_houses())
                )
            elif mapping.device_type == DeviceType.LOAD_LINE:
                house = self._rsgp_hs.get_house(mapping.house_id - 1)
                return house.get_load_line()
            else:
                house = self._rsgp_hs.get_house(mapping.house_id - 1)
                device = house.get_device(mapping.device_type.value)
                envelopes = device.get_envelopes()
                return bool(envelopes[0][2]) if envelopes else False
        except Exception as e:
            print(f"Error getting simulation state for {mapping.control_name}: {e}")
            return False

    def _set_led(self, pin: int, state: bool) -> None:
        if self._led_states.get(pin) != state:
            lgpio.gpio_write(self._gpio_chip, pin, 1 if state else 0)
            self._led_states[pin] = state

    def stop(self) -> None:
        """Stop GPIO controller and cleanup."""
        lgpio.gpiochip_close(self._gpio_chip)
        print("GPIO controller stopped")

    def mainloop(self, dt: float) -> None:
        """Main update loop for GPIO monitoring.

        Args:
            dt (float): Update interval in seconds.

        """

        while True:
            try:
                self._read_buttons()
                self._update_leds()
                time.sleep(dt)
            except Exception as e:
                print(f"Error in GPIO update loop: {e}")
                time.sleep(dt)
