import platform
import psutil
import time
import os
from datetime import datetime

def collect_system_metrics():
    """
    Collect system metrics: CPU, memory, disk, load average, uptime, OS/kernel info, time drift.
    Returns a dict.
    """
    try:
        # Check if we're monitoring host system
        host_root = os.getenv('HOST_ROOT', '/')
        monitoring_host = host_root != '/'
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_count": psutil.cpu_count(),
            "load_avg": psutil.getloadavg() if hasattr(psutil, "getloadavg") else None,
            "mem_total": psutil.virtual_memory().total,
            "mem_used": psutil.virtual_memory().used,
            "mem_percent": psutil.virtual_memory().percent,
            "swap_total": psutil.swap_memory().total,
            "swap_used": psutil.swap_memory().used,
            "disk_total": psutil.disk_usage(host_root).total,
            "disk_used": psutil.disk_usage(host_root).used,
            "disk_percent": psutil.disk_usage(host_root).percent,
            "uptime": time.time() - psutil.boot_time(),
            "os": platform.system(),
            "os_version": platform.version(),
            "platform": platform.platform(),
            "kernel": platform.release(),
            "hostname": platform.node(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "time_utc": datetime.utcnow().isoformat(),
            "monitoring_host": monitoring_host,
            "host_root": host_root,
        }
    except Exception as e:
        return {"error": str(e)}