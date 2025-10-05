import time
import serial
import RPi.GPIO as GPIO
import re
import os 
import json
from picamera2 import Picamera2
from logs import create_logs
from PIL import Image
RELAY_PIN1 = 23
RELAY_PIN2 = 24
RELAY_PIN3 = 25
RELAY_PIN4 = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN1, GPIO.OUT)
GPIO.output(RELAY_PIN1, GPIO.LOW)
GPIO.setup(RELAY_PIN2, GPIO.OUT)
GPIO.output(RELAY_PIN2, GPIO.LOW)
GPIO.setup(RELAY_PIN3, GPIO.OUT)
GPIO.output(RELAY_PIN3, GPIO.LOW)
GPIO.setup(RELAY_PIN4, GPIO.OUT)
GPIO.output(RELAY_PIN4, GPIO.LOW)
SERIAL_PORT = '/dev/serial0'
BAUDRATE = 9600
arduino_serial = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
arduino_serial.flush()
class Sensors:
    def __init__(self):
        self.moisture = None
        self.humidity = None
        self.temp = None
        
    def parse_moisture(self,line):
        match = re.search(r'Moisture:\s*(\d+)', line)
        if match:
            return eval(match.group(1))
        return None
    
    def parse_humidity(self ,line):
        match = re.search(r'Humidity:\s*(\d+)', line)
        if match:
            return eval(match.group(1))
        return None
    
    def parse_temp(self,line):
        match = re.search(r'Temperature:\s*(-?\d+)', line, re.IGNORECASE)
        if match:
            return eval(match.group(1))
        return None
    
    def capture_image(self,filename="./images/image.jpeg"):
        # Initialize the camera
        picam2 = Picamera2()

        # Configure a preview or still configuration
        config = picam2.create_still_configuration()
        picam2.configure(config)

        # Start the camera
        picam2.start()

        # Give the camera some time to adjust (exposure, focus, etc.)
        time.sleep(2)

        # Capture and save the image
        picam2.capture_file(filename,format="jpeg")
        print(f"Image saved as {filename}")
        picam2.close()
        img=Image.open(filename)
        img=img.rotate(180,expand=True)
        img.save(filename)
        return filename
    
    def read_sensors(self):
        create_logs()
        with open("./logs.json","r") as f:
            data=json.load(f)
            self.temp=data[-1]["Temp"]
            self.moisture=data[-1]["Moisture"]
            self.humidity=data[-1]["Humidity"]
            return data[-1]
    def act(self):
        with open("./last_response.json", "r") as f:
            data = json.load(f)
            data=data.replace("'","").replace("json","").replace("`","")
            print(data)
            
            if data:
                try:
                    data = json.loads(data)
                    ideal_moisture = data.get("moisture")
                    ideal_temp = data.get("temperature")
                    ideal_humidity = data.get("humidity")
                    print(f"Ideal Moisture: {ideal_moisture}, Ideal Temp: {ideal_temp}, Ideal Humidity: {ideal_humidity}")
                    print(f"temp:{self.temp},hum:{self.humidity},moist:{self.moisture}")
                    if self.moisture is not None and ideal_moisture is not None:
                        if self.moisture > ideal_moisture:
                            print("Soil moisture low, activating water pump.")
                            GPIO.output(RELAY_PIN1, GPIO.HIGH)
                            time.sleep(5)  # Run pump for 1 second
                            GPIO.output(RELAY_PIN1, GPIO.LOW)
                        else:
                            print("Soil moisture adequate, no action taken.")
                            GPIO.output(RELAY_PIN1, GPIO.LOW)
                    if self.temp is not None and ideal_temp is not None:
                        if self.temp < ideal_temp:
                            print("Temperature low, activating heater.")
                            GPIO.output(RELAY_PIN2, GPIO.HIGH)
                            time.sleep(5)  # Run heater for 1 second
                            GPIO.output(RELAY_PIN2, GPIO.LOW)
                        else:
                            print("Temperature adequate, no action taken.")
                            GPIO.output(RELAY_PIN2, GPIO.LOW)
                    if self.humidity is not None and ideal_humidity is not None:
                        if self.humidity < ideal_humidity:
                            print("Humidity low, activating humidifier.")
                            GPIO.output(RELAY_PIN3, GPIO.HIGH)
                            GPIO.output(RELAY_PIN4, GPIO.HIGH)
                            time.sleep(5)  # Run humidifier for 1 second
                            GPIO.output(RELAY_PIN3, GPIO.LOW)
                            GPIO.output(RELAY_PIN4, GPIO.LOW)
                        else:
                            print("Humidity adequate, no action taken.")
                            GPIO.output(RELAY_PIN3, GPIO.LOW)
                            GPIO.output(RELAY_PIN4, GPIO.LOW)
                    GPIO.output(RELAY_PIN1, GPIO.LOW)
                    GPIO.output(RELAY_PIN1, GPIO.LOW)
                    GPIO.output(RELAY_PIN1, GPIO.LOW)
                    GPIO.output(RELAY_PIN1, GPIO.LOW)
                except json.JSONDecodeError:
                    print("Error decoding JSON from last_response.json")
            else:
                print("No data in last_response.json to act upon.")
