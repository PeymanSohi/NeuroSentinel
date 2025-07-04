import os
import glob
import subprocess
from datetime import datetime

SECURITY_TOOLS = [
    "clamav", "crowdstrike", "sophos", "falcon", "defender", "chkrootkit", "rkhunter", "auditd", "selinux", "apparmor"
]
MAX_LINES = 200


def check_tool_status(tool):
    try:
        # Try systemctl first
        output = subprocess.check_output(["systemctl", "is-active", tool], text=True).strip()
        return output
    except Exception:
        # Try pgrep as fallback
        try:
            output = subprocess.check_output(["pgrep", "-fl", tool], text=True).strip()
            return "running" if output else "not running"
        except Exception as e:
            return f"error: {e}"


def collect_security_tool_logs(log_dirs=["/var/log"], max_lines=MAX_LINES):
    logs = {}
    for tool in SECURITY_TOOLS:
        for ext in [".log", ".err", ".out", ".journal"]:
            pattern = os.path.join(log_dirs[0], f"*{tool}*{ext}")
            for log_file in glob.glob(pattern):
                try:
                    with open(log_file, 'r', errors='ignore') as f:
                        lines = f.readlines()[-max_lines:]
                        logs[log_file] = ''.join(lines)
                except Exception as e:
                    logs[log_file] = f"error: {e}"
    return logs


def collect_security_tool_journalctl(tool, lines=100):
    try:
        output = subprocess.check_output([
            'journalctl', '-u', tool, '-n', str(lines), '--no-pager', '--output', 'short-iso'
        ], text=True)
        return output
    except Exception as e:
        return f"error: {e}"


def collect_security_tools_status():
    """
    Detect and report status of common antivirus, EDR, and security tools. Collect logs from /var/log and journalctl.
    Returns a dict.
    """
    result = {"timestamp": datetime.utcnow().isoformat(), "tools": {}, "logs": {}, "journalctl": {}}
    for tool in SECURITY_TOOLS:
        result["tools"][tool] = check_tool_status(tool)
        result["logs"].update(collect_security_tool_logs(["/var/log"], MAX_LINES))
        result["journalctl"][tool] = collect_security_tool_journalctl(tool)
    return result
