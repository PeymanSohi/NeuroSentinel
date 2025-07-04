import os
import hashlib
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

try:
    import yara
    YARA_AVAILABLE = True
except ImportError:
    YARA_AVAILABLE = False

SENSITIVE_DIRS = ["/etc", "/var", "/home", "/tmp", "/usr/bin", "/usr/sbin"]
FILE_EVENTS = []

class FileChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        FILE_EVENTS.append({
            "event_type": event.event_type,
            "src_path": event.src_path,
            "is_directory": event.is_directory,
            "timestamp": datetime.utcnow().isoformat()
        })

def start_file_monitor(paths=SENSITIVE_DIRS):
    if not WATCHDOG_AVAILABLE:
        return None
    observer = Observer()
    handler = FileChangeHandler()
    for path in paths:
        if os.path.exists(path):
            observer.schedule(handler, path, recursive=True)
    observer.start()
    return observer

def hash_file(path):
    try:
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None

def scan_with_yara(path, rules=None):
    if not YARA_AVAILABLE or not rules:
        return None
    try:
        matches = rules.match(path)
        return [str(m) for m in matches]
    except Exception:
        return None

def find_suspicious_files(root_dirs=SENSITIVE_DIRS):
    suspicious = []
    for root in root_dirs:
        for dirpath, dirnames, filenames in os.walk(root):
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                try:
                    # Example: suspicious if hidden, temp, or script in startup
                    if fname.startswith('.') or fname.endswith(('.tmp', '.bak', '.sh', '.py', '.exe')):
                        suspicious.append(fpath)
                except Exception:
                    continue
    return suspicious

def collect_file_events(yara_rules_path=None):
    """
    Collect file events, hashes, YARA scan results, suspicious files.
    Returns a dict.
    """
    result = {"timestamp": datetime.utcnow().isoformat()}
    # File events (since last call)
    result["file_events"] = list(FILE_EVENTS)
    FILE_EVENTS.clear()
    # Hashes of critical files
    critical_files = ["/etc/passwd", "/etc/shadow", "/etc/hosts", "/bin/bash"]
    result["file_hashes"] = {f: hash_file(f) for f in critical_files if os.path.exists(f)}
    # YARA scan
    if YARA_AVAILABLE and yara_rules_path and os.path.exists(yara_rules_path):
        try:
            rules = yara.compile(filepath=yara_rules_path)
            yara_results = {}
            for root in SENSITIVE_DIRS:
                for dirpath, dirnames, filenames in os.walk(root):
                    for fname in filenames:
                        fpath = os.path.join(dirpath, fname)
                        matches = scan_with_yara(fpath, rules)
                        if matches:
                            yara_results[fpath] = matches
            result["yara_results"] = yara_results
        except Exception as e:
            result["yara_error"] = str(e)
    else:
        result["yara_results"] = {}
    # Suspicious files
    result["suspicious_files"] = find_suspicious_files()
    return result

    