#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "HOME_4G";
const char* password = "taruntanish@8001";

String device_id = "node_1";

void setup() {
  Serial.begin(115200); // Serial to read from Arduino Nano
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
    receivedData.trim();  // Remove newline and whitespace

    Serial.println("Received: " + receivedData);

    // Parse format: Moisture: 1023 | Humidity: 79.00 % | Temperature: 30.80 *C
    int moistureIndex = receivedData.indexOf("Moisture:");
    int humidityIndex = receivedData.indexOf("Humidity:");
    int tempIndex     = receivedData.indexOf("Temperature:");

    if (moistureIndex != -1 && humidityIndex != -1 && tempIndex != -1) {
      // Extract and trim individual values
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
      // Convert strings to numbers
      float moisture = moistureStr.toFloat();
      float humidity = humidityStr.toFloat();
      // float temperature = tempStr.toFloat();

      // Build JSON
      String jsonData = "{";
      jsonData += "\"moisture\":" + String(moisture, 0) + ",";
      jsonData += "\"humidity\":" + String(humidity, 2) + ",";
      jsonData += "\"temperature\":" + String(temperature,2) + ",";
      jsonData += "\"device_id\":\"" + device_id + "\"";
      jsonData += "}";

      Serial.println("Prepared JSON: " + jsonData);

      sendData(jsonData);
    } else {
      Serial.println("Invalid data format.");
    }
  }

  delay(500);  // optional pacing
}

void sendData(String jsonData) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected. Skipping POST.");
    return;
  }

  WiFiClient client;
  HTTPClient http;

  String serverUrl = "http://192.168.29.251:8000/data/";  // Replace with your FastAPI IP

  Serial.println("Sending POST to: " + serverUrl);

  http.begin(client, serverUrl);
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST(jsonData);
  if (httpCode > 0) {
    Serial.printf("HTTP POST code: %d\n", httpCode);
    Serial.println(http.getString());
  } else {
    Serial.printf("POST failed: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}
