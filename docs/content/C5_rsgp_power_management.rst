RSGP Power Management
=====================

Introduction
------------
The power management system serves as the intelligent coordination layer within the residential smart grid prototype, implementing sophisticated algorithms to optimize energy distribution between solar generation, battery storage, and residential demand. This chapter examines the mathematical foundations, algorithmic implementations, and coordination mechanisms that enable the power manager to achieve efficient energy utilization while maintaining system stability.

The power management system addresses the fundamental challenge of balancing supply and demand in distributed energy systems. Unlike traditional centralized power systems, the residential smart grid requires dynamic allocation decisions that account for varying solar generation, battery state-of-charge, and individual house consumption patterns. The power manager implements adaptive algorithms that learn from consumption patterns and adjust distribution weights to minimize utility grid dependence while ensuring reliable power delivery to all connected houses.

The system operates through two primary components: the central ``PowerManager`` that coordinates system-wide decisions, and individual ``VirtualBattery`` instances that represent each house's allocation within the shared battery system. This architecture enables distributed decision-making while maintaining centralized coordination, providing both flexibility and system-wide optimization capabilities.

.. note:: The power management algorithms prioritize long-term system efficiency over short-term optimization, implementing learning mechanisms that adapt to changing consumption patterns and improve performance over time.

System Architecture and Coordination
------------------------------------
The power management system integrates with both the houses simulation and solar system simulation through well-defined interfaces that enable real-time coordination and control. The architecture implements a threaded execution model that ensures power management decisions occur independently of other system components while maintaining synchronized access to shared resources.

.. mermaid::

   graph TB
       subgraph "Power Management System"
           PM[PowerManager]
           VB1[VirtualBattery 1]
           VB2[VirtualBattery 2]
           VBN[VirtualBattery N]
           PM --> VB1
           PM --> VB2
           PM --> VBN
       end
       
       subgraph "Houses Simulation"
           HS[HousesSimulator]
           H1[House 1]
           H2[House 2]
           HN[House N]
           HS --> H1
           HS --> H2
           HS --> HN
       end
       
       subgraph "Solar System Simulation"
           SSS[SolarSystemSimulator]
           INV[Inverter]
           BAT[Battery]
           PAN[Panels]
           SSS --> INV
           SSS --> BAT
           SSS --> PAN
       end
       
       PM <==> HS
       PM <==> SSS
       VB1 <==> H1
       VB2 <==> H2
       VBN <==> HN

The power manager operates on a configurable update cycle, typically set to match the houses simulation update interval of 100 milliseconds. During each update cycle, the manager executes a sequence of coordinated algorithms that process current system state, update virtual battery parameters, and make power distribution decisions.

The coordination interface provides bidirectional communication between components. The houses simulation provides current load demands and accepts load line control commands. The solar system simulation provides generation data, battery state information, and accepts load requirements while returning actual power delivery capabilities.

Virtual Battery System
-----------------------
The virtual battery system implements a distributed energy allocation mechanism that partitions the shared physical battery among individual houses based on their consumption patterns and system optimization requirements. Each house receives a dedicated ``VirtualBattery`` instance that tracks its allocated capacity, manages charge and discharge operations, and maintains dynamic weight parameters that determine its share of the total system capacity.

Mathematical Foundation
~~~~~~~~~~~~~~~~~~~~~~~
The virtual battery allocation system employs several mathematical relationships to ensure fair and efficient energy distribution. The fundamental relationship establishes the connection between virtual battery capacity and system-wide resources:

.. math::

   C_{vb,i} = C_{total} \times w_i

where:
- :math:`C_{vb,i}` represents the total capacity of virtual battery *i*
- :math:`C_{total}` represents the total physical battery capacity  
- :math:`w_i` represents the weight assigned to house *i*

The weight constraint ensures that the sum of all virtual capacities equals the total physical capacity:

.. math::

   \sum_{i=1}^{N} w_i = N

where *N* represents the number of houses in the system. This constraint maintains energy conservation while allowing dynamic reallocation based on consumption patterns.

The system implements weight boundaries to ensure fairness and prevent extreme allocations:

.. math::

   w_{min} \leq w_i \leq w_{max}

where:
- :math:`w_{min} = \alpha` (guaranteed minimum weight, typically 0.8)
- :math:`w_{max} = 1 + (1 - \alpha) \times N`

Virtual Battery Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~
The virtual battery implements charge and discharge operations that model realistic battery behavior while maintaining energy conservation across the distributed system. The charge operation accounts for charging efficiency and capacity constraints:

.. math::

   P_{charge,actual} = \min\left(\frac{P_{charge} \times \eta_{charge} \times \Delta t}{3600}, C_{total} - C_{residual}\right) \times \frac{3600}{\Delta t \times \eta_{charge}}

where:
- :math:`P_{charge,actual}` represents the actual power consumed for charging
- :math:`P_{charge}` represents the requested charging power
- :math:`\eta_{charge}` represents the charging efficiency
- :math:`\Delta t` represents the time interval in seconds
- :math:`C_{residual}` represents the current residual capacity

The discharge operation implements efficiency losses and capacity limitations:

.. math::

   P_{discharge,actual} = \min\left(\frac{P_{discharge} \times \Delta t}{\eta_{charge} \times 3600}, C_{residual}\right) \times \frac{3600 \times \eta_{charge}}{\Delta t}

The energy conversion between power and capacity uses the relationship:

.. math::

   E = P \times \frac{\Delta t}{3600}

where energy is measured in watt-hours and power in watts.

Weight Adjustment Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The virtual battery weight adjustment mechanism implements the core learning algorithm that adapts capacity allocation based on consumption patterns. The adjustment function modifies weights while maintaining system constraints:

.. math::

   w_i^{new} = \max(w_{min}, \min(w_{max}, w_i^{old} + \Delta w_i))

When weight adjustment reduces total capacity below current residual capacity, the excess energy is calculated and returned to the system:

.. math::

   E_{excess} = \max(0, C_{residual} - C_{total}^{new})

This excess energy redistribution mechanism ensures energy conservation during dynamic capacity reallocation while preventing energy loss during system optimization.

Adaptive Learning Algorithm
----------------------------
The power management system implements an adaptive learning algorithm that continuously adjusts virtual battery weights based on consumption patterns. This algorithm enables the system to optimize energy allocation over time, improving efficiency as it learns individual house consumption characteristics.

Load Baseline Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~~
The learning algorithm begins by calculating baseline deviations from average consumption to identify houses with above-average and below-average demand:

.. math::

   L_{baseline,i} = L_i - \bar{L}

where:
- :math:`L_{baseline,i}` represents the baseline deviation for house *i*
- :math:`L_i` represents the current load for house *i*  
- :math:`\bar{L} = \frac{1}{N}\sum_{i=1}^{N} L_i` represents the average load across all houses

The baseline values undergo normalization to ensure consistent scaling across different load magnitudes:

.. math::

   L_{norm,i} = \frac{L_{baseline,i}}{\max_j |L_{baseline,j}|}

This normalization prevents large absolute load values from overwhelming the learning algorithm and ensures that weight adjustments respond proportionally to relative consumption differences rather than absolute values.

Load Redistribution for Minimum Weight Houses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The algorithm implements a sophisticated redistribution mechanism for houses operating at minimum weight thresholds. When a house reaches its minimum weight constraint and exhibits below-average consumption, the algorithm redistributes its negative baseline to houses with above-average consumption:

.. math::

   L_{norm,j}^{adjusted} = L_{norm,j} + L_{norm,i} \times \frac{L_{norm,j}}{\sum_{k \in S_{pos}} L_{norm,k}}

where:
- :math:`S_{pos}` represents the set of houses with positive baseline values
- :math:`i` represents a house at minimum weight with negative baseline
- :math:`j` represents a house with positive baseline

This redistribution ensures that houses at minimum weight do not continue to lose capacity allocation while their unused allocation benefits houses with higher demand. The redistribution maintains proportional sharing among above-average consumers.

Weight Update and Learning Step
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The weight adjustment applies the calculated baseline adjustments scaled by the learning step parameter:

.. math::

   \Delta w_i = L_{norm,i}^{adjusted} \times \alpha_{learning}

where :math:`\alpha_{learning}` represents the learning step size (typically 0.002). The learning step parameter controls the adaptation rate, balancing between rapid response to consumption changes and system stability.

The total excess capacity calculation aggregates capacity releases from all weight adjustments:

.. math::

   E_{excess,total} = \sum_{i=1}^{N} E_{excess,i}

This excess capacity becomes available for redistribution during the charging phase, ensuring that energy released through weight reductions contributes to overall system efficiency.

Power Distribution Algorithms
-----------------------------
The power management system implements sophisticated algorithms for distributing available power sources among connected houses while maintaining fairness and system efficiency. These algorithms coordinate solar panel output, utility grid power, and virtual battery discharge to meet residential demand.

Houses Virtual Battery Usage Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The virtual battery usage calculation determines how much energy each house should draw from their virtual battery allocation after accounting for solar and utility power availability. The algorithm implements a priority-based allocation system that serves houses in order of their current load demand:

.. math::

   \text{For house } i \text{ with load } L_i: \quad P_{vb,i} = L_i - P_{panels,used} - P_{utility,used}

The algorithm processes houses in ascending order of load demand to ensure fair distribution:

.. math::

   P_{panels,used,i} = \min\left(L_i, \frac{P_{panels,available}}{N_{remaining}}\right)

.. math::

   P_{utility,used,i} = \min\left(L_i - P_{panels,used,i}, \frac{P_{utility,available}}{N_{remaining}}\right)

where:
- :math:`P_{panels,available}` represents remaining solar panel power
- :math:`P_{utility,available}` represents remaining utility power
- :math:`N_{remaining}` represents the number of houses not yet processed

This sequential allocation ensures that houses with lower demand receive priority access to available solar and utility power, reducing the burden on virtual battery resources for the entire system.

Virtual Battery Charging Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When excess power becomes available from solar generation, the charging algorithm distributes this power among virtual batteries based on their remaining capacity and charging capabilities. The algorithm implements priority charging for batteries with the highest capacity deficit:

.. math::

   \text{Charging order: } \arg\min_i (C_{total,i} - C_{residual,i})

The charging power allocation follows:

.. math::

   P_{charge,i} = \frac{P_{charge,available}}{N_{remaining}}

where virtual batteries are processed in order of their capacity deficit, ensuring that batteries with the most available space receive charging priority. This approach maximizes overall system energy storage utilization.

Virtual Battery Discharging with Weighted Distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The discharging algorithm implements weighted power distribution based on normalized virtual battery usage requirements. The algorithm calculates discharge weights using min-max normalization:

.. math::

   w_{discharge,i} = \frac{P_{vb,i} - \min_j P_{vb,j}}{\max_j P_{vb,j} - \min_j P_{vb,j}}

When the denominator approaches zero (all houses have similar virtual battery requirements), the algorithm defaults to equal distribution:

.. math::

   w_{discharge,i} = \frac{1}{N} \quad \text{if } \max_j P_{vb,j} - \min_j P_{vb,j} < \epsilon

The actual discharge power for each virtual battery follows:

.. math::

   P_{discharge,i} = P_{discharge,total} \times w_{discharge,i}

The algorithm tracks whether each virtual battery can fully meet its required discharge:

.. math::

   \text{Usage Met} = |P_{discharge,i} - P_{actual,i}| < \epsilon

Houses whose virtual batteries cannot meet their full energy requirements trigger load line disconnection to prevent system instability.

Load Line Management and House Disconnection
---------------------------------------------
The power management system implements dynamic load line control to maintain system stability when available energy sources prove insufficient to meet residential demand. This mechanism prevents system overload while providing graceful degradation of service during energy shortage conditions.

Load Line Control Logic
~~~~~~~~~~~~~~~~~~~~~~~~
The load line management algorithm operates on a house-by-house basis, making individual disconnection decisions based on virtual battery performance and system capacity constraints. The decision-making process follows a clear mathematical criterion:

.. math::

   \text{Disconnect house } i \text{ if: } \frac{P_{actual,discharge,i}}{P_{required,discharge,i}} < \frac{\epsilon}{P_{required,discharge,i}}

This criterion ensures that houses whose virtual batteries cannot provide their required power allocation experience load line disconnection, preventing them from drawing more energy than the system can sustainably provide.

The disconnection mechanism implements immediate action when virtual battery discharge proves insufficient. Houses experience load line disconnection during the same update cycle where their energy requirements exceed available virtual battery capacity. This immediate response prevents cascading failures and maintains system stability for remaining connected houses.

System-Wide Load Line Coordination
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The power manager coordinates load line states between individual houses and the solar system inverter. When the inverter implements load shedding due to extreme power shortage conditions, the power manager propagates this state to all connected houses:

.. math::

   \text{If } \text{Inverter Load Line} = \text{False, then } \forall i: \text{House}_i.\text{Load Line} = \text{False}

This coordination ensures that individual house load line states remain consistent with overall system capacity and prevents conflicts between local and system-wide load management decisions.

The restoration mechanism operates automatically when system conditions improve. Houses whose virtual batteries regain the ability to meet their energy requirements experience automatic load line reconnection during subsequent update cycles, enabling gradual system recovery from power shortage conditions.

Utility Power Export Distribution
---------------------------------
The power management system implements sophisticated algorithms for distributing utility export power among houses when excess energy becomes available for grid export. This mechanism ensures fair distribution of export benefits while accounting for individual house contributions to system efficiency.

Export Eligibility and Weight Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The utility export distribution algorithm operates exclusively on houses that maintain active utility line connections. Houses with disconnected utility lines receive no export allocation, ensuring that only properly connected houses participate in grid export operations:

.. math::

   S_{export} = \{i : \text{House}_i.\text{utility\_line} = \text{True}\}

The export weight calculation employs inverse virtual battery weights to provide higher export allocation to houses with lower virtual battery weights, creating incentives for efficient energy usage:

.. math::

   w_{export,i} = \frac{1}{w_{vb,i}}

The normalized export distribution calculates each house's share of total export power:

.. math::

   d_{export,i} = \frac{w_{export,i}}{\sum_{j \in S_{export}} w_{export,j}}

Export Power Allocation
~~~~~~~~~~~~~~~~~~~~~~~
The final export power allocation for each eligible house follows:

.. math::

   P_{export,i} = P_{export,total} \times d_{export,i}

where :math:`P_{export,total}` represents the total power available for utility export from the solar system. This allocation mechanism ensures that houses with more efficient virtual battery utilization (lower weights) receive proportionally higher export benefits, creating economic incentives for optimal energy usage patterns.

The export allocation algorithm updates house utility exchange power values directly, enabling immediate integration with utility billing and compensation systems. Houses that maintain lower virtual battery weights through efficient energy management receive enhanced export benefits, promoting system-wide efficiency improvements.

Mathematical Learning Framework
-------------------------------
The power management learning framework implements mathematical models that enable continuous adaptation to changing consumption patterns and system conditions. The learning algorithms optimize virtual battery weight allocation through gradient-based adjustments that minimize system-wide utility grid dependence over time.

Baseline Deviation Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The learning framework employs statistical analysis of load patterns to identify optimization opportunities. The baseline calculation establishes a reference point for evaluating individual house performance relative to system average:

.. math::

   \mu_L = \frac{1}{N} \sum_{i=1}^{N} L_i

.. math::

   \sigma_{baseline,i} = L_i - \mu_L

The normalization process ensures consistent weight adjustment scaling regardless of absolute load magnitudes:

.. math::

   \sigma_{norm,i} = \frac{\sigma_{baseline,i}}{\max_j |\sigma_{baseline,j}|}

This normalization prevents large absolute load differences from causing excessive weight adjustments while maintaining proportional response to relative consumption variations.

Load Redistribution Mathematics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The load redistribution algorithm implements mathematical fairness principles for houses operating at minimum weight constraints. The redistribution mechanism calculates proportional sharing among houses with above-average consumption:

.. math::

   \text{For } i \in S_{min\_weight} \cap S_{negative\_baseline}:

.. math::

   \Delta L_{norm,j} = \sigma_{norm,i} \times \frac{\sigma_{norm,j}}{\sum_{k \in S_{positive\_baseline}} \sigma_{norm,k}}

where:
- :math:`S_{min\_weight}` represents houses at minimum weight
- :math:`S_{negative\_baseline}` represents houses with below-average consumption  
- :math:`S_{positive\_baseline}` represents houses with above-average consumption

The redistribution maintains energy conservation while ensuring that houses at minimum weight do not experience further capacity reduction despite their efficient usage patterns.

Convergence and Stability Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The learning algorithm implements convergence mechanisms that ensure system stability over extended operation periods. The weight update process employs bounded adjustments that prevent oscillatory behavior:

.. math::

   w_i^{t+1} = \text{clamp}(w_i^t + \alpha \times \sigma_{norm,i}^{adjusted}, w_{min}, w_{max})

The learning rate parameter :math:`\alpha` (typically 0.002) controls convergence speed and system stability. Smaller values provide more stable convergence at the cost of slower adaptation to changing conditions, while larger values enable rapid adaptation but may introduce oscillatory behavior.

System Integration and Real-Time Control
-----------------------------------------
The power management system maintains continuous coordination with simulation components through real-time interfaces that enable immediate response to changing system conditions. The integration architecture ensures that power management decisions reflect current system state while maintaining performance requirements for interactive simulation control.

Real-Time Update Cycle Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The power manager executes its core algorithm within a threaded update loop that operates independently of other system components. The update cycle duration matches the simulation time step, typically configured to 100-millisecond intervals:

.. math::

   t_{update} = \frac{\Delta t_{sim}}{1000} \text{ seconds}

where :math:`\Delta t_{sim}` represents the simulation time step in milliseconds. This synchronization ensures that power management decisions occur at the same temporal resolution as houses simulation and solar system simulation updates.

The update sequence implements a structured workflow that processes system state, executes learning algorithms, performs power distribution calculations, and updates component states within each cycle:

.. mermaid::
   :caption: Power manager real-time update cycle with detailed learning algorithm workflow

   graph TD
       A[Read System State] --> B[Calculate Load Baseline Deviations]
       B --> C{Load Baseline Max > 0?}
       C -->|Yes| D[Normalize Baseline Values]
       C -->|No| E[Set All Normalized Values to 0]
       D --> F[Identify Min Weight Houses]
       E --> F
       F --> G{Any Min Weight Houses with Negative Baseline?}
       G -->|Yes| H[Redistribute Negative Baseline to Positive Houses]
       G -->|No| I[Apply Weight Adjustments]
       H --> I
       I --> J[Calculate Excess Capacity from Weight Changes]
       J --> K[Determine Power Distribution Strategy]
       K --> L{Battery Exchange Power > ε?}
       L -->|Positive| M[Charge All Virtual Batteries]
       L -->|Negative| N[Calculate Houses VB Usage]
       L -->|~Zero| Q[Skip Battery Operations]
       M --> Q
       N --> O[Normalize VB Usage Weights]
       O --> P[Discharge Virtual Batteries with Weights]
       P --> R{Usage Met for All Houses?}
       R -->|No| S[Disconnect Houses with Unmet Usage]
       R -->|Yes| T[All Houses Remain Connected]
       S --> T
       Q --> T
       T --> U{Utility Export Power > ε?}
       U -->|Yes| V[Calculate Export Distribution]
       U -->|No| W[Update Inverter Load and Utility States]
       V --> W
       W --> X[Log Virtual Battery States to CSV]
       X --> Y[Sleep Until Next Update]
       Y --> A

Inverter Synchronization
~~~~~~~~~~~~~~~~~~~~~~~~
The power manager maintains synchronization with the solar system inverter through bidirectional communication that coordinates load requirements and power delivery capabilities. The synchronization algorithm updates inverter state based on aggregated house demands and virtual battery requirements:

.. math::

   P_{load,inverter} = \sum_{i=1}^{N} L_i \times \text{LoadLine}_i

where :math:`\text{LoadLine}_i` represents the binary load line state for house *i*. The utility line state coordination ensures that the inverter maintains proper grid connection based on house connectivity:

.. math::

   \text{UtilityLine}_{inverter} = \bigvee_{i=1}^{N} \text{UtilityLine}_i

This coordination maintains consistency between individual house utility connections and overall system grid interface requirements.

Performance Monitoring and Data Collection
-------------------------------------------
The power management system implements comprehensive data collection mechanisms that capture system performance metrics, algorithm behavior, and optimization effectiveness. The monitoring system enables both real-time performance assessment and historical analysis of power management effectiveness.

Metrics Collection Framework
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The system collects time-series data for all virtual battery states, capturing capacity utilization, weight evolution, and energy flow patterns throughout simulation execution. The data collection operates at the same frequency as the update cycle, ensuring complete coverage of system behavior:

.. math::

   \text{Data Point}_{t} = \{t, w_1, w_2, \ldots, w_N, C_{res,1}, C_{res,2}, \ldots, C_{res,N}\}

The collected data enables statistical analysis of algorithm convergence, weight distribution evolution, and system efficiency improvements over time. Performance metrics derived from this data include average utility grid dependence, battery utilization efficiency, and load balancing effectiveness.

Algorithm Performance Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The monitoring system tracks key performance indicators that measure power management effectiveness and system optimization success. Primary metrics include utility grid import minimization, battery capacity utilization, and load balancing fairness:

.. math::

   \text{Grid Dependence Ratio} = \frac{\sum_t P_{utility,import,t}}{\sum_t P_{load,total,t}}

.. math::

   \text{Battery Utilization} = \frac{\sum_t C_{used,t}}{\sum_t C_{available,t}}

.. math:

   \text{Load Balance Coefficient} = \frac{\sigma_{loads}}{\mu_{loads}}

These metrics provide quantitative assessment of power management performance and enable comparison between different algorithm configurations and parameter settings.

The performance data supports both immediate system tuning and long-term algorithm development. Real-time metrics enable operators to assess current system efficiency, while historical data analysis supports algorithm improvement and parameter optimization activities.

.. note:: The extensive data collection enables machine learning approaches to enhance power management capabilities, supporting future integration of predictive algorithms and advanced optimization techniques.
