"""Hardware configuration for Raspberry Pi GPIO controller."""

from dataclasses import dataclass
from enum import Enum
from typing import List


class DeviceType(Enum):
    """Device type enumeration."""
    REFRIGERATOR = "REFRIGERATOR"
    HVAC = "HVAC"
    WATER_HEATER = "WATER_HEATER"
    LOAD_LINE = "LOAD_LINE"
    UTILITY_LINE = "UTILITY_LINE"


@dataclass
class GPIOMapping:
    """GPIO pin mapping for a single control."""
    button_gpio: int
    led_gpio: int
    house_id: int
    device_type: DeviceType
    
    @property
    def control_name(self) -> str:
        """Generate control name for identification."""
        if self.device_type == DeviceType.UTILITY_LINE:
            return "UTILITY_LINE"
        return f"H{self.house_id}_{self.device_type.value}"


class HardwareConfig:
    """Hardware configuration manager for Raspberry Pi controller."""
    
    GPIO_MAPPINGS: List[GPIOMapping] = [
        # House 1
        GPIOMapping(2, 15, 1, DeviceType.REFRIGERATOR),
        GPIOMapping(3, 16, 1, DeviceType.HVAC),
        GPIOMapping(4, 17, 1, DeviceType.WATER_HEATER),
        GPIOMapping(5, 18, 1, DeviceType.LOAD_LINE),
        
        # House 2
        GPIOMapping(6, 19, 2, DeviceType.REFRIGERATOR),
        GPIOMapping(7, 20, 2, DeviceType.HVAC),
        GPIOMapping(8, 21, 2, DeviceType.WATER_HEATER),
        GPIOMapping(9, 22, 2, DeviceType.LOAD_LINE),
        
        # House 3
        GPIOMapping(10, 23, 3, DeviceType.REFRIGERATOR),
        GPIOMapping(11, 24, 3, DeviceType.HVAC),
        GPIOMapping(12, 25, 3, DeviceType.WATER_HEATER),
        GPIOMapping(13, 26, 3, DeviceType.LOAD_LINE),
        
        # Utility Line (global)
        GPIOMapping(14, 27, 0, DeviceType.UTILITY_LINE),
    ]
    
    @classmethod
    def get_button_pins(cls) -> List[int]:
        """Get all button GPIO pins."""
        return [mapping.button_gpio for mapping in cls.GPIO_MAPPINGS]
    
    @classmethod
    def get_led_pins(cls) -> List[int]:
        """Get all LED GPIO pins."""
        return [mapping.led_gpio for mapping in cls.GPIO_MAPPINGS]
    
    @classmethod
    def get_mapping_by_button(cls, button_gpio: int) -> GPIOMapping:
        """Get GPIO mapping by button pin."""
        for mapping in cls.GPIO_MAPPINGS:
            if mapping.button_gpio == button_gpio:
                return mapping
        raise ValueError(f"No mapping found for button GPIO {button_gpio}")
    
    @classmethod
    def get_mappings_by_house(cls, house_id: int) -> List[GPIOMapping]:
        """Get all GPIO mappings for a specific house."""
        return [mapping for mapping in cls.GPIO_MAPPINGS if mapping.house_id == house_id]
    
    @classmethod
    def get_utility_mapping(cls) -> GPIOMapping:
        """Get utility line GPIO mapping."""
        for mapping in cls.GPIO_MAPPINGS:
            if mapping.device_type == DeviceType.UTILITY_LINE:
                return mapping
        raise ValueError("No utility line mapping found")