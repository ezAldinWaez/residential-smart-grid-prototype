#!/usr/bin/env python3
"""
Hardware design visualization for Raspberry Pi Controller.

Simple minimalist design showing Raspberry Pi pins and connected components.
"""

from rasp_controller.hardware_config import HardwareConfig, DeviceType

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

def create_hardware_design_plot():
    """Create a simple hardware design visualization."""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    fig.suptitle('Raspberry Pi Controller Hardware Connection', fontsize=16, fontweight='bold')
    
    create_simple_layout(ax)
    
    plt.tight_layout()
    return fig

def create_simple_layout(ax):
    """Create a simple Pi + components layout."""
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.set_aspect('equal')
    
    # Draw Raspberry Pi with 40 pins (left side)
    draw_raspberry_pi(ax, x=4, y=6)
    
    # Draw LED and button components (right side)
    draw_components(ax, start_x=10, start_y=10)
    
    # Draw connections
    draw_connections(ax)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')

def draw_raspberry_pi(ax, x, y):
    """Draw a simple Raspberry Pi representation with 40 pins."""
    
    # Pi board outline
    pi_rect = Rectangle((x-1.5, y-4), 3, 8, 
                       facecolor='lightgray', alpha=0.3, edgecolor='black', linewidth=2)
    ax.add_patch(pi_rect)
    ax.text(x, y+4.5, 'Raspberry Pi GPIO', fontsize=12, fontweight='bold', ha='center')
    
    # Get pin mappings
    button_pins = HardwareConfig.get_button_pins()
    led_pins = HardwareConfig.get_led_pins()
    mappings = HardwareConfig.GPIO_MAPPINGS
    
    # Create pin function lookup
    pin_functions = {}
    for mapping in mappings:
        if mapping.device_type == DeviceType.UTILITY_LINE:
            pin_functions[mapping.button_gpio] = f"BTN-UTIL"
            pin_functions[mapping.led_gpio] = f"LED-UTIL"
        else:
            pin_functions[mapping.button_gpio] = f"BTN-H{mapping.house_id}"
            pin_functions[mapping.led_gpio] = f"LED-H{mapping.house_id}"
    
    # Standard Pi pin functions
    standard_pins = {
        1: "3.3V", 2: "5V", 3: "GPIO2", 4: "5V", 5: "GPIO3", 6: "GND",
        7: "GPIO4", 8: "GPIO14", 9: "GND", 10: "GPIO15", 11: "GPIO17", 12: "GPIO18",
        13: "GPIO27", 14: "GND", 15: "GPIO22", 16: "GPIO23", 17: "3.3V", 18: "GPIO24",
        19: "GPIO10", 20: "GND", 21: "GPIO9", 22: "GPIO25", 23: "GPIO11", 24: "GPIO8",
        25: "GND", 26: "GPIO7", 27: "GPIO0", 28: "GPIO1", 29: "GPIO5", 30: "GND",
        31: "GPIO6", 32: "GPIO12", 33: "GPIO13", 34: "GND", 35: "GPIO19", 36: "GPIO16",
        37: "GPIO26", 38: "GPIO20", 39: "GND", 40: "GPIO21"
    }
    
    # 40-pin header (2 columns, 20 rows)  
    pin_size = 0.1
    
    for pin in range(1, 41):
        # Calculate position
        row = (pin - 1) // 2
        col = (pin - 1) % 2
        
        pin_x = x - 0.4 + (col * 0.8)
        pin_y = y + 3.5 - (row * 0.35)
        
        # Determine pin color and function
        if pin in button_pins or pin in led_pins:
            pin_color = 'gray'
            pin_function = pin_functions.get(pin, f"GPIO{pin}")
        else:
            pin_color = 'lightgray'
            pin_function = standard_pins.get(pin, f"GPIO{pin}")
        
        # Draw pin
        pin_circle = Circle((pin_x, pin_y), pin_size, 
                          color=pin_color, edgecolor='black', linewidth=0.5)
        ax.add_patch(pin_circle)
        
        # Pin number (readable size)
        ax.text(pin_x, pin_y, str(pin), fontsize=6, ha='center', va='center', 
               color='white' if pin in button_pins or pin in led_pins else 'black',
               fontweight='bold')
        
        # Pin labels (left pins get labels on left, right pins on right)
        if col == 0:  # Left column pins
            label_x = pin_x - 0.8
            ha = 'right'
        else:  # Right column pins  
            label_x = pin_x + 0.8
            ha = 'left'
        
        # Only show labels for used pins or important pins
        if pin in button_pins or pin in led_pins or pin in [1, 2, 6, 9, 14, 17, 20, 25, 30, 34, 39]:
            ax.text(label_x, pin_y, pin_function, fontsize=7, ha=ha, va='center',
                   fontweight='bold' if pin in button_pins or pin in led_pins else 'normal')

def draw_components(ax, start_x, start_y):
    """Draw LEDs and buttons in organized layout."""
    
    mappings = HardwareConfig.GPIO_MAPPINGS
    
    # Group by house
    house_mappings = {}
    for mapping in mappings:
        if mapping.house_id not in house_mappings:
            house_mappings[mapping.house_id] = []
        house_mappings[mapping.house_id].append(mapping)
    
    current_y = start_y
    
    # Draw house controls
    for house_id in sorted(house_mappings.keys()):
        if house_id == 0:  # Skip utility (will draw separately)
            continue
            
        # House label
        ax.text(start_x, current_y, f'House {house_id}', fontsize=11, fontweight='bold')
        current_y -= 0.5
        
        for mapping in house_mappings[house_id]:
            # Button (white with black border)
            btn_circle = Circle((start_x, current_y), 0.15,
                              facecolor='white', edgecolor='black', linewidth=1)
            ax.add_patch(btn_circle)
            ax.text(start_x, current_y, 'B', fontsize=8, ha='center', va='center', 
                   color='black', fontweight='bold')
            
            # LED (light gray with black border)
            led_circle = Circle((start_x + 1, current_y), 0.15,
                              facecolor='lightgray', edgecolor='black', linewidth=1)
            ax.add_patch(led_circle)
            ax.text(start_x + 1, current_y, 'L', fontsize=8, ha='center', va='center',
                   color='black', fontweight='bold')
            
            # Device label
            device_name = mapping.device_type.value.replace('_', ' ')
            ax.text(start_x + 2, current_y, device_name, fontsize=9, va='center')
            
            current_y -= 0.6
        
        current_y -= 0.3  # Extra space between houses
    
    # Draw utility control
    utility_mapping = next(m for m in mappings if m.device_type == DeviceType.UTILITY_LINE)
    
    ax.text(start_x, current_y, 'Global', fontsize=11, fontweight='bold')
    current_y -= 0.5
    
    # Utility button
    util_btn = Circle((start_x, current_y), 0.15,
                     facecolor='white', edgecolor='black', linewidth=1)
    ax.add_patch(util_btn)
    ax.text(start_x, current_y, 'B', fontsize=8, ha='center', va='center',
           color='black', fontweight='bold')
    
    # Utility LED
    util_led = Circle((start_x + 1, current_y), 0.15,
                     facecolor='lightgray', edgecolor='black', linewidth=1)
    ax.add_patch(util_led)
    ax.text(start_x + 1, current_y, 'L', fontsize=8, ha='center', va='center',
           color='black', fontweight='bold')
    
    ax.text(start_x + 2, current_y, 'UTILITY LINE', fontsize=9, va='center')
    
    # Simple legend
    ax.text(start_x, 1, 'B = Button, L = LED', fontsize=10, style='italic')

def draw_connections(ax):
    """Draw simple wire connections between Pi and components."""
    
    mappings = HardwareConfig.GPIO_MAPPINGS
    
    # Pi position
    pi_x = 4
    pi_y = 6
    
    # Component starting position
    comp_x = 10
    comp_y = 10
    
    # Group mappings by house for positioning
    house_mappings = {}
    for mapping in mappings:
        if mapping.house_id not in house_mappings:
            house_mappings[mapping.house_id] = []
        house_mappings[mapping.house_id].append(mapping)
    
    current_y = comp_y - 0.5
    
    # Draw connections for each house
    for house_id in sorted(house_mappings.keys()):
        if house_id == 0:  # Skip utility for now
            continue
            
        for mapping in house_mappings[house_id]:
            # Calculate Pi pin positions
            btn_pin = mapping.button_gpio
            led_pin = mapping.led_gpio
            
            # Button pin position on Pi
            btn_row = (btn_pin - 1) // 2
            btn_col = (btn_pin - 1) % 2
            btn_pi_x = pi_x - 0.4 + (btn_col * 0.8)
            btn_pi_y = pi_y + 3.5 - (btn_row * 0.35)
            
            # LED pin position on Pi  
            led_row = (led_pin - 1) // 2
            led_col = (led_pin - 1) % 2
            led_pi_x = pi_x - 0.4 + (led_col * 0.8)
            led_pi_y = pi_y + 3.5 - (led_row * 0.35)
            
            # Draw wire from Pi to button
            ax.plot([btn_pi_x, comp_x], [btn_pi_y, current_y], 
                   'k-', alpha=0.4, linewidth=1)
            
            # Draw wire from Pi to LED
            ax.plot([led_pi_x, comp_x + 1], [led_pi_y, current_y], 
                   'k-', alpha=0.4, linewidth=1)
            
            current_y -= 0.6
        
        current_y -= 0.3
    
    # Draw utility connections
    utility_mapping = next(m for m in mappings if m.device_type == DeviceType.UTILITY_LINE)
    
    # Utility button connection
    btn_pin = utility_mapping.button_gpio
    btn_row = (btn_pin - 1) // 2
    btn_col = (btn_pin - 1) % 2
    btn_pi_x = pi_x - 0.4 + (btn_col * 0.8)
    btn_pi_y = pi_y + 3.5 - (btn_row * 0.35)
    
    ax.plot([btn_pi_x, comp_x], [btn_pi_y, current_y], 
           'k-', alpha=0.4, linewidth=1)
    
    # Utility LED connection
    led_pin = utility_mapping.led_gpio
    led_row = (led_pin - 1) // 2
    led_col = (led_pin - 1) % 2
    led_pi_x = pi_x - 0.4 + (led_col * 0.8)
    led_pi_y = pi_y + 3.5 - (led_row * 0.35)
    
    ax.plot([led_pi_x, comp_x + 1], [led_pi_y, current_y], 
           'k-', alpha=0.4, linewidth=1)

if __name__ == '__main__':
    fig = create_hardware_design_plot()
    plt.show()