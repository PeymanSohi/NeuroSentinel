#!/usr/bin/env python3
"""
Test script to verify what system NeuroSentinel agent is monitoring.
Run this to check if the agent is reading from host or container.
"""

import os
import psutil
import platform
from datetime import datetime

def test_monitoring_scope():
    """Test what system the agent is monitoring."""
    
    print("🔍 NeuroSentinel Monitoring Scope Test")
    print("=" * 50)
    
    # Check environment variables
    host_root = os.getenv('HOST_ROOT', '/')
    print(f"📁 HOST_ROOT: {host_root}")
    print(f"🏠 Monitoring Host: {host_root != '/'}")
    
    # System information
    print(f"\n💻 System Info:")
    print(f"  Hostname: {platform.node()}")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Architecture: {platform.machine()}")
    
    # Disk usage
    try:
        disk = psutil.disk_usage(host_root)
        print(f"\n💾 Disk Usage ({host_root}):")
        print(f"  Total: {disk.total / (1024**3):.2f} GB")
        print(f"  Used: {disk.used / (1024**3):.2f} GB")
        print(f"  Free: {disk.free / (1024**3):.2f} GB")
        print(f"  Usage: {disk.percent:.1f}%")
    except Exception as e:
        print(f"❌ Error reading disk: {e}")
    
    # Process count
    try:
        process_count = len(list(psutil.process_iter()))
        print(f"\n🔄 Process Count: {process_count}")
    except Exception as e:
        print(f"❌ Error counting processes: {e}")
    
    # Memory info
    try:
        mem = psutil.virtual_memory()
        print(f"\n🧠 Memory:")
        print(f"  Total: {mem.total / (1024**3):.2f} GB")
        print(f"  Available: {mem.available / (1024**3):.2f} GB")
        print(f"  Usage: {mem.percent:.1f}%")
    except Exception as e:
        print(f"❌ Error reading memory: {e}")
    
    # Check if we can access host-specific paths
    print(f"\n🔍 Host System Access Test:")
    host_paths = ['/etc/passwd', '/var/log', '/proc', '/sys']
    for path in host_paths:
        if os.path.exists(path):
            print(f"  ✅ {path} - Accessible")
        else:
            print(f"  ❌ {path} - Not accessible")
    
    # Check container vs host indicators
    print(f"\n🐳 Container vs Host Indicators:")
    
    # Check for Docker-specific files
    docker_indicators = ['/.dockerenv', '/proc/1/cgroup']
    for indicator in docker_indicators:
        if os.path.exists(indicator):
            print(f"  🐳 {indicator} - Found (likely in container)")
        else:
            print(f"  🏠 {indicator} - Not found (likely on host)")
    
    # Check cgroup info
    try:
        with open('/proc/1/cgroup', 'r') as f:
            cgroup_content = f.read()
            if 'docker' in cgroup_content or 'kubepods' in cgroup_content:
                print(f"  🐳 Cgroup shows container environment")
            else:
                print(f"  🏠 Cgroup shows host environment")
    except Exception as e:
        print(f"  ❓ Could not read cgroup: {e}")
    
    print(f"\n📊 Summary:")
    if host_root != '/':
        print(f"  ✅ Agent configured to monitor HOST system")
    else:
        print(f"  🐳 Agent configured to monitor CONTAINER system")
    
    print(f"\n💡 To monitor host system, ensure docker-compose.yml has:")
    print(f"   - privileged: true")
    print(f"   - network_mode: host")
    print(f"   - volumes mounted to host directories")

if __name__ == "__main__":
    test_monitoring_scope() 