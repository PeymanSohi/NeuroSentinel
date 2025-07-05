import os
import subprocess
from datetime import datetime

SNAPSHOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../snapshots'))
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

def take_memory_snapshot(pid):
    """Take a memory dump of the given process using gcore."""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    core_path = os.path.join(SNAPSHOT_DIR, f'gcore_{pid}_{timestamp}.core')
    try:
        subprocess.check_call(['gcore', '-o', core_path, str(pid)])
        return core_path
    except Exception as e:
        return f'Error taking memory snapshot: {e}'

def collect_lsof(pid=None):
    """Collect open files for the given PID (or all if None) using lsof."""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    if pid:
        lsof_path = os.path.join(SNAPSHOT_DIR, f'lsof_{pid}_{timestamp}.txt')
        cmd = ['lsof', '-p', str(pid)]
    else:
        lsof_path = os.path.join(SNAPSHOT_DIR, f'lsof_all_{timestamp}.txt')
        cmd = ['lsof']
    try:
        with open(lsof_path, 'w') as f:
            subprocess.check_call(cmd, stdout=f, stderr=subprocess.STDOUT)
        return lsof_path
    except Exception as e:
        return f'Error collecting lsof: {e}' 