Final Results
=============
This chapter presents the results obtained from simulation runs, performance analysis, and validation testing conducted during the development and evaluation of the project.

To restate the purpose of this project, it is this: to create a residential smart grid application that would minimize excess energy and grid dependence using a smart algorithm. The results are as follows.

System Design Validation
------------------------
The system uses three models as the base of its simulation: the ADSR Envelope for device modeling, pvwatts for inverter modeling, and pvlib for solar panels modeling. The results of validating the models are as follows:

**ADSR Device Modeling**: The ADSR envelope model demonstrated good correlation with real power consumption data extracted from scientific literature. Below is a comparison between data collected from a real refrigerator versus that collected from the ADSR envelope for a refrigerator.

.. plot:: _static/plots/C8_ADSR_vs_real_load_profile.py
   :align: center

   RSGP ADSR refrigerator model validation against real power consumption data

**Solar System Modeling Accuracy**: Due to usage of the standard libraries pvlib and pvwatts, and the usage of a dataset from the National Solar Radiation Database, the solar system simulation, including the inverter and panels, closely match reality.

.. plot:: _static/plots/C8_sss_visualization_vs_real_visualization.py
   :align: center

   RSGP solar system simulation validation against real SolarMax inverter data

.. note:: The SSS data represents theoretical maximum power generation capacity calculated by pvlib based on solar irradiance and panel specifications, while the real inverter data shows practical power extraction limited by actual load demand. Solar panels only deliver the power that is actively consumed by the connected loads, which explains potential differences between theoretical generation capacity and measured inverter output.

Simulation Results and Analysis
-------------------------------
The smart power management algorithm implemented in RSGP demonstrates adaptive learning capabilities through dynamic weight adjustment and virtual battery allocation. The system continuously optimizes power distribution among houses based on load patterns and solar generation availability, leading to improved grid independence and efficient energy utilization.

.. note:: Further validation of the project can happen only through a real-world prototype and data from real usage of the project.
