sudo systemctl start redis-server
sudo systemctl start postgresql
uvicorn main:app --reload

wscat -c ws://127.0.0.1:8000/ws/dashboard

# 속도핵
curl -X POST http://127.0.0.1:8000/api/v1/logs \
     -H "Content-Type: application/json" \
     -H "X-API-Key: dev-secret" \
     -d '{
       "player_id": "p1",
       "session_id": "s1",
       "events": [
         {"type": "MOVE", "speed": 20},
         {"type": "MOVE", "speed": 20},
         {"type": "MOVE", "speed": 20},
         {"type": "MOVE", "speed": 20},
         {"type": "MOVE", "speed": 20}
       ]
     }'

# 데미지핵
curl -X POST http://127.0.0.1:8000/api/v1/logs \
     -H "Content-Type: application/json" \
     -H "X-API-Key: dev-secret" \
     -d '{
       "player_id": "p1",
       "session_id": "s1",
       "events": [
         {"type": "HIT", "damage":999, "weapon_id":"rifle","target_id":"p2"}
       ]
     }'

# 연사핵
curl -X POST http://127.0.0.1:8000/api/v1/logs \
     -H "Content-Type: application/json" \
     -H "X-API-Key: dev-secret" \
     -d '{
       "player_id": "p1",
       "session_id": "s1",
       "events": [
         {"type": "FIRE", "fire_rate": 25},
         {"type": "FIRE", "fire_rate": 25},
         {"type": "FIRE", "fire_rate": 25},
         {"type": "FIRE", "fire_rate": 25},
         {"type": "FIRE", "fire_rate": 25}
       ]
     }'

# 비인가 클라이언트
curl -X POST http://127.0.0.1:8000/api/v1/logs \
     -H "Content-Type: application/json" \
     -H "X-API-Key: team-secret-1234" \
     -d '{
       "player_id": "p1",
       "session_id": "s1",
       "events": [
         {"type": "MOVE", "speed": 20},
         {"type": "MOVE", "speed": 20},
         {"type": "MOVE", "speed": 20},
         {"type": "MOVE", "speed": 20},
         {"type": "MOVE", "speed": 20}
       ]
     }'

# DDoS 패턴
for i in {1..6}; do 
  curl -X POST http://127.0.0.1:8000/api/v1/logs \
       -H "Content-Type: application/json" \
       -H "X-API-Key: dev-secret" \
       -d '{
         "player_id": "p1",
         "session_id": "s1",
         "events": [
           {"type": "MOVE", "speed": 10},
           {"type": "MOVE", "speed": 10},
           {"type": "MOVE", "speed": 10},
           {"type": "MOVE", "speed": 10},
           {"type": "MOVE", "speed": 10}
         ]
       }' & 
done; wait

# 비행핵
curl -X POST http://127.0.0.1:8000/api/v1/logs \
     -H "Content-Type: application/json" \
     -H "X-API-Key: dev-secret" \
     -d '{
       "player_id": "p1",
       "session_id": "s1",
       "events": [
         {"type": "STATE", "is_grounded": false, "pos_y": 10.0, "vel_y": 5.0},
         {"type": "STATE", "is_grounded": false, "pos_y": 15.0, "vel_y": 5.0},
         {"type": "STATE", "is_grounded": false, "pos_y": 20.0, "vel_y": 5.0},
         {"type": "STATE", "is_grounded": false, "pos_y": 25.0, "vel_y": 5.0},
         {"type": "STATE", "is_grounded": false, "pos_y": 30.0, "vel_y": 5.0}
       ]
     }'
redis-cli flushall
