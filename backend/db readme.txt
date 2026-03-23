db readme
wsl 기준
서버 켜기
cd /mnt/c/Users/coron/Desktop/FPSecurity-main #FPS-main 자기 컴퓨터 루트 따라가시면 됩니다.
source .venv/bin/activate

sudo service redis-server start
redis-cli ping

sudo service postgresql start

export DATABASE_URL="postgresql+asyncpg://fps:fps1234@localhost:5432/fpsdb"

서버 켜기전 환경변수 설정 
export SECURITY_API_KEY="team-secret-1234"
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

powershell 에서
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/logs" `
  -Method Post `
  -ContentType "application/json" `
  -Headers @{ "X-API-Key"="team-secret-1234" } `
  -Body $bodyJson



---------------------------------------------------------------------------------------------------
WSL새로 켜서
최초 
cd /mnt/c/Users/coron/Desktop/FPSecurity-main
source .venv/bin/activate

웹소켓 연결 
python - <<'PY'
import asyncio, websockets

async def main():
    uri = "ws://127.0.0.1:8000/ws/dashboard"
    async with websockets.connect(uri) as ws:
        print("connected:", uri)

        async def keepalive():
            while True:
                await asyncio.sleep(10)
                await ws.send("ping")   # 서버 receive_text()를 깨워서 연결 유지

        asyncio.create_task(keepalive())

        while True:
            msg = await ws.recv()
            print("ALERT:", msg)

asyncio.run(main())
PY

----------------------------------------------------------------
Sql id password // CREATE USER fps WITH PASSWORD 'fps1234';
