sudo systemctl enable redis-server;
sudo systemctl start redis-server

uvicorn main:app --reload

wscat -c ws://127.0.0.1:8000/ws/security

python test_security.py

redis-cli flushall
