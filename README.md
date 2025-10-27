# 🌿 Smart Plant Monitoring and Control System

A complete **AI-powered smart greenhouse** built using **Raspberry Pi**, **Arduino**, and **FastAPI**, with support for **Gemini** and **Ollama** AI models.
This system monitors **temperature**, **humidity**, and **soil moisture**, captures live plant images, and uses AI to recommend ideal conditions and control devices like pumps, fans, lights, and humidifiers automatically.

---

## 🧠 System Overview

This project combines:

* **Arduino Nano/Uno** → reads sensors and sends data via Serial.
* **Raspberry Pi** → runs Python backend, logs data, captures images, queries AI, and controls relays for automation.
* **AI Models (Gemini/Ollama)** → analyze plant images and sensor data to determine ideal conditions.

---

## 🧩 System Architecture

```
                ┌──────────────────────┐
                │      Sensors (DHT11, │
                │ Soil Moisture Sensor)│
                └──────────┬───────────┘
                           │
                     [Serial /dev/serial0]
                           │
                    ┌──────▼──────┐
                    │  Arduino    │
                    │  nano_multi │
                    └──────┬──────┘
                           │
                     USB / Serial
                           │
                ┌──────────▼──────────┐
                │ Raspberry Pi        │
                │ sensors.py          │
                │ server.py (FastAPI) │
                └──────────┬──────────┘
                           │
                     Camera + AI
                           │
                 ┌─────────▼─────────┐
                 │ Gemini / Ollama AI│
                 └───────────────────┘
```

---

## ⚙️ Hardware Components

| Component                    | Description                                 |
| ---------------------------- | ------------------------------------------- |
| **Arduino Nano / Uno**       | Reads sensor values and sends via Serial    |
| **DHT11 Sensor**             | Measures temperature and humidity           |
| **Soil Moisture Sensor**     | Measures soil wetness                       |
| **Raspberry Pi**             | Main controller (AI + automation)           |
| **Relay Module (5-Channel)** | Controls external devices                   |
| **Camera (Picamera2)**       | Captures plant images for AI analysis       |
| **Actuators**                | Water pump, fan, light, humidifier, exhaust |

---

## 🔌 Pin Configuration

### Raspberry Pi → Relay Mapping

| Relay | Function    | GPIO Pin |
| ----- | ----------- | -------- |
| 1     | Water Pump  | 23       |
| 2     | Grow Light  | 24       |
| 3     | Fan         | 25       |
| 4     | Humidifier  | 26       |
| 5     | Exhaust Fan | 27       |

### Arduino Nano Sensor Pins

| Sensor        | Signal Pin | Description                            |
| ------------- | ---------- | -------------------------------------- |
| DHT11         | D2         | Temperature & Humidity                 |
| Soil Moisture | A0         | Analog moisture sensor                 |
| TX/RX         | D0/D1      | Serial communication with Raspberry Pi |

---

## 🔧 Software Components

| File                 | Description                                                            |
| -------------------- | ---------------------------------------------------------------------- |
| `nano_multi.ino`     | Arduino firmware — reads sensors, prints data to serial                |
| `DHT.h`              | DHT11 library for Arduino                                              |
| `logs.py`            | Reads Arduino serial data, parses and logs it to JSON                  |
| `sensors.py`         | Controls GPIO relays, captures images, and executes AI-based actions   |
| `server.py`          | FastAPI backend providing API endpoints for monitoring and AI analysis |
| `logs.json`          | Stores historical sensor readings                                      |
| `last_response.json` | Stores AI-generated ideal plant conditions                             |
| `req.txt`            | Python dependencies list                                               |

---

## 🧠 Arduino Firmware (`nano_multi.ino`)

The Arduino reads data from the **DHT11** and **Soil Moisture Sensor** and sends it to the Raspberry Pi in this format:

```
Arduino: Moisture: 532 | Humidity: 64.0 % | Temperature: 30.0 *C
```

These values are continuously logged and used for AI analysis and decision-making.

**Sample Output:**

```text
Arduino: Moisture: 450 | Humidity: 63.0 % | Temperature: 29.0 *C
```

---

## 💻 Raspberry Pi Software Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/smart-plant-ai.git
cd smart-plant-ai
```

### 2. Install Dependencies

```bash
pip install -r req.txt
```

### 3. Connect Hardware

* Connect Arduino via `/dev/serial0`
* Wire relays and sensors as shown above
* Enable camera:

  ```bash
  sudo raspi-config
  ```

  → Interface Options → Enable Camera

### 4. Run the FastAPI Server

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

---

## 🌐 API Endpoints

| Endpoint     | Method | Description                                           |
| ------------ | ------ | ----------------------------------------------------- |
| `/sensors`   | GET    | Reads current sensor values                           |
| `/capture`   | GET    | Captures a new image from the Pi Camera               |
| `/ai`        | GET    | Sends data to **Ollama** AI model for analysis        |
| `/ai/gemini` | GET    | Sends data to **Google Gemini** model for analysis    |
| `/act`       | GET    | Executes actions (pump, fan, etc.) based on AI output |

---

## 🧠 AI Integration

### Ollama (Local)

* Runs locally on another machine or network.
* Modify `server.py` → `url = "http://<your_ollama_ip>:11434/api/generate"`

### Gemini (Cloud)

* Requires a valid **Google API key**.
* Add it in:

  ```python
  client = genai.Client(api_key="YOUR_API_KEY")
  ```

### Example AI Output

```json
{
  "plant_name": "Zephyranthes sp. (Rain Lily)",
  "temperature": 24,
  "humidity": 60,
  "moisture": 500
}
```

This JSON is saved in `last_response.json` and used by `sensors.py` to control devices.

---

## 🤖 Automated Actions

The Raspberry Pi reads `last_response.json` and compares AI-recommended values with real-time sensor data:

| Condition           | Action                    |
| ------------------- | ------------------------- |
| Moisture < Ideal    | Activates water pump      |
| Temperature < Ideal | Turns on heater/light     |
| Humidity < Ideal    | Turns on humidifier & fan |
| Else                | Keeps system idle         |

All actuators are controlled via GPIO relays.

---

## 🪵 Data Logging

* **`logs.json`** → Continuous sensor data log
* **`last_response.json`** → AI recommendation record

You can easily visualize logs using any plotting tool or dashboard.

---

## 🧰 Troubleshooting

| Issue               | Possible Cause            | Solution                               |
| ------------------- | ------------------------- | -------------------------------------- |
| Serial not reading  | Wrong port                | Check `/dev/serial0` or `ls /dev/tty*` |
| Camera not working  | Disabled in config        | Enable via `sudo raspi-config`         |
| Relays not toggling | Wrong GPIO mode           | Ensure `GPIO.setmode(GPIO.BCM)`        |
| AI not responding   | Missing API key / bad URL | Check Gemini key or Ollama host IP     |

---

## 🌱 Future Enhancements

* Web dashboard for real-time visualization
* MQTT or WebSocket support for IoT integration
* Cloud data storage and analytics
* AI-based disease detection using captured images
