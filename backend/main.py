import uvicorn
import json
import numpy as np
import redis
from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect, Request, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import time
import os
from backend.db import engine, AsyncSessionLocal, Base
from backend.models import RawLog, Alert
from sqlalchemy import select, func, desc

app = FastAPI(title="Pro Game Security Analysis (Redis + Stats)")
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- [1] Infrastructure Setup ---
# Ensure redis-server is running (Docker or Local)
REDIS_OK = False
try:
    r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
    REDIS_OK = True
except redis.ConnectionError:
    print("❌ Cannot connect to Redis. Running in local memory mode or please start Redis.")
    r = None
# --- [2] Data Models ---
class GameEvent(BaseModel):
    type: str  # e.g., "MOVE", "FIRE"
    speed: Optional[float] = None
    fire_rate: Optional[float] = None
    # Damage Hack용
    damage: Optional[float] = None
    weapon_id: Optional[str] = None
    target_id: Optional[str] = None

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
    # ✅ Unauthorized Client (API Key) - NEW
    "AUTH_API_KEY": os.getenv("SECURITY_API_KEY", "dev-secret"),
    "AUTH_ENFORCE_BLOCK": True,   # True면 401로 차단 / False면 알림만
    "MOVE_THRESHOLD": 12.0,
    "STDEV_MAX": 2.5,
    "WINDOW_SIZE": 15,
    "MIN_SAMPLES": 5,
    "TTL": 1800,

    # ✅ DDoS Pattern (요청 빈도 제한) - NEW
    "RL_WINDOW_SEC": 1,         # 몇 초 창으로 볼지
    "RL_MAX_REQ": 5,            # 창 내 최대 요청 수(초당 5회 초과 시 탐지)
    "RL_ENFORCE_BLOCK": False,  # True면 429로 차단, False면 탐지/알림만
    
    # ✅ Damage Hack - NEW
    "DMG_EVENT_TYPES": {"HIT", "DAMAGE"},
    "DMG_MAX_DEFAULT": 120.0,  # 무기 정보 없을 때 단발 상한
    "DMG_MAX_BY_WEAPON": {     # (선택) 무기별 단발 상한
    "pistol": 35.0,
    "rifle": 45.0,
    "sniper": 120.0,
},
"DMG_DPS_WINDOW_SEC": 1,   # 초당 누적 데미지
"DMG_DPS_MAX": 200.0,      # 1초 동안 누적 데미지 상한
"DMG_ALERT_COOLDOWN_SEC": 5,  # 같은 플레이어는 5초에 1번만 알림(스팸 방지)
}

# ✅ DDoS Pattern 탐지: player_id 또는 IP 기준 요청 폭주 감지
def check_rate_limit(player_id: str, client_ip: str) -> tuple[bool, int]:
    """
    return (is_exceeded, current_count)
    Redis: INCR + EXPIRE로 RL_WINDOW_SEC 동안 카운트
    """
    key = f"rate:{player_id}"   # 가장 쉬운 기준: player_id
    window = CONFIG["RL_WINDOW_SEC"]

    if REDIS_OK and r is not None:
        cnt = r.incr(key)
        if cnt == 1:
            r.expire(key, window)
        return (cnt > CONFIG["RL_MAX_REQ"], cnt)

    # Redis 없을 때(백업): 매우 단순한 메모리 카운터(프로세스 재시작 시 초기화)
    # 과제 데모 목적이면 충분
    now = time.time()
    if not hasattr(check_rate_limit, "_mem"):
        check_rate_limit._mem = {}
    mem = check_rate_limit._mem

    cnt, start = mem.get(key, (0, now))
    if now - start >= window:
        cnt, start = 0, now
    cnt += 1
    mem[key] = (cnt, start)
    return (cnt > CONFIG["RL_MAX_REQ"], cnt)

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
                    
        # --- Damage Hack Analysis ---
        if event.type in CONFIG["DMG_EVENT_TYPES"] and event.damage is not None:
            dmg = float(event.damage)
            weapon = (event.weapon_id or "unknown").lower()

            # 1) 단발 데미지 상한 체크
            max_hit = CONFIG["DMG_MAX_BY_WEAPON"].get(weapon, CONFIG["DMG_MAX_DEFAULT"])
            if dmg > max_hit:
                detected_hacks.append({
                    "type": "Damage Hack",
                    "reason": "Damage per hit exceeds max",
                    "damage": round(dmg, 2),
                    "max_hit": max_hit,
                    "weapon": weapon,
                    "target_id": event.target_id,
                })

            # 2) 초당 누적 데미지(DPS) 체크 (Redis 권장)
            #    같은 초(epoch second) 키에 누적시키고 임계치 넘으면 탐지
            now_sec = int(time.time())
            dps_key = f"player:{pid}:dmg:{now_sec}"

            if REDIS_OK and r is not None:
                total = r.incrbyfloat(dps_key, dmg)
                r.expire(dps_key, CONFIG["DMG_DPS_WINDOW_SEC"] + 1)
            else:
                # Redis 없을 때 메모리 백업
                if not hasattr(analyze_security_risk, "_dmg_mem"):
                    analyze_security_risk._dmg_mem = {}
                mem = analyze_security_risk._dmg_mem
                total = mem.get(dps_key, 0.0) + dmg
                mem[dps_key] = total

            if total > CONFIG["DMG_DPS_MAX"]:
                detected_hacks.append({
                    "type": "Damage Hack",
                    "reason": "Damage per second exceeds max",
                    "dps_total": round(float(total), 2),
                    "window_sec": CONFIG["DMG_DPS_WINDOW_SEC"],
                    "dps_max": CONFIG["DMG_DPS_MAX"],
                })

    # Alert manager if violations are found
    if detected_hacks:
        alert_data = {
            "player_id": pid,
            "session_id": payload.session_id,
            "violations": detected_hacks,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # ✅ DB에 alerts 저장 (send_alert 전에)
        async with AsyncSessionLocal() as session:
            session.add(Alert(
                player_id=alert_data["player_id"],
                session_id=alert_data["session_id"],
                alert=alert_data,
            ))
            await session.commit()

        await manager.send_alert(alert_data)

# --- [5] API Endpoints ---
@app.post("/api/v1/logs")
async def collect_logs(
    payload: LogPayload,
    background_tasks: BackgroundTasks,
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    # 비인가 클라이언트 탐지
    if x_api_key != CONFIG["AUTH_API_KEY"]:
        client_ip = request.client.host if request.client else "unknown"
        alert_data = {
            "player_id": payload.player_id,
            "session_id": payload.session_id,
            "violations": [{
                "type": "Unauthorized Client",
                "client_ip": client_ip,
                "has_api_key": bool(x_api_key),
            }],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        await manager.send_alert(alert_data)

        if CONFIG["AUTH_ENFORCE_BLOCK"]:
            raise HTTPException(status_code=401, detail="Unauthorized client (invalid API key)")

    # DDoS / Speed / Fire 로직 수행
    client_ip = request.client.host if request.client else "unknown"
    exceeded, cnt = check_rate_limit(payload.player_id, client_ip)
    if exceeded:
        alert_data = {
            "player_id": payload.player_id,
            "session_id": payload.session_id,
            "violations": [{
                "type": "DDoS Pattern",
                "count": cnt,
                "window_sec": CONFIG["RL_WINDOW_SEC"],
                "max_req": CONFIG["RL_MAX_REQ"],
                "client_ip": client_ip
            }],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        await manager.send_alert(alert_data)
        if CONFIG["RL_ENFORCE_BLOCK"]:
            raise HTTPException(status_code=429, detail="Too many requests (rate limit exceeded)")
        
    #  원본 payload DB 저장 (인증/레이트리밋 통과 후)
    async with AsyncSessionLocal() as session:
        session.add(RawLog(
            player_id=payload.player_id,
            session_id=payload.session_id,
            payload=payload.model_dump(),  # pydantic v2
        ))
        await session.commit()

    background_tasks.add_task(analyze_security_risk, payload)
    return {"status": "ok", "received": len(payload.events), "rate_count": cnt}

# =========================
#  Helpers for GET APIs
# =========================
def _require_api_key(x_api_key: str | None):
    if x_api_key != CONFIG["AUTH_API_KEY"]:
        raise HTTPException(status_code=401, detail="Unauthorized client (invalid API key)")


def _rawlog_to_dict(row: RawLog) -> dict:
    payload = row.payload if isinstance(row.payload, dict) else {}
    return {
        "id": row.id,
        "player_id": row.player_id,
        "session_id": row.session_id,
        "created_at": row.created_at,
        "event_count": len(payload.get("events", [])),
        "payload": payload,
    }


def _alert_to_dict(row: Alert) -> dict:
    alert = row.alert if isinstance(row.alert, dict) else {}
    return {
        "id": row.id,
        "player_id": row.player_id,
        "session_id": row.session_id,
        "created_at": row.created_at,
        "alert": alert,
    }


# =========================
#  GET 1) 이벤트(raw_logs) 목록 조회
# =========================
@app.get("/api/v1/events")
async def list_events(
    player_id: str | None = None,
    session_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _require_api_key(x_api_key)

    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    stmt = select(RawLog)
    cnt_stmt = select(func.count()).select_from(RawLog)

    if player_id:
        stmt = stmt.where(RawLog.player_id == player_id)
        cnt_stmt = cnt_stmt.where(RawLog.player_id == player_id)
    if session_id:
        stmt = stmt.where(RawLog.session_id == session_id)
        cnt_stmt = cnt_stmt.where(RawLog.session_id == session_id)

    stmt = stmt.order_by(RawLog.created_at.desc()).limit(limit).offset(offset)

    async with AsyncSessionLocal() as session:
        total = await session.scalar(cnt_stmt)
        result = await session.execute(stmt)
        rows = result.scalars().all()

    return {
        "total": int(total or 0),
        "limit": limit,
        "offset": offset,
        "items": [_rawlog_to_dict(r) for r in rows],
    }


# =========================
#  GET 2) 알림(alerts) 목록 조회
# =========================
@app.get("/api/v1/alerts")
async def list_alerts(
    player_id: str | None = None,
    session_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _require_api_key(x_api_key)

    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    stmt = select(Alert)
    cnt_stmt = select(func.count()).select_from(Alert)

    if player_id:
        stmt = stmt.where(Alert.player_id == player_id)
        cnt_stmt = cnt_stmt.where(Alert.player_id == player_id)
    if session_id:
        stmt = stmt.where(Alert.session_id == session_id)
        cnt_stmt = cnt_stmt.where(Alert.session_id == session_id)

    stmt = stmt.order_by(Alert.created_at.desc()).limit(limit).offset(offset)

    async with AsyncSessionLocal() as session:
        total = await session.scalar(cnt_stmt)
        result = await session.execute(stmt)
        rows = result.scalars().all()

    return {
        "total": int(total or 0),
        "limit": limit,
        "offset": offset,
        "items": [_alert_to_dict(r) for r in rows],
    }


# =======================
#  GET 3) 플레이어 상세 조회
# ========================
@app.get("/api/v1/players/{player_id}")
async def get_player_detail(
    player_id: str,
    events_limit: int = 50,
    alerts_limit: int = 50,
    sessions_limit: int = 20,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _require_api_key(x_api_key)

    events_limit = max(1, min(events_limit, 200))
    alerts_limit = max(1, min(alerts_limit, 200))
    sessions_limit = max(1, min(sessions_limit, 200))

    async with AsyncSessionLocal() as session:
        last_seen = await session.scalar(
            select(func.max(RawLog.created_at)).where(RawLog.player_id == player_id)
        )

        # 세션 목록(최근 세션부터)
        sess_stmt = (
            select(RawLog.session_id, func.max(RawLog.created_at).label("last_seen"))
            .where(RawLog.player_id == player_id)
            .group_by(RawLog.session_id)
            .order_by(desc("last_seen"))
            .limit(sessions_limit)
        )
        sess_rows = (await session.execute(sess_stmt)).all()
        sessions = [{"session_id": s, "last_seen": t} for (s, t) in sess_rows]

        # 최근 이벤트들
        ev_stmt = (
            select(RawLog)
            .where(RawLog.player_id == player_id)
            .order_by(RawLog.created_at.desc())
            .limit(events_limit)
        )
        ev_rows = (await session.execute(ev_stmt)).scalars().all()

        # 최근 알림들
        al_stmt = (
            select(Alert)
            .where(Alert.player_id == player_id)
            .order_by(Alert.created_at.desc())
            .limit(alerts_limit)
        )
        al_rows = (await session.execute(al_stmt)).scalars().all()

    return {
        "player_id": player_id,
        "last_seen": last_seen,
        "sessions": sessions,
        "recent_events": [_rawlog_to_dict(r) for r in ev_rows],
        "recent_alerts": [_alert_to_dict(r) for r in al_rows],
    }

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
