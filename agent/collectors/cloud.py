import os
import requests
from datetime import datetime

METADATA_TIMEOUT = 2  # seconds

CLOUD_PROVIDERS = {
    "aws": {
        "url": "http://169.254.169.254/latest/meta-data/",
        "fields": [
            ("instance_id", "instance-id"),
            ("instance_type", "instance-type"),
            ("ami_id", "ami-id"),
            ("region", "placement/region"),
            ("availability_zone", "placement/availability-zone"),
            ("public_ipv4", "public-ipv4"),
            ("local_ipv4", "local-ipv4"),
        ]
    },
    "gcp": {
        "url": "http://169.254.169.254/computeMetadata/v1/instance/",
        "headers": {"Metadata-Flavor": "Google"},
        "fields": [
            ("instance_id", "id"),
            ("machine_type", "machine-type"),
            ("zone", "zone"),
            ("hostname", "hostname"),
            ("tags", "tags"),
            ("public_ip", "network-interfaces/0/access-configs/0/external-ip"),
            ("internal_ip", "network-interfaces/0/ip"),
        ]
    },
    "azure": {
        "url": "http://169.254.169.254/metadata/instance?api-version=2021-02-01",
        "headers": {"Metadata": "true"},
        "json": True
    },
    "do": {
        "url": "http://169.254.169.254/metadata/v1/",
        "fields": [
            ("droplet_id", "id"),
            ("hostname", "hostname"),
            ("region", "region"),
            ("public_ip", "interfaces/public/0/ipv4/address"),
            ("private_ip", "interfaces/private/0/ipv4/address"),
        ]
    }
}

def detect_cloud_provider():
    for provider, meta in CLOUD_PROVIDERS.items():
        try:
            r = requests.get(meta["url"], headers=meta.get("headers", {}), timeout=METADATA_TIMEOUT)
            if r.status_code == 200:
                return provider
        except Exception:
            continue
    return None

def collect_cloud_info():
    """
    Detect cloud provider and collect instance metadata (ID, type, region, IP, etc).
    Returns a dict.
    """
    result = {"timestamp": datetime.utcnow().isoformat(), "cloud": {}}
    provider = detect_cloud_provider()
    result["cloud"]["provider"] = provider
    if not provider:
        result["cloud"]["detected"] = False
        return result
    meta = CLOUD_PROVIDERS[provider]
    try:
        if provider == "azure":
            r = requests.get(meta["url"], headers=meta["headers"], timeout=METADATA_TIMEOUT)
            if r.status_code == 200:
                data = r.json()
                result["cloud"].update(data)
        else:
            for key, path in meta.get("fields", []):
                try:
                    url = meta["url"] + path
                    r = requests.get(url, headers=meta.get("headers", {}), timeout=METADATA_TIMEOUT)
                    if r.status_code == 200:
                        result["cloud"][key] = r.text.strip()
                except Exception:
                    result["cloud"][key] = None
    except Exception as e:
        result["cloud"]["error"] = str(e)
    return result
