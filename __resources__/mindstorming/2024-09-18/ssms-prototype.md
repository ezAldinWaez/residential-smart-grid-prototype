# Solar System Management System (SSMS) - Prototype

## 1. System Architecture

The Solar System with SSMS consists of four main components:

1. Solar System (SS)
2. Solar System Management System (SSMS)
3. Houses
4. Users Mobile App

### 1.1 Solar System (SS)

- **Solar Panels**: Convert sunlight into DC electricity.
- **Batteries**: Store excess energy for use during low-sunlight periods.
- **Inverter**: Converts DC to AC and manages power flow between panels, batteries, and the grid.

### 1.2 Solar System Management System (SSMS)

- **Power Management Module (PMM)**: Core component for power distribution and management.
- **Mobile API Module (MAM)**: Interfaces between the PMM and user mobile apps.

### 1.3 Houses

- Multiple residential units connected to the SSMS.
- Each house has a smart meter to measure power consumption.

### 1.4 Users Mobile App

- Individual apps for each household to monitor and manage power usage.

![Systems Architecture](2_ss_with_ssms.png "Systems Architecture")

## 2. Detailed Component Descriptions

### 2.1 Power Management Module (PMM)

The PMM is the brain of the SSMS, responsible for:

1. **Real-time monitoring**: Tracks power generation, storage, and consumption.
2. **Smart power distribution**: Allocates power based on usage patterns and predefined rules.
3. **Overuse management**: Allows temporary overuse when excess power is available.
4. **Predictive analytics**: Forecasts power generation and consumption to optimize distribution.
5. **Reporting**: Generates usage reports and system health status.

### 2.2 Mobile API Module (MAM)

The MAM serves as the interface between the PMM and user mobile apps:

1. **Authentication**: Ensures secure user access to the system.
2. **Data transmission**: Sends real-time and historical data to user apps.
3. **Command reception**: Receives and processes user commands (e.g., setting usage limits).
4. **Push notifications**: Sends alerts and important updates to users.

### 2.3 User Mobile App

The mobile app provides users with:

1. **Dashboard**: Real-time overview of power generation, consumption, and savings.
2. **Usage history**: Detailed charts and graphs of historical power usage.
3. **Control panel**: Allows users to set preferences and usage limits.
4. **Notifications**: Alerts for unusual consumption patterns or system issues.
5. **Community features**: Comparison with neighbors, energy-saving tips.

## 3. System Workflow

1. Solar panels generate electricity, which is either used immediately or stored in batteries.
2. The inverter manages power flow and communicates with the PMM.
3. The PMM continuously monitors power generation and consumption.
4. Based on predefined rules and current conditions, the PMM allocates power to each house.
5. If a house exceeds its allocation but others are underusing, the PMM may allow temporary overuse.
6. The MAM receives data from the PMM and transmits it to user mobile apps.
7. Users can view their consumption, set preferences, and receive notifications through their apps.

## 4. Key Features

1. **Autonomous operation**: The system operates without daily administrative intervention.
2. **Flexible power allocation**: Allows for dynamic power distribution based on real-time usage.
3. **User empowerment**: Provides users with tools to monitor and manage their energy consumption.
4. **Scalability**: Can accommodate additional houses or expanded solar systems.
5. **Energy optimization**: Maximizes the use of solar energy and minimizes grid dependence.

## 5. Prototype Components

### 5.1 Power Management Module (PMM) Prototype

```python
class PowerManagementModule:
    def __init__(self):
        self.total_power = 0
        self.house_allocations = {}
        self.house_consumption = {}

    def update_power_generation(self, power):
        self.total_power = power

    def allocate_power(self):
        base_allocation = self.total_power / len(self.house_allocations)
        for house in self.house_allocations:
            self.house_allocations[house] = base_allocation

    def allow_overuse(self, house, amount):
        available_power = sum(self.house_allocations.values()) - sum(self.house_consumption.values())
        if amount <= available_power:
            self.house_allocations[house] += amount
            return True
        return False

    def update_consumption(self, house, amount):
        self.house_consumption[house] = amount
        if amount > self.house_allocations[house]:
            self.allow_overuse(house, amount - self.house_allocations[house])

```

### 5.2 Mobile API Module (MAM) Prototype

```python
import json

class MobileAPIModule:
    def __init__(self, power_management_module):
        self.pmm = power_management_module
        self.users = {}

    def authenticate_user(self, user_id, password):
        # Implement secure authentication
        pass

    def get_user_data(self, user_id):
        if user_id in self.users:
            return json.dumps({
                "allocation": self.pmm.house_allocations.get(user_id, 0),
                "consumption": self.pmm.house_consumption.get(user_id, 0)
            })
        return None

    def set_user_preference(self, user_id, preference):
        # Implement user preference setting
        pass

    def send_notification(self, user_id, message):
        # Implement push notification
        pass
```

### 5.3 User Mobile App Prototype (React Native)

```jsx
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { LineChart } from 'react-native-chart-kit';

const DashboardScreen = () => {
  const [powerData, setPowerData] = useState(null);

  useEffect(() => {
    // Fetch data from API
    fetchPowerData();
  }, []);

  const fetchPowerData = async () => {
    // Implement API call to get power data
    // setPowerData(result);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Energy Dashboard</Text>
      {powerData && (
        <>
          <Text>Current Consumption: {powerData.currentConsumption} kWh</Text>
          <Text>Allocated Power: {powerData.allocation} kWh</Text>
          <LineChart
            data={powerData.history}
            width={300}
            height={200}
            yAxisLabel="kWh"
            chartConfig={{
              backgroundColor: "#e26a00",
              backgroundGradientFrom: "#fb8c00",
              backgroundGradientTo: "#ffa726",
              decimalPlaces: 2,
              color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
              style: {
                borderRadius: 16
              }
            }}
            bezier
            style={{
              marginVertical: 8,
              borderRadius: 16
            }}
          />
        </>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
});

export default DashboardScreen;
```

This prototype provides a foundation for the SSMS. It includes basic implementations of the Power Management Module, Mobile API Module, and a React Native component for the user mobile app. To create a fully functional system, you would need to expand on these components, implement proper error handling, add security measures, and integrate with actual hardware interfaces.
