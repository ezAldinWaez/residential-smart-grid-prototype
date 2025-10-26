.. default-role:: math

Power Management
================
Introduction
------------
The power management system serves as the intelligent coordination layer. This chapter examines the algorithms and mathematical foundation that enable the power manager to achieve efficient energy utilization.

The power manager implements an adaptive algorithm that learns from the consumption patterns and adjusts distribution weights as to minimize utility grid dependence. The system operates through two primary components: the central ``PowerManager`` that coordinates system-wide decisions, and individual ``VirtualBattery`` instances that represent each house's allocation within the shared battery.

System Architecture
-------------------
The power management system integrates with both the houses simulation and solar system simulation through well-defined interfaces that enable real-time coordination and control.

The power manager operates on a configurable update cycle, typically set to match the houses simulation update interval of 100 milliseconds. During each update cycle, the manager executes a sequence of coordinated algorithms that process current system state, update virtual battery parameters, and make power distribution decisions.

The coordination interface provides bidirectional communication between components. The houses simulation provides current load demands and accepts load line control commands. The solar system simulation provides generation data, battery state information, and accepts load requirements while returning actual power delivery.

.. only:: html

   .. container:: diagram-75

      .. mermaid:: ../_static/diagrams/C5_pm_arch.mmd
         :align: center
         :caption: Power management architecture

.. only:: latex

   .. raw:: latex

      \begin{figure}[h]
      \centering
      \scalebox{0.75}{

   .. mermaid:: ../_static/diagrams/C5_pm_arch.mmd

   .. raw:: latex

      }
      \caption{Power management architecture}
      \end{figure}

Virtual Battery System
----------------------
The virtual battery system partitions the shared physical battery among individual houses based on their consumption patterns. Each house receives a dedicated ``VirtualBattery`` instance that tracks its allocated capacity, manages charge and discharge, and tracks the house's weight that determines its share of the total system capacity.

Mathematical Foundation
~~~~~~~~~~~~~~~~~~~~~~~
The virtual battery allocation system employs several mathematical relationships to ensure fair and efficient energy distribution. The fundamental relationship establishes the connection between virtual battery capacity and system-wide resources:

.. math::

   C_{vb,i} = \frac {C_{total}}{N} \times w_i

where:

- `C_{vb,i}` represents the total capacity of the i-th virtual battery

- `C_{total}` represents the total capacity of the physical battery

- `N` represents the number of houses in the system

- `w_{i}` represents the weight assigned to the i-th house

The weight constraint ensures that the sum of all virtual capacities equals the total physical capacity:

.. math::

   \sum_{i=1}^{N} w_{i} = N

where *N* represents the number of houses in the system. This constraint ensures energy conservation between the physical battery and the virtual batteries.

The system implements weight boundaries to ensure fairness and prevent extreme allocations:

.. math::

   w_{min} \leq w_i \leq w_{max}

where:

- `w_{min} = \alpha` (guaranteed minimum weight, typically 0.8)

- `w_{max} = 1 + (1 - \alpha) \times (N - 1)`

Virtual Battery Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~
The virtual battery implements charge and discharge operations that maintain energy conservation across the distributed system. The charge operation accounts for charging efficiency and capacity constraints:

.. math::

   P_{charge,actual} = \min\left(P_{charge} \times \eta_{charge} \times \Delta t, C_{total} - C_{residual}\right) \times \frac{1}{\Delta t \times \eta_{charge}}

where:

- `P_{charge,actual}` represents the actual power consumed for charging
- `P_{charge}` represents the requested charging power
- `\eta_{charge}` represents the charging efficiency
- `\Delta t` represents the time interval in hours: `\Delta t = \frac{\Delta t_{s}}{3600}` where `\Delta t_{s}` represents the time interval in seconds
- `C_{total}` represents the maximum capacity
- `C_{residual}` represents the current residual capacity

The discharge operation implements efficiency losses and capacity limitations:

.. math::

   P_{discharge,actual} = \min\left(\frac{P_{discharge} \times \Delta t}{\eta_{charge}}, C_{residual}\right) \times \frac{\eta_{charge}}{\Delta t}

The energy conversion between power and capacity uses the relationship:

.. math::

   E = P \times \Delta t

where energy is measured in watt-hours and power in watts.

Weight Adjustment Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The adjustment function modifies weights while maintaining system constraints:

.. math::

   w_{i}^{t+1} = \text{clamp}(w_{i}^{t} + \Delta w_{i}, w_{min}, w_{max})

After adjusting the weights, the new capacity for the virtual battery is calculated:

.. math::

   C_{vb,i}^{t+1} = \frac {C_{total}}{N} \times w_{i}^{t+1}

When weight adjustment reduces total capacity `C_{vb,i}^{t+1}` below current residual capacity `C_{vb,i}^{residual}`, the excess energy is calculated and returned to the system:

.. math::

   E_{excess} = \max(0, C_{vb,i}^{residual} - C_{vb,i}^{t+1})

This excess energy is then redistributed among the other virtual batteries to conserve the energy during system optimization.

Virtual Battery Synchronization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The system implements a periodic synchronization mechanism to ensure the virtual batteries maintain perfect alignment with the physical battery state. This corrects accumulated floating-point precision errors that can arise from iterative charge and discharge operations.

The synchronization treats the physical battery as the authoritative source of truth and distributes any detected error proportionally among virtual batteries based on their total capacities. This approach reflects real-world implementation where the power manager reads from but does not directly control the physical battery system.

.. plot:: _static/plots/C5_virtual_battery_weight_and_allocation.py
   :align: center

   Virtual battery weight evolution and capacity allocation

Adaptive Learning Algorithm
---------------------------
The power management system implements an adaptive learning algorithm that continuously adjusts virtual battery weights based on consumption. This algorithm enables the system to optimize energy allocation over time, improving efficiency as it learns each house's consumption patterns.

Load Deviation Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~~
The learning algorithm employs statistical analysis of houses consumption to make decisions regarding their weights. It begins by calculating deviations from the mean consumption to identify houses with above-average and below-average demand:

.. math::

   \mu_{L} = \frac{1}{N} \sum_{i=1}^{N} L_{i}

.. math::

   \sigma_{i} = L_i - \mu_{L}

where:

- `L_{i}` represents the current load for the i-th house

The deviation values undergo normalization to ensure consistent scaling across different load magnitudes:

.. math::

   \sigma_{norm,i} = \frac{\sigma_{i}}{\max_j |\sigma_{j}|}

This normalization prevents large load values from overwhelming the learning algorithm and ensures that weight adjustments respond proportionally to relative consumption differences rather than absolute values.

Load Redistribution for Minimum Weight Houses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The algorithm implements a redistribution mechanism for houses operating at a minimum weight. When a house reaches its minimum weight and exhibits below-average consumption, the algorithm redistributes its negative deviation to houses with above-average consumption:

.. math::

   S_{pos} = \{i \mid \sigma_{i} > 0 \}

.. math::

   S_{neg} = \{i \mid \sigma_{i} < 0 \}

.. math::

   S_{min} = \{i \mid w_{i} = w_{min} \}

.. math::

   \sigma_{norm,j}^{adjusted} = \sigma_{norm,j} + \sigma_{norm,i} \times \frac{\sigma_{norm,j}}{\sum_{k \in S_{pos}} \sigma_{norm,k}}, \quad i \in S_{min} \cap S_{neg}, \; j \in S_{pos}

This redistribution maintains energy conservation and ensures that houses at minimum weight do not continue to lose capacity allocation.

Weight Update and Learning Step
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The calculated adjustments are then scaled by the learning rate and sent to the virtual battery to calculate its new weight:

.. math::

   \Delta w_{i}^{t+1} = \sigma_{norm,i}^{adjusted} \times \alpha_{learning}

where `\alpha_{learning}` represents the learning rate (typically 0.002). The learning rate parameter controls the convergence speed and system stability. Smaller values provide more stable convergence at the cost of slower adaptation, while larger values enable rapid adaptation but may introduce oscillatory behavior.

.. plot:: _static/plots/C5_learning_convergence_analysis.py
   :align: center

   Learning algorithm convergence analysis

.. plot:: _static/plots/C5_weight_variance_analysis.py
   :align: center

   Weight variance and convergence metrics analysis

The total excess capacity released from all weight adjustments is then aggregated:

.. math::

   E_{excess} = \sum_{i=1}^{N} E_{excess,i}

This excess capacity becomes available for redistribution during the charging phase, ensuring that energy released through weight reductions does not disappear, thus maintaining energy conservation.

Power Distribution Algorithms
-----------------------------
The power management system implements algorithms for distributing available power sources among connected houses while maintaining fairness and system efficiency. These algorithms coordinate solar panel output, utility grid power, and virtual battery discharge to meet residential demand.

Houses Virtual Battery Usage Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The virtual battery usage calculation determines how much energy each house should draw from their virtual battery after accounting for the solar and utility power available. The algorithm implements a priority-based allocation system that processes houses in ascending order of load demand to ensure fair distribution:

.. math::

   P_{panels,used,i} = \min\left(L_i, \frac{P_{panels,available}}{N_{remaining}}\right)

.. math::

   P_{utility,used,i} = \min\left(L_i - P_{panels,used,i}, \frac{P_{utility,available}}{N_{remaining}}\right)

.. math::

   P_{vb,i} = L_i - P_{panels,used,i} - P_{utility,used,i}

where:

- `L_{i}` represents the load of the i-th house
- `P_{panels,available}` represents remaining solar panel power
- `P_{utility,available}` represents remaining utility power
- `N_{remaining}` represents the number of houses not yet processed
- `P_{vb,i}` represents the i-th house power demand from its virtual battery

.. plot:: _static/plots/C5_power_distribution_waterfall.py
   :align: center

   Power distribution waterfall visualization

This sequential allocation ensures that houses with lower demand receive priority access to available solar and utility power, as they might not use their full share, thus allowing for efficient redistribution of the remainder equally among the remaining houses.

Virtual Battery Charging Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When excess power becomes available from solar generation, the charging algorithm distributes this power among virtual batteries based on their remaining capacity and charging capabilities. The algorithm implements priority charging for batteries with the lowest capacity deficit:

.. math::

   \text{Charging order: } \arg\min_i (C_{total,i} - C_{residual,i})

The charging power allocation follows:

.. math::

   P_{charge,i} = \frac{P_{charge,available}}{N_{remaining}}

where virtual batteries are processed in order of their capacity deficit, ensuring that batteries with the least available space receive charging priority as they might not need their full share, thus allowing for efficient redistribution of the remainder of their share equally among the remaining virtual batteries.

Virtual Battery Discharging with Weighted Distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The discharging algorithm implements weighted power distribution based on the normalized power demands from the virtual batteries. The algorithm calculates discharge weights using sum normalization:

.. math::

   w_{discharge,i} = \begin{cases} \dfrac{P_{vb,i}}{\sum_{j=1}^{N} P_{vb,j}} & \sum_{j=1}^{N} P_{vb,j} > \epsilon \\[2ex] \dfrac{1}{N} & \text{otherwise} \end{cases}

When the denominator approaches zero (no house demands discharging of its virtual battery), the algorithm defaults to equal distribution.

The actual discharge power for each virtual battery follows:

.. math::

   P_{discharge,i} = P_{discharge,total} \times w_{discharge,i}

The algorithm tracks whether each virtual battery can fully meet its required discharge:

.. math::

   \text{Usage Met} = |P_{discharge,i} - P_{actual,i}| < \epsilon

Houses whose virtual batteries cannot meet their full energy requirements trigger load line disconnection to prevent system instability.

.. plot:: _static/plots/C5_virtual_battery_soc_tracking.py
   :align: center

   Virtual battery state-of-charge tracking

System-Wide Load Line Coordination
----------------------------------
The power manager coordinates load line states between individual houses and the solar system inverter. When the inverter implements load shedding due to extreme power shortage, the power manager propagates this state to all connected houses:

.. math::

   \neg LL_{inverter} \rightarrow \neg LL_{i}, \quad \forall i

where:

- `LL_{inverter}` represents the state of the inverter load line connection
- `LL_{i}` represents the state of the load line connection of the i-th house

This ensures individual house load line states remain consistent with overall system capacity and prevents conflicts between local and system-wide load management decisions.

Restoration operates automatically after a configurable set interval (typically 30 seconds).

Utility Power Export Distribution
---------------------------------
The power management system implements an algorithm for distributing utility export power among houses when excess energy becomes available for grid export. The algorithm ensures fair distribution of export benefits while accounting for individual house contributions to system efficiency.

Export Eligibility and Weight Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The utility export distribution algorithm operates exclusively on houses that maintain active utility line connections:

.. math::

   S_{export} = \{i \mid UL_{i} \}

where:

- `UL_{i}` represents the utility line connection state of the i-th house

The export weight calculation employs inverse virtual battery weights to provide higher export allocation to houses with lower virtual battery weights, creating incentives for efficient energy usage:

.. math::

   w_{export,i} = \frac{1}{w_{vb,i}}

The normalized export distribution calculates each house's share of total export power using sum normalization:

.. math::

   w_{export,norm,i} = \frac{w_{export,i}}{\sum_{j \in S_{export}} w_{export,j}}, \quad \forall i \in S_{export}

Export Power Allocation
~~~~~~~~~~~~~~~~~~~~~~~
The final export power allocation for each eligible house follows:

.. math::

   P_{export,i} = P_{export,total} \times w_{export,norm,i}

where `P_{export,total}` represents the total power available for utility export from the solar system.

This ensures that houses with more efficient virtual battery utilization (lower weights) receive proportionally higher export benefits, creating economic incentives for optimal energy usage.

.. plot:: _static/plots/C5_export_distribution_fairness.py
   :align: center

   Utility export distribution fairness demonstration

System Integration and Real-Time Control
----------------------------------------
The power management system maintains continuous coordination with simulation components through real-time interfaces. The integration architecture ensures that power management decisions reflect current system state.

Real-Time Update Cycle Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The power manager executes its core algorithm within a threaded update loop that operates independently of other system components. The update cycle duration matches the simulation time step, typically configured to 100-millisecond intervals. This synchronization ensures that power management decisions occur at the same time as houses simulation and solar system simulation updates.

The update sequence implements a structured workflow that processes system state, executes learning algorithms, performs power distribution calculations, and updates component states within each cycle:

.. mermaid:: ../_static/diagrams/C5_pm_flowchart.mmd
   :align: center
   :caption: Power manager real-time update cycle

Inverter Synchronization
~~~~~~~~~~~~~~~~~~~~~~~~
The power manager maintains synchronization with the solar system inverter through bidirectional communication that coordinates load requirements and power delivery capabilities. The synchronization algorithm updates inverter state based on aggregated house demands:

.. math::

   P_{load,inverter} = \sum_{i=1}^{N} L_{i} \times LL_{i}

where `LL_{i}` represents the binary load line state for the i-th house.

The utility line state coordination ensures that the inverter maintains proper grid connection based on house connectivity:

.. math::

   UL_{inverter} = \bigvee_{i=1}^{N} UL_{i}

where `UL_{i}` represents the binary utility line state for the i-th house. This coordination maintains consistency between individual house utility connections and overall system grid interface requirements.

.. note:: The current model for setting the inverter's utility line is not representative of the real world and thus must be changed to one more closely reflective of reality. It was set as this for now for the lack of a better idea, and further analysis of the problem was precluded by approaching deadlines.

Performance Monitoring and Data Collection
------------------------------------------
The power management system implements data collection that captures system performance metrics and algorithm behavior. The monitoring system enables both real-time performance assessment and historical analysis of power management effectiveness.

The system collects time-series data for all virtual battery states, capturing capacity utilization, weight evolution, and energy flow throughout simulation execution. The collected data enables statistical analysis of algorithm convergence, weight distribution evolution, and system efficiency improvements over time. Performance metrics derived from this data include average utility grid dependence, battery utilization efficiency, and load balancing effectiveness.

The collected data allows for the calculation of key performance metrics that measure power management effectiveness and system optimization success. Primary metrics include utility grid import minimization and battery capacity utilization:

.. math::

   \text{Grid Dependence Ratio} = \frac{\sum_t P_{utility,import,t}}{\sum_t P_{load,total,t}}

.. math::

   \text{Battery Utilization} = \frac{\sum_t C_{discharge,t}}{\sum_t C_{residual,t}}

These metrics provide quantitative assessment of power management performance and enable comparison between different algorithm configurations and parameter settings.

.. note:: The extensive data collection enables future integration of machine learning for predictive algorithms and advanced optimization techniques.
