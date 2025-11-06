# One-Step Outline #1

## Current Progess
Implemented the basic framework of the solar simulation and the housing simulation, albeit with no linking between them and no semblance of a grid line simulation.

## Outline
### Phase 1:
Understand how grid lines work.

### Phase 2:
Add the Solar-Power-Management Interface and link it with Solar Sim; the interface is the one that manages the battery and manages the logic to switch from solar power to battery power.

### Phase 3:
Outline the basic structure of the mobile app API and commence its development.

### Phase 4:
Separate Housing Sim into three:

- The Housing-Power-Management Interface that takes in as API requests for running new devices from the Housing Sim and returns whether or not they are working and simulate the load and grid and sends the total data to the Power Management Module
- The Power Management Module that takes in that data and data from the solar sim and the interface
- The Housing Sim that sends requests to the  interface and receives responses as to whether the device ran successfully and whether the house's breaker went off

### Phase 5:
Implement basic logic for the Power Management Module as to link the interfaces and have a working prototype to present, as follows:
1. Implement basic logic as a State Machine.
2. Expand the states available and make the State Machine more intricate and assign rewards / score for each state along commands possible for an AI to train with, and provide the data relevant for the judgment to be made about management.
3. Implement reinforcement learning to have the power management be done with AI.
