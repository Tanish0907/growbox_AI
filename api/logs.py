import serial
import time
import json
import os
import re
SERIAL_PORT = '/dev/serial0'
BAUDRATE = 9600

arduino_serial = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)  # Allow serial to initialize
arduino_serial.flush()
def parse_moisture(line):
    """
    Extracts integer moisture value from a line like:
    "Arduino: Moisture: 1018 | Humidity: nan % | Temperature: nan *C"
    Returns None if parsing fails.
    """
    match = re.search(r'Moisture:\s*(\d+)', line)
    if match:
        return int(match.group(1))
    return None
def parse_humidity(line):
    """
    Extracts integer moisture value from a line like:
    "Arduino: Moisture: 1018 | Humidity: nan % | Temperature: nan *C"
    Returns None if parsing fails.
    """
    match = re.search(r'Humidity:\s*(\d+)', line)
    if match:
        return float(match.group(1))
    return None
import re

def parse_temp(line):
    """
    Extracts integer temperature value from a line like:
    "Arduino: Moisture: 1018 | Humidity: nan % | Temperature: 25 *C"
    Returns None if parsing fails.
    """
    match = re.search(r'Temperature:\s*(-?\d+)', line, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None
def create_logs():
    count=0
    try:
        try:
            while arduino_serial.in_waiting>0:
                line = arduino_serial.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"[{count}]:Arduino: {line}")
                count+=1
                moisture = parse_moisture(line)
                humidity=parse_humidity(line)
                temp=parse_temp(line)
                data={"Moisture": moisture, "Humidity": humidity, "Temp": temp}
                        # Ensure logs.json exists and is a valid JSON array
                if not os.path.exists("logs.json"):
                    with open("logs.json", "w") as f:
                        json.dump([], f)
                with open("logs.json", "r+") as logs:
                    try:
                        logs_data = json.load(logs)
                    except json.JSONDecodeError:
                        logs_data = []  # if file is empty or corrupted, reset to list
                    logs_data.append(data)
                    logs.seek(0)   # move cursor back to start of file
                    json.dump(logs_data, logs, indent=4)
                    logs.truncate()  # remove leftover old content
        except serial.SerialException as e:
            print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nStopped by user")
