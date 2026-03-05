import requests
import random

URL = "http://localhost:8000/api/v1/logs"

def send_logs(player_id, speeds):
    events = [{"type": "MOVE", "speed": s} for s in speeds]
    payload = {"player_id": player_id, "session_id": "test_sn", "events": events}
    res = requests.post(URL, json=payload)
    print(f"[{player_id}] Status: {res.status_code}")

# Case 1: Normal (No Alert)
send_logs("Normal_User", [random.uniform(5, 8) for _ in range(10)])

# Case 2: Lag/Jitter (Suspicious log, but no Alert)
send_logs("Laggy_User", [2.0, 40.0, 1.5, 35.0, 3.0, 38.0, 2.5, 42.0])

# Case 3: Speed Hack (Dashboard Alert Triggered!)
send_logs("Hacker_99", [15.0, 15.1, 14.9, 15.0, 15.1, 14.8, 15.0, 15.2])
