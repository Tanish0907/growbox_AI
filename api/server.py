from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sensors import Sensors
import requests
import json
import base64
from google import genai
from google.genai import types
app = FastAPI()
client=genai.Client(api_key="your api key")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
sense=Sensors()
@app.get("/sensors")
def get_sensor_data():
    return sense.read_sensors()
@app.get("/capture")
def capture_image():
    image_path = sense.capture_image()
    return {"image_path": image_path}
@app.get("/ai")
def query_ollama(model: str = "gpt-oss:20b"):
    """Send sensor data + image to Ollama model for analysis"""

    # API endpoint
    url = "http://100.91.41.61:11434/api/generate"
    headers = {"Content-Type": "application/json"}

    # Get sensor data safely
    sensor_data = sense.read_sensors()

    # Capture image and convert to base64
    image_path = sense.capture_image()
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Build the structured prompt
    prompt =f"""
You are an expert botanist and plant care advisor. 
You have access to the following sensor readings:
- Temperature and humidity from a DHT11 sensor
- Soil moisture from a resistive soil moisture sensor

Analyze the image of the plant and provide the following JSON object:

{{
  "plant_name": "scientific or common name of the plant",
  "temperature": "ideal temperature in °C",
  "humidity": "ideal humidity in %",
  "moisture": "ideal soil moisture in "
}}

Do NOT include any explanation or text outside the JSON. 
Ensure the JSON is properly formatted and parseable. 
Return numeric values only for ideal conditions (no JSON objects inside JSON).
the current plant conditions are "{json.dumps(sensor_data)}"
"""

    # Create request payload
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [image_b64],
        "stream": True
    }

    # Send request to Ollama
    response = requests.post(url, headers=headers, json=payload, stream=True)

    # Collect streaming output
    result = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            if "response" in data:
                result += data["response"]
            if data.get("done", False):
                break
    with open("last_response.json", "w") as f:
        json.dump(result.strip(), f)
    return result.strip()
@app.get("/ai/gemini")
def query_gemini(model: str = "gemini-2.5-flash"):
    """Send sensor data + image to Gemini model for analysis"""

    # Get sensor data safely
    sensor_data = sense.read_sensors()

    # Capture image and load bytes
    image_path = sense.capture_image()
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # Structured prompt
    prompt =f"""
You are an expert botanist and plant care advisor. 
You have access to the following sensor readings:
- Temperature and humidity from a DHT11 sensor
- Soil moisture from a resistive soil moisture sensor

Analyze the image of the plant and provide the following JSON object:

{{
  "plant_name": "scientific or common name of the plant",
  "temperature": "ideal temperature in °C",
  "humidity": "ideal humidity in %",
  "moisture": "ideal soil moisture in "
}}

Do NOT include any explanation or text outside the JSON. 
Ensure the JSON is properly formatted and parseable. 
Return numeric values only for ideal conditions (no JSON objects inside JSON).
the current plant conditions are "{json.dumps(sensor_data)}"
"""


    # Request to Gemini API
    response = client.models.generate_content(
        model=model,
        contents=[
            prompt,
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
        ],
        config=types.GenerateContentConfig(
            # Disable "thinking" for faster + cheaper responses
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
    )
    with open("last_response.json", "w") as f:
        json.dump(response.text.strip(), f)
    # Return only the structured output
    return response.text.strip()
@app.get("/act")
def act():
    sense.read_sensors()
    sense.act()
    return {"status": "Actions executed based on last AI response."}
