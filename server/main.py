from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import json
from datetime import datetime
import logging

from database import get_db, init_db, check_db_connection
from models import Event as EventModel, Agent as AgentModel, Alert as AlertModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NeuroSentinel API", version="1.0.0")

# Allow dashboard (frontend) to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class EventCreate(BaseModel):
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

class EventResponse(BaseModel):
    id: str
    agent_id: str
    timestamp: datetime
    event_type: str
    cpu_percent: Optional[float]
    memory_percent: Optional[float]
    anomaly_score: Optional[float]
    is_anomaly: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AlertCreate(BaseModel):
    event_id: str
    agent_id: str
    alert_type: str
    severity: str = "medium"
    title: str
    description: str
    details: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        if check_db_connection():
            init_db()
            logger.info("Database initialized successfully")
        else:
            logger.error("Database connection failed")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.get("/")
def root():
    return {"message": "NeuroSentinel API is running.", "version": "1.0.0"}

@app.get("/health")
def health():
    db_status = "ok" if check_db_connection() else "error"
    return {
        "status": "ok", 
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status
    }

@app.post("/events")
async def receive_event(event: EventCreate, db: Session = Depends(get_db)):
    """Receive an event from an agent and store it in database."""
    try:
        # Ensure agent exists
        agent = db.query(AgentModel).filter(AgentModel.id == event.agent_id).first()
        if not agent:
            # Create agent if it doesn't exist
            agent = AgentModel(
                id=event.agent_id,
                name=f"Agent-{event.agent_id[:8]}",
                hostname=event.system.get("hostname", "unknown"),
                ip_address=event.system.get("ip_address", "unknown"),
                version="1.0.0"
            )
            db.add(agent)
            db.commit()
            logger.info(f"Created new agent: {event.agent_id}")
        
        # Create database event
        db_event = EventModel(
            agent_id=event.agent_id,
            timestamp=datetime.fromtimestamp(event.timestamp),
            event_type="system_scan",
            cpu_percent=event.system.get("cpu_percent"),
            memory_percent=event.system.get("memory_percent"),
            disk_usage_percent=event.system.get("disk_usage_percent"),
            load_average=event.system.get("load_average"),
            boot_time=event.system.get("boot_time"),
            total_processes=len(event.process.get("processes", [])),
            process_data=event.process,
            network_connections=event.network.get("connections"),
            listening_ports=event.network.get("listening_ports"),
            file_events=event.file.get("events"),
            logged_in_users=event.user.get("logged_in_users"),
            user_data=event.user,
            security_alerts=event.security_tools.get("ids_alerts"),
            threat_indicators=event.threat_intel.get("indicators"),
            firewall_rules=event.firewall.get("rules"),
            container_data=event.container,
            cloud_metadata=event.cloud,
            raw_data=event.dict()
        )
        
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        logger.info(f"Event stored: {db_event.id}")
        return {"status": "received", "event_id": db_event.id, "timestamp": datetime.utcnow().isoformat()}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error storing event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events", response_model=List[EventResponse])
async def get_events(
    limit: int = 100, 
    offset: int = 0, 
    agent_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Return events from database with pagination and filtering."""
    try:
        query = db.query(EventModel)
        
        if agent_id:
            query = query.filter(EventModel.agent_id == agent_id)
        
        events = query.order_by(EventModel.timestamp.desc()).offset(offset).limit(limit).all()
        return events
        
    except Exception as e:
        logger.error(f"Error retrieving events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/count")
async def get_event_count(db: Session = Depends(get_db)):
    """Get total count of events."""
    try:
        count = db.query(EventModel).count()
        return {"count": count}
    except Exception as e:
        logger.error(f"Error counting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/anomalies")
async def get_anomalies(limit: int = 50, db: Session = Depends(get_db)):
    """Get events flagged as anomalies."""
    try:
        anomalies = db.query(EventModel).filter(
            EventModel.is_anomaly == True
        ).order_by(EventModel.timestamp.desc()).limit(limit).all()
        return anomalies
    except Exception as e:
        logger.error(f"Error retrieving anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/alerts")
async def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert."""
    try:
        db_alert = AlertModel(
            event_id=alert.event_id,
            agent_id=alert.agent_id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            title=alert.title,
            description=alert.description,
            details=alert.details
        )
        
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        
        logger.info(f"Alert created: {db_alert.id}")
        return {"status": "created", "alert_id": db_alert.id}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts")
async def get_alerts(
    limit: int = 50, 
    resolved: bool = False,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get alerts with filtering."""
    try:
        query = db.query(AlertModel).filter(AlertModel.is_resolved == resolved)
        
        if severity:
            query = query.filter(AlertModel.severity == severity)
        
        alerts = query.order_by(AlertModel.created_at.desc()).limit(limit).all()
        return alerts
        
    except Exception as e:
        logger.error(f"Error retrieving alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time event streaming."""
    await websocket.accept()
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            event_data = json.loads(data)
            
            # Store the event in database
            try:
                db = next(get_db())
                event = EventCreate(**event_data)
                
                # Ensure agent exists
                agent = db.query(AgentModel).filter(AgentModel.id == event.agent_id).first()
                if not agent:
                    # Create agent if it doesn't exist
                    agent = AgentModel(
                        id=event.agent_id,
                        name=f"Agent-{event.agent_id[:8]}",
                        hostname=event.system.get("hostname", "unknown"),
                        ip_address=event.system.get("ip_address", "unknown"),
                        version="1.0.0"
                    )
                    db.add(agent)
                    db.commit()
                
                db_event = EventModel(
                    agent_id=event.agent_id,
                    timestamp=datetime.fromtimestamp(event.timestamp),
                    event_type="system_scan",
                    cpu_percent=event.system.get("cpu_percent"),
                    memory_percent=event.system.get("memory_percent"),
                    raw_data=event.dict()
                )
                db.add(db_event)
                db.commit()
                
                # Send acknowledgment back to client
                await websocket.send_text(json.dumps({
                    "status": "received",
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_id": db_event.id
                }))
                
            except Exception as e:
                logger.error(f"Error storing WebSocket event: {e}")
                await websocket.send_text(json.dumps({
                    "status": "error",
                    "message": str(e)
                }))
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
