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
from collectors import system, process, network, file, user, logs, persistence, firewall, container, cloud, threat_intel, integrity, security_tools

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

def main():
    print(f"Starting agent {AGENT_ID}, reporting to {SERVER_URL} every {INTERVAL}s using {SEND_MODE.upper()}...")
    # Disable file monitoring for now to avoid issues
    observer = None
    try:
        while True:
            event = collect_all_data()
            if SEND_MODE == "websocket":
                asyncio.run(send_event_ws(event))
            else:
                send_event_rest(event)
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        if observer:
            observer.stop()
            observer.join()
        print("Agent stopped.")

if __name__ == "__main__":
    main() 