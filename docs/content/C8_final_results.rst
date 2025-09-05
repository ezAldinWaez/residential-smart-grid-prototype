Final Results
=============
This chapter presents the results obtained from simulation runs, performance analysis, and validation testing conducted during the development and evaluation of the project.

To restate the purpose of this project, it is this: to create a residential smart grid application that would minimize the grid dependence using a smart algorithm, while also providing the residential house owners a way to monitor their system. The results are as follows.

System Design Validation
------------------------
The system uses three models as the base of its simulation: the ADSR Envelope for device modeling, pvwatts for inverter modeling, and pvlib for solar panels modeling. The results of validating the models are as follows:

**ADSR Device Modeling**: The ADSR envelope model demonstrates good correlation with real refrigerator power consumption data extracted from scientific literature.

.. plot:: _static/plots/C8_ADSR_vs_real_load_profile.py
   :align: center

   RSGP ADSR refrigerator model validation against real power consumption data from MDPI paper (Energies 2018, 11, 607). The comparison shows the ADSR envelope model's ability to approximate real device behavior with synchronized timing and comparable power levels.

**Solar System Modeling Accuracy**: Due to usage of the standard libraries pvlib and pvwatts, and the usage of a dataset from the National Solar Radiation Database, the solar system simulation, including the inverter and panels, closely match reality.

.. .. plot:: _static/plots/C8_sss_visualization_vs_real_visualization.py
..    :align: center

..    RSGP solar system simulation validation against real inverter data from physical SolarMax installation (DataLog_929321041053717_20250203-20250209). The comparison demonstrates pvlib and NSRDB integration accuracy for solar power prediction and battery state modeling under real-world conditions.

Simulation Results and Analysis
-------------------------------
The smart power management algorithm implemented showed a reduction in grid dependence.

.. .. plot:: _static/plots/C8_plot_grid_dependence_algorithm_vs_no_management.py
..     :align: center

..     Grid dependence with the power management solution versus without it

Calculate RMSE and add maths and maybe like use plots or sth I don't know. This one needs work.

.. note:: The results of the project are tentative and must be subject to further testing and validation against real life scenarios.
