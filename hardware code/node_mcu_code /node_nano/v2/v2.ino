#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include "./ArduinoJson-v7.4.2.h"

const char* ssid = "HOME_4G";
const char* password = "taruntanish@8001";

String device_id = "node_1";

// Relay connected to D2 (GPIO 2 on ESP32)
#define RELAY_PIN D2   

// Set threshold for soil moisture (adjust as needed)
#define MOISTURE_THRESHOLD 700  

void setup() {
  Serial.begin(115200); 
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);  // Relay OFF initially

  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (Serial.available()) {
    String receivedData = Serial.readStringUntil('\n');
    receivedData.trim();  

    Serial.println("Received: " + receivedData);

    int moistureIndex = receivedData.indexOf("Moisture:");
    int humidityIndex = receivedData.indexOf("Humidity:");
    int tempIndex     = receivedData.indexOf("Temperature:");

    if (moistureIndex != -1 && humidityIndex != -1 && tempIndex != -1) {
      String moistureStr = receivedData.substring(moistureIndex + 9, receivedData.indexOf("|", moistureIndex));
      moistureStr.trim();

      String humidityStr = receivedData.substring(humidityIndex + 9, receivedData.indexOf("%", humidityIndex));
      humidityStr.trim();

      String tempStr = receivedData.substring(tempIndex + 12, receivedData.indexOf("*", tempIndex));
      tempStr.trim();
      tempStr.replace("C", "");
      tempStr.replace("*", "");
      tempStr.replace("°", "");
      tempStr.replace(" ", "");

      float temperature = tempStr.toFloat();
      float moisture = moistureStr.toFloat();
      float humidity = humidityStr.toFloat();

      // Build JSON
      String jsonData = "{";
      jsonData += "\"moisture\":" + String(moisture, 0) + ",";
      jsonData += "\"humidity\":" + String(humidity, 2) + ",";
      jsonData += "\"temperature\":" + String(temperature,2) + ",";
      jsonData += "\"device_id\":\"" + device_id + "\"";
      jsonData += "}";

      Serial.println("Prepared JSON: " + jsonData);

      sendData(jsonData,moisture);
    } else {
      Serial.println("Invalid data format.");
    }
  }

  delay(1000); 
}

// ✅ Small function to handle relay logic
void controlRelay(int moisture,int smoisture) {
  if (moisture > smoisture) {
    digitalWrite(RELAY_PIN, HIGH);  // Relay ON
    Serial.println("Soil is DRY -> Relay ON (Pump ON)");
  } else {
    digitalWrite(RELAY_PIN, LOW);   // Relay OFF
    Serial.println("Soil is WET -> Relay OFF (Pump OFF)");
  }
}

void sendData(String jsonData,int moisture) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected. Skipping POST.");
    return;
  }

  WiFiClient client;
  HTTPClient http;

  String serverUrl = "http://192.168.29.251:8000/data/";  

  Serial.println("Sending POST to: " + serverUrl);

  http.begin(client, serverUrl);
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST(jsonData);

  if (httpCode > 0) {
    Serial.printf("HTTP POST code: %d\n", httpCode);
    String response = http.getString();
    Serial.println("Response payload:");
    Serial.println(response);

    // Parse JSON response
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, response);

    if (!error) {
      int returnedMoisture = doc["ai_response"]["moisture"];
      Serial.printf("Moisture from server: %d\n", returnedMoisture);

      // ✅ Use helper function
      controlRelay(moisture,returnedMoisture);
    } else {
      Serial.println("Failed to parse server response!");
    }

  } else {
    Serial.printf("POST failed: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}
