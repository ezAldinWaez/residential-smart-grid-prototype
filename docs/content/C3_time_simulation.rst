Time Simulation
===============

The time simulation speeds up the passage of time in the system. One second of real time can represent one hour of simulation time, making it possible to study long-term patterns that would take too long to observe in real time. This time compression affects all parts of the system equally, keeping their relative timing intact.

.. graphviz::
   :align: center
   :caption: Time Scaling Process

   digraph time_scaling {
      rankdir=TD;
      node [shape=box, style="rounded,filled", fillcolor="#f0f0f0", fontname="Helvetica"];
      edge [fontname="Helvetica", fontsize=8];
      
      "Real Time" -> "Simulation Time" [label="Scale Factor", style="dashed"];
      "Simulation Time" -> "Solar Patterns";
      "Simulation Time" -> "Power Management";
      "Simulation Time" -> "System Behavior";
      "Solar Patterns" -> "Analysis";
      "Power Management" -> "Analysis";
      "System Behavior" -> "Analysis";
   }

The time scaling factor determines how fast the simulation runs. A factor of 3600 means one second equals one hour. This factor must be large enough to make long-term studies practical but small enough to keep the simulation stable and accurate. The factor of 3600 works well for studying solar patterns and household energy use.

.. warning::
   Choose the time scaling factor carefully. Too large a factor may cause instability, while too small a factor makes long-term studies impractical.

The system keeps track of time in three ways: when the simulation started, how much time has passed, and how to convert between real and simulation time. This ensures all parts of the system use the same time reference, regardless of how often they need to update. The start time serves as the reference point for all time calculations.

.. graphviz::
   :align: center
   :caption: Time Tracking System

   digraph time_tracking {
      rankdir=LR;
      node [shape=box, style="rounded,filled", fillcolor="#f0f0f0", fontname="Helvetica"];
      edge [fontname="Helvetica", fontsize=8];
      
      "Start Time" -> "Elapsed Time";
      "Elapsed Time" -> "Time Conversion";
      "Time Conversion" -> "System Updates";
      "System Updates" -> "State Changes";
   }

The pause function lets users stop the simulation at any point. When paused, the system keeps track of how long it was stopped and adjusts the elapsed time accordingly. This ensures the simulation continues from exactly where it left off, maintaining the correct timing of all events.

The system provides two ways to check the time: total elapsed time and current timestamp. Elapsed time works for processes that need to know how long something has been running, while timestamps are better for scheduling events. This dual approach handles both continuous and discrete timing needs.

The system's time resolution depends on the computer's clock and the scaling factor. With a factor of 3600, the smallest time step is one second of real time, or one hour of simulation time. This resolution works well for daily and seasonal patterns but may miss very rapid changes.

.. warning::
   The system may not capture events that occur faster than the minimum time step. Consider this limitation when analyzing rapid changes in power demand or generation.

The time simulation coordinates all parts of the system. It ensures solar calculations, battery operations, and other processes stay in sync. This coordination is crucial for maintaining accurate energy flows and system states over time.

.. graphviz::
   :align: center
   :caption: System Coordination

   digraph system_coordination {
      rankdir=TD;
      node [shape=box, style="rounded,filled", fillcolor="#f0f0f0", fontname="Helvetica"];
      edge [fontname="Helvetica", fontsize=8];
      
      "Time Simulation" -> "Solar System";
      "Time Simulation" -> "Power Management";
      "Time Simulation" -> "Battery System";
      "Solar System" -> "Energy Flow";
      "Power Management" -> "Energy Flow";
      "Battery System" -> "Energy Flow";
   }

The system handles events that happen at different speeds. Solar position changes slowly over hours, while power demand can change in seconds. The time simulation keeps these different rates in proportion, allowing all processes to advance at their correct relative speeds.

When the simulation pauses, all parts of the system maintain their current state. This state preservation ensures the simulation can resume exactly where it stopped, keeping the system's behavior consistent. The pause function is not just for user control but also helps in analyzing system behavior.

The time simulation provides a central timing service for the entire system. This centralized approach prevents timing errors that could occur if each part kept its own time. The simple interface hides the complexity of maintaining consistent timing across all components.

.. warning::
   Avoid implementing custom timing mechanisms in individual components. Always use the central time simulation service to maintain system consistency.

The system makes it possible to study long-term behavior efficiently. By speeding up time while keeping all events in the correct sequence, the simulation can show how the system performs over days, weeks, or years. This capability is essential for understanding seasonal changes in solar generation and their effects on the system.

The system maintains consistent timing while allowing different parts to update at different rates. Some components need frequent updates for accuracy, while others can work with less frequent updates. The time simulation ensures all parts stay synchronized regardless of their update frequency.

The time simulation coordinates data flow between components. As different parts operate at different speeds, it ensures data exchanges happen at the right times, preventing timing errors. This coordination is essential for keeping the simulation accurate while running efficiently.

.. graphviz::
   :align: center
   :caption: Data Flow Coordination

   digraph data_flow {
      rankdir=LR;
      node [shape=box, style="rounded,filled", fillcolor="#f0f0f0", fontname="Helvetica"];
      edge [fontname="Helvetica", fontsize=8];
      
      "Component 1" -> "Time Sync" [label="Data", style="dashed"];
      "Component 2" -> "Time Sync" [label="Data", style="dashed"];
      "Component 3" -> "Time Sync" [label="Data", style="dashed"];
      "Time Sync" -> "Coordinated Output";
   }

The system can study behavior across different time scales, from daily cycles to seasonal changes. This multi-scale capability helps understand how different timing patterns affect overall performance. The time simulation makes this analysis possible without waiting for real time to pass.

When paused, the system must handle more than just stopping time. It must preserve all component states and relationships, ensuring everything can resume exactly as it was. This state preservation is crucial for maintaining simulation accuracy across pause and resume cycles.

The time simulation provides the timing foundation for the entire system. It enables all parts to work together while maintaining correct timing. This foundation is essential for accurate simulation and meaningful analysis of long-term system behavior. The simple interface belies its importance in keeping the system running smoothly.
