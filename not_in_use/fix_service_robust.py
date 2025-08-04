#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix LANET Agent Service - Create Robust Windows Service
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def remove_existing_service():
    """Remove existing service"""
    print("🗑️ Removing existing service...")
    
    try:
        subprocess.run(['sc.exe', 'stop', 'LANETAgent'], capture_output=True)
        subprocess.run(['sc.exe', 'delete', 'LANETAgent'], capture_output=True)
        print("✅ Existing service removed")
    except Exception as e:
        print(f"⚠️ Service removal: {e}")

def create_robust_service_wrapper():
    """Create a robust service wrapper using pywin32"""
    print("📝 Creating robust service wrapper...")
    
    install_dir = Path("C:/Program Files/LANET Agent")
    
    # Create a proper Windows service using pywin32
    service_wrapper = f'''
import sys
import os
import time
import logging
import servicemanager
import win32event
import win32service
import win32serviceutil
from pathlib import Path

class LANETAgentService(win32serviceutil.ServiceFramework):
    """LANET Agent Windows Service"""
    
    _svc_name_ = "LANETAgent"
    _svc_display_name_ = "LANET Helpdesk Agent"
    _svc_description_ = "LANET Helpdesk Agent - Professional MSP monitoring and BitLocker recovery key collection"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        
        # Setup paths
        self.install_dir = Path(r"{install_dir}")
        os.chdir(str(self.install_dir))
        sys.path.insert(0, str(self.install_dir))
        
        # Setup logging
        self.setup_logging()
        
        # Set environment variables
        os.environ['LANET_SERVICE_MODE'] = '1'
        os.environ['LANET_NO_UI'] = '1'
        os.environ['LANET_AUTO_REGISTER'] = '1'
    
    def setup_logging(self):
        """Setup service logging"""
        log_dir = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / "LANET Agent" / "Logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'service.log', encoding='utf-8'),
            ]
        )
        
        self.logger = logging.getLogger('LANETService')
    
    def SvcStop(self):
        """Stop the service"""
        self.logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False
    
    def SvcDoRun(self):
        """Main service execution"""
        try:
            self.logger.info("LANET Agent Service starting...")
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            
            # Import and run the main agent
            self.run_agent()
            
        except Exception as e:
            self.logger.error(f"Service error: {{e}}", exc_info=True)
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_ERROR_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, str(e))
            )
    
    def run_agent(self):
        """Run the LANET Agent"""
        try:
            self.logger.info("Importing main agent...")
            
            # Import main agent
            from main import main as agent_main
            
            self.logger.info("Starting agent main function...")
            
            # Run in a separate thread to allow service control
            import threading
            
            def agent_thread():
                try:
                    agent_main()
                except Exception as e:
                    self.logger.error(f"Agent thread error: {{e}}", exc_info=True)
            
            # Start agent thread
            thread = threading.Thread(target=agent_thread, daemon=True)
            thread.start()
            
            self.logger.info("Agent thread started, waiting for stop signal...")
            
            # Wait for stop signal
            while self.is_alive:
                # Wait for stop event with timeout
                rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
                if rc == win32event.WAIT_OBJECT_0:
                    # Stop event was signaled
                    break
                
                # Check if agent thread is still alive
                if not thread.is_alive():
                    self.logger.warning("Agent thread died, restarting...")
                    thread = threading.Thread(target=agent_thread, daemon=True)
                    thread.start()
            
            self.logger.info("Service stopping...")
            
        except Exception as e:
            self.logger.error(f"Agent execution error: {{e}}", exc_info=True)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(LANETAgentService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(LANETAgentService)
'''
    
    # Write service wrapper
    service_file = install_dir / "lanet_service.py"
    with open(service_file, 'w', encoding='utf-8') as f:
        f.write(service_wrapper)
    
    print(f"✅ Service wrapper created: {service_file}")
    return service_file

def install_service_with_pywin32(service_file):
    """Install service using pywin32"""
    print("🔧 Installing service with pywin32...")
    
    try:
        # Install service
        result = subprocess.run([
            sys.executable, str(service_file), 'install'
        ], capture_output=True, text=True, cwd=str(service_file.parent))
        
        if result.returncode == 0:
            print("✅ Service installed with pywin32")
            
            # Set service to auto start
            subprocess.run([
                'sc.exe', 'config', 'LANETAgent', 'start=', 'auto'
            ], capture_output=True)
            
            # Set service description
            subprocess.run([
                'sc.exe', 'description', 'LANETAgent',
                'LANET Helpdesk Agent - Professional MSP monitoring and BitLocker recovery key collection'
            ], capture_output=True)
            
            return True
        else:
            print(f"❌ Service installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Service installation error: {e}")
        return False

def test_service():
    """Test the service"""
    print("🧪 Testing service...")
    
    try:
        # Start service
        result = subprocess.run(['sc.exe', 'start', 'LANETAgent'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Service started successfully")
            
            # Wait and check status
            time.sleep(10)
            
            status_result = subprocess.run(['sc.exe', 'query', 'LANETAgent'], 
                                         capture_output=True, text=True)
            
            if "RUNNING" in status_result.stdout:
                print("✅ Service is running")
                return True
            else:
                print("⚠️ Service started but not running")
                return False
        else:
            print(f"❌ Service start failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Service test error: {e}")
        return False

def main():
    """Main function"""
    print("🔧 LANET Agent Robust Service Fix")
    print("=" * 50)
    
    # Check if pywin32 is installed
    try:
        import win32serviceutil
        print("✅ pywin32 is available")
    except ImportError:
        print("❌ pywin32 not found, installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pywin32'])
        print("✅ pywin32 installed")
    
    # Remove existing service
    remove_existing_service()
    
    # Create robust service wrapper
    service_file = create_robust_service_wrapper()
    
    # Install service
    if install_service_with_pywin32(service_file):
        # Test service
        if test_service():
            print("\n✅ SERVICE FIX COMPLETED SUCCESSFULLY!")
            print("The LANET Agent service should now work properly.")
        else:
            print("\n⚠️ Service installed but failed to start properly")
    else:
        print("\n❌ SERVICE FIX FAILED")
    
    print("\n📋 Next steps:")
    print("1. Check Windows Services for 'LANET Helpdesk Agent'")
    print("2. Check logs in C:\\ProgramData\\LANET Agent\\Logs\\")
    print("3. Verify agent appears in helpdesk dashboard")

if __name__ == "__main__":
    main()
    input("\nPress Enter to continue...")
