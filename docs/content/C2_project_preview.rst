Project Preview
===============
The Residential Smart Grid Project (RSGP) aims to solve the following problem: in residential buildings where each house has its own solar system and battery, some houses have excess generated energy where others lack energy. That excess could have gone to the houses lacking energy at no cost of the houses with excess. As such, RSGP comes in to provide a smart solution that tracks the houses' needs and consumption patterns to allocate to each house the amount it needs. 

The current status of RSGP is a prototype operating on a simulation of houses and a solar system with one shared battery, with a power management algorithm that allocates and alters virtual batteries allocated to the houses. 

System Architecture Overview
----------------------------
RSGP system consists of three core simulation modules, supporting infrastructure, and analysis tools that collectively provide a foundation for analysis to improve RSGP and validate its algorithms before it is applied in the real world.

.. mermaid:: ../_static/diagrams/C2_system_arch_simple.mmd
   :align: center
   :caption: RSGP System Architecture Overview showing the relationships between core simulation components, supporting infrastructure, and external interfaces

The time simulation engine provides synchronized timestep coordination across all system components, ensuring that houses simulation, solar system simulation, and power management operate consistently. The configurable time acceleration factor enables for simulating the results of applying RSGP over larger periods of time to facilitate studying and analyzing the results before applying RSGP to the real world. 

Core Simulation Components
--------------------------
The core components are the houses simulation, solar system simulation, and power management. 

- **Houses Simulation** consists of a collection of simulated houses, each containing simulated devices that can be activated and deactivated per user input or using scripts. The ability to script activation and deactivation of devices allow for scripting scenarios and running them to collect data and use it to analyze both the simulation and the power management algorithm. 

- **Solar System Simulation** consists of simulated solar panels, battery, and inverter. This simulation uses a dataset provided for research purposes from the National Solar Radiation Database (NSRDB). As for the rest of the components, their simulation use the standard libraries pvlib and pvwatts. 

- **Power Management** consists of virtual batteries and a power manager that serves as the decision-making unit and connector between all the other components. The smart algorithm implemented is based on statistics to assign a weight to each house that represents its share of the shared battery. The algorithm implements a minimum weight and a maximum weight to ensure no house is left without an adequate share; so that only the excess is shared. 

All components log data into csv files for later analysis to improve the simulation and the algorithms implemented. 

System Integration and Communication
------------------------------------
The system uses Pyro5 remote objects to provide access to component methods and properties while maintaining network transparency.

.. mermaid:: ../_static/diagrams/C2_system_dataflow.mmd
   :align: center
   :caption: RSGP System Component Interconnection Diagram showing data flow and control signals between core modules and supporting infrastructure

The primary data exchange patterns include:

**Power Generation Data**: Solar system simulation provides power generation, battery state information, and inverter operational status to power management for decision-making.

**Load Demand Data**: Houses simulation reports individual house loads, device states, and line connection status to power management for decision-making.

**Control Commands**: Power management issues load shedding commands, utility line controls, and battery discharge instructions based on the decisions of the algorithm.

Technology Stack and Development Tools
--------------------------------------
The system foundation uses **Python** as the primary programming language, providing access to extensive scientific computing libraries. 

- **NumPy** serves as the foundation for mathematical operations, enabling efficient array operations essential for power management calculations.

- **Pandas** provides data manipulation, particularly valuable for processing NSRDB datasets and managing simulation logs. 

- **PVLib** provides photovoltaic system modeling, including solar position calculations and irradiance computations.

- **PVWatts** inverter models from the National Renewable Energy Laboratory (NREL) provide realistic DC-AC conversion efficiency curves and power electronic behavior modeling.

- **NSRDB** (National Solar Radiation Database) serves as the primary data source, providing hourly solar irradiance measurements required for realistic solar system modeling.

- **timezonefinder** provides geographic timezone detection.

- **Pyro5** (Python Remote Objects) enables the distributed simulation architecture by providing remote method invocation.

- **Tkinter** provides the graphical user interfaces. 

- **ttkbootstrap** extends the interface with modern themes and enhanced widget styling.

- **Matplotlib** generates visualizations for system analysis. 

- **Mermaid** creates system architecture diagrams and workflow visualizations integrated directly into documentation. 

- **Raspberry Pi** serves as the embedded computing platform for hardware integration. 

- **lgpio** library provides modern GPIO control with improved performance and reliability compared to legacy alternatives. 

Physical prototyping utilizes standard **breadboards**, **wires**, **LEDs**, and electronic components to create tangible representations of simulated devices and system states.

Data Analysis and Notebook Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- **Marimo** provides notebooks for interactive data analysis and system exploration. 

- **Altair** extends the visualization through statistical plotting and interactive charting features. 

Documentation and Internationalization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- **Sphinx** generates documentation with support for mathematical notation, code highlighting, and multi-format output generation. The system produces both HTML and PDF documentation.

- **LaTeX** integration enables mathematical notation and document formatting. 

- **sphinxcontrib-mermaid** integrates diagram generation directly into the documentation.

Development and Deployment Tools
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- **Git** version control manages collaborative development and maintains complete project history. 

- **Make** automates builds maintains the consistency of the process across each development environment.

- **pip** package management handles dependency resolution and virtual environment management.

- **python-dotenv** provides environment variable management for configuration settings for deployment flexibility without code modification.

Conclusion and Future Development Potential
-------------------------------------------
The system serves as both a practical solution to a real problem and a research tool that collects data and visualizes it to facilitate research and development of its algorithms. Using standard libraries like pvlib and pvwatts and international data sources like NSRDB, and implementing smart algorithms that are based on statistics, RSGP has demonstrated great results and showed potential for real world application to fairly distribute the generated solar power without wasting resources and efficiently manage the shared battery to meet each house's demand. 