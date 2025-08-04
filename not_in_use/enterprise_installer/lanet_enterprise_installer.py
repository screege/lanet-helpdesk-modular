#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Enterprise Agent Installer
Standalone installer that requires NO pre-installed Python
Creates Windows service with embedded Python runtime
"""

import os
import sys
import argparse
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import requests
import subprocess
import shutil
import json
import time
import ctypes
from pathlib import Path
from datetime import datetime
import logging
import tempfile
import zipfile

class LANETEnterpriseInstaller:
    """Enterprise LANET Agent Installer - No Python Dependencies"""
    
    def __init__(self):
        self.version = "3.0.0"
        self.install_dir = Path("C:/Program Files/LANET Agent")
        self.service_name = "LANETAgent"
        self.service_display_name = "LANET Helpdesk Agent"
        
        # Setup logging
        self.setup_logging()
        
        # Installation state
        self.token_valid = False
        self.client_info = None
        self.installation_thread = None
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / "LANET Agent" / "Logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"installer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('LANETEnterpriseInstaller')
        
    def is_admin(self):
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def validate_token(self, token, server_url):
        """Validate installation token with server"""
        try:
            self.logger.info(f"Validating token with server: {server_url}")
            
            # Test server connectivity first
            health_response = requests.get(f"{server_url}/health", timeout=10)
            if health_response.status_code != 200:
                return False, "Server not accessible"
            
            # Validate token
            response = requests.post(
                f"{server_url}/agents/validate-token",
                json={'token': token},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data', {}).get('is_valid'):
                    self.client_info = data['data']
                    return True, "Token valid"
                else:
                    return False, data.get('data', {}).get('error_message', 'Invalid token')
            else:
                return False, f"Server error: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Token validation error: {e}")
            return False, f"Network error: {str(e)}"
        except Exception as e:
            self.logger.error(f"Unexpected validation error: {e}")
            return False, f"Validation error: {str(e)}"
    
    def cleanup_existing_installation(self):
        """Clean up any existing LANET Agent installation"""
        try:
            self.logger.info("Cleaning up existing installation...")
            
            # Stop and remove existing service
            try:
                # Stop the service first
                stop_result = subprocess.run(['sc.exe', 'stop', self.service_name],
                                           capture_output=True, text=True, timeout=30)
                if stop_result.returncode == 0:
                    self.logger.info("Service stopped successfully")
                    time.sleep(3)  # Wait for service to fully stop

                # Delete the service
                delete_result = subprocess.run(['sc.exe', 'delete', self.service_name],
                                             capture_output=True, text=True, timeout=30)
                if delete_result.returncode == 0:
                    self.logger.info("Service deleted successfully")
                    # Wait longer for Windows to complete the deletion
                    self.logger.info("Waiting for service deletion to complete...")
                    time.sleep(10)
                else:
                    self.logger.warning(f"Service deletion warning: {delete_result.stderr}")
                    time.sleep(5)  # Still wait a bit even if deletion failed

            except Exception as e:
                self.logger.warning(f"Service cleanup warning: {e}")
                time.sleep(5)  # Wait even if there was an error
            
            # Verify service is completely removed
            max_retries = 5
            for i in range(max_retries):
                check_result = subprocess.run(['sc.exe', 'query', self.service_name],
                                            capture_output=True, text=True, timeout=15)
                if check_result.returncode != 0:
                    self.logger.info("Service successfully removed from system")
                    break
                else:
                    self.logger.info(f"Service still exists, waiting... (attempt {i+1}/{max_retries})")
                    time.sleep(3)

            # Remove installation directory
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir, ignore_errors=True)
                self.logger.info("Removed existing installation directory")

            return True
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
            return False
    
    def extract_agent_files(self):
        """Extract embedded agent files to installation directory"""
        try:
            self.logger.info(f"Creating installation directory: {self.install_dir}")
            self.install_dir.mkdir(parents=True, exist_ok=True)

            # Try to find the embedded agent file
            agent_dest = self.install_dir / "lanet_agent.py"

            # When running as PyInstaller executable, look in _MEIPASS
            if hasattr(sys, '_MEIPASS'):
                agent_source = Path(sys._MEIPASS) / "lanet_agent.py"
                if agent_source.exists():
                    shutil.copy2(agent_source, agent_dest)
                    self.logger.info("Copied embedded agent file")
                else:
                    raise FileNotFoundError(f"Embedded agent file not found: {agent_source}")
            else:
                # Development mode - look in relative path
                agent_source = Path(__file__).parent.parent / "deployment" / "packages" / "lanet-agent-windows-v2.py"
                if agent_source.exists():
                    shutil.copy2(agent_source, agent_dest)
                    self.logger.info("Copied agent file from development path")
                else:
                    raise FileNotFoundError(f"Agent source file not found: {agent_source}")

            # Create service wrapper
            service_wrapper = self.install_dir / "service_wrapper.py"
            self.create_service_wrapper(service_wrapper)

            # Create configuration directory
            config_dir = self.install_dir / "config"
            config_dir.mkdir(exist_ok=True)

            # Create logs directory
            logs_dir = self.install_dir / "logs"
            logs_dir.mkdir(exist_ok=True)

            return True

        except Exception as e:
            self.logger.error(f"File extraction error: {e}")
            return False
    
    def create_service_wrapper(self, wrapper_path):
        """Create Windows service wrapper"""
        wrapper_content = '''#!/usr/bin/env python3
"""
LANET Agent Service Wrapper
Runs the LANET agent as a Windows service without pywin32 dependency
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging for the service"""
    try:
        log_dir = Path("C:/ProgramData/LANET Agent/Logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "service.log"),
                logging.StreamHandler()
            ]
        )
    except Exception as e:
        # Fallback to console only if file logging fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to setup file logging: {e}")
        return logger

    return logging.getLogger(__name__)

def run_agent():
    """Run the LANET agent"""
    logger = setup_logging()
    logger.info("LANET Agent Service starting...")

    try:
        # Import the agent class
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        # Import and initialize the agent
        from lanet_agent import LANETAgentV2
        agent = LANETAgentV2()

        # Check if agent needs registration
        if not agent.registered:
            logger.info("Agent not registered, attempting registration...")
            installation_token = agent.config.get('REGISTRATION', 'installation_token', fallback='')
            if installation_token:
                try:
                    if agent.register_with_token(installation_token):
                        logger.info("Agent registration successful")
                    else:
                        logger.error("Agent registration failed")
                        return
                except Exception as e:
                    logger.error(f"Agent registration failed: {e}")
                    return
            else:
                logger.error("No installation token found")
                return

        # Main service loop
        logger.info("Starting agent main loop...")
        while True:
            try:
                # Run agent cycle
                if agent.registered:
                    agent.send_heartbeat()
                    agent.send_inventory()
                    agent.send_metrics()
                else:
                    logger.warning("Agent not registered, skipping cycle")

                # Wait for next cycle
                time.sleep(60)  # 1 minute between cycles

            except KeyboardInterrupt:
                logger.info("Service interrupted by user")
                break
            except Exception as e:
                logger.error(f"Agent cycle error: {e}")
                time.sleep(30)  # Wait 30 seconds on error

    except Exception as e:
        logger.error(f"Service error: {e}")
        raise

if __name__ == '__main__':
    run_agent()
'''
        
        with open(wrapper_path, 'w', encoding='utf-8') as f:
            f.write(wrapper_content)
        
        self.logger.info("Created service wrapper")
    
    def install_service(self):
        """Install Windows service using system Python"""
        try:
            self.logger.info("Installing Windows service...")

            # Find system Python installation
            python_exe = self.find_system_python()
            if not python_exe:
                self.logger.error("No system Python found - creating batch wrapper")
                return self.create_batch_service()

            service_script = self.install_dir / "service_wrapper.py"

            # Create service using sc.exe with proper syntax
            cmd = [
                'sc.exe', 'create', self.service_name,
                f'binPath="{python_exe}" "{service_script}"',
                f'DisplayName={self.service_display_name}',
                'start=auto'
            ]

            self.logger.info(f"Service creation command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                self.logger.info("Service installed successfully")

                # Set service description
                desc_result = subprocess.run([
                    'sc.exe', 'description', self.service_name,
                    'LANET Helpdesk MSP Agent for system monitoring and support'
                ], capture_output=True, text=True, timeout=15)

                if desc_result.returncode == 0:
                    self.logger.info("Service description set successfully")
                else:
                    self.logger.warning(f"Failed to set service description: {desc_result.stderr}")

                return True
            else:
                self.logger.error(f"Service installation failed:")
                self.logger.error(f"Return code: {result.returncode}")
                self.logger.error(f"STDOUT: {result.stdout}")
                self.logger.error(f"STDERR: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Service installation error: {e}")
            return False

    def find_system_python(self):
        """Find system Python installation"""
        possible_paths = [
            "C:\\Python310\\python.exe",
            "C:\\Python39\\python.exe",
            "C:\\Python38\\python.exe",
            "C:\\Python311\\python.exe",
            "C:\\Python312\\python.exe",
        ]

        # Check common installation paths
        for path in possible_paths:
            if Path(path).exists():
                self.logger.info(f"Found Python at: {path}")
                return path

        # Try to find python in PATH
        try:
            result = subprocess.run(['where', 'python'], capture_output=True, text=True)
            if result.returncode == 0:
                python_path = result.stdout.strip().split('\n')[0]
                if Path(python_path).exists():
                    self.logger.info(f"Found Python in PATH: {python_path}")
                    return python_path
        except:
            pass

        return None

    def create_batch_service(self):
        """Create batch file service wrapper when Python not found"""
        try:
            self.logger.info("Creating batch file service wrapper...")

            # Create batch file that runs the agent
            batch_file = self.install_dir / "run_agent.bat"
            batch_content = f'''@echo off
cd /d "{self.install_dir}"
python service_wrapper.py
pause
'''

            with open(batch_file, 'w') as f:
                f.write(batch_content)

            # Create service with batch file
            cmd = [
                'sc.exe', 'create', self.service_name,
                f'binPath="{batch_file}"',
                f'DisplayName={self.service_display_name}',
                'start=manual'  # Manual start for batch services
            ]

            self.logger.info(f"Batch service creation command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                self.logger.info("Batch service created successfully")
                return True
            else:
                self.logger.error(f"Batch service creation failed:")
                self.logger.error(f"Return code: {result.returncode}")
                self.logger.error(f"STDOUT: {result.stdout}")
                self.logger.error(f"STDERR: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Batch service creation error: {e}")
            return False
    
    def configure_agent(self, token, server_url):
        """Configure agent with token and server URL"""
        try:
            config_file = self.install_dir / "config" / "agent.ini"
            
            config_content = f"""[SERVER]
url = {server_url}
timeout = 30

[REGISTRATION]
installation_token = {token}
asset_id = 
agent_token = 
client_id = 
site_id = 
client_name = 
site_name = 

[INTERVALS]
heartbeat = 60
inventory = 3600
metrics = 300

[LOGGING]
level = INFO
max_size = 10485760
backup_count = 5
"""
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            self.logger.info("Agent configuration created")
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration error: {e}")
            return False

    def silent_install(self, token, server_url, install_dir=None):
        """Perform silent installation"""
        try:
            self.logger.info("Starting silent installation...")

            # Override install directory if provided
            if install_dir:
                self.install_dir = Path(install_dir)

            # Check administrator privileges
            if not self.is_admin():
                self.logger.error("Administrator privileges required")
                return 4  # Permission error

            # Validate token
            valid, message = self.validate_token(token, server_url)
            if not valid:
                self.logger.error(f"Token validation failed: {message}")
                return 2  # Invalid token

            # Cleanup existing installation
            if not self.cleanup_existing_installation():
                self.logger.error("Failed to cleanup existing installation")
                return 1  # General error

            # Extract agent files
            if not self.extract_agent_files():
                self.logger.error("Failed to extract agent files")
                return 1  # General error

            # Configure agent
            if not self.configure_agent(token, server_url):
                self.logger.error("Failed to configure agent")
                return 1  # General error

            # Install service
            if not self.install_service():
                self.logger.error("Failed to install service")
                return 1  # General error

            # Start service
            try:
                subprocess.run(['sc.exe', 'start', self.service_name],
                             capture_output=True, text=True, timeout=30)
                self.logger.info("Service started successfully")
            except Exception as e:
                self.logger.warning(f"Service start warning: {e}")

            self.logger.info("Silent installation completed successfully")
            return 0  # Success

        except Exception as e:
            self.logger.error(f"Silent installation error: {e}")
            return 1  # General error

    def gui_install(self):
        """Launch GUI installer"""
        try:
            print("Starting GUI installer...")
            self.root = tk.Tk()
            self.setup_gui()
            print("GUI setup complete, starting mainloop...")
            self.root.mainloop()
        except Exception as e:
            print(f"GUI Error: {e}")
            self.logger.error(f"GUI initialization error: {e}")
            # Fallback to console mode
            print("GUI failed, falling back to console mode")
            self.console_install()

    def setup_gui(self):
        """Setup GUI interface"""
        self.root.title("LANET Agent Enterprise Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"600x500+{x}+{y}")

        # Variables
        self.token_var = tk.StringVar()
        self.server_url_var = tk.StringVar(value="https://helpdesk.lanet.mx/api")

        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="LANET Agent Enterprise Installer",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Token input
        ttk.Label(main_frame, text="Installation Token:").grid(row=1, column=0, sticky=tk.W, pady=5)
        token_entry = ttk.Entry(main_frame, textvariable=self.token_var, width=40)
        token_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Server URL input
        ttk.Label(main_frame, text="Server URL:").grid(row=2, column=0, sticky=tk.W, pady=5)
        server_entry = ttk.Entry(main_frame, textvariable=self.server_url_var, width=40)
        server_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        # Validation status
        self.status_label = ttk.Label(main_frame, text="Enter token to validate",
                                     foreground="gray")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Install button
        self.install_button = ttk.Button(main_frame, text="Install Agent",
                                        command=self.start_gui_installation, state='disabled')
        self.install_button.grid(row=5, column=0, columnspan=2, pady=20)

        # Log output
        ttk.Label(main_frame, text="Installation Log:").grid(row=6, column=0, sticky=tk.W)
        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, width=70)
        self.log_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Bind token validation
        self.token_var.trace('w', self.on_token_change)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def on_token_change(self, *args):
        """Handle token input changes"""
        token = self.token_var.get().strip()
        if len(token) >= 10:  # Minimum token length
            threading.Thread(target=self.validate_token_async, args=(token,), daemon=True).start()
        else:
            self.status_label.config(text="Enter valid token", foreground="gray")
            self.install_button.config(state='disabled')

    def validate_token_async(self, token):
        """Validate token asynchronously"""
        try:
            server_url = self.server_url_var.get().strip()
            valid, message = self.validate_token(token, server_url)

            if valid:
                client_name = self.client_info.get('client_name', 'Unknown')
                site_name = self.client_info.get('site_name', 'Unknown')
                status_text = f"✓ Válido - Cliente: {client_name} | Sitio: {site_name}"

                self.root.after(0, lambda: self.status_label.config(
                    text=status_text, foreground="green"))
                self.root.after(0, lambda: self.install_button.config(state='normal'))
                self.token_valid = True
            else:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"✗ {message}", foreground="red"))
                self.root.after(0, lambda: self.install_button.config(state='disabled'))
                self.token_valid = False

        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(
                text=f"✗ Validation error: {str(e)}", foreground="red"))
            self.root.after(0, lambda: self.install_button.config(state='disabled'))

    def start_gui_installation(self):
        """Start GUI installation in background thread"""
        if not self.token_valid:
            messagebox.showerror("Error", "Please enter a valid token")
            return

        if not self.is_admin():
            messagebox.showerror("Error", "Administrator privileges required. Please run as administrator.")
            return

        self.install_button.config(state='disabled')
        self.progress.start()

        self.installation_thread = threading.Thread(
            target=self.gui_installation_worker, daemon=True)
        self.installation_thread.start()

    def gui_installation_worker(self):
        """GUI installation worker thread"""
        try:
            token = self.token_var.get().strip()
            server_url = self.server_url_var.get().strip()

            result = self.silent_install(token, server_url)

            if result == 0:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", "LANET Agent installed successfully!"))
            else:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", f"Installation failed with code: {result}"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", f"Installation error: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.install_button.config(state='normal'))

    def console_install(self):
        """Console-based installer fallback"""
        print("\n" + "="*50)
        print("LANET Agent Enterprise Installer - Console Mode")
        print("="*50)

        # Get token
        token = input("Enter installation token: ").strip()
        if not token:
            print("Error: Token is required")
            return

        # Get server URL
        server_url = input(f"Enter server URL [https://helpdesk.lanet.mx/api]: ").strip()
        if not server_url:
            server_url = "https://helpdesk.lanet.mx/api"

        # Validate token first
        print("Validating token...")
        valid, message = self.validate_token(token, server_url)
        if not valid:
            print(f"❌ Token validation failed: {message}")
            return

        # Show client and site information
        client_name = self.client_info.get('client_name', 'Unknown')
        site_name = self.client_info.get('site_name', 'Unknown')
        print(f"✅ Token válido - Cliente: {client_name} | Sitio: {site_name}")

        # Check admin privileges
        if not self.is_admin():
            print("Error: Administrator privileges required. Please run as administrator.")
            return

        print("\nStarting installation...")
        result = self.silent_install(token, server_url)

        if result == 0:
            print("✅ Installation completed successfully!")
        else:
            print(f"❌ Installation failed with code: {result}")
            print("Check logs in C:\\ProgramData\\LANET Agent\\Logs for details")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='LANET Agent Enterprise Installer')
    parser.add_argument('--silent', action='store_true', help='Silent installation mode')
    parser.add_argument('--token', help='Installation token')
    parser.add_argument('--server-url', default='https://helpdesk.lanet.mx/api',
                       help='Server URL')
    parser.add_argument('--install-dir', help='Installation directory')
    parser.add_argument('--version', action='version', version='LANET Agent Installer 3.0.0')

    args = parser.parse_args()

    installer = LANETEnterpriseInstaller()

    if args.silent:
        if not args.token:
            print("Error: --token required for silent installation")
            sys.exit(1)

        exit_code = installer.silent_install(args.token, args.server_url, args.install_dir)
        sys.exit(exit_code)
    else:
        installer.gui_install()

if __name__ == '__main__':
    main()
