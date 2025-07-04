import os

SERVER_URL = os.getenv("SERVER_URL", "http://server:8000/events")
AGENT_ID = os.getenv("AGENT_ID", os.uname().nodename)
INTERVAL = int(os.getenv("AGENT_INTERVAL", 10))  # seconds
