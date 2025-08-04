#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Windows Service Wrapper
Runs the LANET agent as a Windows service with SYSTEM privileges
This enables automatic BitLocker data collection without user intervention
"""

import sys
import os
import time
import logging
import subprocess
import threading
from pathlib import Path

# Add the parent directory to the path to import agent modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    WINDOWS_SERVICE_AVAILABLE = True
except ImportError:
    WINDOWS_SERVICE_AVAILABLE = False
    logging.warning("Windows service modules not available")

class LANETAgentService(win32serviceutil.ServiceFramework):
    """Windows Service wrapper for LANET Agent"""
    
    _svc_name_ = "LANETAgent"
    _svc_display_name_ = "LANET Helpdesk Agent"
    _svc_description_ = "LANET Helpdesk MSP Agent - Collects system information, monitors health, and manages BitLocker data"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        self.agent_process = None
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup service logging"""
        log_dir = Path("C:/Program Files/LANET Agent/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'service.log'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('LANETService')
        
    def SvcStop(self):
        """Stop the service"""
        self.logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        
        # Stop the agent process
        self.is_alive = False
        if self.agent_process:
            try:
                self.agent_process.terminate()
                self.agent_process.wait(timeout=30)
                self.logger.info("Agent process terminated gracefully")
            except subprocess.TimeoutExpired:
                self.logger.warning("Agent process did not terminate gracefully, killing...")
                self.agent_process.kill()
            except Exception as e:
                self.logger.error(f"Error stopping agent process: {e}")
        
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        """Main service execution"""
        self.logger.info("LANET Agent Service starting...")
        
        # Log service account information
        self.log_service_info()
        
        # Report service started
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        # Start the agent monitoring thread
        agent_thread = threading.Thread(target=self.run_agent_loop, daemon=True)
        agent_thread.start()
        
        # Wait for stop signal
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        
        self.logger.info("LANET Agent Service stopped")
        
    def log_service_info(self):
        """Log service account and privilege information"""
        try:
            import getpass
            import ctypes
            
            username = getpass.getuser()
            self.logger.info(f"Service running as: {username}")
            
            # Check if running as SYSTEM
            if username.upper() in ['SYSTEM', 'NT AUTHORITY\\SYSTEM']:
                self.logger.info("✅ Service running with SYSTEM privileges")
                self.logger.info("✅ BitLocker access should be available")
            else:
                self.logger.warning(f"⚠️ Service running as {username} - may not have BitLocker access")
            
            # Check admin privileges
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                self.logger.info(f"Administrator privileges: {is_admin}")
            except:
                self.logger.debug("Could not check administrator privileges")
                
        except Exception as e:
            self.logger.error(f"Error logging service info: {e}")
    
    def run_agent_loop(self):
        """Run the agent in a loop with automatic restart"""
        agent_path = self.get_agent_path()
        restart_delay = 30  # seconds
        
        self.logger.info(f"Starting agent loop with path: {agent_path}")
        
        while self.is_alive:
            try:
                self.logger.info("Starting LANET Agent process...")
                
                # Start the agent process
                self.agent_process = subprocess.Popen(
                    [sys.executable, agent_path],
                    cwd=str(Path(agent_path).parent),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Monitor the process
                while self.is_alive and self.agent_process.poll() is None:
                    time.sleep(5)
                
                if self.is_alive:
                    # Process exited unexpectedly
                    return_code = self.agent_process.returncode
                    stdout, stderr = self.agent_process.communicate()
                    
                    self.logger.error(f"Agent process exited with code {return_code}")
                    if stdout:
                        self.logger.error(f"STDOUT: {stdout}")
                    if stderr:
                        self.logger.error(f"STDERR: {stderr}")
                    
                    self.logger.info(f"Restarting agent in {restart_delay} seconds...")
                    time.sleep(restart_delay)
                
            except Exception as e:
                self.logger.error(f"Error in agent loop: {e}")
                if self.is_alive:
                    self.logger.info(f"Retrying in {restart_delay} seconds...")
                    time.sleep(restart_delay)
        
        self.logger.info("Agent loop stopped")
    
    def get_agent_path(self):
        """Get the path to the agent main script"""
        # Try different possible locations
        possible_paths = [
            "C:/Program Files/LANET Agent/main.py",
            "C:/Program Files/LANET Agent/agent/main.py",
            str(Path(__file__).parent.parent / "main.py"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"Found agent at: {path}")
                return path
        
        # Default fallback
        default_path = "C:/Program Files/LANET Agent/main.py"
        self.logger.warning(f"Agent not found, using default: {default_path}")
        return default_path

def install_service():
    """Install the LANET Agent as a Windows service"""
    if not WINDOWS_SERVICE_AVAILABLE:
        print("❌ Windows service modules not available")
        print("   Install with: pip install pywin32")
        return False
    
    try:
        # Install the service
        win32serviceutil.InstallService(
            LANETAgentService,
            LANETAgentService._svc_name_,
            LANETAgentService._svc_display_name_,
            description=LANETAgentService._svc_description_
        )
        
        print(f"✅ Service '{LANETAgentService._svc_display_name_}' installed successfully")
        
        # Configure service to run as LocalSystem (SYSTEM account)
        configure_service_account()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to install service: {e}")
        return False

def configure_service_account():
    """Configure the service to run as LocalSystem (SYSTEM account)"""
    try:
        import subprocess
        
        service_name = LANETAgentService._svc_name_
        
        # Configure service to run as LocalSystem
        cmd = [
            'sc.exe', 'config', service_name,
            'obj=', 'LocalSystem',
            'start=', 'auto'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Service configured to run as LocalSystem (SYSTEM account)")
            print("✅ Service will have BitLocker access privileges")
        else:
            print(f"⚠️ Warning: Could not configure service account: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ Warning: Could not configure service account: {e}")

def uninstall_service():
    """Uninstall the LANET Agent service"""
    if not WINDOWS_SERVICE_AVAILABLE:
        print("❌ Windows service modules not available")
        return False
    
    try:
        win32serviceutil.RemoveService(LANETAgentService._svc_name_)
        print(f"✅ Service '{LANETAgentService._svc_display_name_}' uninstalled successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to uninstall service: {e}")
        return False

def main():
    """Main entry point for service management"""
    if len(sys.argv) == 1:
        # Run as service
        if WINDOWS_SERVICE_AVAILABLE:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(LANETAgentService)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            print("❌ Windows service modules not available")
            print("   Install with: pip install pywin32")
            sys.exit(1)
    else:
        # Handle command line arguments
        if sys.argv[1] == 'install':
            install_service()
        elif sys.argv[1] == 'remove':
            uninstall_service()
        elif sys.argv[1] == 'start':
            win32serviceutil.StartService(LANETAgentService._svc_name_)
            print("✅ Service started")
        elif sys.argv[1] == 'stop':
            win32serviceutil.StopService(LANETAgentService._svc_name_)
            print("✅ Service stopped")
        elif sys.argv[1] == 'restart':
            win32serviceutil.RestartService(LANETAgentService._svc_name_)
            print("✅ Service restarted")
        else:
            print("Usage: windows_service.py [install|remove|start|stop|restart]")

if __name__ == '__main__':
    main()
