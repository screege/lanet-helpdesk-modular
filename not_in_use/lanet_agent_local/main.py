#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Windows Client Agent
Main entry point for the LANET Windows agent
"""

import sys
import os
import argparse
import logging
import threading
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent_core import AgentCore
from core.logger import setup_logging
from core.config_manager import ConfigManager

def cleanup_existing_installation():
    """Clean up any existing LANET Agent installation"""
    try:
        import subprocess
        import shutil
        from pathlib import Path

        print("Performing cleanup of existing installation...")
        cleanup_success = True

        # STEP 1: Stop and remove existing service
        print("  Checking for existing service...")
        try:
            # Stop service if running
            result = subprocess.run(['sc.exe', 'stop', 'LANETAgent'],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("  Stopped existing service")
                # Wait a moment for service to stop
                import time
                time.sleep(3)

            # Remove service
            result = subprocess.run(['sc.exe', 'delete', 'LANETAgent'],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("  Removed existing service")

        except Exception as e:
            print(f"  Warning: Service cleanup failed: {e}")
            cleanup_success = False

        # STEP 2: Kill any running LANET processes
        print("  Checking for running LANET processes...")
        try:
            # Kill any LANET Agent processes
            subprocess.run(['taskkill', '/F', '/IM', 'LANET_Agent_Installer.exe'],
                          capture_output=True, text=True)
            subprocess.run(['taskkill', '/F', '/IM', 'LANET_Agent.exe'],
                          capture_output=True, text=True)
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'],
                          capture_output=True, text=True)
            print("  Terminated any running LANET processes")

            # Wait for processes to terminate
            import time
            time.sleep(2)

        except Exception as e:
            print(f"  Warning: Process cleanup failed: {e}")

        # STEP 3: Remove existing installation directory
        print("  Checking for existing installation directory...")
        try:
            install_dir = Path("C:/Program Files/LANET Agent")
            if install_dir.exists():
                print(f"  Removing existing directory: {install_dir}")

                # Try to remove directory multiple times if needed
                for attempt in range(3):
                    try:
                        shutil.rmtree(install_dir)
                        print("  Successfully removed existing directory")
                        break
                    except PermissionError:
                        if attempt < 2:
                            print(f"  Retry {attempt + 1}: Directory in use, waiting...")
                            import time
                            time.sleep(2)
                        else:
                            print("  Warning: Could not remove some files (may be in use)")
                            cleanup_success = False
                    except Exception as e:
                        print(f"  Warning: Directory removal failed: {e}")
                        cleanup_success = False
                        break
            else:
                print("  No existing installation directory found")

        except Exception as e:
            print(f"  Warning: Directory cleanup failed: {e}")
            cleanup_success = False

        # STEP 4: Clean up any remaining registry entries
        print("  Cleaning up registry entries...")
        try:
            # Remove service registry entries if they exist
            subprocess.run(['reg.exe', 'delete',
                          'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LANETAgent',
                          '/f'], capture_output=True, text=True)
            print("  Cleaned up registry entries")
        except Exception as e:
            # This is expected if the service doesn't exist
            pass

        print("Cleanup completed")
        return cleanup_success

    except Exception as e:
        print(f"Error during cleanup: {e}")
        return False

def install_as_service(token=None, server_url=None):
    """Install the agent as a production Windows service"""
    try:
        import ctypes
        import subprocess
        import json
        import shutil
        from pathlib import Path

        # Check admin privileges
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("❌ Administrator privileges required for service installation")
            return False

        print("Installing LANET Agent as production Windows service...")
        print("This will install a completely background service with no visible windows")

        # Get installation parameters
        if not token:
            token = input("Enter installation token: ").strip()
        if not server_url:
            server_url = input("Enter server URL [http://localhost:5001/api]: ").strip()
            if not server_url:
                server_url = "http://localhost:5001/api"

        print(f"Token: {token}")
        print(f"Server: {server_url}")

        # STEP 1: Cleanup existing installation
        print("Checking for existing installation...")
        cleanup_success = cleanup_existing_installation()

        if not cleanup_success:
            print("Warning: Some cleanup operations failed, but continuing...")

        # STEP 2: Create installation directory
        install_dir = Path("C:/Program Files/LANET Agent")
        install_dir.mkdir(parents=True, exist_ok=True)
        print(f"Installation directory: {install_dir}")

        # Create subdirectories
        for subdir in ["logs", "data", "config", "service"]:
            (install_dir / subdir).mkdir(exist_ok=True)

        # Copy all agent files
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable
            current_dir = Path(sys._MEIPASS)
        else:
            # Running as script
            current_dir = Path(__file__).parent

        print("Copying agent files...")

        # Copy main files and directories
        items_to_copy = ["core", "modules", "ui", "service"]

        # Copy main.py specifically
        main_py_src = current_dir / "main.py"
        main_py_dst = install_dir / "main.py"

        if main_py_src.exists():
            shutil.copy2(main_py_src, main_py_dst)
            print(f"  Copied file: main.py")
        else:
            print(f"  Warning: main.py not found at: {main_py_src}")
            # Try to copy from the original source
            try:
                original_main = Path(__file__)
                if original_main.exists():
                    shutil.copy2(original_main, main_py_dst)
                    print(f"  Copied main.py from: {original_main}")
            except:
                print(f"  Could not copy main.py")

        for item in items_to_copy:
            src = current_dir / item
            dst = install_dir / item

            if src.exists():
                if src.is_file():
                    shutil.copy2(src, dst)
                    print(f"  Copied file: {item}")
                else:
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                    print(f"  Copied directory: {item}")
            else:
                print(f"  Warning: Not found: {item}")

        # Create configuration
        print("Creating configuration...")
        config = {
            "server": {
                "url": server_url,
                "timeout": 30,
                "retry_attempts": 3
            },
            "agent": {
                "name": os.environ.get('COMPUTERNAME', 'Unknown'),
                "version": "3.0",
                "log_level": "INFO",
                "heartbeat_interval": 300,
                "inventory_interval": 3600
            },
            "registration": {
                "installation_token": token,
                "auto_register": True
            },
            "bitlocker": {
                "enabled": True,
                "collection_interval": 3600,
                "require_admin_privileges": False
            },
            "service": {
                "name": "LANETAgent",
                "display_name": "LANET Helpdesk Agent",
                "account": "LocalSystem",
                "start_type": "auto"
            }
        }

        config_path = install_dir / "config" / "agent_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"Configuration created: {config_path}")

        # Install production Windows service
        print("Installing production Windows service...")

        # Use the production service script
        service_script = install_dir / "service" / "production_service.py"

        if not service_script.exists():
            print(f"Error: Production service script not found: {service_script}")
            return False

        # Install service directly using win32serviceutil
        print("Installing Windows service directly...")

        try:
            # Import the production service class
            sys.path.insert(0, str(install_dir))
            from service.production_service import LANETProductionService

            # Install the service
            import win32serviceutil

            print("Installing Windows service...")
            win32serviceutil.InstallService(
                LANETProductionService,
                LANETProductionService._svc_name_,
                LANETProductionService._svc_display_name_,
                description=LANETProductionService._svc_description_
            )

            # Configure service to run as LocalSystem with automatic startup
            result = subprocess.run([
                'sc.exe', 'config', LANETProductionService._svc_name_,
                'obj=', 'LocalSystem',
                'start=', 'auto'
            ], capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Warning: Failed to configure service account: {result.stderr}")

            service_installed = True

        except Exception as e:
            print(f"Error: Direct service installation failed: {e}")
            service_installed = False

        if service_installed:
            print("Production service installed successfully")
            print("Service configured with SYSTEM privileges")
            print("BitLocker access enabled")
            print("No visible windows - completely background operation")

            # Start service
            print("Starting production service...")
            try:
                import win32serviceutil
                win32serviceutil.StartService(LANETProductionService._svc_name_)
                print("Production service started successfully")
                print("Agent is now running in background collecting inventory data")
            except Exception as e:
                print("Warning: Service installed but failed to start")
                print(f"Start error: {e}")

            return True
        else:
            print("Error: Service installation failed")
            return False

    except Exception as e:
        print(f"Error: Service installation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def remove_service():
    """Remove the Windows service"""
    try:
        import subprocess

        # Stop service
        subprocess.run(['sc.exe', 'stop', 'LANETAgent'], capture_output=True)

        # Remove service
        result = subprocess.run(['sc.exe', 'delete', 'LANETAgent'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Service removed successfully")
            return True
        else:
            print(f"❌ Service removal failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Service removal error: {e}")
        return False

def run_as_service():
    """Run the agent as a Windows service"""
    try:
        # Import Windows service modules
        import win32serviceutil
        import win32service
        import win32event
        import servicemanager

        class LANETAgentService(win32serviceutil.ServiceFramework):
            _svc_name_ = "LANETAgent"
            _svc_display_name_ = "LANET Helpdesk Agent"

            def __init__(self, args):
                win32serviceutil.ServiceFramework.__init__(self, args)
                self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
                self.is_alive = True

            def SvcStop(self):
                self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
                self.is_alive = False
                win32event.SetEvent(self.hWaitStop)

            def SvcDoRun(self):
                servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                    servicemanager.PYS_SERVICE_STARTED,
                                    (self._svc_name_, ''))

                # Run the agent
                try:
                    config_manager = ConfigManager("C:/Program Files/LANET Agent/config/agent_config.json")
                    agent = AgentCore(config_manager, ui_enabled=False)
                    agent.start()

                    while self.is_alive:
                        time.sleep(1)

                    agent.stop()
                except Exception as e:
                    servicemanager.LogErrorMsg(f"Service error: {e}")

        # Run the service
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(LANETAgentService)
        servicemanager.StartServiceCtrlDispatcher()

        return True

    except ImportError:
        print("❌ Windows service modules not available")
        print("   Install with: pip install pywin32")
        return False
    except Exception as e:
        print(f"❌ Service runtime error: {e}")
        return False

def main():
    """Main entry point for the LANET Agent"""
    parser = argparse.ArgumentParser(description='LANET Helpdesk Windows Agent')
    parser.add_argument('--register', type=str, help='Register agent with installation token')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--no-ui', action='store_true', help='Run without system tray UI')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--install-service', action='store_true', help='Install as Windows service')
    parser.add_argument('--remove-service', action='store_true', help='Remove Windows service')
    parser.add_argument('--service', action='store_true', help='Run as Windows service')
    parser.add_argument('--install-token', help='Installation token for service installation')
    parser.add_argument('--server-url', help='Server URL for service installation')
    
    args = parser.parse_args()

    # Handle service installation
    if args.install_service:
        return install_as_service(args.install_token, args.server_url)

    # Handle service removal
    if args.remove_service:
        return remove_service()

    # Handle service mode
    if args.service:
        return run_as_service()

    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger('lanet_agent')
    
    logger.info("🚀 LANET Helpdesk Agent Starting...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager(args.config)
        
        # Initialize agent core
        agent = AgentCore(config_manager, ui_enabled=not args.no_ui)
        
        # Handle registration mode
        if args.register:
            logger.info(f"Registration mode with token: {args.register}")
            success = agent.register_with_token(args.register)
            if success:
                logger.info("✅ Agent registered successfully!")
                print("✅ Agent registered successfully!")
                print("🚀 Starting agent in normal operation mode...")
                # Continue to normal operation after successful registration
            else:
                logger.error("❌ Agent registration failed!")
                print("❌ Agent registration failed!")
                sys.exit(1)

        # Check if agent is already registered
        if not agent.is_registered():
            logger.info("Agent not registered, showing installation window...")

            # Show installation window
            from ui.installation_window import InstallationWindow
            installation_window = InstallationWindow(config_manager, agent.database)

            installation_success = installation_window.show()

            if not installation_success:
                logger.info("Installation cancelled by user")
                print("Installation cancelled")
                sys.exit(0)

            logger.info("Installation completed, restarting agent...")
            # Reload configuration after installation
            config_manager.reload()
            agent = AgentCore(config_manager, ui_enabled=not args.no_ui)
        
        # Handle test mode
        if args.test:
            logger.info("Running in test mode...")
            agent.run_tests()
            return
        
        # Normal operation mode
        logger.info("Starting agent in normal operation mode...")
        agent.start()
        
        # Keep the main thread alive
        try:
            while agent.is_running():
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        
        # Graceful shutdown
        agent.stop()
        logger.info("Agent stopped successfully")
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
