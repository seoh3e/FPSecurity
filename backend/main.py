import uvicorn
import json
import numpy as np
import redis
from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Pro Game Security Analysis (Redis + Stats)")

# --- [1] Infrastructure Setup ---
# Ensure redis-server is running (Docker or Local)
try:
    r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
except redis.ConnectionError:
    print("❌ Cannot connect to Redis. Running in local memory mode or please start Redis.")

# --- [2] Data Models ---
class GameEvent(BaseModel):
    type: str  # e.g., "MOVE", "FIRE"
    speed: Optional[float] = None
    fire_rate: Optional[float] = None

class LogPayload(BaseModel):
    player_id: str
    session_id: str
    events: List[GameEvent]

# --- [3] Real-time Dashboard Manager ---
class DashboardManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_alert(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = DashboardManager()

# --- [4] Security Detection Engine (Redis + Statistical Analysis) ---
CONFIG = {
    "MOVE_THRESHOLD": 12.0,      # Avg speed limit
    "STDEV_MAX": 2.5,           # Max deviation (Low value implies 'Consistent Hack')
    "WINDOW_SIZE": 15,          # Number of recent events to analyze
    "MIN_SAMPLES": 8,           # Minimum data points required
    "TTL": 1800                 # User data retention (30 mins)
}

async def analyze_security_risk(payload: LogPayload):
    pid = payload.player_id
    detected_hacks = []

    for event in payload.events:
        # --- Speed Hack Analysis ---
        if event.type == "MOVE" and event.speed is not None:
            key = f"player:{pid}:move_history"
            
            # 1. Store in Redis & Maintain Sliding Window
            r.lpush(key, event.speed)
            r.ltrim(key, 0, CONFIG["WINDOW_SIZE"] - 1)
            r.expire(key, CONFIG["TTL"])

            # 2. Statistical Analysis
            raw_history = r.lrange(key, 0, -1)
            if len(raw_history) >= CONFIG["MIN_SAMPLES"]:
                history = [float(v) for v in raw_history]
                
                avg_speed = np.mean(history)
                std_dev = np.std(history)

                # Detection Algorithm:
                # - If Avg Speed > Threshold AND Std Dev is Low (Consistent speed boost, not lag)
                if avg_speed > CONFIG["MOVE_THRESHOLD"]:
                    if std_dev < CONFIG["STDEV_MAX"]:
                        detected_hacks.append({
                            "type": "Consistent Speed Hack",
                            "avg": round(float(avg_speed), 2),
                            "std_dev": round(float(std_dev), 2),
                            "status": "High Probability"
                        })
                    else:
                        # High average but high variance -> Likely Network Jitter
                        print(f"⚠️ [SUSPICIOUS] Player {pid}: High speed but unstable (Jitter).")

        # --- Rapid Fire Analysis ---
        if event.type == "FIRE" and event.fire_rate is not None:
            key = f"player:{pid}:fire_history"
            r.lpush(key, event.fire_rate)
            r.ltrim(key, 0, CONFIG["WINDOW_SIZE"] - 1)
            
            raw_fire = r.lrange(key, 0, -1)
            if len(raw_fire) >= CONFIG["MIN_SAMPLES"]:
                avg_fire = np.mean([float(v) for v in raw_fire])
                if avg_fire > 15.0:  # Threshold: e.g., 15+ rounds per second
                    detected_hacks.append({
                        "type": "Rapid Fire Hack",
                        "avg": round(float(avg_fire), 2)
                    })

    # Alert manager if violations are found
    if detected_hacks:
        alert_data = {
            "player_id": pid,
            "session_id": payload.session_id,
            "violations": detected_hacks,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        await manager.send_alert(alert_data)

# --- [5] API Endpoints ---
@app.post("/api/v1/logs")
async def collect_logs(payload: LogPayload, background_tasks: BackgroundTasks):
    # Offload analysis to background tasks for low latency
    background_tasks.add_task(analyze_security_risk, payload)
    return {"status": "ok", "received": len(payload.events)}

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
