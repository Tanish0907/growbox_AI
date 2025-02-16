void setup() {
  Serial.begin(115200);  // Open serial communication
}

void loop() {
  // Check if data is available
  if (Serial.available()) {
    // Read and print incoming data
    String receivedData = Serial.readStringUntil('\n');
    Serial.println("Received from Arduino Nano: " + receivedData);
  }
}
