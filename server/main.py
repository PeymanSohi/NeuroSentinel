from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import json
from datetime import datetime

app = FastAPI()

# Allow dashboard (frontend) to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory event storage
EVENTS = []

class Event(BaseModel):
    agent_id: str
    timestamp: float
    system: Dict[str, Any]
    process: Dict[str, Any]
    network: Dict[str, Any]
    file: Dict[str, Any]
    user: Dict[str, Any]
    logs: Dict[str, Any]
    persistence: Dict[str, Any]
    firewall: Dict[str, Any]
    container: Dict[str, Any]
    cloud: Dict[str, Any]
    threat_intel: Dict[str, Any]
    integrity: Dict[str, Any]
    security_tools: Dict[str, Any]

@app.get("/")
def root():
    return {"message": "NeuroSentinel API is running."}

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.post("/events")
async def receive_event(event: Event):
    """Receive an event from an agent and store it."""
    EVENTS.append(event.dict())
    return {"status": "received", "timestamp": datetime.utcnow().isoformat()}

@app.get("/events", response_model=List[Event])
async def get_events():
    """Return all received events."""
    return EVENTS

@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time event streaming."""
    await websocket.accept()
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            event_data = json.loads(data)
            
            # Store the event
            EVENTS.append(event_data)
            
            # Send acknowledgment back to client
            await websocket.send_text(json.dumps({
                "status": "received",
                "timestamp": datetime.utcnow().isoformat(),
                "event_count": len(EVENTS)
            }))
            
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "status": "error",
            "message": str(e)
        }))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
