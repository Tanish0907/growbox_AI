from ollama import Client, ChatResponse
import re
import os
import json
def get_content_after_think(response_text: str) -> str:
    # Find the last </think> tag
    split_content = response_text.rsplit("</think>", 1)
    if len(split_content) == 2:
        # Return everything that comes after the last </think>
        return split_content[1].strip()
    return ""  # Return empty if </think> not found


def generate_response(plant: str, sensordata: dict) -> str:
    if (plant+".json") in os.listdir("./plants"):
        with open(f"./plants/{plant}.json", "r") as f:
            plant_data = json.load(f)
            return plant_data
    else:
        system_prompt = (
            "You are a helpful bot that assists with plant care by analyzing sensor data and recommending optimal conditions. "
            "You receive the plant name and a dictionary of sensor readings. Based on this input, provide target values in JSON format. "
            "Strictly adhere to the following JSON structure: {moisture: value, humidity: value, temperature: value}. "
            "Definitions:\n"
            "- 'moisture' refers to **soil moisture level** measured by a resistive soil moisture sensor value is bw 1023 and 0  .\n"
            "- 'humidity' is the **environmental humidity** in percentage, measured by the **DHT11 sensor**.\n"
            "- 'temperature' is the **environmental temperature** in Celsius, also measured by the **DHT11 sensor**.\n"
            "Always return the response strictly in the specified JSON format and include no additional explanation."
        )   

        try:
            prompt = f"{system_prompt}, Input: {plant}: {sensordata}"

            client = Client(host='http://100.76.223.120:11434')
            response: ChatResponse = client.chat(
                model='deepseek-r1:14b',
                messages=[
                    {'role': 'user', 'content': prompt}
                ]
            )
            with open(f"./plants/{plant}.json", "x") as f:
                json.dump(get_content_after_think(response.message.content).replace("'", '').replace("json", ""), f, indent=2)
            return get_content_after_think(response.message.content).replace("'", '').replace("json", "")
        except Exception as e:
            return str(e)
