# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from datetime import datetime
# import json
# import os
# from ai import generate_response
# app = FastAPI()

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )

# # Path to the log file
# LOG_FILE = "sensor_logs.json"

# class SensorData(BaseModel):
#     moisture: int
#     humidity: float
#     temperature: float
#     device_id: str
# @app.get("/")
# def test():
#     return "gud working api"
# @app.post("/data/")
# async def receive_data(data: SensorData):
#     try:
#         # Add timestamp to the received data
#         log_entry = {
#             **data.dict(),
#             "timestamp": datetime.now().isoformat()
#         }

#         # Ensure the log file exists before appending
#         if not os.path.exists(LOG_FILE):
#             with open(LOG_FILE, "w") as f:
#                 f.write("")

#         # Append data to the log file
#         with open(LOG_FILE, "a") as f:
#             f.write(json.dumps(log_entry) + "\n")
#         # Generate response using the AI model
#         plant = data["device_id"]
#         if plant in # Assuming device_id is the plant name
#         sensordata = {
#             "moisture": data.moisture,
#             "humidity": data.humidity,
#             "temperature": data.temperature
#         }
#         print(f"sensors{sensordata}")
#         response = generate_response(plant, sensordata)
#         print(f"ai:{response}")  # For debugging purposes
#         return {"status": "success"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import os
from ai import generate_response

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_FILE = "sensor_logs.json"

class SensorData(BaseModel):
    moisture: int
    humidity: float
    temperature: float
    device_id: str

@app.get("/")
def test():
    return {"status": "ok", "message": "API is working"}

@app.post("/data/")
async def receive_data(data: SensorData):
    try:
        # Create log entry with timestamp
        log_entry = {
            **data.dict(),
            "timestamp": datetime.now().isoformat()
        }

        # If file doesn't exist, start a new array
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                json.dump([log_entry], f, indent=2)
        else:
            # Load existing logs (or fallback to empty list if corrupted/empty)
            with open(LOG_FILE, "r") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []

            # Append new entry
            logs.append(log_entry)

            # Write back as a JSON array
            with open(LOG_FILE, "w") as f:
                json.dump(logs, f, indent=2)

        # Prepare sensor data for AI response
        sensordata = {
            "moisture": data.moisture,
            "humidity": data.humidity,
            "temperature": data.temperature
        }

        # plant = data.device_id
        plant="cotton"
        print(f"sensors: {sensordata}")

        response = generate_response(plant, sensordata)
        print(f"ai: {response}")

        return {"status": "success", "ai_response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
