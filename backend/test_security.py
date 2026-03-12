import requests
import time
import random

URL = "http://localhost:8000/api/v1/report"

def send_report(player_id, events):
    payload = {
        "player_id": player_id,
        "session_id": "session_fps_001",
        "events": events
    }
    try:
        res = requests.post(URL, json=payload)
        print(f"[{player_id}] 전송 결과: {res.status_code} | 데이터 개수: {len(events)}")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")

# 1. 속도핵 테스트 (Speed Hack)
# - 평균 속도가 높고 표준편차가 낮음 (일정한 고속 이동)
speed_hack_events = [
    {"type": "MOVE", "speed": 17.0 + random.uniform(-0.1, 0.1), "timestamp": time.time()}
    for _ in range(12)
]

# 2. 데미지핵 테스트 (Damage Hack)
# - AK-47의 최대 데미지(35)를 초과하는 999 데미지 전송
damage_hack_events = [
    {
        "type": "HIT", 
        "weapon_id": "AK-47", 
        "damage": 999.0, 
        "target_id": "enemy_01", 
        "timestamp": time.time()
    }
]

# 3. 연사핵 테스트 (Fire Rate Hack)
# - AK-47의 최소 간격(0.1초)보다 훨씬 빠른 0.01초 간격으로 발사
fire_rate_events = []
for i in range(5):
    fire_rate_events.append({
        "type": "FIRE", 
        "weapon_id": "AK-47", 
        "timestamp": time.time() + (i * 0.01) # 매우 짧은 간격
    })

# 4. 에임핵 테스트 (Aim Snap)
# - 시야각(Pitch, Yaw)이 1프레임만에 90도 급회전
aim_hack_events = [
    {"type": "AIM", "view_angles": [0.0, 0.0], "timestamp": time.time()},
    {"type": "AIM", "view_angles": [0.0, 95.0], "timestamp": time.time() + 0.01} # 95도 급회전
]

# 5. 정상 유저 테스트 (Normal User)
normal_events = [
    {"type": "MOVE", "speed": random.uniform(5, 7), "timestamp": time.time()},
    {"type": "AIM", "view_angles": [10.0, 10.5], "timestamp": time.time() + 0.1}
]

if __name__ == "__main__":
    print("🚀 FPS 보안 분석 엔진 테스트 시작...\n")
    
    send_report("Hacker_Speed", speed_hack_events)
    time.sleep(0.5)
    
    send_report("Hacker_Damage", damage_hack_events)
    time.sleep(0.5)
    
    send_report("Hacker_RapidFire", fire_rate_events)
    time.sleep(0.5)
    
    send_report("Hacker_Aim", aim_hack_events)
    time.sleep(0.5)
    
    send_report("Normal_Player", normal_events)
    
    print("\n✅ 모든 테스트 로그 전송 완료. 대시보드(WS)에서 알림을 확인하세요.")
