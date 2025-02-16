from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
import os

app = FastAPI()

# Path to the log file
LOG_FILE = "sensor_logs.json"

class SensorData(BaseModel):
    moisture: int
    humidity: float
    temperature: float
    device_id: str

@app.post("/data/")
async def receive_data(data: SensorData):
    try:
        # Add timestamp to the received data
        log_entry = {
            **data.dict(),
            "timestamp": datetime.now().isoformat()
        }

        # Ensure the log file exists before appending
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                f.write("")

        # Append data to the log file
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

