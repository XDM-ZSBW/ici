#!/usr/bin/env python3
"""
Graceful Shutdown Helper
Provides utilities for clean application shutdown and port management.
"""
import os
import sys
import signal
import atexit
import threading
import time
import socket
import subprocess
import psutil
from typing import Optional, List

class GracefulShutdownManager:
    """Manages graceful shutdown of the application"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.app_instance = None
        self.socketio_instance = None
        self.server_thread = None
        self.shutdown_requested = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        atexit.register(self.cleanup)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        print(f"\n[SIGNAL] Received signal {signum}. Shutting down gracefully...")
        self.shutdown_requested = True
        self.cleanup()
        sys.exit(0)
    
    def is_port_in_use(self, port: Optional[int] = None) -> bool:
        """Check if a port is already in use"""
        port = port or self.port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return False
            except OSError:
                return True
    
    def find_processes_on_port(self, port: Optional[int] = None) -> List[int]:
        """Find all processes using a specific port"""
        port = port or self.port
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info['connections'] or []:
                        if (conn.laddr.port == port and 
                            conn.status == psutil.CONN_LISTEN):
                            processes.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"[ERROR] Failed to find processes on port {port}: {e}")
            # Fallback to netstat method
            return self._netstat_find_processes(port)
        
        return processes
    
    def _netstat_find_processes(self, port: int) -> List[int]:
        """Fallback method using netstat to find processes"""
        processes = []
        try:
            result = subprocess.run(
                ['netstat', '-ano'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            pid = int(parts[-1])
                            processes.append(pid)
                        except ValueError:
                            continue
        except Exception as e:
            print(f"[ERROR] Netstat fallback failed: {e}")
        
        return processes
    
    def kill_processes_on_port(self, port: Optional[int] = None, force: bool = False):
        """Kill processes using the specified port"""
        port = port or self.port
        processes = self.find_processes_on_port(port)
        
        if not processes:
            print(f"[CLEANUP] No processes found on port {port}")
            return
        
        for pid in processes:
            try:
                proc = psutil.Process(pid)
                print(f"[CLEANUP] Terminating process {pid} ({proc.name()}) using port {port}")
                
                if force:
                    proc.kill()
                else:
                    proc.terminate()
                      # Wait for process to terminate
                try:
                    proc.wait(timeout=5)
                    print(f"[CLEANUP] Process {pid} terminated successfully")
                except psutil.TimeoutExpired:
                    print(f"[CLEANUP] Process {pid} didn't terminate, force killing...")
                    proc.kill()
                    proc.wait(timeout=2)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"[CLEANUP] Failed to terminate process {pid}: {e}")
                # Fallback to system command
                try:
                    subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                 capture_output=True, check=False)
                except Exception:
                    pass
    
    def register_app(self, app, socketio):
        """Register Flask app and SocketIO instances for cleanup"""
        self.app_instance = app
        self.socketio_instance = socketio
    
    def cleanup(self):
        """Clean up resources and close connections"""
        if self.shutdown_requested:
            return  # Avoid multiple cleanup calls
        
        self.shutdown_requested = True
        print("\n[SHUTDOWN] Cleaning up resources...")
        
        # Stop SocketIO server gracefully
        if self.socketio_instance:
            try:
                print("[SHUTDOWN] Stopping SocketIO server...")
                self.socketio_instance.stop()
                time.sleep(1)  # Give it time to stop
            except Exception as e:
                print(f"[SHUTDOWN] Error stopping SocketIO: {e}")
        
        # Close Flask app if possible
        if self.app_instance:
            try:
                print("[SHUTDOWN] Shutting down Flask app...")
                # Flask doesn't have a direct shutdown method in development mode
                # The server should stop when the main thread exits
            except Exception as e:
                print(f"[SHUTDOWN] Error shutting down Flask: {e}")
        
        # Force kill any remaining processes on the port
        print(f"[SHUTDOWN] Cleaning up port {self.port}...")
        self.kill_processes_on_port(self.port, force=True)
        
        # Also check for any other Python processes that might be hanging
        self._cleanup_hanging_python_processes()
        
        # Final check
        time.sleep(1)
        if self.is_port_in_use(self.port):
            print(f"[WARNING] Port {self.port} still appears to be in use after cleanup")
            # One more aggressive attempt
            self._force_port_cleanup()
        else:
            print(f"[SUCCESS] Port {self.port} is now free")
        
        print("[SHUTDOWN] Cleanup complete.")
    
    def _cleanup_hanging_python_processes(self):
        """Clean up any hanging Python processes that might be holding the port"""
        try:
            current_pid = os.getpid()
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if (proc.info['name'] and 'python' in proc.info['name'].lower() and
                        proc.info['pid'] != current_pid and
                        proc.info['cmdline'] and any('app.py' in str(cmd) or 'run_refactored.py' in str(cmd) 
                                                   for cmd in proc.info['cmdline'])):
                        print(f"[CLEANUP] Found hanging Python process: {proc.info['pid']}")
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"[CLEANUP] Error cleaning up Python processes: {e}")
    
    def _force_port_cleanup(self):
        """Force cleanup the port using system commands"""
        try:
            print(f"[CLEANUP] Force cleaning port {self.port} using system commands...")
            # Windows-specific force cleanup
            subprocess.run([
                'netstat', '-ano', '|', 'findstr', f':{self.port}', '|', 
                'for', '/f', 'tokens=5', '%i', 'in', "('more')", 'do', 
                'taskkill', '/F', '/PID', '%i'
            ], shell=True, capture_output=True)
            time.sleep(1)
        except Exception as e:
            print(f"[CLEANUP] Force cleanup failed: {e}")
    
    def prepare_for_startup(self):
        """Prepare the environment for a clean startup"""
        print(f"[STARTUP] Checking port {self.port}...")
        
        if self.is_port_in_use(self.port):
            print(f"[STARTUP] Port {self.port} is in use. Cleaning up...")
            self.kill_processes_on_port(self.port)
            time.sleep(2)  # Wait for cleanup
            
            if self.is_port_in_use(self.port):
                print(f"[ERROR] Port {self.port} is still in use after cleanup. Exiting.")
                sys.exit(1)
            else:
                print(f"[SUCCESS] Port {self.port} is now available")
        else:
            print(f"[SUCCESS] Port {self.port} is available")

# Global instance
shutdown_manager = GracefulShutdownManager()

def get_shutdown_manager() -> GracefulShutdownManager:
    """Get the global shutdown manager instance"""
    return shutdown_manager
