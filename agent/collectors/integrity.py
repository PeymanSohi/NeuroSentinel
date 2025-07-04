import os
import hashlib
import glob
import subprocess
from datetime import datetime

MAX_LINES = 200
AGENT_PATHS = [
    __file__,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agent.py")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "collectors")),
]

# Optionally, store known-good hashes for comparison
KNOWN_GOOD_HASHES = {
    # "filename": "sha256hash",
}

def hash_file(path):
    try:
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        return f"error: {e}"

def hash_directory(directory):
    hashes = {}
    for root, dirs, files in os.walk(directory):
        for fname in files:
            fpath = os.path.join(root, fname)
            hashes[fpath] = hash_file(fpath)
    return hashes

def check_agent_integrity():
    """
    Hash agent binary/scripts, check for tampering, compare to known-good hashes, collect integrity logs.
    Returns a dict.
    """
    result = {"timestamp": datetime.utcnow().isoformat(), "hashes": {}, "tamper": {}, "logs": {}, "journalctl": ""}
    # Hash agent.py and all collectors
    for path in AGENT_PATHS:
        if os.path.isfile(path):
            result["hashes"][path] = hash_file(path)
        elif os.path.isdir(path):
            result["hashes"].update(hash_directory(path))
    # Compare to known-good hashes
    for fname, known_hash in KNOWN_GOOD_HASHES.items():
        actual_hash = result["hashes"].get(fname)
        if actual_hash and actual_hash != known_hash:
            result["tamper"][fname] = {"expected": known_hash, "actual": actual_hash}
    # Collect logs
    result["logs"] = collect_integrity_logs()
    result["journalctl"] = collect_integrity_journalctl()
    return result

def collect_integrity_logs(log_dirs=["/var/log"], max_lines=MAX_LINES):
    logs = {}
    keywords = ["integrity", "tamper", "hash", "checksum", "tripwire"]
    for log_dir in log_dirs:
        for ext in [".log", ".err", ".out", ".journal"]:
            pattern = os.path.join(log_dir, f"*{ext}")
            for log_file in glob.glob(pattern):
                if any(kw in log_file.lower() for kw in keywords):
                    try:
                        with open(log_file, 'r', errors='ignore') as f:
                            lines = f.readlines()[-max_lines:]
                            logs[log_file] = ''.join(lines)
                    except Exception as e:
                        logs[log_file] = f"error: {e}"
    return logs

def collect_integrity_journalctl(lines=200):
    try:
        output = subprocess.check_output([
            'journalctl', '-g', 'integrity', '-n', str(lines), '--no-pager', '--output', 'short-iso'
        ], text=True)
        return output
    except Exception as e:
        return f"error: {e}"
