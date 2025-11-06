# Detailed Simulation Plan for Solar System (SS) and Houses System (HS) for SSMS

## 1. Solar System (SS) Simulation

We'll implement a hybrid approach, combining software simulation with hardware interaction for added realism.

### 1.1 Software-based Simulation (Primary Method)

Implement this on the Raspberry Pi (SSMS server):

1. Create a Python script to generate sample data for a regular day:
   - Solar irradiance patterns
   - Battery charge/discharge cycles
   - Inverter efficiency

2. Use libraries like NumPy and Pandas for data generation and manipulation.

3. Implement time-based variations:
   - Day/night cycles
   - Seasonal changes
   - Random cloud cover events

4. Sample Python code structure:

```python
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class SolarSystemSimulator:
    def __init__(self):
        self.panel_capacity = 5000  # 5kW system
        self.battery_capacity = 13500  # 13.5kWh battery

    def generate_daily_data(self, date):
        hours = 24
        time_index = pd.date_range(date, periods=hours, freq='H')
        
        # Generate solar irradiance data
        irradiance = np.sin(np.linspace(0, np.pi, hours)) * 1000
        irradiance[0:6] = 0  # Night time
        irradiance[18:] = 0  # Night time
        
        # Add some randomness for cloud cover
        cloud_cover = np.random.rand(hours) * 0.3
        irradiance = irradiance * (1 - cloud_cover)
        
        # Calculate power generation
        power_generation = irradiance * self.panel_capacity / 1000
        
        # Simulate battery state
        battery_state = np.zeros(hours)
        battery_state[0] = self.battery_capacity * 0.5  # Start at 50%
        
        for i in range(1, hours):
            battery_state[i] = battery_state[i-1] + power_generation[i] - 250  # Assume 250W constant load
            battery_state[i] = np.clip(battery_state[i], 0, self.battery_capacity)
        
        return pd.DataFrame({
            'timestamp': time_index,
            'irradiance': irradiance,
            'power_generation': power_generation,
            'battery_state': battery_state
        })

    def get_current_state(self):
        # Return the current state based on time of day
        pass

simulator = SolarSystemSimulator()
daily_data = simulator.generate_daily_data(datetime.now())
print(daily_data)
```

5. Integrate this simulator with the SSMS Power Management Module.

### 1.2 Hardware-based Enhancement (Optional)

Use an Arduino to add real-world variability and hardware interaction:

1. Set up an Arduino Uno with:
   - Photoresistor to simulate varying sunlight intensity
   - Potentiometer to manually adjust "weather conditions"
   - LED to represent solar panel activity

2. Arduino code structure:

```cpp
const int PHOTO_RESISTOR_PIN = A0;
const int POTENTIOMETER_PIN = A1;
const int SOLAR_LED_PIN = 9;

void setup() {
  Serial.begin(9600);
  pinMode(SOLAR_LED_PIN, OUTPUT);
}

void loop() {
  int lightLevel = analogRead(PHOTO_RESISTOR_PIN);
  int weatherCondition = analogRead(POTENTIOMETER_PIN);
  
  // Combine readings to simulate solar intensity
  int solarIntensity = map(lightLevel, 0, 1023, 0, 255) * map(weatherCondition, 0, 1023, 0, 100) / 100;
  
  analogWrite(SOLAR_LED_PIN, solarIntensity);
  
  // Send data to Raspberry Pi
  Serial.print(lightLevel);
  Serial.print(",");
  Serial.println(weatherCondition);
  
  delay(1000);
}
```

3. Connect the Arduino to the Raspberry Pi via USB.

4. Modify the Python simulation script to read data from the Arduino and adjust the simulated solar output accordingly.

## 2. Houses System (HS) Simulation

We'll use a combination of hardware and software to simulate multiple houses.

### 2.1 Hardware Setup

For each simulated house:

1. Use a breadboard with:
   - 3 push buttons (to simulate high, medium, low power consumption)
   - 3 LEDs (green, yellow, red to indicate power consumption level)
   - 1 switch (to simulate grid electricity availability)
   - 1 NodeMCU ESP8266 (to control the setup and communicate with SSMS)

2. Wiring:
   - Connect push buttons and switch to digital input pins on NodeMCU
   - Connect LEDs to digital output pins on NodeMCU (use appropriate resistors)

### 2.2 Software Implementation

1. NodeMCU (ESP8266) code structure:

```cpp
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "YourWiFiSSID";
const char* password = "YourWiFiPassword";
const char* serverAddress = "http://192.168.1.100:5000/update_house_data";  // Replace with your Raspberry Pi's IP

const int BUTTON_LOW = D1;
const int BUTTON_MED = D2;
const int BUTTON_HIGH = D3;
const int SWITCH_GRID = D4;
const int LED_GREEN = D5;
const int LED_YELLOW = D6;
const int LED_RED = D7;

int currentConsumption = 0;
bool gridAvailable = true;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  pinMode(BUTTON_LOW, INPUT_PULLUP);
  pinMode(BUTTON_MED, INPUT_PULLUP);
  pinMode(BUTTON_HIGH, INPUT_PULLUP);
  pinMode(SWITCH_GRID, INPUT_PULLUP);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);
}

void loop() {
  updateConsumption();
  updateGridStatus();
  updateLEDs();
  sendDataToServer();
  delay(1000);
}

void updateConsumption() {
  if (digitalRead(BUTTON_LOW) == LOW) currentConsumption = 100;
  else if (digitalRead(BUTTON_MED) == LOW) currentConsumption = 500;
  else if (digitalRead(BUTTON_HIGH) == LOW) currentConsumption = 1000;
  else currentConsumption = 0;
}

void updateGridStatus() {
  gridAvailable = digitalRead(SWITCH_GRID) == HIGH;
}

void updateLEDs() {
  digitalWrite(LED_GREEN, currentConsumption > 0 ? HIGH : LOW);
  digitalWrite(LED_YELLOW, currentConsumption >= 500 ? HIGH : LOW);
  digitalWrite(LED_RED, currentConsumption >= 1000 ? HIGH : LOW);
}

void sendDataToServer() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverAddress);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    
    String httpRequestData = "house_id=1&consumption=" + String(currentConsumption) + "&grid_available=" + String(gridAvailable);
    int httpResponseCode = http.POST(httpRequestData);
    
    if (httpResponseCode > 0) {
      Serial.println("Data sent successfully");
    } else {
      Serial.println("Error sending data");
    }
    http.end();
  }
}
```

2. Raspberry Pi (SSMS) server code to receive house data:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/update_house_data', methods=['POST'])
def update_house_data():
    house_id = request.form.get('house_id')
    consumption = request.form.get('consumption')
    grid_available = request.form.get('grid_available')
    
    # Process and store the received data
    # Update the SSMS power management logic
    
    return "Data received", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 2.3 Integration with SSMS

1. Modify the Power Management Module to consider the real-time data from simulated houses.
2. Implement logic to handle grid availability changes and adjust power distribution accordingly.
3. Update the Mobile API Module to include house-specific data for the User Mobile App.

This simulation setup provides a realistic and interactive way to test and demonstrate the SSMS functionality. The software-based Solar System simulation offers flexibility and control over various scenarios, while the hardware-based Houses System simulation allows for tangible interaction and real-time data generation.
