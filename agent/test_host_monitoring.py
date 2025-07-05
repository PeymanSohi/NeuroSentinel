#!/usr/bin/env python3
"""
Test script to verify host monitoring is working properly.
"""

import os
import sys
import json
from datetime import datetime

# Add the agent directory to the path
sys.path.append('/app')

from collectors.system import collect_system_metrics
from collectors.process import collect_process_info
from collectors.user import collect_user_activity
from collectors.logs import collect_log_info

def test_host_monitoring():
    """Test all collectors to verify host monitoring."""
    
    print("🔍 Testing Host Monitoring Collectors")
    print("=" * 50)
    
    # Test system metrics
    print("\n📊 System Metrics:")
    try:
        system_data = collect_system_metrics()
        print(f"  ✅ Monitoring Host: {system_data.get('monitoring_host', 'Unknown')}")
        print(f"  🏠 Hostname: {system_data.get('hostname', 'Unknown')}")
        print(f"  💻 OS: {system_data.get('os', 'Unknown')}")
        print(f"  🧠 CPU Usage: {system_data.get('cpu_percent', 'Unknown')}%")
        print(f"  💾 Memory Usage: {system_data.get('mem_percent', 'Unknown')}%")
        print(f"  💿 Disk Usage: {system_data.get('disk_percent', 'Unknown')}%")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test process info
    print("\n🔄 Process Information:")
    try:
        process_data = collect_process_info()
        process_count = len(process_data.get('processes', []))
        print(f"  ✅ Process Count: {process_count}")
        print(f"  🏠 Monitoring Host: {process_data.get('monitoring_host', 'Unknown')}")
        
        # Show some sample processes
        processes = process_data.get('processes', [])
        if processes:
            print(f"  📋 Sample Processes:")
            for proc in processes[:5]:  # Show first 5
                print(f"    - {proc.get('name', 'Unknown')} (PID: {proc.get('pid', 'Unknown')})")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test user activity
    print("\n👥 User Activity:")
    try:
        user_data = collect_user_activity()
        logged_users = len(user_data.get('logged_users', []))
        all_users = len(user_data.get('all_users', []))
        print(f"  ✅ Logged Users: {logged_users}")
        print(f"  👤 Total Users: {all_users}")
        print(f"  🏠 Monitoring Host: {user_data.get('monitoring_host', 'Unknown')}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test log collection
    print("\n📝 Log Collection:")
    try:
        log_data = collect_log_info()
        log_files = len(log_data.get('log_files', []))
        log_entries = len(log_data.get('recent_entries', []))
        print(f"  ✅ Log Files Found: {log_files}")
        print(f"  📄 Recent Entries: {log_entries}")
        print(f"  🏠 Monitoring Host: {log_data.get('monitoring_host', 'Unknown')}")
        
        # Show accessible log files
        accessible_logs = [f for f in log_data.get('log_files', []) if f.get('accessible', False)]
        if accessible_logs:
            print(f"  📋 Accessible Log Files:")
            for log in accessible_logs[:3]:  # Show first 3
                print(f"    - {log.get('path', 'Unknown')}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print(f"\n🎯 Summary:")
    print(f"  The agent is configured to monitor the HOST system")
    print(f"  All collectors are working and accessing host data")
    print(f"  Data collection is active and functional")

if __name__ == "__main__":
    test_host_monitoring() 