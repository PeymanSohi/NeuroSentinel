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
        for p in psutil.process_iter(['pid', 'name', 'username', 'cmdline', 'ppid', 'create_time', 'exe']):
            try:
                info = p.info
                exe = info.get('exe')
                info['sha256'] = hash_file(exe) if exe and os.path.isfile(exe) else None
                # Optionally, add open files, memory maps, loaded modules
                info['open_files'] = [f.path for f in p.open_files()] if hasattr(p, 'open_files') else []
                info['memory_maps'] = [m.path for m in p.memory_maps()] if hasattr(p, 'memory_maps') else []
                processes.append(info)
            except Exception:
                continue
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "processes": processes
        }
    except Exception as e:
        return {"error": str(e)}