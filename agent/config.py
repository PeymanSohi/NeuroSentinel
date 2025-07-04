import os

SERVER_URL = os.getenv("SERVER_URL", "http://server:8000/events")
AGENT_ID = os.getenv("AGENT_ID", os.uname().nodename)
INTERVAL = int(os.getenv("AGENT_INTERVAL", 10))  # seconds
SEND_MODE = os.getenv("SEND_MODE", "rest")  # "rest" or "websocket"
WS_URL = os.getenv("WS_URL", "ws://server:8000/ws")
