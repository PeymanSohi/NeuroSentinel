import os
import subprocess
from datetime import datetime
import glob

FIREWALL_LOG_EXTENSIONS = [".log", ".err", ".out", ".journal"]
FIREWALL_LOG_KEYWORDS = ["firewall", "iptables", "nft", "ufw", "firewalld"]
MAX_LINES = 200


def collect_iptables_rules():
    try:
        output = subprocess.check_output(['iptables', '-S'], text=True)
        return output
    except Exception as e:
        return f"error: {e}"

def collect_nftables_rules():
    try:
        output = subprocess.check_output(['nft', 'list', 'ruleset'], text=True)
        return output
    except Exception as e:
        return f"error: {e}"

def collect_ufw_status():
    try:
        output = subprocess.check_output(['ufw', 'status', 'verbose'], text=True)
        return output
    except Exception as e:
        return f"error: {e}"

def collect_firewalld_status():
    try:
        output = subprocess.check_output(['firewall-cmd', '--list-all'], text=True)
        return output
    except Exception as e:
        return f"error: {e}"

def collect_firewall_logs(log_dirs=["/var/log"], extensions=FIREWALL_LOG_EXTENSIONS, max_lines=MAX_LINES):
    logs = {}
    for log_dir in log_dirs:
        for ext in extensions:
            pattern = os.path.join(log_dir, f"*{ext}")
            for log_file in glob.glob(pattern):
                if any(kw in log_file.lower() for kw in FIREWALL_LOG_KEYWORDS):
                    try:
                        with open(log_file, 'r', errors='ignore') as f:
                            lines = f.readlines()[-max_lines:]
                            logs[log_file] = ''.join(lines)
                    except Exception as e:
                        logs[log_file] = f"error: {e}"
    return logs

def collect_firewall_journalctl(lines=200):
    try:
        output = subprocess.check_output([
            'journalctl', '-g', 'firewall', '-n', str(lines), '--no-pager', '--output', 'short-iso'
        ], text=True)
        return output
    except Exception as e:
        return f"error: {e}"

def collect_firewall_rules():
    """
    Collect iptables, nftables, ufw, firewalld rules, and firewall-related logs.
    Returns a dict.
    """
    result = {"timestamp": datetime.utcnow().isoformat()}
    result["iptables_rules"] = collect_iptables_rules()
    result["nftables_rules"] = collect_nftables_rules()
    result["ufw_status"] = collect_ufw_status()
    result["firewalld_status"] = collect_firewalld_status()
    result["firewall_logs"] = collect_firewall_logs()
    result["firewall_journalctl"] = collect_firewall_journalctl()
    return result
