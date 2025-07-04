import os
import requests
import glob
import subprocess
from datetime import datetime

MAX_LINES = 200

# API keys from environment variables
VT_API_KEY = os.getenv("VT_API_KEY")
OTX_API_KEY = os.getenv("OTX_API_KEY")
ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")


def vt_file_hash(hash):
    if not VT_API_KEY:
        return {"error": "VirusTotal API key not set"}
    try:
        url = f"https://www.virustotal.com/api/v3/files/{hash}"
        headers = {"x-apikey": VT_API_KEY}
        r = requests.get(url, headers=headers, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def otx_ip(ip):
    if not OTX_API_KEY:
        return {"error": "OTX API key not set"}
    try:
        url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"
        headers = {"X-OTX-API-KEY": OTX_API_KEY}
        r = requests.get(url, headers=headers, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def abuseipdb_ip(ip):
    if not ABUSEIPDB_API_KEY:
        return {"error": "AbuseIPDB API key not set"}
    try:
        url = f"https://api.abuseipdb.com/api/v2/check"
        headers = {"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"}
        params = {"ipAddress": ip, "maxAgeInDays": 90}
        r = requests.get(url, headers=headers, params=params, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def shodan_ip(ip):
    if not SHODAN_API_KEY:
        return {"error": "Shodan API key not set"}
    try:
        url = f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_API_KEY}"
        r = requests.get(url, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def collect_threat_intel_logs(log_dirs=["/var/log"], max_lines=MAX_LINES):
    logs = {}
    keywords = ["threat", "intel", "virustotal", "otx", "abuseipdb", "shodan"]
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

def collect_threat_intel_journalctl(lines=200):
    try:
        output = subprocess.check_output([
            'journalctl', '-g', 'threat', '-n', str(lines), '--no-pager', '--output', 'short-iso'
        ], text=True)
        return output
    except Exception as e:
        return f"error: {e}"

def enrich_with_threat_intel(data):
    """
    Enrich IPs/domains/files with threat intelligence lookups (VirusTotal, OTX, AbuseIPDB, Shodan).
    Collect logs related to threat intel from /var/log and journalctl.
    Returns a dict.
    """
    result = {"timestamp": datetime.utcnow().isoformat(), "intel": {}, "logs": {}, "journalctl": ""}
    # Example: data = {"ips": [...], "hashes": [...], "domains": [...]}
    ips = data.get("ips", [])
    hashes = data.get("hashes", [])
    # IP enrichment
    for ip in ips:
        result["intel"][ip] = {
            "otx": otx_ip(ip),
            "abuseipdb": abuseipdb_ip(ip),
            "shodan": shodan_ip(ip)
        }
    # File hash enrichment
    for h in hashes:
        result["intel"][h] = {"virustotal": vt_file_hash(h)}
    # Logs
    result["logs"] = collect_threat_intel_logs()
    result["journalctl"] = collect_threat_intel_journalctl()
    return result
