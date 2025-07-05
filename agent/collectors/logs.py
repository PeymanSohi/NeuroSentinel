import os
import glob
import subprocess
from datetime import datetime

LOG_DIRS = ["/var/log"]
LOG_EXTENSIONS = [".log", ".err", ".out", ".journal"]
MAX_LINES = 200  # Number of lines to collect per log file


def collect_journalctl_logs(lines=200):
    """
    Collect the last N lines from systemd journal (if available).
    """
    try:
        output = subprocess.check_output([
            'journalctl', '-n', str(lines), '--no-pager', '--output', 'short-iso'
        ], text=True)
        return {"journalctl": output}
    except Exception as e:
        return {"journalctl_error": str(e)}


def collect_log_files(log_dirs=LOG_DIRS, extensions=LOG_EXTENSIONS, max_lines=MAX_LINES):
    """
    Collect the last N lines from all log files in specified directories.
    """
    logs = {}
    for log_dir in log_dirs:
        for ext in extensions:
            pattern = os.path.join(log_dir, f"*{ext}")
            for log_file in glob.glob(pattern):
                try:
                    with open(log_file, 'r', errors='ignore') as f:
                        lines = f.readlines()[-max_lines:]
                        logs[log_file] = ''.join(lines)
                except Exception as e:
                    logs[log_file] = f"error: {e}"
    return logs


def collect_service_logs(services=None, lines=100):
    """
    Collect logs for specific services using journalctl (if available).
    """
    if services is None:
        services = ["sshd", "nginx", "docker", "postgresql", "redis"]
    service_logs = {}
    for svc in services:
        try:
            output = subprocess.check_output([
                'journalctl', '-u', svc, '-n', str(lines), '--no-pager', '--output', 'short-iso'
            ], text=True)
            service_logs[svc] = output
        except Exception as e:
            service_logs[svc] = f"error: {e}"
    return service_logs


def collect_system_logs():
    """
    Collect system logs: journalctl, /var/log/* files, and key service logs.
    Returns a dict.
    """
    result = {"timestamp": datetime.utcnow().isoformat()}
    try:
        result.update(collect_journalctl_logs())
    except Exception as e:
        result["journalctl_error"] = str(e)
    
    try:
        result["log_files"] = collect_log_files()
    except Exception as e:
        result["log_files_error"] = str(e)
    
    try:
        result["service_logs"] = collect_service_logs()
    except Exception as e:
        result["service_logs_error"] = str(e)
    
    return result


def collect_log_info():
    """
    Collect log file information and recent entries.
    Returns a dict.
    """
    try:
        # Check if we're monitoring host system
        host_root = os.getenv('HOST_ROOT', '/')
        monitoring_host = host_root != '/'
        
        log_files = []
        log_entries = []
        
        # Common log file paths
        log_paths = [
            '/var/log/auth.log',
            '/var/log/syslog',
            '/var/log/messages',
            '/var/log/secure',
            '/var/log/kern.log',
            '/var/log/dmesg'
        ]
        
        # Adjust paths for host monitoring
        if monitoring_host:
            log_paths = [os.path.join(host_root, path.lstrip('/')) for path in log_paths]
        
        for log_path in log_paths:
            if os.path.exists(log_path):
                try:
                    # Get file info
                    stat = os.stat(log_path)
                    log_files.append({
                        "path": log_path,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "accessible": True
                    })
                    
                    # Read last few lines
                    try:
                        with open(log_path, 'r', errors='ignore') as f:
                            lines = f.readlines()
                            recent_lines = lines[-10:] if len(lines) > 10 else lines
                            log_entries.extend([{
                                "file": log_path,
                                "line": line.strip(),
                                "timestamp": datetime.utcnow().isoformat()
                            } for line in recent_lines if line.strip()])
                    except Exception as e:
                        log_entries.append({
                            "file": log_path,
                            "error": f"Could not read file: {str(e)}",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        
                except Exception as e:
                    log_files.append({
                        "path": log_path,
                        "error": str(e),
                        "accessible": False
                    })
            else:
                log_files.append({
                    "path": log_path,
                    "accessible": False,
                    "error": "File not found"
                })
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "log_files": log_files,
            "recent_entries": log_entries[:50],  # Limit to 50 entries
            "monitoring_host": monitoring_host,
            "host_root": host_root
        }
    except Exception as e:
        return {"error": str(e)}
