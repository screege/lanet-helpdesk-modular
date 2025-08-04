#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Standalone Installer
Enterprise-grade single executable installer for field technician deployment

This creates a complete standalone installer that:
- Requires no Python installation on target computers
- Handles all dependencies automatically
- Provides one-click installation experience
- Includes GUI for token validation
- Installs Windows service with SYSTEM privileges
- Comparable to commercial MSP agent installers
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import requests
import os
import sys
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
import base64

class LANETStandaloneInstaller:
    """Complete standalone installer for LANET Agent"""
    
    def __init__(self):
        self.setup_logging()
        
        # Installation state
        self.install_dir = Path("C:/Program Files/LANET Agent")
        self.temp_dir = None
        self.installation_successful = False
        
        # Check admin privileges immediately
        if not self.is_admin():
            self.request_admin_privileges()
            return
        
        # Initialize GUI
        self.root = tk.Tk()
        self.token_var = tk.StringVar()
        self.server_url_var = tk.StringVar(value="https://helpdesk.lanet.mx/api")
        
        # Validation state
        self.token_valid = False
        self.client_info = None
        self.installation_thread = None
        self.python_executable = None  # Store found Python executable
        
        self.setup_ui()
        self.logger.info("LANET Standalone Installer initialized")
    
    def setup_logging(self):
        """Setup logging system"""
        # Create temp log directory
        log_dir = Path(tempfile.gettempdir()) / "LANET_Installer"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"installer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('LANETStandaloneInstaller')
        self.logger.info("=== LANET Agent Standalone Installer Started ===")
    
    def is_admin(self):
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def request_admin_privileges(self):
        """Request administrator privileges and restart"""
        try:
            # Show message to user
            root = tk.Tk()
            root.withdraw()  # Hide main window
            
            result = messagebox.askokcancel(
                "Administrator Privileges Required",
                "LANET Agent Installer requires administrator privileges to:\n\n"
                "• Install Windows service with SYSTEM privileges\n"
                "• Access BitLocker data\n"
                "• Configure automatic startup\n\n"
                "The installer will restart with administrator privileges.\n\n"
                "Click OK to continue or Cancel to exit."
            )
            
            if result:
                # Restart with admin privileges
                ctypes.windll.shell32.ShellExecuteW(
                    None, 
                    "runas", 
                    sys.executable, 
                    f'"{__file__}"', 
                    None, 
                    1
                )
            
            root.destroy()
            sys.exit(0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to request administrator privileges: {e}")
            sys.exit(1)
    
    def setup_ui(self):
        """Setup the installer GUI"""
        self.root.title("LANET Agent Installer")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Set window icon and properties
        self.root.configure(bg='#f0f0f0')
        
        # Center window on screen
        self.center_window()
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_frame)

        # Configuration section (always visible)
        self.create_config_section(main_frame)

        # Progress section
        self.create_progress_section(main_frame)

        # Action buttons
        self.create_action_buttons(main_frame)

        # Log section
        self.create_log_section(main_frame)
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Logo/Title
        title_label = ttk.Label(
            header_frame, 
            text="LANET Helpdesk Agent", 
            font=('Arial', 20, 'bold')
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame, 
            text="Enterprise MSP Agent Installer", 
            font=('Arial', 12)
        )
        subtitle_label.pack()
        
        version_label = ttk.Label(
            header_frame, 
            text="Version 3.0 • One-Click Deployment • 2000+ Computer Support", 
            font=('Arial', 9),
            foreground='gray'
        )
        version_label.pack(pady=(5, 0))
    
    def create_config_section(self, parent):
        """Create configuration section"""
        config_frame = ttk.LabelFrame(parent, text="Agent Configuration", padding="15")
        config_frame.pack(fill=tk.X, pady=(0, 15))

        # Server URL
        ttk.Label(config_frame, text="Helpdesk Server URL:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        server_entry = ttk.Entry(config_frame, textvariable=self.server_url_var, width=60, font=('Arial', 10))
        server_entry.pack(fill=tk.X, pady=(5, 15))

        # Token input
        ttk.Label(config_frame, text="Installation Token:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        token_entry = ttk.Entry(config_frame, textvariable=self.token_var, width=60, font=('Consolas', 10))
        token_entry.pack(fill=tk.X, pady=(5, 5))

        # Token format hint
        format_label = ttk.Label(
            config_frame,
            text="Format: LANET-{CLIENT_CODE}-{SITE_CODE}-{RANDOM}",
            font=('Arial', 8),
            foreground='gray'
        )
        format_label.pack(anchor=tk.W, pady=(0, 10))

        # Validation status
        self.token_status_label = ttk.Label(config_frame, text="Enter token to validate", foreground='gray')
        self.token_status_label.pack(anchor=tk.W)

        # Client info
        self.client_info_label = ttk.Label(config_frame, text="", font=('Arial', 10, 'bold'))
        self.client_info_label.pack(anchor=tk.W, pady=(5, 0))

        # Test connection button
        test_frame = ttk.Frame(config_frame)
        test_frame.pack(fill=tk.X, pady=(10, 0))

        self.test_button = ttk.Button(
            test_frame,
            text="Test Connection",
            command=self.test_connection
        )
        self.test_button.pack(side=tk.LEFT)

        # Bind token validation
        self.token_var.trace('w', self.on_token_change)
    

    
    def create_progress_section(self, parent):
        """Create progress section"""
        progress_frame = ttk.LabelFrame(parent, text="Installation Progress", padding="15")
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            maximum=100, 
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Status label
        self.progress_status_label = ttk.Label(progress_frame, text="Ready to install", foreground='blue')
        self.progress_status_label.pack(anchor=tk.W)
    
    def create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 15))

        # Install button (centered and prominent)
        button_container = ttk.Frame(button_frame)
        button_container.pack(expand=True)

        self.install_button = ttk.Button(
            button_container,
            text="Install LANET Agent",
            command=self.start_installation,
            style='Accent.TButton'
        )
        self.install_button.pack(side=tk.LEFT, padx=(0, 20))

        # Exit button
        exit_button = ttk.Button(
            button_container,
            text="Exit",
            command=self.root.quit
        )
        exit_button.pack(side=tk.LEFT)

        # Initially disable install button until token is validated
        self.install_button.config(state='disabled')
    
    def create_log_section(self, parent):
        """Create log section"""
        log_frame = ttk.LabelFrame(parent, text="Installation Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=8, 
            width=70,
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
    

    
    def on_token_change(self, *args):
        """Handle token input changes with debounced validation"""
        # Cancel any existing validation
        if hasattr(self, 'validation_timer'):
            self.validation_timer.cancel()

        # Start new validation with delay
        self.validation_timer = threading.Timer(0.5, self.validate_token_async)
        self.validation_timer.start()
    
    def validate_token_async(self):
        """Validate token asynchronously"""
        token = self.token_var.get().strip()
        
        if not token:
            self.root.after(0, lambda: self.update_token_status("Enter token to validate", 'gray', False))
            return
        
        # Check format
        import re
        if not re.match(r'^LANET-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+$', token):
            self.root.after(0, lambda: self.update_token_status("Invalid token format", 'red', False))
            return
        
        self.root.after(0, lambda: self.update_token_status("Validating...", 'blue', False))
        
        try:
            server_url = self.server_url_var.get().strip()
            response = requests.post(
                f"{server_url}/agents/validate-token",
                json={'token': token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data', {}).get('is_valid'):
                    client_info = data['data']
                    self.client_info = client_info
                    
                    client_name = client_info.get('client_name', 'Unknown')
                    site_name = client_info.get('site_name', 'Unknown')
                    
                    self.root.after(0, lambda: self.update_token_status("Token valid", 'green', True))
                    self.root.after(0, lambda: self.client_info_label.config(
                        text=f"Client: {client_name} | Site: {site_name}", 
                        foreground='green'
                    ))
                else:
                    error_msg = data.get('data', {}).get('error_message', 'Invalid token')
                    self.root.after(0, lambda: self.update_token_status(error_msg, 'red', False))
            else:
                self.root.after(0, lambda: self.update_token_status("Server error", 'red', False))
                
        except Exception as e:
            self.root.after(0, lambda: self.update_token_status(f"Connection error", 'red', False))
    
    def update_token_status(self, message, color, valid):
        """Update token validation status"""
        self.token_status_label.config(text=message, foreground=color)
        self.token_valid = valid

        # Enable/disable install button based on validation
        self.install_button.config(state='normal' if valid else 'disabled')

        if not valid:
            self.client_info_label.config(text="")
    
    def test_connection(self):
        """Test server connection"""
        def test():
            server_url = self.server_url_var.get().strip()
            try:
                response = requests.get(f"{server_url}/health", timeout=10)
                if response.status_code == 200:
                    self.log_message("✅ Server connection successful")
                else:
                    self.log_message("❌ Server connection failed")
            except Exception as e:
                self.log_message(f"❌ Connection error: {str(e)}")
        
        threading.Thread(target=test, daemon=True).start()
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"
        
        self.log_text.insert(tk.END, formatted_message + '\n')
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        self.logger.info(message)
    
    def update_progress(self, value, status):
        """Update progress bar and status"""
        self.progress_var.set(value)
        self.progress_status_label.config(text=status)
        self.root.update_idletasks()
    
    def start_installation(self):
        """Start the installation process"""
        if not self.token_valid:
            messagebox.showerror("Error", "Please enter a valid installation token first.")
            return

        if not self.token_var.get().strip():
            messagebox.showerror("Error", "Installation token is required.")
            return
        
        # Disable UI during installation
        self.install_button.config(state='disabled')
        self.test_button.config(state='disabled')
        
        # Start installation thread
        self.installation_thread = threading.Thread(target=self.perform_installation, daemon=True)
        self.installation_thread.start()
    
    def perform_installation(self):
        """Perform the complete installation"""
        try:
            self.log_message("=== Starting LANET Agent Installation ===")
            self.update_progress(0, "Initializing installation...")
            
            # Step 1: Extract embedded files
            self.log_message("Extracting installation files...")
            if not self.extract_embedded_files():
                return
            self.update_progress(20, "Files extracted")
            
            # Step 2: Install Python runtime and dependencies
            self.log_message("Installing Python runtime and dependencies...")
            if not self.install_python_runtime():
                return
            self.update_progress(40, "Python runtime installed")
            
            # Step 3: Install agent files
            self.log_message("Installing LANET Agent files...")
            if not self.install_agent_files():
                return
            self.update_progress(60, "Agent files installed")
            
            # Step 4: Create and install Windows service
            self.log_message("Creating Windows service...")
            if not self.install_windows_service():
                return
            self.update_progress(80, "Windows service installed")
            
            # Step 5: Configure and start service
            self.log_message("Starting LANET Agent service...")
            if not self.start_agent_service():
                return
            self.update_progress(100, "Installation completed successfully!")
            
            self.installation_successful = True
            self.log_message("=== Installation Completed Successfully ===")
            
            # Show success message
            self.root.after(0, self.show_success_message)
            
        except Exception as e:
            self.log_message(f"❌ Installation failed: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Installation Failed", f"Installation failed:\n\n{str(e)}"))
        finally:
            # Cleanup and re-enable UI
            self.cleanup_temp_files()
            self.root.after(0, lambda: self.install_button.config(state='normal' if self.token_valid else 'disabled'))
            self.root.after(0, lambda: self.test_button.config(state='normal'))
    
    def extract_embedded_files(self):
        """Extract embedded agent files to temporary directory"""
        try:
            self.temp_dir = Path(tempfile.mkdtemp(prefix="lanet_install_"))
            self.log_message(f"Using temporary directory: {self.temp_dir}")

            # Try to extract from PyInstaller bundle first
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller executable
                bundle_dir = Path(sys._MEIPASS)
                source_dir = bundle_dir / "agent_files"
                if source_dir.exists():
                    shutil.copytree(source_dir, self.temp_dir / "agent_files")
                    self.log_message("✅ Agent files extracted from bundle")
                    return True

            # Fallback to local directory (development mode)
            source_dir = Path(__file__).parent / "agent_files"
            if source_dir.exists():
                shutil.copytree(source_dir, self.temp_dir / "agent_files")
                self.log_message("✅ Agent files extracted from local directory")
                return True
            else:
                self.log_message("❌ Agent files not found")
                return False

        except Exception as e:
            self.log_message(f"❌ Failed to extract files: {str(e)}")
            return False

    def install_python_runtime(self):
        """Install embedded Python runtime and dependencies"""
        try:
            # When running as PyInstaller executable, we need to find system Python
            python_executable = None

            if getattr(sys, 'frozen', False):
                # Running as PyInstaller executable - find system Python
                possible_python_paths = [
                    'python',
                    'python.exe',
                    r'C:\Python310\python.exe',
                    r'C:\Python39\python.exe',
                    r'C:\Python38\python.exe',
                    r'C:\Program Files\Python310\python.exe',
                    r'C:\Program Files\Python39\python.exe'
                ]

                for python_path in possible_python_paths:
                    try:
                        result = subprocess.run([python_path, '--version'],
                                              capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            python_executable = python_path
                            self.log_message(f"✅ Python runtime found: {result.stdout.strip()}")
                            break
                    except:
                        continue

                if not python_executable:
                    self.log_message("❌ Python runtime not available on system")
                    return False
            else:
                # Development mode - use current Python
                python_executable = sys.executable
                result = subprocess.run([python_executable, '--version'],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.log_message(f"✅ Python runtime available: {result.stdout.strip()}")
                else:
                    self.log_message("❌ Python runtime not available")
                    return False

            # Store the found Python executable for later use
            self.python_executable = python_executable

            # Install required packages
            required_packages = [
                'pywin32',
                'psutil',
                'requests',
                'wmi',
                'psycopg2-binary'
            ]

            for package in required_packages:
                self.log_message(f"Installing {package}...")
                result = subprocess.run(
                    [python_executable, '-m', 'pip', 'install', package, '--quiet'],
                    capture_output=True, text=True, timeout=120
                )

                if result.returncode == 0:
                    self.log_message(f"✅ {package} installed")
                else:
                    self.log_message(f"❌ Failed to install {package}: {result.stderr}")
                    return False

            return True

        except Exception as e:
            self.log_message(f"❌ Python runtime installation failed: {str(e)}")
            return False

    def install_agent_files(self):
        """Install LANET Agent files to Program Files"""
        try:
            # Create installation directory
            self.install_dir.mkdir(parents=True, exist_ok=True)

            # Create subdirectories
            for subdir in ['logs', 'data', 'config', 'service']:
                (self.install_dir / subdir).mkdir(exist_ok=True)

            # Copy agent files
            agent_source = self.temp_dir / "agent_files"
            if agent_source.exists():
                for item in agent_source.iterdir():
                    if item.name not in ['.git', '__pycache__', '.pytest_cache']:
                        dest = self.install_dir / item.name
                        if item.is_file():
                            shutil.copy2(item, dest)
                        else:
                            if dest.exists():
                                shutil.rmtree(dest)
                            shutil.copytree(item, dest)

                self.log_message("✅ Agent files copied to Program Files")
            else:
                self.log_message("❌ Agent source files not found")
                return False

            # Create agent configuration
            self.create_agent_configuration()

            # Create service wrapper
            self.create_service_wrapper()

            return True

        except Exception as e:
            self.log_message(f"❌ Failed to install agent files: {str(e)}")
            return False

    def create_agent_configuration(self):
        """Create agent configuration file"""
        try:
            config_file = self.install_dir / "config" / "agent_config.json"

            # Use the configured values from the UI
            server_url = self.server_url_var.get().strip()
            token = self.token_var.get().strip()

            config = {
                "server": {
                    "url": server_url,
                    "base_url": server_url,
                    "timeout": 30,
                    "retry_attempts": 3,
                    "verify_ssl": True
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
                "database": {
                    "local_db_path": "data/agent.db",
                    "backup_interval": 86400,
                    "max_backup_files": 7
                }
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            self.log_message(f"✅ Agent configuration created")

        except Exception as e:
            self.log_message(f"❌ Failed to create configuration: {str(e)}")

    def create_service_wrapper(self):
        """Create Windows service wrapper"""
        try:
            service_wrapper_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Windows Service Wrapper
Auto-generated by standalone installer
"""

import sys
import os
import logging
from pathlib import Path

# Configure paths
AGENT_DIR = Path(r"{self.install_dir}")
sys.path.insert(0, str(AGENT_DIR))
sys.path.insert(0, str(AGENT_DIR / "core"))
sys.path.insert(0, str(AGENT_DIR / "modules"))

# Change working directory
os.chdir(str(AGENT_DIR))

# Setup logging
log_file = Path(r"C:/ProgramData/LANET Agent/Logs/service.log")
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(log_file), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('LANETService')

def main():
    """Service entry point"""
    try:
        logger.info("=== LANET Agent Service Starting ===")

        # Import and run agent
        from main import main as agent_main

        # Set registration arguments
        token = "{self.token_var.get().strip()}"
        sys.argv = ['main.py', '--register', token]

        logger.info("Starting agent main process...")
        agent_main()

    except Exception as e:
        logger.error(f"Service error: {{e}}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
'''

            service_wrapper_path = self.install_dir / "service" / "service_wrapper.py"
            with open(service_wrapper_path, 'w', encoding='utf-8') as f:
                f.write(service_wrapper_content)

            self.log_message("✅ Service wrapper created")

        except Exception as e:
            self.log_message(f"❌ Failed to create service wrapper: {str(e)}")

    def install_windows_service(self):
        """Install Windows service using pywin32"""
        try:
            # Create Windows service script
            windows_service_content = f'''#!/usr/bin/env python3
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import os
from pathlib import Path

class LANETAgentService(win32serviceutil.ServiceFramework):
    _svc_name_ = "LANETAgent"
    _svc_display_name_ = "LANET Helpdesk Agent"
    _svc_description_ = "LANET Helpdesk MSP Agent - Collects system information and BitLocker data"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )

        try:
            sys.path.insert(0, r"{self.install_dir}")
            sys.path.insert(0, r"{self.install_dir / 'service'}")

            from service_wrapper import main as service_main
            service_main()

        except Exception as e:
            servicemanager.LogErrorMsg(f"Service error: {{e}}")

        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(LANETAgentService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(LANETAgentService)
'''

            service_script_path = self.install_dir / "service" / "windows_service.py"
            with open(service_script_path, 'w', encoding='utf-8') as f:
                f.write(windows_service_content)

            # Install the service using the found Python executable
            python_to_use = self.python_executable or sys.executable
            result = subprocess.run(
                [python_to_use, str(service_script_path), 'install'],
                capture_output=True, text=True, cwd=str(self.install_dir), timeout=60
            )

            if result.returncode == 0:
                self.log_message("✅ Windows service installed")

                # Configure service for automatic startup and LocalSystem
                subprocess.run(['sc.exe', 'config', 'LANETAgent', 'start=auto'],
                             capture_output=True, timeout=30)
                subprocess.run(['sc.exe', 'config', 'LANETAgent', 'obj=LocalSystem'],
                             capture_output=True, timeout=30)

                self.log_message("✅ Service configured for automatic startup with SYSTEM privileges")
                return True
            else:
                error_msg = result.stderr.strip() or result.stdout.strip() or f"Return code: {result.returncode}"
                self.log_message(f"❌ Service installation failed: {error_msg}")
                if result.stdout:
                    self.log_message(f"Installation output: {result.stdout}")
                return False

        except Exception as e:
            self.log_message(f"❌ Windows service installation failed: {str(e)}")
            return False

    def start_agent_service(self):
        """Start the LANET Agent service"""
        try:
            result = subprocess.run(
                ['sc.exe', 'start', 'LANETAgent'],
                capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                self.log_message("✅ LANET Agent service started successfully")

                # Wait and check status
                time.sleep(3)
                status_result = subprocess.run(
                    ['sc.exe', 'query', 'LANETAgent'],
                    capture_output=True, text=True, timeout=30
                )

                if 'RUNNING' in status_result.stdout:
                    self.log_message("✅ Service is running correctly")
                else:
                    self.log_message("⚠️ Service started but status unclear")
                    self.log_message(f"Service status output: {status_result.stdout}")

                return True
            else:
                error_msg = result.stderr.strip() or result.stdout.strip() or f"Return code: {result.returncode}"
                self.log_message(f"❌ Failed to start service: {error_msg}")

                # Try to get more detailed error information
                query_result = subprocess.run(
                    ['sc.exe', 'query', 'LANETAgent'],
                    capture_output=True, text=True, timeout=30
                )
                if query_result.stdout:
                    self.log_message(f"Service status: {query_result.stdout}")

                return False

        except Exception as e:
            self.log_message(f"❌ Failed to start service: {str(e)}")
            return False

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.log_message("✅ Temporary files cleaned up")
        except Exception as e:
            self.log_message(f"⚠️ Failed to cleanup temp files: {str(e)}")

    def show_success_message(self):
        """Show installation success message"""
        messagebox.showinfo(
            "Installation Complete",
            "LANET Agent has been installed successfully!\n\n"
            "✅ Windows service installed and started\n"
            "✅ SYSTEM privileges configured for BitLocker access\n"
            "✅ Automatic startup enabled\n"
            "✅ Agent will appear in helpdesk within 5-10 minutes\n\n"
            "The installation is complete. You can close this installer."
        )

    def run(self):
        """Run the installer"""
        if hasattr(self, 'root'):
            self.root.mainloop()

# Embedded agent files will be added here by the build script
EMBEDDED_AGENT_FILES = {}

def main():
    """Main entry point"""
    installer = LANETStandaloneInstaller()
    if hasattr(installer, 'root'):
        installer.run()

if __name__ == "__main__":
    main()
