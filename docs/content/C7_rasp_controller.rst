Raspberry Pi Controller
=======================

Introduction
------------
The Raspberry Pi controller serves as the physical hardware interface for the residential smart grid project. This chapter examines the implementation of the GPIO controller system that bridges the gap between the software simulation and physical hardware controls. The controller enables real-time interaction with the RSGP simulation through physical buttons and visual feedback via LEDs; thus providing an intuitive hardware-in-the-loop testing environment.

The significance of the Raspberry Pi controller extends beyond simple input and output operations. It demonstrates the practical application of smart grid control systems in a physical environment. The controller implements a bidirectional communication system that synchronizes hardware state with simulation components. This approach enables researchers to evaluate system behavior under realistic manual intervention scenarios; scenarios that mirror real-world smart grid operations where human operators must interact with automated systems.

The Raspberry Pi controller addresses the challenge of validating simulation algorithms in environments where physical interaction proves necessary. Traditional simulation systems operate in isolation; limiting their ability to demonstrate real-world applicability. The controller bridges this gap by providing tactile feedback mechanisms that enable users to understand system responses to manual interventions.

System Architecture Overview
----------------------------
The Raspberry Pi controller architecture separates hardware abstraction, GPIO management, and simulation integration into distinct layers. This modular design ensures that hardware-specific code remains isolated from simulation logic; thus maintaining system flexibility and enabling future expansion to different hardware platforms.


.. mermaid::

   graph TB
      subgraph "Raspberry Pi Hardware"
         BTN1[Button GPIO 2-14]
         LED1[LED GPIO 15-27]
         GPIO[GPIO Chip]
         BTN1 --> GPIO
         GPIO --> LED1
      end

      subgraph "GPIO Controller Layer"
         GC[GPIOController]
         HC[HardwareConfig]
         GM[GPIO Mappings]
         GC --> HC
         HC --> GM
      end

      subgraph "Remote Communication"
         PROXY[Pyro5 Proxy]
         RSGP[RSGP Remote Object]
         PROXY --> RSGP
      end

      subgraph "RSGP Simulation"
         HS[Houses Simulator]
         PM[Power Manager]
         SSS[Solar System]
         HS --> PM
         PM --> SSS
      end

      GPIO --> GC
      GC --> PROXY
      RSGP --> HS


The architecture implements a three-layer approach: the hardware layer manages physical GPIO operations; the controller layer provides abstraction and mapping logic; and the communication layer enables remote interaction with the RSGP simulation. This separation ensures that each layer operates independently; thus allowing for individual component testing and modification without affecting other system elements.

.. note:: The modular architecture enables future expansion to support additional hardware platforms by implementing new hardware abstraction layers while maintaining the same controller interface.

Hardware Configuration and GPIO Mapping
---------------------------------------
The hardware configuration system manages the mapping between physical GPIO pins and logical device controls. The system employs a structured approach to GPIO allocation that ensures consistent hardware layout and prevents pin conflicts between different control elements.

GPIO Pin Allocation Strategy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The pin allocation follows a systematic approach that groups related controls and maintains logical separation between houses and device types. The allocation strategy ensures that each house receives dedicated GPIO pins for its device controls; while global controls such as the utility line receive separate pin assignments.

.. mermaid::

   graph LR
      subgraph "House 1 Controls"
         B2[Button 2: Refrigerator] --> L15[LED 15]
         B3[Button 3: HVAC] --> L16[LED 16] 
         B4[Button 4: Water Heater] --> L17[LED 17]
         B5[Button 5: Load Line] --> L18[LED 18]
      end
      
      subgraph "House 2 Controls"
         B6[Button 6: Refrigerator] --> L19[LED 19]
         B7[Button 7: HVAC] --> L20[LED 20]
         B8[Button 8: Water Heater] --> L21[LED 21]
         B9[Button 9: Load Line] --> L22[LED 22]
      end
      
      subgraph "House 3 Controls"
         B10[Button 10: Refrigerator] --> L23[LED 23]
         B11[Button 11: HVAC] --> L24[LED 24]
         B12[Button 12: Water Heater] --> L25[LED 25]
         B13[Button 13: Load Line] --> L26[LED 26]
      end
      
      subgraph "Global Controls"
         B14[Button 14: Utility Line] --> L27[LED 27]
      end

The GPIO mapping employs a paired button-LED configuration where each control function receives both an input button and a corresponding output LED. The button enables user interaction; while the LED provides visual feedback about the current state of the associated simulation component. This pairing ensures that users receive immediate confirmation of their actions and continuous state information.

Device Type Enumeration
~~~~~~~~~~~~~~~~~~~~~~~
The system implements a comprehensive device type enumeration that covers the primary controllable elements within the residential smart grid simulation:

.. code-block:: python

   class DeviceType(Enum):
       REFRIGERATOR = "REFRIGERATOR"
       HVAC = "HVAC" 
       WATER_HEATER = "WATER_HEATER"
       LOAD_LINE = "LOAD_LINE"
       UTILITY_LINE = "UTILITY_LINE"

The enumeration provides type safety and ensures consistent device identification across the hardware configuration system. Each device type maps to specific GPIO pins and callback functions; thus enabling targeted control over individual simulation elements.

Mathematical GPIO Pin Assignment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The GPIO pin assignment follows a mathematical pattern that ensures systematic allocation across houses and device types. The button pin allocation for house devices follows:

.. math::

   P_{button,h,d} = (h-1) \times 4 + d + 1

where :math:`h` represents the house number (1-3), :math:`d` represents the device index (0-3), and :math:`P_{button}` represents the assigned button GPIO pin.

The LED pin allocation maintains a consistent offset from button pins:

.. math::

   P_{LED,h,d} = P_{button,h,d} + 13

This mathematical relationship ensures predictable pin assignments and simplifies hardware layout planning. The utility line receives dedicated pin assignments outside the house-specific allocation range to prevent conflicts with house-level controls.

GPIOController Implementation
-----------------------------
The ``GPIOController`` class serves as the primary interface between the Raspberry Pi hardware and the RSGP simulation system. The controller implements comprehensive GPIO management; including input monitoring; output control; and bidirectional communication with simulation components.

Controller Initialization and Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The controller initialization process establishes GPIO chip access; configures pin modes; and sets up callback mechanisms for user interactions. The initialization sequence ensures that all hardware resources are properly allocated before beginning the main control loop.

.. code-block:: python

   def _setup_gpio(self) -> None:
       self._gpio_chip = lgpio.gpiochip_open(0)
       for pin in HardwareConfig.get_button_pins():
           lgpio.gpio_claim_input(self._gpio_chip, pin, lgpio.SET_PULL_UP)
       for pin in HardwareConfig.get_led_pins():
           lgpio.gpio_claim_output(self._gpio_chip, pin, 0)

The GPIO setup employs pull-up resistors for button inputs to ensure reliable signal detection; while LED outputs initialize to the off state to provide a consistent starting configuration. The controller maintains internal state tracking for both buttons and LEDs to enable efficient change detection and minimize unnecessary GPIO operations.

Button State Monitoring Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The button monitoring system implements edge detection to identify button press events while filtering noise and preventing multiple triggers from single user actions. The algorithm maintains previous button states and compares them with current readings to detect falling edge transitions that indicate button presses.

.. math::

   \text{Button Press} = S_{previous} \land \neg S_{current}

where :math:`S_{previous}` represents the previous button state and :math:`S_{current}` represents the current button state. This logical operation identifies the transition from high to low that occurs when a button is pressed with pull-up configuration.

The button reading cycle operates continuously within the main update loop:

.. mermaid::

   graph TD
      A[Read All Button States] --> B{State Changed?}
      B -->|Yes| C[Identify Changed Buttons]
      B -->|No| A
      C --> D{Falling Edge Detected?}
      D -->|Yes| E[Execute Callback Function]
      D -->|No| F[Update State Cache]
      E --> F
      F --> A

LED State Synchronization
~~~~~~~~~~~~~~~~~~~~~~~~~
The LED state synchronization system maintains visual feedback that accurately reflects the current state of simulation components. The synchronization algorithm queries simulation components to determine their current operational status; then updates LED states accordingly to provide real-time visual feedback.

The LED update process implements efficient change detection to minimize GPIO write operations:

.. math::

   \text{LED Update Required} = S_{LED,cached} \neq S_{simulation,current}

where :math:`S_{LED,cached}` represents the cached LED state and :math:`S_{simulation,current}` represents the current simulation component state. This comparison prevents unnecessary GPIO operations when states remain unchanged.

Device Control Callback Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The controller implements specialized callback functions for each device type; ensuring that user interactions trigger appropriate simulation responses. The callback system employs a mapping mechanism that associates GPIO pins with specific control functions.

Utility Line Control
""""""""""""""""""""
The utility line control callback affects all houses simultaneously; reflecting the global nature of utility grid connection in the smart grid system:

.. code-block:: python

   def _toggle_utility_line(self) -> None:
       for house_idx in range(self._rsgp_hs.get_num_houses()):
           house = self._rsgp_hs.get_house(house_idx)
           house.toggle_utility_line()

This global control mechanism demonstrates the hierarchical nature of smart grid operations where system-wide decisions affect multiple individual components.

Individual Device Control
"""""""""""""""""""""""""
Individual device controls target specific house devices; enabling fine-grained control over simulation behavior:

.. math::

   \text{Device Toggle} = f(\text{house\_id}, \text{device\_type}, \text{simulation\_time})

The device control function requires three parameters: the target house identifier; the specific device type; and the current simulation time. The simulation time parameter ensures that device state changes occur at the correct temporal position within the simulation timeline.

Remote Communication Interface
------------------------------
The Raspberry Pi controller implements remote communication with the RSGP simulation through the Pyro5 distributed object system. This communication enables the controller to operate independently of the main simulation while maintaining synchronized state information and control capabilities.

Pyro5 Proxy Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~
The proxy configuration establishes connection parameters for remote simulation access. The system employs environment variable configuration to enable flexible deployment across different network configurations:

.. code-block:: python

   HOST = os.getenv('RSGP_REMOTE_OBJECT_HOST', '0.0.0.0')
   PORT = int(os.getenv('RSGP_REMOTE_OBJECT_PORT', 41991))
   BASE = f'PYRO:{{name}}@{HOST}:{PORT}'

The proxy configuration supports both local and networked deployment scenarios. Local deployment enables single-machine testing; while networked deployment enables distributed system evaluation where the Raspberry Pi controller operates on separate hardware from the main simulation.

Error Handling and Resilience
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The remote communication system implements comprehensive error handling to maintain operation despite network interruptions or simulation component failures. The error handling approach employs graceful degradation that continues controller operation while logging communication errors for debugging purposes.

.. code-block:: python

   try:
       self._button_callbacks[pin]()
   except Exception as e:
       print(f"Error executing callback for button {pin}: {e}")

The error handling strategy prevents single component failures from disrupting the entire controller system. This approach ensures that users retain access to functional controls even when some simulation components experience problems.

Communication Protocol Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The communication protocol between the controller and simulation employs a request-response pattern for state queries and command execution. The protocol design minimizes network overhead while ensuring reliable command delivery and state synchronization.

.. mermaid::

   sequenceDiagram

      participant RC as Raspberry Controller
      participant P as Pyro5 Proxy
      participant HS as Houses Simulator
      participant PM as Power Manager
      
      RC->>P: get_house(house_id)
      P->>HS: Remote method call
      HS-->>P: House object reference
      P-->>RC: House proxy object
      
      RC->>P: toggle_load_line()
      P->>HS: Execute toggle command
      HS->>PM: Update power management
      PM-->>HS: Acknowledge update
      HS-->>P: Command confirmation
      P-->>RC: Operation result

The sequence demonstrates the multi-layer communication that occurs when users interact with hardware controls. User button presses trigger cascading updates through the remote communication layer; the simulation components; and finally the power management system.

Real-Time Control Loop Implementation
-------------------------------------
The real-time control loop serves as the primary execution environment for the Raspberry Pi controller. The loop implements periodic hardware monitoring; simulation state synchronization; and error recovery mechanisms that ensure consistent controller operation.

Update Cycle Timing
~~~~~~~~~~~~~~~~~~~
The controller employs a fixed update cycle timing that balances responsiveness with system resource utilization. The default update interval of 100 milliseconds provides adequate responsiveness for human interaction while preventing excessive GPIO polling that could impact system performance.

.. math::

   f_{update} = \frac{1}{\Delta t_{update}} = \frac{1}{0.1} = 10 \text{ Hz}

The update frequency of 10 Hz ensures that button presses receive prompt recognition while LED updates occur frequently enough to provide smooth visual feedback. This timing strikes an optimal balance between responsiveness and computational efficiency.

Main Loop Workflow
~~~~~~~~~~~~~~~~~~
The main control loop implements a structured workflow that processes hardware inputs; updates simulation states; and manages error conditions within each update cycle:

.. mermaid::

   graph TD
      A[Start Update Cycle] --> B[Read All Button States]
      B --> C[Process Button Press Events]
      C --> D[Execute Device Callbacks]
      D --> E[Query Simulation States]
      E --> F[Update LED Indicators]
      F --> G{Error Occurred?}
      G -->|Yes| H[Log Error Information]
      G -->|No| I[Sleep Until Next Cycle]
      H --> I
      I --> J{Shutdown Requested?}
      J -->|No| A
      J -->|Yes| K[Cleanup GPIO Resources]
      K --> L[End Controller Operation]

The workflow ensures that each update cycle completes all necessary operations before beginning the next cycle. The error handling mechanism prevents individual operation failures from disrupting the overall control loop.

Performance Optimization Strategies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The controller implements several performance optimization strategies that minimize computational overhead while maintaining reliable operation:

State Caching
"""""""""""""
The controller maintains cached copies of button and LED states to reduce unnecessary GPIO operations. The caching mechanism compares current states with cached values before performing hardware writes:

.. math::

   \text{GPIO Write} = \begin{cases} 
   \text{Execute} & \text{if } S_{current} \neq S_{cached} \\
   \text{Skip} & \text{if } S_{current} = S_{cached}
   \end{cases}

This optimization reduces GPIO bus utilization and improves overall system performance by eliminating redundant operations.

Batch GPIO Operations
"""""""""""""""""""""
The controller groups related GPIO operations to minimize the number of individual hardware accesses. Button reading operations process all input pins within a single iteration; while LED updates handle all output pins in a coordinated manner.

Hardware Integration and Deployment
-----------------------------------
The Raspberry Pi controller requires specific hardware configuration and deployment considerations to ensure reliable operation within the residential smart grid testing environment.

Physical Hardware Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The controller implementation requires a Raspberry Pi single-board computer with sufficient GPIO pins to support the defined control mappings. The system requires:

- Raspberry Pi 4 or equivalent with 40-pin GPIO header
- 13 push-button switches with pull-up configuration
- 13 LED indicators with appropriate current-limiting resistors
- Breadboard or custom PCB for component mounting
- Power supply suitable for Raspberry Pi and connected components

The hardware configuration employs standard electronic components that enable cost-effective deployment for educational and research applications.

Physical Hardware Layout and Wiring Specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The hardware configuration implements a comprehensive physical layout that maps logical device controls to specific GPIO pins on the Raspberry Pi header. The design employs standard electronic components with careful attention to electrical specifications and signal integrity.

.. plot:: _static/plots/C7_rasp_hardware_design.py
   :align: center

   Raspberry Pi Controller Hardware Design showing GPIO pin assignments, physical component layout, and wiring connections for all house controls and utility management

The GPIO pin allocation follows the mathematical assignment pattern defined in the hardware configuration system. Button inputs employ internal pull-up resistors provided by the Raspberry Pi GPIO controller; thus simplifying external wiring requirements and ensuring reliable signal detection. The pull-up configuration means that buttons register as active-low signals; generating logic transitions from high to low when pressed.

LED outputs require current-limiting resistors to prevent excessive current flow that could damage the GPIO pins or LED components. The recommended resistor values range from 220Ω to 470Ω depending on the LED specifications and desired brightness level. The GPIO outputs operate at 3.3V logic levels with a maximum current capacity of 16mA per pin; necessitating proper current limiting for reliable operation.



Software Deployment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The software deployment requires proper installation of the lgpio library and appropriate system permissions for GPIO access. The deployment process includes:

Installation Dependencies
"""""""""""""""""""""""""
.. code-block:: bash

   sudo apt update
   sudo apt install python3-lgpio
   pip install python-dotenv Pyro5

Environment Configuration
"""""""""""""""""""""""""
The controller requires environment variable configuration for remote communication:

.. code-block:: bash

   export RSGP_REMOTE_OBJECT_HOST=192.168.1.100
   export RSGP_REMOTE_OBJECT_PORT=41991

These environment variables enable the controller to establish communication with the RSGP simulation regardless of its network location.

System Integration Testing
--------------------------
The Raspberry Pi controller undergoes comprehensive integration testing to verify proper operation within the complete residential smart grid system. The testing approach validates hardware functionality; software integration; and end-to-end system behavior.

Hardware Functionality Verification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Hardware testing verifies that all GPIO pins respond correctly to input signals and generate appropriate output responses. The testing process includes:

Button Response Testing
"""""""""""""""""""""""
Each button undergoes individual testing to verify proper signal detection and callback execution. The test procedure validates that button presses trigger the correct simulation responses without false triggering or missed events.

LED Indicator Verification
""""""""""""""""""""""""""
LED testing confirms that each indicator correctly reflects the associated simulation component state. The verification process includes testing LED response to both manual button presses and programmatic simulation state changes.

Remote Communication Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The remote communication testing verifies reliable operation across network configurations and error conditions. The testing approach includes:

.. note:: Remote communication testing requires coordination with the main RSGP simulation to ensure proper end-to-end functionality.

Network Latency Impact Analysis
"""""""""""""""""""""""""""""""
The system undergoes testing under various network latency conditions to ensure acceptable response times for user interactions. The testing establishes acceptable latency thresholds and verifies system behavior when communication delays exceed normal ranges.

Connection Resilience Testing
"""""""""""""""""""""""""""""
The controller undergoes testing with intentional network interruptions to verify error handling and recovery mechanisms. The testing confirms that the controller maintains local operation capabilities during communication outages and resumes normal operation when communication is restored.

Performance Metrics and Monitoring
----------------------------------
The Raspberry Pi controller implements performance monitoring capabilities that enable evaluation of system responsiveness and resource utilization during operation.

Response Time Measurements
~~~~~~~~~~~~~~~~~~~~~~~~~~
The system measures response times for various operation types to ensure acceptable performance characteristics:

.. math::

   T_{response} = T_{callback\_complete} - T_{button\_press}

where :math:`T_{response}` represents the total response time from button press to completion of the associated callback function.

Resource Utilization Tracking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The controller monitors computational resource utilization to ensure efficient operation within the constraints of the Raspberry Pi hardware platform. The monitoring includes CPU utilization; memory consumption; and GPIO bus utilization measurements.

Future Enhancement Possibilities
--------------------------------
The Raspberry Pi controller architecture provides a foundation for several potential enhancements that could extend its capabilities and applicability:

Expanded Device Support
~~~~~~~~~~~~~~~~~~~~~~~
The modular architecture enables straightforward addition of new device types and control mechanisms. Future enhancements could include support for analog controls; PWM output for variable-speed devices; and integration with sensors for automated feedback control.

Advanced User Interface Features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The current button-and-LED interface could be enhanced with LCD displays; rotary encoders; and audio feedback to provide richer user interaction capabilities. These enhancements would enable more sophisticated control scenarios and improved user experience.

Network-Based Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Future versions could implement network-based configuration systems that enable remote hardware setup and modification without requiring direct access to the Raspberry Pi. This enhancement would facilitate deployment in distributed testing environments.

.. warning:: Any future enhancements must maintain backward compatibility with existing hardware configurations to ensure continued support for current deployment scenarios.

The Raspberry Pi controller demonstrates the practical application of embedded systems in smart grid research and education. The system provides an accessible platform for exploring the intersection between software simulation and physical hardware control in distributed energy systems.
