Houses Simulation
=================
Introduction
------------
The houses simulation serves as the primary load generator within the system. This chapter examines the implementation of the residential home model, the device modeling framework, and the coordination mechanisms between the components of the house simulation.

The significance of the houses simulation extends beyond simple load modeling. It provides the testing environment to evaluate power management algorithms under varying consumption scenarios. The simulation tracks :math:`N` houses implementing the same model. Each house contains multiple devices with different consumption patterns. This aims to mirror real world residential demand.

Architecture Overview
---------------------
The architecture separates simulation coordination, individual house modeling, and device-level power consumption calculations.

.. mermaid:: ../_static/graphs/C3_hs_arch.mmd
   :align: center
   :caption: Houses simulation architecture

- The ``HousesSimulator`` serves as the coordination layer; it manages the house instances and coordinates their execution.
- The ``House`` serves as the individual unit; it maintains state information about its devices and utility and load lines.
- The ``DeviceClass`` serves as the base for the loads; it does the calculations per each device's parameters to simulate realistic load consumption patterns.

.. note:: The design prioritizes modularity and allows for dynamic addition of new device types without modification to the core simulation. This makes it easier to craft testing scenarios.

The Houses Simulator
--------------------
The ``HousesSimulator`` coordinates the execution of individual house instances; it aggregates system-wide load calculations and provides the interface between the residential demand and the power management system. The simulator operates on its own thread to ensure that house load calculations proceed independently of the other components. The system-wide load aggregation follows:

.. math::

   L_{system} = \sum_{i=1}^{N} L_{i} \times LL_{i}

where :math:`N` represents the number of the houses, :math:`L_{i}` the load of the i-th house, and :math:`LL_{i}` the binary connection state for the i-th house.

.. mermaid:: ../_static/graphs/C3_hs_workflow.mmd
   :align: center
   :caption: HousesSimulator coordination and load aggregation workflow

The simulator implements a configurable update cycle usually set to 100-millisecond intervals. During each update cycle, the simulator queries all house instances for their current power consumption and aggregates these values. The system-wide total load is then made available to the power management system.

.. warning:: Load line disconnection affects only the connectivity between houses and the power providers; internal house simulations continue to maintain realistic behavior on reconnection.

Individual House Modeling
-------------------------
The ``House`` model maintains state information about connectivity and devices.Multiple device instances coexist and contribute to the overall house load. Each house contains a predefined set of device types, which include heating and cooling systems, lighting, major appliances, and miscellaneous electrical loads.

The model aggregates individual device loads and tracks its energy exchange with the utility. This supports both scenarios where the house exports excess renewable energy or imports power when that renewable energy is insufficient. The house load aggregation follows:

.. math::

   L_{house} = \sum_{d=1}^{N_{devices}} L_{device,d}

where utility exchange power is calculated as the difference between available renewable energy and house demand, with positive values indicating export and negative values indicating import.

Device Modeling Framework
-------------------------
The ``Device`` modeling framework implements a mathematical model that captures the dynamic behavior of residential electrical appliances. This framework borrows the **Attack-Decay-Sustain-Release envelope (ADSR)** from sound synthesis and uses it along wave modulation techniques to approximate the load profiles. These techniques generate realistic power consumption patterns that mimic real electrical devices.

.. plot:: _static/plots/C3_adsr_envelope_basic.py
   :align: center

   ADSR envelope showing Attack-Decay-Sustain-Release phases with device state transitions

The **ADSR envelope** provides the temporal structure for the device's power consumption. It models the startup spike, steady-state operation, and shutdown characteristics of the device. The mathematical representation of the envelope uses piecewise linear functions with configurable timing parameters:

- The **Attack** phase models the initial power spike that occurs when the device activates. This typically involves inrush currents for motor-driven appliances or heating element activation for thermal devices. The mathematical representation follows: :math:`P(t) = \frac{1}{a} \times t` for :math:`0 \leq t \leq a`.
- The **Decay** phase models the transition from that startup spike to normal operation as the device's components stabilize. The decay function implements: :math:`P(t) = \frac{s-1}{d} \times t + 1 - a \times \frac{s-1}{d}` for :math:`a < t \leq a+d`.
- The **Sustain** phase models the steady-state operation where the device maintains its power consumption level. This phase also uses wave modulation to model load variations due to changing conditions. The sustain level maintains: :math:`P(t) = s` for :math:`t > a+d`.
- The **Release** phase models the shutdown. This includes braking effects in motor systems and thermal cool-down periods that continue to consume power for a short while until complete shutdown. The release function follows: :math:`P(t) = -\frac{s}{r} \times t + P_{toggle}` where :math:`P_{toggle}` represents the power level at device deactivation.

Wave modulation introduces realistic variations in power consumption over the ADSR envelope. The framework supports multiple modulation types: sine waves, square waves, and random modulation. These modulation patterns operate at different frequencies and amplitudes to create complex power signatures that more closely match measured residential devices' behavior.

The wave modulation mathematical functions include:

- **Sine wave modulation**: :math:`W(t) = 1 + w_a \times \sin\left(\frac{2\pi t}{w_p}\right)`
- **Square wave modulation**: :math:`W(t) = 1 + w_a \times \text{sgn}\left(\sin\left(\frac{2\pi t}{w_p}\right)\right)`
- **Random modulation**: :math:`W(t) = 1 + w_a \times \mathcal{U}(-1, 1)`

where :math:`w_a` represents wave amplitude, :math:`w_p` represents wave period, and :math:`\mathcal{U}(-1, 1)` represents uniform random distribution.

.. plot:: _static/plots/C3_some_regular_devices_loads_over_time.py
   :align: center

   Some regular devices simulated load profiles

.. plot:: _static/plots/C3_device_parameter_impact.py
   :align: center

   ADSR parameter impact comparison showing how Attack time, Sustain level, Release time, and Wave modulation affect device load curves

The device modeling framework organizes electrical devices into categories. Each category implements specialized ADSR parameters and wave modulation to capture the unique behavior of the device. The total device class load calculation combines all active device instances:

.. math::

   L_{total} = \sum_{i=1}^{N_{active}} P_{base} \times W(t) \times ADSR_i(t)

where :math:`P_{base}` represents the base wattage, :math:`W(t)` represents the wave modulation function, and :math:`ADSR_i(t)` represents the envelope multiplier for device instance *i*.

Integration with Power Management
---------------------------------
The ``HousesSimulator`` provides the aggregated system load to the ``PowerManager``, along the specific load for each house in the simulation. The ``PowerManager`` then does its calculation and may communicate back to the simulation, connecting or disconnecting some of the houses' load or utility lines. The ``HouseSimulator`` thus offers an interface for the ``PowerManager`` to read the data it needs and modify the simulation per its judgment.

.. note:: The interface maintains loose coupling between the ``HouseSimulator`` and the ``PowerManager`` to enable independent development and testing.

Data Collection
---------------
The houses simulation captures device operation statistics and system performance metrics for later analysis. The data is stored as a time-series dataset (in a CSV file) to enable examination of the effectiveness of power management solutions.

CSV logging operates in the update cycle (usually once every 100-milliseconds). It records total house loads, individual device loads, connectivity states, and utility exchange values for each house throughout the simulation. The goal is to track the utility exchange power and minimize it through an effective power management solution.

.. plot:: _static/plots/C3_houses_simulation_visualization.py
   :align: center

   Real-time data demonstration showing system load and individual house loads during a controlled device operation scenario
