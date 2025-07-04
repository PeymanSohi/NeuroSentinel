from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, Boolean, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Agent(Base):
    """Agent information table."""
    __tablename__ = "agents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    hostname = Column(String(100))
    ip_address = Column(String(45))
    version = Column(String(20))
    status = Column(String(20), default="active")
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to events
    events = relationship("Event", back_populates="agent")

class Event(Base):
    """System events table with all collected data."""
    __tablename__ = "events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    event_type = Column(String(50), default="system_scan")
    
    # System metrics
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_usage_percent = Column(Float)
    load_average = Column(JSON)  # [1m, 5m, 15m]
    boot_time = Column(Float)
    
    # Process data
    total_processes = Column(Integer)
    process_data = Column(JSON)  # Detailed process list
    
    # Network data
    network_connections = Column(JSON)
    listening_ports = Column(JSON)
    
    # File system data
    file_events = Column(JSON)
    
    # User data
    logged_in_users = Column(JSON)
    user_data = Column(JSON)
    
    # Security data
    security_alerts = Column(JSON)
    threat_indicators = Column(JSON)
    firewall_rules = Column(JSON)
    
    # Container data
    container_data = Column(JSON)
    
    # Cloud metadata
    cloud_metadata = Column(JSON)
    
    # Raw data for ML processing
    raw_data = Column(JSON)
    
    # ML predictions
    anomaly_score = Column(Float)
    is_anomaly = Column(Boolean, default=False)
    ml_model_used = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to agent
    agent = relationship("Agent", back_populates="events")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_events_timestamp', 'timestamp'),
        Index('idx_events_agent_timestamp', 'agent_id', 'timestamp'),
        Index('idx_events_anomaly', 'is_anomaly', 'timestamp'),
    )

class MLModel(Base):
    """ML model metadata and versions."""
    __tablename__ = "ml_models"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)  # isolation_forest, autoencoder, etc.
    file_path = Column(String(255))
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    training_samples = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Model parameters and metadata
    parameters = Column(JSON)
    model_metadata = Column(JSON)

class Alert(Base):
    """Security alerts and notifications."""
    __tablename__ = "alerts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id"))
    agent_id = Column(String(36), ForeignKey("agents.id"))
    alert_type = Column(String(50), nullable=False)  # anomaly, threat, security, etc.
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    description = Column(Text)
    details = Column(JSON)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_alerts_severity', 'severity'),
        Index('idx_alerts_resolved', 'is_resolved'),
        Index('idx_alerts_created', 'created_at'),
    )

class SystemMetrics(Base):
    """Aggregated system metrics for dashboards."""
    __tablename__ = "system_metrics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id"))
    timestamp = Column(DateTime, nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # cpu, memory, network, etc.
    value = Column(Float, nullable=False)
    unit = Column(String(20))  # %, MB, GB, etc.
    
    # Indexes for time-series queries
    __table_args__ = (
        Index('idx_metrics_timestamp_type', 'timestamp', 'metric_type'),
        Index('idx_metrics_agent_type', 'agent_id', 'metric_type'),
    ) 