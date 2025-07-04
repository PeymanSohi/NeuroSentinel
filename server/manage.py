#!/usr/bin/env python3
"""
NeuroSentinel Management CLI
Provides administrative commands for database operations and system management.
"""

import argparse
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, create_tables, check_db_connection, engine
from models import Base, Event, Agent, Alert, MLModel, SystemMetrics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with all tables."""
    try:
        if not check_db_connection():
            logger.error("Database connection failed")
            return False
        
        init_db()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

def create_database_tables():
    """Create all database tables."""
    try:
        if not check_db_connection():
            logger.error("Database connection failed")
            return False
        
        create_tables()
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        return False

def drop_database_tables():
    """Drop all database tables (DESTRUCTIVE)."""
    try:
        if not check_db_connection():
            logger.error("Database connection failed")
            return False
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.info("All database tables dropped successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        return False

def check_database():
    """Check database connection and table status."""
    try:
        if not check_db_connection():
            logger.error("Database connection failed")
            return False
        
        # Check if tables exist
        inspector = engine.dialect.inspector(engine)
        existing_tables = inspector.get_table_names()
        expected_tables = ['agents', 'events', 'alerts', 'ml_models', 'system_metrics']
        
        logger.info("Database connection: OK")
        logger.info(f"Existing tables: {existing_tables}")
        
        missing_tables = [table for table in expected_tables if table not in existing_tables]
        if missing_tables:
            logger.warning(f"Missing tables: {missing_tables}")
        else:
            logger.info("All expected tables exist")
        
        return True
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return False

def reset_database():
    """Reset database by dropping and recreating all tables."""
    try:
        logger.info("Dropping all tables...")
        if not drop_database_tables():
            return False
        
        logger.info("Creating all tables...")
        if not create_database_tables():
            return False
        
        logger.info("Database reset completed successfully")
        return True
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        return False

def show_database_stats():
    """Show database statistics."""
    try:
        if not check_db_connection():
            logger.error("Database connection failed")
            return False
        
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # Count records in each table
            agent_count = db.query(Agent).count()
            event_count = db.query(Event).count()
            alert_count = db.query(Alert).count()
            model_count = db.query(MLModel).count()
            
            logger.info("Database Statistics:")
            logger.info(f"  Agents: {agent_count}")
            logger.info(f"  Events: {event_count}")
            logger.info(f"  Alerts: {alert_count}")
            logger.info(f"  ML Models: {model_count}")
            
            # Show recent events
            if event_count > 0:
                recent_events = db.query(Event).order_by(Event.timestamp.desc()).limit(5).all()
                logger.info("\nRecent Events:")
                for event in recent_events:
                    logger.info(f"  {event.timestamp}: Agent {event.agent_id} - CPU: {event.cpu_percent}%")
            
            return True
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return False

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="NeuroSentinel Management CLI")
    parser.add_argument("command", choices=[
        "init-db", "create-tables", "drop-tables", "reset-db", 
        "check-db", "stats", "help"
    ], help="Command to execute")
    
    args = parser.parse_args()
    
    if args.command == "help":
        parser.print_help()
        return
    
    # Execute the requested command
    success = False
    
    if args.command == "init-db":
        success = init_database()
    elif args.command == "create-tables":
        success = create_database_tables()
    elif args.command == "drop-tables":
        success = drop_database_tables()
    elif args.command == "reset-db":
        success = reset_database()
    elif args.command == "check-db":
        success = check_database()
    elif args.command == "stats":
        success = show_database_stats()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 