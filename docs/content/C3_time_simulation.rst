Chapter 03: Time Simulation
===========================
Time Simulation offers one function: to allow for time to pass quicker in the simulation. Due to the amount of time it takes to witness meaningful trends in solar energy and in power management, a time simulation that quickens the passage of time is necessary. 

Time Simulation works by storing the timestamp the simulation started at, and whenever any function requests the current time, it calculates the elapsed time in the simulation by multiplying the real elapsed time by a time factor stored in the settings. It can return the simulated elapsed time or the current timestamp in the simulation. 

Time Simulation is then used across the project to syncronize time. 

.. note:: Time Simulation also provides a way to pause the simulation and resume. It takes into consideration the amount of time it was paused and subtracts that from the total elapsed time to get the unpaused elapsed time. 
