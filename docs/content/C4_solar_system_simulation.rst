Chapter 04: Solar System Simulation
===================================
The main work of calculating the solar irradiance is done by the Python library Pvlib. However, it requires the following parameters to calculate it: DNI, DHI, GHI, Zenith Angle, and Time Zone. 

DNI is the Direct Normal Irradiance, which is the irradiance of the solar beams on a surface perpendicular to the sun beams. 
DHI is the Diffused Horizontal Irradiance, which is the irradiance that reaches the surface after it gets diffused from the atmosphere, clouds, the ground, other surfaces, etc. 
GHI is the Global Horizontal Irradiance, which is calculated as DHI + DNI * Coz(Z), where Z is the Zenith Angle. 
The Zenith Angle is the angle between the zenith and the sun beams. 

The data is taken from NSRDB, the National Solar Radiation Database. 

The mechanism of Solar System Simulation is this: it requests the timestamp from the Time Simulation, then it seeks to the timestamp in the NSRDB dataset that is closest to that timestamp, and it takes the related DNI, DHI, GHI, and Zenith Angle. Then using Pvlib, the solar irradiance is calculated, then the total generated power is calculated based on the settings; the amount of solar panels, their angling, the panels' efficiency, etc. 

.. note:: Optionally, Solar System Simulation logs the total power generated over time into a csv file. The behavior is set in the settings. 
