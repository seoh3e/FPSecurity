import uvicorn
import numpy as np
import redis.asyncio as redis
from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json

app = FastAPI(title="FPS Pro-Guard: Real-time Security Analysis")

# --- [1] 비동기 인프라 설정 ---
# Redis 연결 (비동기 모드)
r = redis.from_url("redis://localhost:6379", decode_responses=True)

# --- [2] 데이터 모델 (FPS 특화) ---
class GameEvent(BaseModel):
    type: str  # MOVE, FIRE, HIT, AIM
    # 공통 데이터
    pos: Optional[List[float]] = None  # [x, y, z]
    # 특정 이벤트 데이터
    speed: Optional[float] = None
    weapon_id: Optional[str] = None
    damage: Optional[float] = None
    target_id: Optional[str] = None
    view_angles: Optional[List[float]] = None  # [pitch, yaw]
    timestamp: float

class LogPayload(BaseModel):
    player_id: str
    session_id: str
    events: List[GameEvent]

# --- [3] 실시간 알림 시스템 ---
class DashboardManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_alert(self, alert: dict):
        for connection in self.active_connections:
            await connection.send_json(alert)

manager = DashboardManager()

# --- [4] FPS 보안 엔진 (4대 핵심 로직) ---
class FPSSecurityEngine:
    # 총기 데이터베이스 (서버 측 검증용)
    WEAPON_DB = {
        "AK-47": {"max_dmg": 35.0, "min_interval": 0.1, "max_rpm": 600},
        "AWM": {"max_dmg": 120.0, "min_interval": 1.2, "max_rpm": 50}
    }
    
    CONFIG = {
        "MOVE_THRESHOLD": 15.0,
        "STDEV_MAX": 1.5,       # 속도핵 판별용 (낮을수록 일관된 핵)
        "AIM_ANGLE_JUMP": 45.0, # 프레임간 비정상적인 시야 회전값
        "WINDOW_SIZE": 20,
        "TTL": 1800
    }

    @staticmethod
    async def analyze(payload: LogPayload):
        pid = payload.player_id
        violations = []

        for event in payload.events:
            # 1. 속도핵 (Speed Hack) - 통계적 변동성 분석
            if event.type == "MOVE" and event.speed:
                key = f"player:{pid}:speed"
                await r.lpush(key, event.speed)
                await r.ltrim(key, 0, FPSSecurityEngine.CONFIG["WINDOW_SIZE"])
                
                history = await r.lrange(key, 0, -1)
                if len(history) >= 10:
                    speeds = [float(v) for v in history]
                    avg_speed = np.mean(speeds)
                    std_dev = np.std(speeds)
                    
                    if avg_speed > FPSSecurityEngine.CONFIG["MOVE_THRESHOLD"] and std_dev < FPSSecurityEngine.CONFIG["STDEV_MAX"]:
                        violations.append({"type": "Speed Hack", "val": round(avg_speed, 2), "prob": "High"})

            # 2. 데미지핵 (Damage Hack) - 서버 데이터 대조
            elif event.type == "HIT" and event.weapon_id:
                w_info = FPSSecurityEngine.WEAPON_DB.get(event.weapon_id)
                if w_info and event.damage > w_info["max_dmg"]:
                    violations.append({"type": "Damage Hack", "expected": w_info["max_dmg"], "actual": event.damage})

            # 3. 연사핵 (Fire Rate Hack) - 발사 간격 검증
            elif event.type == "FIRE" and event.weapon_id:
                key = f"player:{pid}:last_fire"
                last_time = await r.get(key)
                if last_time:
                    interval = event.timestamp - float(last_time)
                    w_info = FPSSecurityEngine.WEAPON_DB.get(event.weapon_id)
                    if w_info and interval < w_info["min_interval"] * 0.9: # 10% 오차 허용
                        violations.append({"type": "Fire Rate Hack", "interval": round(interval, 4)})
                await r.setex(key, 60, event.timestamp)

            # 4. 에임핵 (Aim Hack) - 시야각 엔트로피/점프 분석
            elif event.type == "AIM" and event.view_angles:
                key = f"player:{pid}:aim"
                # 이전 각도 가져오기
                prev_angles_raw = await r.get(key)
                if prev_angles_raw:
                    prev_angles = json.loads(prev_angles_raw)
                    # 각도 차이(Delta) 계산
                    delta_pitch = abs(event.view_angles[0] - prev_angles[0])
                    delta_yaw = abs(event.view_angles[1] - prev_angles[1])
                    
                    # 1프레임만에 비정상적으로 큰 회전 (Snap Aim)
                    if delta_pitch > FPSSecurityEngine.CONFIG["AIM_ANGLE_JUMP"] or delta_yaw > FPSSecurityEngine.CONFIG["AIM_ANGLE_JUMP"]:
                        violations.append({"type": "Aim Snap Detected", "delta": [delta_pitch, delta_yaw]})
                
                await r.setex(key, 60, json.dumps(event.view_angles))

        if violations:
            alert = {
                "player_id": pid,
                "violations": violations,
                "timestamp": datetime.now().isoformat()
            }
            await manager.broadcast_alert(alert)

# --- [5] API 엔드포인트 ---

@app.post("/api/v1/report")
async def report_logs(payload: LogPayload, background_tasks: BackgroundTasks):
    # 비동기 백그라운드 분석 실행
    background_tasks.add_task(FPSSecurityEngine.analyze, payload)
    return {"status": "processing"}

@app.websocket("/ws/security")
async def security_ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
