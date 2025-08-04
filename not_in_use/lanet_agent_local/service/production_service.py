#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Production Windows Service
Runs completely in background with no visible windows
Designed for 2000+ client deployment with SYSTEM privileges
"""

import os
import sys
import time
import logging
import threading
from pathlib import Path

# Windows service imports
try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    WINDOWS_SERVICE_AVAILABLE = True
except ImportError:
    WINDOWS_SERVICE_AVAILABLE = False

class LANETProductionService(win32serviceutil.ServiceFramework):
    """Production Windows Service - Completely silent background operation"""
    
    _svc_name_ = "LANETAgent"
    _svc_display_name_ = "LANET Helpdesk Agent"
    _svc_description_ = "LANET Helpdesk Agent - Background system monitoring with SYSTEM privileges for BitLocker access"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        self.agent = None
        
        # Setup logging (file only - no console output)
        self.setup_production_logging()
        
    def setup_production_logging(self):
        """Setup production logging - file only, no console output"""
        try:
            # Create logs directory
            log_dir = Path("C:/Program Files/LANET Agent/logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Setup file logging ONLY (no console for production)
            log_file = log_dir / "service.log"
            
            # Configure logging with rotation
            from logging.handlers import RotatingFileHandler
            
            handler = RotatingFileHandler(
                log_file, 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            
            # Setup logger
            self.logger = logging.getLogger('LANETProductionService')
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(handler)
            
            # Prevent propagation to avoid console output
            self.logger.propagate = False
            
            self.logger.info("🚀 LANET Production Service logging initialized")
            
        except Exception as e:
            # Fallback to Windows Event Log
            servicemanager.LogErrorMsg(f"Failed to setup file logging: {e}")
    
    def SvcStop(self):
        """Stop the service gracefully"""
        try:
            self.logger.info("🛑 Production service stop requested")
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            self.is_alive = False
            
            # Stop the agent gracefully
            if self.agent:
                self.logger.info("Stopping agent core...")
                self.agent.stop()
                
            win32event.SetEvent(self.hWaitStop)
            self.logger.info("✅ Production service stopped successfully")
            
        except Exception as e:
            error_msg = f"Error stopping production service: {e}"
            self.logger.error(error_msg)
            servicemanager.LogErrorMsg(error_msg)
    
    def SvcDoRun(self):
        """Main production service execution - completely silent"""
        try:
            # Log to Windows Event Log
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, 'LANET Agent started with SYSTEM privileges for BitLocker access')
            )
            
            self.logger.info("🚀 LANET Production Service starting...")
            self.logger.info(f"🔧 Service account: {os.environ.get('USERNAME', 'Unknown')}")
            self.logger.info(f"📁 Current directory: {os.getcwd()}")
            
            # Set working directory to installation path
            install_path = "C:/Program Files/LANET Agent"
            if os.path.exists(install_path):
                os.chdir(install_path)
                self.logger.info(f"📁 Changed to installation directory: {install_path}")
            else:
                error_msg = f"Installation directory not found: {install_path}"
                self.logger.error(error_msg)
                servicemanager.LogErrorMsg(error_msg)
                return
            
            # Add installation path to Python path
            sys.path.insert(0, install_path)
            
            # Import agent components
            try:
                from core.config_manager import ConfigManager
                from core.agent_core import AgentCore
                self.logger.info("✅ Agent modules imported successfully")
            except ImportError as e:
                error_msg = f"Failed to import agent modules: {e}"
                self.logger.error(error_msg)
                servicemanager.LogErrorMsg(error_msg)
                return
            
            # Initialize configuration
            config_path = os.path.join(install_path, "config", "agent_config.json")
            self.logger.info(f"📋 Loading configuration from: {config_path}")
            
            if not os.path.exists(config_path):
                error_msg = f"Configuration file not found: {config_path}"
                self.logger.error(error_msg)
                servicemanager.LogErrorMsg(error_msg)
                return
            
            try:
                config_manager = ConfigManager(config_path)
                self.logger.info("✅ Configuration loaded successfully")
            except Exception as e:
                error_msg = f"Failed to load configuration: {e}"
                self.logger.error(error_msg)
                servicemanager.LogErrorMsg(error_msg)
                return
            
            # Initialize agent core in production mode (NO UI, completely headless)
            self.logger.info("🔧 Initializing agent core in production mode...")
            try:
                self.agent = AgentCore(config_manager, ui_enabled=False)
                self.logger.info("✅ Agent core initialized successfully")
            except Exception as e:
                error_msg = f"Failed to initialize agent core: {e}"
                self.logger.error(error_msg)
                servicemanager.LogErrorMsg(error_msg)
                return
            
            # Check if agent is registered
            if not self.agent.is_registered():
                error_msg = "Agent not registered. Service cannot start. Please register the agent first."
                self.logger.error(error_msg)
                servicemanager.LogErrorMsg(error_msg)
                return
            
            self.logger.info("✅ Agent registration verified")
            
            # Start the agent
            self.logger.info("🚀 Starting agent core...")
            try:
                self.agent.start()
                self.logger.info("✅ Agent core started successfully")
            except Exception as e:
                error_msg = f"Failed to start agent core: {e}"
                self.logger.error(error_msg)
                servicemanager.LogErrorMsg(error_msg)
                return
            
            # Production service main loop - completely silent background operation
            self.logger.info("✅ Production service running in background")
            self.logger.info("📊 Monitoring system, collecting BitLocker data, sending inventory updates")
            
            heartbeat_counter = 0
            
            while self.is_alive:
                # Wait for stop event with timeout
                rc = win32event.WaitForSingleObject(self.hWaitStop, 30000)  # 30 second timeout
                
                if rc == win32event.WAIT_OBJECT_0:
                    # Stop event was signaled
                    self.logger.info("🛑 Stop event received")
                    break
                    
                # Check if agent is still running
                if self.agent and not self.agent.is_running():
                    self.logger.error("❌ Agent stopped unexpectedly, restarting...")
                    try:
                        self.agent.start()
                        self.logger.info("✅ Agent restarted successfully")
                    except Exception as e:
                        self.logger.error(f"❌ Failed to restart agent: {e}")
                        break
                
                # Log heartbeat every 10 minutes (20 cycles * 30 seconds)
                heartbeat_counter += 1
                if heartbeat_counter >= 20:
                    self.logger.info("💓 Service heartbeat - running normally in background")
                    heartbeat_counter = 0
            
            # Cleanup
            self.logger.info("🧹 Cleaning up production service...")
            if self.agent:
                self.agent.stop()
                
            self.logger.info("✅ Production service execution completed")
            
        except Exception as e:
            error_msg = f"Production service execution error: {e}"
            self.logger.error(error_msg, exc_info=True)
            servicemanager.LogErrorMsg(error_msg)
            raise

def install_production_service():
    """Install the production service with SYSTEM privileges"""
    if not WINDOWS_SERVICE_AVAILABLE:
        print("❌ Windows service modules not available")
        return False
    
    try:
        print("🔧 Installing LANET Agent as production Windows service...")
        
        # Install the service
        win32serviceutil.InstallService(
            LANETProductionService,
            LANETProductionService._svc_name_,
            LANETProductionService._svc_display_name_,
            description=LANETProductionService._svc_description_
        )
        
        print(f"✅ Service '{LANETProductionService._svc_display_name_}' installed successfully")
        
        # Configure service to run as LocalSystem with automatic startup
        import subprocess
        
        # Set service to run as LocalSystem (SYSTEM account)
        result = subprocess.run([
            'sc.exe', 'config', LANETProductionService._svc_name_,
            'obj=', 'LocalSystem',
            'start=', 'auto'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Service configured with SYSTEM privileges and automatic startup")
        else:
            print(f"⚠️ Warning: Failed to configure service account: {result.stderr}")
        
        # Set service description
        subprocess.run([
            'sc.exe', 'description', LANETProductionService._svc_name_,
            LANETProductionService._svc_description_
        ], capture_output=True)
        
        print("✅ Production service installation completed")
        print("📋 Service details:")
        print(f"   • Name: {LANETProductionService._svc_name_}")
        print(f"   • Account: LocalSystem (SYSTEM privileges)")
        print(f"   • Startup: Automatic")
        print(f"   • BitLocker Access: Enabled")
        print(f"   • Visible Windows: None (completely background)")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to install production service: {e}")
        return False

def uninstall_production_service():
    """Uninstall the production service"""
    if not WINDOWS_SERVICE_AVAILABLE:
        print("❌ Windows service modules not available")
        return False
    
    try:
        print("🗑️ Uninstalling LANET Agent production service...")
        
        # Stop service first
        try:
            win32serviceutil.StopService(LANETProductionService._svc_name_)
            print("✅ Service stopped")
        except:
            pass  # Service might not be running
        
        # Remove service
        win32serviceutil.RemoveService(LANETProductionService._svc_name_)
        print("✅ Production service uninstalled successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to uninstall production service: {e}")
        return False

def main():
    """Main entry point for service management"""
    if len(sys.argv) == 1:
        # Run as service
        if WINDOWS_SERVICE_AVAILABLE:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(LANETProductionService)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            print("❌ Windows service modules not available")
            sys.exit(1)
    else:
        # Handle command line arguments
        if sys.argv[1] == 'install':
            install_production_service()
        elif sys.argv[1] == 'remove':
            uninstall_production_service()
        elif sys.argv[1] == 'start':
            win32serviceutil.StartService(LANETProductionService._svc_name_)
            print("✅ Production service started")
        elif sys.argv[1] == 'stop':
            win32serviceutil.StopService(LANETProductionService._svc_name_)
            print("✅ Production service stopped")
        elif sys.argv[1] == 'restart':
            win32serviceutil.RestartService(LANETProductionService._svc_name_)
            print("✅ Production service restarted")
        else:
            print("Usage: production_service.py [install|remove|start|stop|restart]")

if __name__ == "__main__":
    main()
