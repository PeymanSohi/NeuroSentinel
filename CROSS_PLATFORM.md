# 🌐 Cross-Platform Compatibility Guide

NeuroSentinel is designed to work across different operating systems, with varying levels of support and functionality.

## 🎯 **Supported Platforms**

### ✅ **Linux (Primary Support)**
- **Full Support**: All features work as designed
- **Collectors**: System, Process, User, Logs, Network, Security Tools
- **Features**: Complete host monitoring, anomaly detection, threat intelligence
- **Requirements**: Standard Linux distribution (Ubuntu, CentOS, RHEL, etc.)

### ✅ **macOS (Good Support)**
- **Most Features**: Core monitoring works with some limitations
- **Collectors**: System, Process, User (partial), Logs (different paths)
- **Features**: Host monitoring, anomaly detection
- **Limitations**: 
  - Different log file locations (`/Library/Logs/` vs `/var/log/`)
  - Different user management system
  - No `/proc` filesystem (some process info limited)
  - Different firewall (`pf` vs `iptables`)

### ⚠️ **Windows (Basic Support)**
- **Limited Features**: Basic monitoring with significant limitations
- **Collectors**: System (basic), Process (basic), User (requires additional setup)
- **Features**: Basic host monitoring
- **Limitations**:
  - No Unix-style user/group management
  - Different log system (Event Log vs text files)
  - No `/proc` filesystem
  - Different firewall (Windows Firewall)
  - Different file system and permissions

## 🔧 **Platform-Specific Configuration**

### **Linux Configuration**
```yaml
agent:
  build: ./agent
  privileged: true
  network_mode: host
  volumes:
    - /:/host:ro
    - /var/run:/var/run:ro
    - /proc:/proc:ro
    - /sys:/sys:ro
    - /var/log:/var/log:ro
  environment:
    - HOST_ROOT=/host
```

### **macOS Configuration**
```yaml
agent:
  build: ./agent
  privileged: true
  network_mode: host
  volumes:
    - /:/host:ro
    - /var/run:/var/run:ro
    - /proc:/proc:ro
    - /sys:/sys:ro
    - /var/log:/var/log:ro
    - /Library/Logs:/Library/Logs:ro
  environment:
    - HOST_ROOT=/host
```

### **Windows Configuration**
```yaml
agent:
  build: ./agent
  privileged: true
  network_mode: host
  volumes:
    - C:\:/host:ro
    - C:\Windows\System32\winevt\Logs:/logs:ro
  environment:
    - HOST_ROOT=/host
```

## 🛠️ **Required Changes for Full Cross-Platform Support**

### **For Windows Support**
1. **Add Windows-specific libraries**:
   ```python
   # In requirements.txt
   pywin32>=305  # For Windows API access
   wmi>=1.5.1    # For Windows Management Instrumentation
   ```

2. **Create Windows-specific collectors**:
   ```python
   # agent/collectors/windows_user.py
   import wmi
   import win32net
   
   def collect_windows_users():
       # Windows user enumeration
       pass
   ```

3. **Windows Event Log integration**:
   ```python
   # agent/collectors/windows_logs.py
   import win32evtlog
   
   def collect_windows_logs():
       # Windows Event Log collection
       pass
   ```

### **For Enhanced macOS Support**
1. **macOS-specific log paths**:
   ```python
   # In logs.py
   elif current_os == "darwin":
       log_paths = [
           '/var/log/system.log',
           '/var/log/secure.log',
           '/Library/Logs/DiagnosticReports/',
           '/var/log/asl/'
       ]
   ```

2. **macOS firewall integration**:
   ```python
   # In firewall.py
   def collect_macos_firewall():
       # pf firewall rules
       pass
   ```

## 📊 **Feature Matrix**

| Feature | Linux | macOS | Windows |
|---------|-------|-------|---------|
| **System Metrics** | ✅ Full | ✅ Full | ✅ Basic |
| **Process Monitoring** | ✅ Full | ✅ Full | ✅ Basic |
| **User Management** | ✅ Full | ✅ Partial | ⚠️ Limited |
| **Log Collection** | ✅ Full | ✅ Partial | ⚠️ Limited |
| **Network Monitoring** | ✅ Full | ✅ Full | ✅ Basic |
| **Firewall Rules** | ✅ Full | ⚠️ Partial | ⚠️ Limited |
| **Security Tools** | ✅ Full | ⚠️ Partial | ⚠️ Limited |
| **Anomaly Detection** | ✅ Full | ✅ Full | ✅ Basic |
| **Threat Intelligence** | ✅ Full | ✅ Full | ✅ Full |

## 🚀 **Getting Started by Platform**

### **Linux (Recommended)**
```bash
# Standard installation
git clone https://github.com/peymansohi/NeuroSentinel.git
cd NeuroSentinel
docker-compose up -d
```

### **macOS**
```bash
# Install Docker Desktop for Mac first
git clone https://github.com/peymansohi/NeuroSentinel.git
cd NeuroSentinel
# Modify docker-compose.yml for macOS paths
docker-compose up -d
```

### **Windows**
```bash
# Install Docker Desktop for Windows first
git clone https://github.com/peymansohi/NeuroSentinel.git
cd NeuroSentinel
# Modify docker-compose.yml for Windows paths
# Install additional Windows dependencies
docker-compose up -d
```

## 🔍 **Testing Cross-Platform Compatibility**

Run the platform detection test:
```bash
docker exec neurosentinel-agent-1 python3 /app/test_host_monitoring.py
```

Expected output:
- **Linux**: `platform_type: linux`
- **macOS**: `platform_type: darwin`
- **Windows**: `platform_type: windows`

## 📝 **Platform-Specific Notes**

### **macOS Notes**
- Uses `launchd` instead of `systemd`
- Log files are in `/Library/Logs/` and `/var/log/asl/`
- User management is different from Linux
- Some system calls may require additional permissions

### **Windows Notes**
- Requires Windows 10/11 or Windows Server 2016+
- Docker Desktop must be running
- Some features require administrative privileges
- Event Log access requires specific permissions

## 🤝 **Contributing Cross-Platform Support**

To add support for a new platform:

1. **Create platform-specific collector modules**
2. **Update the main collectors with platform detection**
3. **Add platform-specific configuration examples**
4. **Update tests and documentation**
5. **Test on the target platform**

## 📞 **Support**

For platform-specific issues:
- **Linux**: Full support, all features tested
- **macOS**: Good support, most features work
- **Windows**: Basic support, limited features

---

*NeuroSentinel - Cross-platform cyber defense for the modern world.* 🛡️ 