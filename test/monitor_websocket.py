#!/usr/bin/env python3
"""
WebSocket Monitor for NeuroSentinel
Monitors WebSocket connections and shows real-time events
"""

import asyncio
import websockets
import json
import time
from datetime import datetime
import signal
import sys

class WebSocketMonitor:
    def __init__(self, uri="ws://localhost:8000/ws/events"):
        self.uri = uri
        self.running = True
        self.connection_count = 0
        self.message_count = 0
        self.start_time = time.time()
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n🛑 Stopping WebSocket monitor...")
        self.running = False
        
    async def monitor_connection(self):
        """Monitor WebSocket connection and messages"""
        
        print("🔌 NeuroSentinel WebSocket Monitor")
        print("=" * 50)
        print(f"📍 Connecting to: {self.uri}")
        print(f"⏰ Started at: {datetime.now()}")
        print("📋 Press Ctrl+C to stop monitoring")
        print("-" * 50)
        
        while self.running:
            try:
                async with websockets.connect(self.uri) as websocket:
                    self.connection_count += 1
                    print(f"✅ Connection #{self.connection_count} established at {datetime.now()}")
                    
                    # Send a heartbeat message
                    heartbeat = {
                        "type": "heartbeat",
                        "timestamp": time.time(),
                        "monitor": True
                    }
                    await websocket.send(json.dumps(heartbeat))
                    print("💓 Heartbeat sent")
                    
                    # Listen for messages
                    while self.running:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                            self.message_count += 1
                            
                            # Parse and display message
                            try:
                                data = json.loads(message)
                                print(f"\n📥 Message #{self.message_count} at {datetime.now()}")
                                print(f"📋 Type: {data.get('event_type', 'unknown')}")
                                print(f"🆔 Agent: {data.get('agent_id', 'unknown')}")
                                
                                # Show relevant data based on event type
                                if data.get('event_type') == 'system_scan':
                                    system = data.get('system', {})
                                    print(f"💻 CPU: {system.get('cpu_percent', 'N/A')}%")
                                    print(f"🧠 Memory: {system.get('memory_percent', 'N/A')}%")
                                    
                                elif data.get('event_type') == 'anomaly_detected':
                                    print(f"🚨 Anomaly Score: {data.get('anomaly_score', 'N/A')}")
                                    print(f"⚠️  Severity: {data.get('severity', 'N/A')}")
                                    
                                # Show full message for non-standard events
                                if data.get('event_type') not in ['system_scan', 'anomaly_detected']:
                                    print(f"📄 Full message: {json.dumps(data, indent=2)}")
                                    
                            except json.JSONDecodeError:
                                print(f"⚠️  Non-JSON message: {message}")
                                
                        except asyncio.TimeoutError:
                            # No message received, continue monitoring
                            continue
                        except websockets.exceptions.ConnectionClosed:
                            print(f"❌ Connection #{self.connection_count} closed")
                            break
                            
            except websockets.exceptions.ConnectionRefused:
                print(f"❌ Connection refused at {datetime.now()}")
                await asyncio.sleep(5)  # Wait before retrying
            except Exception as e:
                print(f"❌ Error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                
        # Print summary
        duration = time.time() - self.start_time
        print("\n" + "=" * 50)
        print("📊 WebSocket Monitor Summary")
        print(f"⏱️  Duration: {duration:.1f} seconds")
        print(f"🔗 Connections: {self.connection_count}")
        print(f"📨 Messages: {self.message_count}")
        print(f"📈 Rate: {self.message_count/duration:.2f} messages/second")
        print("=" * 50)

async def test_websocket_health():
    """Test WebSocket health and functionality"""
    
    print("🏥 WebSocket Health Check")
    print("=" * 30)
    
    uri = "ws://localhost:8000/ws/events"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connection: OK")
            
            # Test sending a message
            test_msg = {
                "agent_id": "health-check",
                "timestamp": time.time(),
                "event_type": "health_check",
                "system": {"cpu_percent": 0, "memory_percent": 0},
                "process": {"count": 0, "new_processes": []},
                "network": {"connections": 0, "listening_ports": []},
                "file": {"new_files": [], "modified_files": []},
                "user": {"logged_users": [], "new_users": []},
                "logs": {"new_entries": 0, "error_count": 0},
                "persistence": {"scheduled_tasks": [], "startup_items": []},
                "firewall": {"rules": [], "blocked_ips": []},
                "container": {"running_containers": [], "new_containers": []},
                "cloud": {"instances": [], "configurations": []},
                "threat_intel": {"indicators": [], "matches": []},
                "integrity": {"file_changes": [], "system_changes": []},
                "security_tools": {"antivirus_status": "unknown", "ids_alerts": []}
            }
            
            await websocket.send(json.dumps(test_msg))
            print("✅ Message sending: OK")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                if data.get('status') == 'received':
                    print("✅ Message processing: OK")
                else:
                    print(f"⚠️  Message processing: {data}")
            except asyncio.TimeoutError:
                print("⚠️  Message processing: Timeout")
                
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
        
    return True

def main():
    """Main function"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "health":
        # Run health check only
        asyncio.run(test_websocket_health())
        return
        
    # Set up signal handler for graceful shutdown
    monitor = WebSocketMonitor()
    signal.signal(signal.SIGINT, monitor.signal_handler)
    
    # Run the monitor
    asyncio.run(monitor.monitor_connection())

if __name__ == "__main__":
    main() 