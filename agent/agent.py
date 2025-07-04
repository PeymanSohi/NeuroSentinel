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

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

SERVER_URL = os.getenv("SERVER_URL", "http://server:8000/events")
AGENT_ID = socket.gethostname()
INTERVAL = int(os.getenv("AGENT_INTERVAL", 10))  # seconds

# --- File System Monitoring (Watchdog) ---
file_events = []

class FileChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        file_events.append({
            "event_type": event.event_type,
            "src_path": event.src_path,
            "is_directory": event.is_directory,
            "timestamp": datetime.utcnow().isoformat()
        })

def start_file_monitor(path="/etc"):
    if not WATCHDOG_AVAILABLE:
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

def collect_event():
    """
    Collect advanced system, process, network, file, user, and environment data.
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        users, groups = get_users_groups()
        event = {
            "agent_id": AGENT_ID,
            "event_type": "advanced_system_stats",
            "timestamp": time.time(),
            "data": {
                "system": {
                    "cpu_percent": cpu_percent,
                    "mem_total": mem.total,
                    "mem_used": mem.used,
                    "mem_percent": mem.percent,
                    "disk_total": disk.total,
                    "disk_used": disk.used,
                    "disk_percent": disk.percent,
                    "uptime": time.time() - psutil.boot_time(),
                    "os_info": get_os_info(),
                },
                "processes": get_processes(),
                "network": {
                    "connections": get_network_connections(),
                    "net_bytes_sent": net.bytes_sent,
                    "net_bytes_recv": net.bytes_recv,
                },
                "users": {
                    "logged_in": get_logged_in_users(),
                    "all_users": users,
                    "groups": groups,
                },
                "cron_jobs": get_cron_jobs(),
                "services": get_services(),
                "firewall_rules": get_firewall_rules(),
                "file_events": list(file_events),
            }
        }
        # Clear file events after reporting
        file_events.clear()
        return event
    except Exception as e:
        return {"agent_id": AGENT_ID, "event_type": "error", "timestamp": time.time(), "data": {"error": str(e)}}

def report_event(event):
    try:
        response = requests.post(SERVER_URL, json=event, timeout=10)
        print(f"[INFO] Event reported: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[ERROR] Failed to report event: {e}")

def main():
    print(f"Starting advanced agent {AGENT_ID}, reporting to {SERVER_URL} every {INTERVAL}s...")
    observer = start_file_monitor("/etc") if WATCHDOG_AVAILABLE else None
    try:
        while True:
            event = collect_event()
            report_event(event)
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        if observer:
            observer.stop()
            observer.join()
        print("Agent stopped.")

if __name__ == "__main__":
    main() 