// Example testing sketch for DHT and Soil Moisture sensor data transmission

#include "DHT.h"
#include <SoftwareSerial.h>

#define DHTPIN 2          // Pin for DHT sensor
#define MoisturePin A7    // Pin for Moisture sensor
#define DHTTYPE DHT11     // DHT11 Sensor

SoftwareSerial espSerial(8, 9);  // RX = 8, TX = 9 (Ensure these are correct pins)

// Initialize DHT sensor
DHT dht(DHTPIN, DHTTYPE, 6);

void setup() {
  Serial.begin(115200);      // Debugging on Arduino Serial
  espSerial.begin(115200);   // Communication with NodeMCU
  Serial.println("DHTxx and Moisture sensor test!");
  dht.begin();               // Initialize the DHT sensor
}

void loop() {
  delay(2000);   // Wait for sensor data stabilization

  // Read data from sensors
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();    // Celsius reading
  int moistureLevel = analogRead(MoisturePin);  // Read moisture value

  // Check if sensor readings are valid
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Display data on Serial monitor
  Serial.print("Moisture: ");
  Serial.print(moistureLevel);
  Serial.print(" | Humidity: ");
  Serial.print(humidity);
  Serial.print(" % | Temperature: ");
  Serial.print(temperature);
  Serial.println(" *C");

  // Create data string to send
  String data = String("Moisture: ") + moistureLevel + 
                ", Humidity: " + humidity + 
                ", Temperature: " + temperature + " *C";

  // Send data to NodeMCU
  espSerial.println(data);
}
