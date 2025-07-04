import os
import glob
import subprocess
from datetime import datetime

MAX_LINES = 200


def collect_cron_jobs():
    try:
        output = subprocess.check_output(['crontab', '-l'], text=True)
        return output
    except Exception as e:
        return f"error: {e}"

def collect_systemd_services():
    try:
        output = subprocess.check_output(['systemctl', 'list-units', '--type=service', '--all', '--no-pager'], text=True)
        return output
    except Exception as e:
        return f"error: {e}"

def collect_enabled_services():
    try:
        output = subprocess.check_output(['systemctl', 'list-unit-files', '--type=service', '--state=enabled', '--no-pager'], text=True)
        return output
    except Exception as e:
        return f"error: {e}"

def collect_init_scripts():
    scripts = []
    for path in ["/etc/init.d", "/etc/rc.d", "/etc/rc.local"]:
        if os.path.isdir(path):
            for fname in os.listdir(path):
                scripts.append(os.path.join(path, fname))
        elif os.path.isfile(path):
            scripts.append(path)
    return scripts

def collect_at_jobs():
    try:
        output = subprocess.check_output(['atq'], text=True)
        return output
    except Exception as e:
        return f"error: {e}"

def collect_persistence_logs(log_dirs=["/var/log"], max_lines=MAX_LINES):
    logs = {}
    keywords = ["cron", "systemd", "init", "rc.local", "at", "autorun", "service"]
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

def collect_persistence_journalctl(lines=200):
    try:
        output = subprocess.check_output([
            'journalctl', '-g', 'cron', '-n', str(lines), '--no-pager', '--output', 'short-iso'
        ], text=True)
        return output
    except Exception as e:
        return f"error: {e}"

def collect_persistence_info():
    """
    Collect cron jobs, systemd/init scripts, autoruns, scheduled tasks, running/enabled services, and related logs.
    Returns a dict.
    """
    result = {"timestamp": datetime.utcnow().isoformat()}
    result["cron_jobs"] = collect_cron_jobs()
    result["systemd_services"] = collect_systemd_services()
    result["enabled_services"] = collect_enabled_services()
    result["init_scripts"] = collect_init_scripts()
    result["at_jobs"] = collect_at_jobs()
    result["persistence_logs"] = collect_persistence_logs()
    result["persistence_journalctl"] = collect_persistence_journalctl()
    return result
