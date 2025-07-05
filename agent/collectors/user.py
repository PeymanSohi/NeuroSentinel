import os
import pwd
import grp
import subprocess
import glob
from datetime import datetime

MAX_LINES = 200


def collect_logged_in_users():
    try:
        output = subprocess.check_output(['who'], text=True)
        return output
    except Exception as e:
        return f"error: {e}"

def collect_last_logins():
    try:
        output = subprocess.check_output(['last', '-n', '20'], text=True)
        return output
    except Exception as e:
        return f"error: {e}"

def collect_sudo_usage():
    try:
        if os.path.exists('/var/log/auth.log'):
            output = subprocess.check_output(['grep', 'sudo', '/var/log/auth.log'], text=True)
            return output
        else:
            return "auth.log not available"
    except Exception as e:
        return f"error: {e}"

def collect_ssh_sessions():
    try:
        if os.path.exists('/var/log/auth.log'):
            output = subprocess.check_output(['grep', 'sshd', '/var/log/auth.log'], text=True)
            return output
        else:
            return "auth.log not available"
    except Exception as e:
        return f"error: {e}"

def collect_user_group_changes():
    try:
        if os.path.exists('/var/log/auth.log'):
            output = subprocess.check_output(['grep', '-E', 'useradd|userdel|groupadd|groupdel', '/var/log/auth.log'], text=True)
            return output
        else:
            return "auth.log not available"
    except Exception as e:
        return f"error: {e}"

def collect_users_groups():
    try:
        users = [u.pw_name for u in pwd.getpwall()]
        groups = [g.gr_name for g in grp.getgrall()]
        return {"users": users, "groups": groups}
    except Exception as e:
        return {"error": str(e)}

def collect_user_logs(log_dirs=["/var/log"], max_lines=MAX_LINES):
    logs = {}
    keywords = ["auth", "secure", "sudo", "sshd", "user", "group", "login", "logout"]
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

def collect_user_journalctl(lines=200):
    try:
        output = subprocess.check_output([
            'journalctl', '-g', 'user', '-n', str(lines), '--no-pager', '--output', 'short-iso'
        ], text=True)
        return output
    except Exception as e:
        return f"error: {e}"

def collect_user_activity():
    """
    Collect logins, sudo, SSH, user/group changes, and related logs from /var/log and journalctl.
    Returns a dict.
    """
    result = {"timestamp": datetime.utcnow().isoformat()}
    result["logged_in_users"] = collect_logged_in_users()
    result["last_logins"] = collect_last_logins()
    result["sudo_usage"] = collect_sudo_usage()
    result["ssh_sessions"] = collect_ssh_sessions()
    result["user_group_changes"] = collect_user_group_changes()
    result["users_groups"] = collect_users_groups()
    result["user_logs"] = collect_user_logs()
    result["user_journalctl"] = collect_user_journalctl()
    return result
