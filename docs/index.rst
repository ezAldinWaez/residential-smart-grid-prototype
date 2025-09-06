Residential Smart Grid
======================
Residential solar energy systems create distribution inefficiencies where individual houses generate excess energy while others lack energy, resulting in wasted resources and increased grid dependence despite available energy. The Residential Smart Grid Prototype (RSGP) addresses this problem by implementing an intelligent power management solution that optimizes energy allocation among houses with varying consumption patterns. The system employs a distributed simulation architecture consisting of houses simulation using Attack-Decay-Sustain-Release envelope modeling for realistic device behavior, solar system simulation integrating National Solar Radiation Database data with pvlib and pvwatts libraries, and power management implementing a statistical learning algorithm for virtual battery allocation based on consumption patterns. The power management algorithm partitions shared physical battery among individual houses through a virtual battery system with dynamically adjusted allocation weights, employing normalized load deviation calculations and fairness constraints to ensure fair energy distribution while minimizing grid dependence. Implementation includes real-time monitoring interfaces through tkinter-based dashboard systems and Raspberry Pi GPIO controllers enabling physical interaction through button controls and LED feedback. Results of validation demonstrate correlation between ADSR device modeling and published consumption data, with system performance metrics indicating reduced utility grid dependence.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :numbered:

   content/C1_introduction
   content/C2_project_preview
   content/C3_rsgp_houses_simulation
   content/C4_rsgp_solar_system_simulation
   content/C5_rsgp_power_management
   content/C6_dashboard
   content/C7_rasp_controller
   content/C8_final_results
   content/C9_conclusions_and_suggestions

.. toctree::
   :maxdepth: 2

   content/_thanks_and_appreciation
   content/_references

.. toctree::
   :maxdepth: 2
   :numbered:

   content/A1_docs_workflow
   content/A2_notebooks_workflow
   content/A3_api_reference

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
