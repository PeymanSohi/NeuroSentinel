# NeuroSentinel Test Scripts

This directory contains test scripts for verifying NeuroSentinel functionality.

## Test Scripts

### `test_websocket.py`
Tests WebSocket connectivity and HTTP endpoints.

**Usage:**
```bash
# Run from within Docker container (recommended)
docker exec neurosentinel-server-1 python3 /app/test_websocket.py

# Run locally (requires dependencies)
pip install -r requirements.txt
python3 test_websocket.py
```

### `monitor_websocket.py`
Monitors WebSocket connections and shows real-time events.

**Usage:**
```bash
# Health check only
docker exec neurosentinel-server-1 python3 /app/monitor_websocket.py health

# Full monitoring (Ctrl+C to stop)
docker exec neurosentinel-server-1 python3 /app/monitor_websocket.py

# Run locally (requires dependencies)
pip install -r requirements.txt
python3 monitor_websocket.py
```

## Dependencies

To run the scripts locally, install the required packages:
```bash
pip install -r requirements.txt
```

## Notes

- The scripts are designed to test the NeuroSentinel system running in Docker containers
- Running from within the containers is recommended as all dependencies are pre-installed
- The scripts test WebSocket connectivity to `ws://localhost:8000/ws/events`
- HTTP endpoints are tested against `http://localhost:8000` and `http://localhost:9000` 