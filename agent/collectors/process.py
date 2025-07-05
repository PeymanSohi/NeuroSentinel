import psutil
import os
import hashlib
from datetime import datetime

def hash_file(path):
    try:
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None

def collect_process_info():
    """
    Collect process list, memory maps, loaded modules, hashes, suspicious behaviors.
    Returns a dict.
    """
    processes = []
    try:
        # Check if we're monitoring host system
        host_root = os.getenv('HOST_ROOT', '/')
        monitoring_host = host_root != '/'
        
        for p in psutil.process_iter(['pid', 'name', 'username', 'cmdline', 'ppid', 'create_time', 'exe']):
            try:
                info = p.info
                exe = info.get('exe')
                
                # Adjust executable path for host monitoring
                if monitoring_host and exe and exe.startswith('/'):
                    # If monitoring host, executable paths should be relative to host root
                    # but psutil will already show the correct paths when using host network mode
                    pass
                
                info['sha256'] = hash_file(exe) if exe and os.path.isfile(exe) else None
                # Optionally, add open files, memory maps, loaded modules
                info['open_files'] = [f.path for f in p.open_files()] if hasattr(p, 'open_files') else []
                info['memory_maps'] = [m.path for m in p.memory_maps()] if hasattr(p, 'memory_maps') else []
                processes.append(info)
            except Exception:
                continue
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "processes": processes,
            "monitoring_host": monitoring_host,
            "host_root": host_root,
        }
    except Exception as e:
        return {"error": str(e)}