"""GPIO controller for Raspberry Pi hardware interface."""

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Callable
import threading
import time
import os
from dotenv import load_dotenv

try:
    import lgpio
    GPIO_LIB = "lgpio"
except ImportError:
    try:
        import RPi.GPIO as GPIO
        GPIO_LIB = "RPi.GPIO"
    except ImportError:
        print("No GPIO library available. Running in simulation mode.")
        GPIO_LIB = None

from Pyro5.api import Proxy
from .hardware_config import HardwareConfig, GPIOMapping, DeviceType

if TYPE_CHECKING:
    from ..rsgp.houses_sim.simulator import HousesSimulator


class GPIOController:
    """GPIO controller for Raspberry Pi hardware interface.
    
    Manages physical buttons and LEDs for controlling the smart grid simulation.
    Synchronizes hardware state with RSGP simulation components.
    
    Args:
        rsgp_hs (HousesSimulator): Houses simulator instance for remote control.
    """
    
    def __init__(self, rsgp_hs: 'HousesSimulator') -> None:
        self._main_rsgp_hs = rsgp_hs
        self._thread_rsgp_hs = None
        self._running = False
        self._update_thread: threading.Thread = None
        
        self._button_states: Dict[int, bool] = {}
        self._led_states: Dict[int, bool] = {}
        self._button_callbacks: Dict[int, Callable] = {}
        
        self._gpio_chip = None
        
        self._setup_gpio()
        self._setup_callbacks()
    
    def _setup_gpio(self) -> None:
        """Initialize GPIO pins and setup hardware."""
        if GPIO_LIB is None:
            print("GPIO simulation mode - no actual hardware control")
            return
            
        if GPIO_LIB == "lgpio":
            self._gpio_chip = lgpio.gpiochip_open(0)
            
            for pin in HardwareConfig.get_button_pins():
                lgpio.gpio_claim_input(self._gpio_chip, pin, lgpio.SET_PULL_UP)
                self._button_states[pin] = bool(lgpio.gpio_read(self._gpio_chip, pin))
                
            for pin in HardwareConfig.get_led_pins():
                lgpio.gpio_claim_output(self._gpio_chip, pin, 0)
                self._led_states[pin] = False
                
        elif GPIO_LIB == "RPi.GPIO":
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            for pin in HardwareConfig.get_button_pins():
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                self._button_states[pin] = GPIO.input(pin)
                
            for pin in HardwareConfig.get_led_pins():
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
                self._led_states[pin] = False
    
    def _setup_callbacks(self) -> None:
        """Setup button callback functions."""
        for mapping in HardwareConfig.GPIO_MAPPINGS:
            if mapping.device_type == DeviceType.UTILITY_LINE:
                self._button_callbacks[mapping.button_gpio] = self._toggle_utility_line
            elif mapping.device_type == DeviceType.LOAD_LINE:
                self._button_callbacks[mapping.button_gpio] = lambda m=mapping: self._toggle_load_line(m)
            else:
                self._button_callbacks[mapping.button_gpio] = lambda m=mapping: self._toggle_device(m)
    
    def _toggle_utility_line(self) -> None:
        """Toggle utility line for all houses."""
        try:
            for house_idx in range(self._main_rsgp_hs.get_num_houses()):
                house = self._main_rsgp_hs.get_house(house_idx)
                house.toggle_utility_line()
        except Exception as e:
            print(f"Error toggling utility line: {e}")
    
    def _toggle_load_line(self, mapping: GPIOMapping) -> None:
        """Toggle load line for specific house."""
        try:
            house = self._main_rsgp_hs.get_house(mapping.house_id - 1)
            house.toggle_load_line()
        except Exception as e:
            print(f"Error toggling load line for house {mapping.house_id}: {e}")
    
    def _toggle_device(self, mapping: GPIOMapping) -> None:
        """Toggle device envelope for specific house and device."""
        try:
            house = self._main_rsgp_hs.get_house(mapping.house_id - 1)
            device = house.get_device(mapping.device_type.value)
            elapsed = self._main_rsgp_hs.get_time_sim_elapsed()
            device.toggle_envelope_state(idx=0, elapsed=elapsed)
        except Exception as e:
            print(f"Error toggling {mapping.device_type.value} for house {mapping.house_id}: {e}")
    
    def _read_buttons(self) -> None:
        """Read button states and detect presses."""
        if GPIO_LIB is None:
            return
            
        for pin in HardwareConfig.get_button_pins():
            if GPIO_LIB == "lgpio":
                current_state = bool(lgpio.gpio_read(self._gpio_chip, pin))
            else:
                current_state = GPIO.input(pin)
            
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
        """Update LED states based on RSGP simulation state."""
        try:
            for mapping in HardwareConfig.GPIO_MAPPINGS:
                led_state = self._get_simulation_state(mapping)
                self._set_led(mapping.led_gpio, led_state)
        except Exception as e:
            print(f"Error updating LEDs: {e}")
    
    def _get_simulation_state(self, mapping: GPIOMapping) -> bool:
        """Get current state from RSGP simulation."""
        try:
            rsgp_hs = self._thread_rsgp_hs or self._main_rsgp_hs
            
            if mapping.device_type == DeviceType.UTILITY_LINE:
                return any(
                    rsgp_hs.get_house(i).get_utility_line() 
                    for i in range(rsgp_hs.get_num_houses())
                )
            elif mapping.device_type == DeviceType.LOAD_LINE:
                house = rsgp_hs.get_house(mapping.house_id - 1)
                return house.get_load_line()
            else:
                house = rsgp_hs.get_house(mapping.house_id - 1)
                device = house.get_device(mapping.device_type.value)
                envelopes = device.get_envelopes()
                return bool(envelopes[0][2]) if envelopes else False
        except Exception as e:
            print(f"Error getting simulation state for {mapping.control_name}: {e}")
            return False
    
    def _set_led(self, pin: int, state: bool) -> None:
        """Set LED state."""
        if GPIO_LIB is None:
            return
            
        if self._led_states.get(pin) != state:
            if GPIO_LIB == "lgpio":
                lgpio.gpio_write(self._gpio_chip, pin, 1 if state else 0)
            else:
                GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
            self._led_states[pin] = state
    
    def start(self, update_interval: float = 0.1) -> None:
        """Start GPIO monitoring and LED updates.
        
        Args:
            update_interval (float): Update interval in seconds.
        """
        if self._running:
            return
            
        self._running = True
        self._update_thread = threading.Thread(
            target=self._update_loop,
            args=(update_interval,),
            daemon=True
        )
        self._update_thread.start()
        print("GPIO controller started")
    
    def stop(self) -> None:
        """Stop GPIO controller and cleanup."""
        self._running = False
        
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=1.0)
        
        if GPIO_LIB == "lgpio" and self._gpio_chip is not None:
            lgpio.gpiochip_close(self._gpio_chip)
        elif GPIO_LIB == "RPi.GPIO":
            GPIO.cleanup()
        
        print("GPIO controller stopped")
    
    def _update_loop(self, update_interval: float) -> None:
        """Main update loop for GPIO monitoring."""
        load_dotenv()
        HOST = os.getenv('RSGP_REMOTE_OBJECT_HOST', 'localhost')
        PORT = int(os.getenv('RSGP_REMOTE_OBJECT_PORT', 41991))
        BASE = f'PYRO:{{name}}@{HOST}:{PORT}'
        
        self._thread_rsgp_hs = Proxy(BASE.format(name='houses_sim'))
        
        try:
            while self._running:
                try:
                    self._read_buttons()
                    self._update_leds()
                    time.sleep(update_interval)
                except Exception as e:
                    print(f"Error in GPIO update loop: {e}")
                    time.sleep(update_interval)
        finally:
            if self._thread_rsgp_hs:
                try:
                    self._thread_rsgp_hs._pyroRelease()
                except:
                    pass
    
    def get_status(self) -> Dict[str, Dict[str, bool]]:
        """Get current hardware status.
        
        Returns:
            Dict containing button and LED states for each control.
        """
        status = {}
        for mapping in HardwareConfig.GPIO_MAPPINGS:
            status[mapping.control_name] = {
                'button_pressed': not self._button_states.get(mapping.button_gpio, True),
                'led_on': self._led_states.get(mapping.led_gpio, False),
                'simulation_state': self._get_simulation_state(mapping)
            }
        return status