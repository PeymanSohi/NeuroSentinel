import os
import pwd
import grp
import psutil
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
    Collect user information, logged in users, groups, sudoers, cron jobs.
    Returns a dict.
    """
    try:
        # Check if we're monitoring host system
        host_root = os.getenv('HOST_ROOT', '/')
        monitoring_host = host_root != '/'
        
        # Get logged in users
        logged_users = []
        try:
            for user in psutil.users():
                logged_users.append({
                    "name": user.name,
                    "terminal": user.terminal,
                    "host": user.host,
                    "started": datetime.fromtimestamp(user.started).isoformat(),
                    "pid": user.pid
                })
        except Exception as e:
            logged_users = [{"error": f"Could not get logged users: {str(e)}"}]
        
        # Get all users
        all_users = []
        try:
            for user in pwd.getpwall():
                all_users.append({
                    "name": user.pw_name,
                    "uid": user.pw_uid,
                    "gid": user.pw_gid,
                    "home": user.pw_dir,
                    "shell": user.pw_shell
                })
        except Exception as e:
            all_users = [{"error": f"Could not get users: {str(e)}"}]
        
        # Get all groups
        all_groups = []
        try:
            for group in grp.getgrall():
                all_groups.append({
                    "name": group.gr_name,
                    "gid": group.gr_gid,
                    "members": group.gr_mem
                })
        except Exception as e:
            all_groups = [{"error": f"Could not get groups: {str(e)}"}]
        
        # Get sudoers file info
        sudoers_info = {}
        sudoers_path = '/etc/sudoers'
        if monitoring_host:
            sudoers_path = os.path.join(host_root, 'etc/sudoers')
        
        if os.path.exists(sudoers_path):
            try:
                stat = os.stat(sudoers_path)
                sudoers_info = {
                    "exists": True,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "accessible": True
                }
            except Exception as e:
                sudoers_info = {
                    "exists": True,
                    "error": str(e),
                    "accessible": False
                }
        else:
            sudoers_info = {
                "exists": False,
                "accessible": False
            }
        
        # Get cron jobs
        cron_jobs = []
        try:
            # Check system crontab
            cron_paths = ['/etc/crontab']
            if monitoring_host:
                cron_paths = [os.path.join(host_root, 'etc/crontab')]
            
            for cron_path in cron_paths:
                if os.path.exists(cron_path):
                    try:
                        with open(cron_path, 'r') as f:
                            lines = f.readlines()
                            for line in lines:
                                if line.strip() and not line.startswith('#'):
                                    cron_jobs.append({
                                        "file": cron_path,
                                        "line": line.strip()
                                    })
                    except Exception as e:
                        cron_jobs.append({
                            "file": cron_path,
                            "error": f"Could not read: {str(e)}"
                        })
        except Exception as e:
            cron_jobs = [{"error": f"Could not get cron jobs: {str(e)}"}]
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "logged_users": logged_users,
            "all_users": all_users,
            "all_groups": all_groups,
            "sudoers": sudoers_info,
            "cron_jobs": cron_jobs,
            "monitoring_host": monitoring_host,
            "host_root": host_root
        }
    except Exception as e:
        return {"error": str(e)}
