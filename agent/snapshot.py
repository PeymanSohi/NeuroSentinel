import os
import subprocess
import time
import psutil
from datetime import datetime

def take_memory_snapshot(pid):
    """Take a memory snapshot of a process using gcore."""
    try:
        # Check if gcore is available
        if not os.path.exists('/usr/bin/gcore'):
            return {"error": "gcore not available", "pid": pid}
        
        # Create snapshot directory if it doesn't exist
        snapshot_dir = "/tmp/neurosentinel_snapshots"
        os.makedirs(snapshot_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        core_file = f"{snapshot_dir}/gcore_{pid}_{timestamp}.core"
        
        # Take memory snapshot
        result = subprocess.run(
            ['gcore', '-o', core_file, str(pid)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "pid": pid,
                "core_file": core_file,
                "timestamp": timestamp,
                "output": result.stdout
            }
        else:
            return {
                "status": "error",
                "pid": pid,
                "error": result.stderr,
                "returncode": result.returncode
            }
            
    except subprocess.TimeoutExpired:
        return {"error": "gcore timeout", "pid": pid}
    except Exception as e:
        return {"error": str(e), "pid": pid}

def collect_lsof(pid=None):
    """Collect lsof information for a specific process or all processes."""
    try:
        # Check if lsof is available
        if not os.path.exists('/usr/bin/lsof'):
            return {"error": "lsof not available"}
        
        # Create snapshot directory if it doesn't exist
        snapshot_dir = "/tmp/neurosentinel_snapshots"
        os.makedirs(snapshot_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if pid:
            # Collect lsof for specific process
            lsof_file = f"{snapshot_dir}/lsof_{pid}_{timestamp}.txt"
            result = subprocess.run(
                ['lsof', '-p', str(pid)],
                capture_output=True,
                text=True,
                timeout=10
            )
        else:
            # Collect lsof for all processes
            lsof_file = f"{snapshot_dir}/lsof_all_{timestamp}.txt"
            result = subprocess.run(
                ['lsof'],
                capture_output=True,
                text=True,
                timeout=30
            )
        
        # Save output to file
        with open(lsof_file, 'w') as f:
            f.write(result.stdout)
        
        if result.returncode == 0:
            return {
                "status": "success",
                "pid": pid,
                "lsof_file": lsof_file,
                "timestamp": timestamp,
                "line_count": len(result.stdout.splitlines())
            }
        else:
            return {
                "status": "error",
                "pid": pid,
                "error": result.stderr,
                "returncode": result.returncode
            }
            
    except subprocess.TimeoutExpired:
        return {"error": "lsof timeout", "pid": pid}
    except Exception as e:
        return {"error": str(e), "pid": pid}

def get_process_info(pid):
    """Get detailed information about a process."""
    try:
        process = psutil.Process(pid)
        return {
            "pid": pid,
            "name": process.name(),
            "cmdline": process.cmdline(),
            "cpu_percent": process.cpu_percent(),
            "memory_percent": process.memory_percent(),
            "memory_info": process.memory_info()._asdict(),
            "status": process.status(),
            "create_time": process.create_time(),
            "num_threads": process.num_threads(),
            "connections": [conn._asdict() for conn in process.connections()],
            "open_files": [f.path for f in process.open_files()],
            "environ": dict(process.environ())
        }
    except psutil.NoSuchProcess:
        return {"error": f"Process {pid} not found"}
    except Exception as e:
        return {"error": str(e), "pid": pid}

def collect_system_snapshot():
    """Collect a comprehensive system snapshot."""
    try:
        snapshot_dir = "/tmp/neurosentinel_snapshots"
        os.makedirs(snapshot_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        snapshot_data = {
            "timestamp": timestamp,
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": psutil.virtual_memory()._asdict(),
                "disk": psutil.disk_usage('/')._asdict(),
                "network": psutil.net_io_counters()._asdict()
            },
            "processes": [],
            "snapshots": {}
        }
        
        # Get top processes by memory usage
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by memory usage and get top 10
        top_processes = sorted(processes, key=lambda x: x.get('memory_percent', 0), reverse=True)[:10]
        snapshot_data["processes"] = top_processes
        
        # Take snapshots of top processes
        for proc in top_processes[:3]:  # Top 3 processes
            pid = proc['pid']
            snapshot_data["snapshots"][f"process_{pid}"] = {
                "info": proc,
                "lsof": collect_lsof(pid),
                "memory": take_memory_snapshot(pid)
            }
        
        # Save snapshot data
        snapshot_file = f"{snapshot_dir}/system_snapshot_{timestamp}.json"
        import json
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot_data, f, indent=2, default=str)
        
        return {
            "status": "success",
            "snapshot_file": snapshot_file,
            "timestamp": timestamp,
            "process_count": len(top_processes)
        }
        
    except Exception as e:
        return {"error": str(e)} 