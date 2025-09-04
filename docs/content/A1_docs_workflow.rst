.. raw:: latex

  \appendix

Documentation Workflow
======================
Introduction
------------
The workflow implements a multi-phase approach that ensures content accuracy, visual consistency, and mathematical precision while supporting both web-based development documentation and academic publication formats. The system uses version control to allow for collaborative development and it separates the work into writing, editing, enrichment, and validation phases.

Collaborative Development Approach
----------------------------------
The collaborative approach implements clear role separation to optimize the development process:

- **Content Authors**: Focus on technical accuracy and comprehensive coverage of system components without concern for formatting or presentation details.
- **Technical Editors**: Verify mathematical formulas and algorithm representations, and cross-reference accuracy between documentation and implementation.
- **Content Enrichers**: Add diagrams, plots, figures, and visual elements that support the text without modifying core technical information.
- **Language Reviewers**: Ensure consistency in technical terminology, writing style, and adherence to academic standards.

This separation enables parallel development where multiple team members can contribute simultaneously without conflicts or redundant effort.

Documentation Development Phases
--------------------------------
The documentation development follows four phases that ensure content accuracy and presentation quality.

Phase 1: Initial Writing
~~~~~~~~~~~~~~~~~~~~~~~~
The initial writing phase focuses on content creation without concern for formatting, diagrams, or presentation elements. Authors concentrate on technical accuracy, comprehensive coverage, and clear explanation of system components.

During this phase, content authors:

- Document system architecture, algorithms, and mathematical formulas

- Create comprehensive technical explanations using plain reStructuredText markup

- Create placeholders for diagrams and plots to be added later

- Focus on content completeness rather than presentation quality

The writing phase employs minimal markup to avoid distraction from content development. 

Phase 2: Technical Editing
~~~~~~~~~~~~~~~~~~~~~~~~~~
The technical editing phase goes through two rounds of reviews: one for mathematical formulas and one for algorithms. 

**Mathematical Formula Verification**: All mathematical formulas undergo consistency checking between related equations. 

.. math::

   P_{total} = POA_{irradiance} \times A_{panel} \times \eta_{panel} \times N_{panels}

Each formula receives validation for:

- **Implementation correlation**: Verification that documented formulations match actual code implementations
- **Cross-reference accuracy**: Ensuring mathematical symbols maintain consistent meaning throughout documentation
- **Consistence formatting**: Ensuring the mathematical formulas all follow the same conventions

**Algorithm Representation Review**: All algorithm descriptions undergo verification to ensure accurate representation of the actual implementation. The review process examines:

- Flowchart accuracy against actual code execution paths
- Decision tree completeness for all conditional branches
- Consistency between flowcharts in the conventions they use

Phase 3: Content Enrichment
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The content enrichment phase adds visual elements, diagrams, and plots that support the text without modifying core technical information.

**Mermaid Diagram Integration**: System architecture and workflow diagrams use Mermaid markup for consistency and maintainability:

.. code-block:: text

   graph TD
     A[Houses Simulation] --> B[Power Management]
     B --> C[Solar System Simulation]
     C --> A

Diagrams undergo iterative refinement to ensure visual clarity and technical accuracy. The diagram development process includes validation against actual system architecture to prevent documentation drift from implementation reality.

**Matplotlib Plot Generation**: Technical visualizations use Python scripts that generate plots dynamically during documentation builds:

Plot generation scripts exist as separate Python files in ``docs/_static/plots/`` to maintain separation between content and visualization code. This approach enables independent development and testing of visualizations without affecting documentation content.

Phase 4: Final Validation
~~~~~~~~~~~~~~~~~~~~~~~~~
The final validation phase implements quality assurance to verify documentation integrity across all dimensions.

**Flowchart Integrity Verification**: All diagrams undergo systematic verification against actual system behavior through:

- Execution path tracing to ensure flowcharts represent actual code paths
- State transition validation for simulation components
- Interface verification between system components

**Build Verification**: Final validation includes verification of compilation success for all output formats to ensure that content renders correctly.

Sphinx
------
The documentation uses Sphinx as the primary documentation generator and reStructuredText as the primary markup language, as it proves extensibility for technical content:

.. code-block:: rst

   .. math::
   
      C_{vb,i} = \frac {C_{total}}{N} \times w_i
   
   .. mermaid:: ../_static/graphs/C5_pm_arch.mmd
      :align: center
      :caption: Power management architecture

The documentation integrates multiple Sphinx extensions that provide specialized functionality for technical documentation.

**Autodoc Extension**: Automatic API documentation generation from Python docstrings:

The autodoc extension maintains synchronization between code documentation and generated API reference, ensuring that documentation remains current with implementation changes.

**Napoleon Extension**: Support for Google and NumPy docstring formats that provide structured parameter and return value documentation within source code.

Automated API Reference Generation
----------------------------------
All source code employs Google-style docstrings that provide structured, machine-readable documentation directly within the codebase:

.. code-block:: python

   def _S(available_panels_dc_power: float, required_load_dc_power: float) -> tuple[float, float, float]:
      """Meet load from panels dc (S is for solar), convert it to ac, charge battery with the remaining.
      The function is given the vague name _S because it is a function defined within a function, 
      that of the inverter's operation, and the functions were then supposed to be called like this: 
         _S()
         _U()
         _B()
      Thus making it clear where the inverter's mode of operation was implemented in the code. 

      Args:
            available_panels_dc_power (float): The current DC power available from panels [Watt].
            required_load_dc_power (float): The DC power required by the load [Watt].

      Returns:
          tuple[float, float, float]: A tuple containing:
               - **remaining_panels_dc_power** (*float*): Solar power left after meeting load and charging battery [Watt].
               - **remaining_load_dc_power** (*float*): Load power still needed after solar contribution [Watt].
               - **battery_charge_power** (*float*): Power used to charge the battery from solar [Watt].

            """

This structured approach provides API documentation directly within source code, ensuring that documentation matches implementation behavior.

Matplotlib Plot Integration
---------------------------
The documentation uses matplotlib for technical visualizations, mathematical concepts, and simulation results.

Technical plots exist as executable Python scripts within ``docs/_static/plots/`` that generate visualizations during documentation builds:

.. code-block:: python

   import matplotlib.pyplot as plt
   from rsgp.utils.nsrdb_data import NSRDBData
   
   data = NSRDBData()
   plt.plot(data.time, data.ghi, label='Global Horizontal Irradiance')
   plt.show()

This architecture provides several advantages:

- **Live data integration**: Plots use actual simulation data and code
- **Automatic updates**: Visualizations automatically reflect code changes
- **Reproducibility**: Plot generation is completely automated and reproducible
- **Version control**: Plot scripts maintain change history independently

Scenario-Based Plot Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Plots use a scenario-based system where events are defined with their time of arrival and the corresponding lambda function that changes the state of the simulation. The Python script runs the simulation and calls those lambda functions at the times specified in the scenario, then it plots the results for visualization. Events are not arbitrary and are meant to reflect typical usage patterns in residential houses:

.. code-block:: python

   SCENARIO_EVENTS = [
       # Morning routine (6-9 AM)
       (1.0, lambda hs: hs.get_house(0).get_device('WATER_HEATER').toggle_envelope_state(0, 1.0)),
       (1.5, lambda hs: hs.get_house(1).get_device('MICROWAVE').toggle_envelope_state(0, 1.5)),
       (2.0, lambda hs: hs.get_house(2).get_device('DISHWASHER').toggle_envelope_state(0, 2.0)),
       
       # Mid-day activity (10 AM - 2 PM) 
       (3.0, lambda hs: hs.get_house(1).get_device('WASHING_MACHINE').toggle_envelope_state(0, 3.0)),
       (4.5, lambda hs: hs.get_house(2).get_device('HVAC').toggle_envelope_state(0, 4.5)),
       
       # Evening routine (6-10 PM)
       (10.0, lambda hs: hs.get_house(2).get_device('MICROWAVE').toggle_envelope_state(0, 10.0)),
       (11.0, lambda hs: hs.get_house(0).get_device('WATER_HEATER').toggle_envelope_state(0, 11.0)),
       
       # Night shutdowns (10 PM - 12 AM)
       (14.0, lambda hs: hs.get_house(0).get_device('HVAC').toggle_envelope_state(0, 14.0)),
       (15.0, lambda hs: hs.get_house(1).get_device('HVAC').toggle_envelope_state(0, 15.0)),
   ]

Scenario files enable:

- **Realistic Load Patterns**: Multi-house coordination that mimics actual residential behavior
- **Sequencing**: Time-based event orchestration for morning, afternoon, and evening routines
- **System Stress Testing**: Peak demand scenarios and load distribution analysis
- **Demonstrations**: Clear examples of power management algorithm responses

Build System Integration
~~~~~~~~~~~~~~~~~~~~~~~~
Matplotlib plots integrate with Sphinx through the ``matplotlib.sphinxext.plot_directive``:

.. code-block:: rst

   .. plot:: _static/plots/C3_adsr_envelope_basic.py
      :align: center
      
      ADSR envelope showing Attack-Decay-Sustain-Release phases

The plot directive executes Python scripts during documentation builds and embeds the generated visualizations directly into the output.
