import os
import time
import socket
import requests
import psutil
import platform
import hashlib
import pwd
import grp
from datetime import datetime
import asyncio
import json

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

try:
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

from config import SERVER_URL, AGENT_ID, INTERVAL, SEND_MODE, WS_URL
from collectors import system, process, network, file, user, logs, persistence, firewall, container, cloud, threat_intel, integrity, security_tools, snapshot

# --- File System Monitoring (Watchdog) ---
file_events = []

class FileChangeHandler:
    def on_any_event(self, event):
        file_events.append({
            "event_type": event.event_type,
            "src_path": event.src_path,
            "is_directory": event.is_directory,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def dispatch(self, event):
        self.on_any_event(event)

def start_file_monitor(path="/etc"):
    if not WATCHDOG_AVAILABLE:
        print("[WARNING] watchdog library not installed. File monitoring disabled.")
        return None
    observer = Observer()
    handler = FileChangeHandler()
    observer.schedule(handler, path, recursive=True)
    observer.start()
    return observer

# --- Utility Functions ---
def get_logged_in_users():
    try:
        return [u.name for u in psutil.users()]
    except Exception:
        return []

def get_processes():
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'username', 'cmdline', 'ppid', 'create_time', 'exe']):
        try:
            info = p.info
            # Hash the binary if possible
            exe = info.get('exe')
            file_hash = None
            if exe and os.path.isfile(exe):
                with open(exe, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
            info['sha256'] = file_hash
            procs.append(info)
        except Exception:
            continue
    return procs

def get_network_connections():
    conns = []
    for c in psutil.net_connections(kind='inet'):
        try:
            conns.append({
                "fd": c.fd,
                "family": str(c.family),
                "type": str(c.type),
                "laddr": c.laddr,
                "raddr": c.raddr,
                "status": c.status,
                "pid": c.pid
            })
        except Exception:
            continue
    return conns

def get_users_groups():
    try:
        users = [u.pw_name for u in pwd.getpwall()]
        groups = [g.gr_name for g in grp.getgrall()]
        return users, groups
    except Exception:
        return [], []

def get_cron_jobs():
    try:
        with os.popen('crontab -l') as f:
            return f.read().splitlines()
    except Exception:
        return []

def get_services():
    try:
        with os.popen('systemctl list-units --type=service --state=running') as f:
            return f.read().splitlines()
    except Exception:
        return []

def get_firewall_rules():
    try:
        with os.popen('iptables -S') as f:
            return f.read().splitlines()
    except Exception:
        return []

def get_os_info():
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "platform": platform.platform(),
        "kernel": platform.release(),
        "hostname": socket.gethostname(),
        "architecture": platform.machine(),
        "python_version": platform.python_version()
    }

def collect_all_data():
    data = {
        "agent_id": AGENT_ID,
        "timestamp": time.time(),
        "system": system.collect_system_metrics(),
        "process": process.collect_process_info(),
        "network": network.collect_network_info(),
        "file": {"events": []},  # Simplified for now
        "user": user.collect_user_activity(),
        "logs": {"timestamp": datetime.utcnow().isoformat()},  # Simplified for now
        "persistence": persistence.collect_persistence_info(),
        "firewall": firewall.collect_firewall_rules(),
        "container": container.collect_container_info(),
        "cloud": cloud.collect_cloud_info(),
        "threat_intel": threat_intel.enrich_with_threat_intel({}),  # Pass relevant data as needed
        "integrity": integrity.check_agent_integrity(),
        "security_tools": security_tools.collect_security_tools_status(),
    }
    return data

def send_event_rest(event):
    try:
        response = requests.post(SERVER_URL, json=event, timeout=10)
        print(f"[INFO] Event reported via REST: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[ERROR] Failed to report event via REST: {e}")

async def send_event_ws(event):
    if not WEBSOCKETS_AVAILABLE:
        print("[ERROR] websockets library not installed. Cannot send via WebSocket.")
        return
    try:
        async with websockets.connect(WS_URL) as ws:
            await ws.send(json.dumps(event))
            ack = await ws.recv()
            print(f"[INFO] Event reported via WebSocket: {ack}")
    except Exception as e:
        print(f"[ERROR] Failed to report event via WebSocket: {e}")

ML_CORE_URL = os.getenv("ML_CORE_URL", "http://ml_core:9000/predict")

def detect_anomaly(event):
    try:
        response = requests.post(ML_CORE_URL, json={"data": event}, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result.get("is_anomalous", False), result.get("anomaly_score", 0.0)
        else:
            print(f"[ERROR] ML core returned {response.status_code}: {response.text}")
            return False, 0.0
    except Exception as e:
        print(f"[ERROR] Failed to call ML core: {e}")
        return False, 0.0

SNAPSHOT_WS_PORT = int(os.getenv("SNAPSHOT_WS_PORT", 8080))

async def handle_snapshot_request(websocket, path):
    """Handle snapshot requests from server via WebSocket."""
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                snapshot_type = data.get("type", "all")  # "agent", "all", "process", or "all"
                target_pid = data.get("pid")
                
                print(f"[SNAPSHOT] Received request: {snapshot_type}")
                
                results = {}
                
                if snapshot_type in ["agent", "all"]:
                    # Snapshot agent process
                    agent_pid = os.getpid()
                    results["agent"] = {
                        "pid": agent_pid,
                        "memory": snapshot.take_memory_snapshot(agent_pid),
                        "lsof": snapshot.collect_lsof(agent_pid)
                    }
                
                if snapshot_type in ["all", "all_processes"]:
                    # Snapshot all processes (lsof)
                    results["all_processes"] = {
                        "lsof": snapshot.collect_lsof()
                    }
                
                if snapshot_type == "process" and target_pid:
                    # Snapshot specific process
                    results["target_process"] = {
                        "pid": target_pid,
                        "memory": snapshot.take_memory_snapshot(target_pid),
                        "lsof": snapshot.collect_lsof(target_pid)
                    }
                
                # Send results back
                await websocket.send(json.dumps({
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "results": results
                }))
                
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "status": "error",
                    "message": "Invalid JSON"
                }))
            except Exception as e:
                await websocket.send(json.dumps({
                    "status": "error",
                    "message": str(e)
                }))
    except websockets.exceptions.ConnectionClosed:
        print("[SNAPSHOT] WebSocket connection closed")

async def start_snapshot_server():
    """Start WebSocket server for snapshot requests."""
    server = await websockets.serve(handle_snapshot_request, "0.0.0.0", SNAPSHOT_WS_PORT)
    print(f"[SNAPSHOT] WebSocket server started on port {SNAPSHOT_WS_PORT}")
    return server

def main():
    print(f"Starting agent {AGENT_ID}, reporting to {SERVER_URL} every {INTERVAL}s using {SEND_MODE.upper()}...")
    print(f"[SNAPSHOT] WebSocket server will start on port {SNAPSHOT_WS_PORT}")
    
    observer = None
    
    # Start WebSocket server in background
    async def run_agent_with_websocket():
        # Start snapshot WebSocket server
        snapshot_server = await start_snapshot_server()
        
        # Main agent loop
        while True:
            try:
                event = collect_all_data()
                is_anomaly, anomaly_score = detect_anomaly(event)
                if is_anomaly:
                    print(f"[ALERT] Anomaly detected! Score: {anomaly_score}")
                    # 1. Snapshot agent process
                    agent_pid = os.getpid()
                    print(f"[SNAPSHOT] Agent process PID: {agent_pid}")
                    print(snapshot.take_memory_snapshot(agent_pid))
                    print(snapshot.collect_lsof(agent_pid))
                    # 2. Snapshot all processes (lsof)
                    print("[SNAPSHOT] All processes (lsof)")
                    print(snapshot.collect_lsof())
                    # 3. Snapshot most suspicious process (if available)
                    processes = event.get("process", {}).get("processes", [])
                    if processes:
                        # Example: pick process with highest memory_percent or cpu_percent if available
                        suspicious_proc = max(processes, key=lambda p: p.get("memory_percent", 0) + p.get("cpu_percent", 0))
                        pid = suspicious_proc.get("pid")
                        if pid:
                            print(f"[SNAPSHOT] Most suspicious process PID: {pid}")
                            print(snapshot.take_memory_snapshot(pid))
                            print(snapshot.collect_lsof(pid))
                # Send event as usual
                if SEND_MODE == "websocket":
                    await send_event_ws(event)
                else:
                    send_event_rest(event)
                await asyncio.sleep(INTERVAL)
            except Exception as e:
                print(f"[ERROR] Error in main loop: {e}")
                await asyncio.sleep(INTERVAL)
    
    try:
        asyncio.run(run_agent_with_websocket())
    except KeyboardInterrupt:
        if observer:
            observer.stop()
            observer.join()
        print("Agent stopped.")

if __name__ == "__main__":
    main() 