import uvicorn
from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from collections import deque

app = FastAPI(title="Game Security Analysis System")

# --- [1] Data Models ---
class GameEvent(BaseModel):
    type: str  # e.g., "MOVE", "FIRE"
    speed: Optional[float] = None
    fire_rate: Optional[float] = None

class LogPayload(BaseModel):
    player_id: str
    session_id: str
    events: List[GameEvent]

# --- [2] Real-time Dashboard Manager (WebSocket) ---
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

# --- [3] Security Detection Engine (Integrated) ---

# Threshold configuration
THRESHOLD = {
    "MOVE": 10.0,        # Max allowed average speed
    "FIRE": 12.0,        # Max allowed average fire rate
    "WINDOW_SIZE": 10,   # Number of recent events to track
    "MIN_SAMPLES": 5     # Minimum events required before triggering an alert
}

# In-memory store for player history
# For production/scaling, replace this with Redis.
player_history = {}

async def analyze_security_risk(payload: LogPayload):
    pid = payload.player_id
    detected_hacks = []
    
    # Initialize history for new players
    if pid not in player_history:
        player_history[pid] = {
            "MOVE": deque(maxlen=THRESHOLD["WINDOW_SIZE"]),
            "FIRE": deque(maxlen=THRESHOLD["WINDOW_SIZE"])
        }

    for event in payload.events:
        # 1. Speed Hack Detection (Rolling Average)
        if event.type == "MOVE" and event.speed is not None:
            player_history[pid]["MOVE"].append(event.speed)
            
            # Analyze only if we have enough data points
            if len(player_history[pid]["MOVE"]) >= THRESHOLD["MIN_SAMPLES"]:
                avg_speed = sum(player_history[pid]["MOVE"]) / len(player_history[pid]["MOVE"])
                if avg_speed > THRESHOLD["MOVE"]:
                    detected_hacks.append({
                        "type": "Speed Hack (Avg)", 
                        "value": round(avg_speed, 2),
                        "instant_value": event.speed
                    })

        # 2. Fire Rate Hack Detection (Rolling Average)
        if event.type == "FIRE" and event.fire_rate is not None:
            player_history[pid]["FIRE"].append(event.fire_rate)
            
            if len(player_history[pid]["FIRE"]) >= THRESHOLD["MIN_SAMPLES"]:
                avg_fire = sum(player_history[pid]["FIRE"]) / len(player_history[pid]["FIRE"])
                if avg_fire > THRESHOLD["FIRE"]:
                    detected_hacks.append({
                        "type": "Fire Rate Hack (Avg)", 
                        "value": round(avg_fire, 2)
                    })

    # Trigger Alert if violations were found
    if detected_hacks:
        alert_data = {
            "player_id": pid,
            "session_id": payload.session_id,
            "violations": detected_hacks,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        print(f"🚨 [ALERT] {alert_data}")
        await manager.send_alert(alert_data)

# --- [4] API Endpoints ---
@app.post("/api/v1/logs")
async def collect_logs(payload: LogPayload, background_tasks: BackgroundTasks):
    # Offload analysis to background to keep response time fast
    background_tasks.add_task(analyze_security_risk, payload)
    return {"status": "ok", "processed_events": len(payload.events)}

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
