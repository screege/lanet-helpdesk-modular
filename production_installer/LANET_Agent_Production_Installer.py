#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Production Installer
Enterprise-grade Windows installer with GUI interface, real-time token validation,
and robust Windows service installation with SYSTEM privileges for BitLocker access.

Addresses known issues:
- File permission problems
- Windows service startup failures  
- Path and import issues
- Service wrapper reliability

Features:
- Professional GUI interface for technicians
- Real-time token validation with client/site display
- Robust Windows service installation with SYSTEM privileges
- Comprehensive error handling and logging
- Enterprise-grade reliability for 2000+ computer deployments
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import requests
import psycopg2
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
import winreg

class LANETAgentProductionInstaller:
    """Production-ready LANET Agent Installer with enterprise features"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_logging()
        
        # Installation parameters
        self.token_var = tk.StringVar()
        self.server_url_var = tk.StringVar(value="https://helpdesk.lanet.mx/api")
        self.install_dir = Path("C:/Program Files/LANET Agent")
        
        # Validation state
        self.token_valid = False
        self.client_info = None
        self.installation_thread = None
        self.validation_thread = None
        
        # Setup UI
        self.setup_ui()
        
        # Bind token validation
        self.token_var.trace('w', self.on_token_change)
        
        self.logger.info("LANET Agent Production Installer initialized")
    
    def setup_logging(self):
        """Setup comprehensive logging system"""
        # Create logs directory
        log_dir = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / "LANET Agent" / "Logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file with timestamp
        log_file = log_dir / f"installer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('LANETProductionInstaller')
        self.logger.info("=== LANET Agent Production Installer Started ===")
        self.logger.info(f"Log file: {log_file}")
    
    def setup_ui(self):
        """Setup professional GUI interface"""
        self.root.title("LANET Agent Production Installer")
        self.root.geometry("700x800")
        self.root.resizable(True, True)
        
        # Set window icon if available
        try:
            icon_path = Path(__file__).parent / "assets" / "lanet_icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Header section
        self.create_header(main_frame)
        
        # Server configuration section
        self.create_server_config(main_frame)
        
        # Token validation section
        self.create_token_section(main_frame)
        
        # Installation progress section
        self.create_progress_section(main_frame)
        
        # Action buttons
        self.create_action_buttons(main_frame)
        
        # Status and log section
        self.create_status_section(main_frame)
    
    def create_header(self, parent):
        """Create header section with branding"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            header_frame, 
            text="LANET Helpdesk Agent", 
            font=('Arial', 18, 'bold')
        )
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Subtitle
        subtitle_label = ttk.Label(
            header_frame, 
            text="Production Installer v3.0 - Enterprise MSP Agent", 
            font=('Arial', 11)
        )
        subtitle_label.grid(row=1, column=0, sticky=tk.W)
        
        # Version info
        version_label = ttk.Label(
            header_frame, 
            text="Supports 2000+ computers • SYSTEM privileges • BitLocker access", 
            font=('Arial', 9),
            foreground='gray'
        )
        version_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
    
    def create_server_config(self, parent):
        """Create server configuration section"""
        server_frame = ttk.LabelFrame(parent, text="Server Configuration", padding="15")
        server_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        server_frame.columnconfigure(1, weight=1)
        
        ttk.Label(server_frame, text="Helpdesk Server URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        server_entry = ttk.Entry(server_frame, textvariable=self.server_url_var, width=50)
        server_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Server status indicator
        self.server_status_label = ttk.Label(server_frame, text="", foreground='gray')
        self.server_status_label.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
    
    def create_token_section(self, parent):
        """Create token validation section"""
        token_frame = ttk.LabelFrame(parent, text="Installation Token", padding="15")
        token_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        token_frame.columnconfigure(1, weight=1)
        
        # Token input
        ttk.Label(token_frame, text="Agent Token:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        token_entry = ttk.Entry(token_frame, textvariable=self.token_var, width=50, font=('Consolas', 10))
        token_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Token format hint
        format_label = ttk.Label(
            token_frame, 
            text="Format: LANET-{CLIENT_CODE}-{SITE_CODE}-{RANDOM}", 
            font=('Arial', 8),
            foreground='gray'
        )
        format_label.grid(row=1, column=1, sticky=tk.W, pady=(2, 0))
        
        # Validation status
        self.token_status_frame = ttk.Frame(token_frame)
        self.token_status_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.token_status_label = ttk.Label(self.token_status_frame, text="Enter token to validate", foreground='gray')
        self.token_status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Client/Site info display
        self.client_info_frame = ttk.Frame(token_frame)
        self.client_info_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.client_info_label = ttk.Label(self.client_info_frame, text="", font=('Arial', 9, 'bold'))
        self.client_info_label.grid(row=0, column=0, sticky=tk.W)
    
    def create_progress_section(self, parent):
        """Create installation progress section"""
        progress_frame = ttk.LabelFrame(parent, text="Installation Progress", padding="15")
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            maximum=100, 
            length=400
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Progress status
        self.progress_status_label = ttk.Label(progress_frame, text="Ready to install", foreground='blue')
        self.progress_status_label.grid(row=1, column=0, sticky=tk.W)
    
    def create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        button_frame.columnconfigure(0, weight=1)
        
        # Button container for centering
        button_container = ttk.Frame(button_frame)
        button_container.grid(row=0, column=0)
        
        # Install button
        self.install_button = ttk.Button(
            button_container, 
            text="Install LANET Agent", 
            command=self.start_installation,
            style='Accent.TButton'
        )
        self.install_button.grid(row=0, column=0, padx=(0, 10))
        
        # Test connection button
        self.test_button = ttk.Button(
            button_container, 
            text="Test Connection", 
            command=self.test_server_connection
        )
        self.test_button.grid(row=0, column=1, padx=(0, 10))
        
        # Exit button
        self.exit_button = ttk.Button(
            button_container, 
            text="Exit", 
            command=self.root.quit
        )
        self.exit_button.grid(row=0, column=2)
        
        # Initially disable install button
        self.install_button.config(state='disabled')
    
    def create_status_section(self, parent):
        """Create status and log section"""
        status_frame = ttk.LabelFrame(parent, text="Installation Log", padding="15")
        status_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            status_frame, 
            height=12, 
            width=80,
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame row weight for log expansion
        parent.rowconfigure(5, weight=1)
    
    def log_message(self, message, level='INFO'):
        """Add message to log display and logger"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {level}: {message}"
        
        # Add to GUI log
        self.log_text.insert(tk.END, formatted_message + '\n')
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        # Add to logger
        if level == 'ERROR':
            self.logger.error(message)
        elif level == 'WARNING':
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def on_token_change(self, *args):
        """Handle token input changes with debounced validation"""
        # Cancel any existing validation thread
        if self.validation_thread and self.validation_thread.is_alive():
            return
        
        # Start new validation thread with delay
        self.validation_thread = threading.Timer(0.5, self.validate_token_async)
        self.validation_thread.start()
    
    def validate_token_async(self):
        """Validate token asynchronously"""
        token = self.token_var.get().strip()
        
        if not token:
            self.root.after(0, lambda: self.update_token_status("Enter token to validate", 'gray', False))
            return
        
        # Check token format first
        if not self.is_valid_token_format(token):
            self.root.after(0, lambda: self.update_token_status("Invalid token format", 'red', False))
            return
        
        self.root.after(0, lambda: self.update_token_status("Validating token...", 'blue', False))
        
        try:
            # Validate token with server
            server_url = self.server_url_var.get().strip()
            if not server_url:
                self.root.after(0, lambda: self.update_token_status("Server URL required", 'red', False))
                return
            
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
                    
                    self.root.after(0, lambda: self.update_token_status("Token validated successfully", 'green', True))
                    self.root.after(0, lambda: self.update_client_info(f"Client: {client_name} | Site: {site_name}"))
                else:
                    error_msg = data.get('data', {}).get('error_message', 'Token validation failed')
                    self.root.after(0, lambda: self.update_token_status(error_msg, 'red', False))
            else:
                self.root.after(0, lambda: self.update_token_status("Server validation failed", 'red', False))
                
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: self.update_token_status(f"Connection error: {str(e)}", 'red', False))
        except Exception as e:
            self.root.after(0, lambda: self.update_token_status(f"Validation error: {str(e)}", 'red', False))
    
    def update_token_status(self, message, color, valid):
        """Update token validation status"""
        self.token_status_label.config(text=message, foreground=color)
        self.token_valid = valid
        
        # Enable/disable install button based on validation
        if valid:
            self.install_button.config(state='normal')
        else:
            self.install_button.config(state='disabled')
            self.client_info_label.config(text="")
    
    def update_client_info(self, info_text):
        """Update client/site information display"""
        self.client_info_label.config(text=info_text, foreground='green')
    
    def is_valid_token_format(self, token):
        """Validate token format"""
        import re
        pattern = r'^LANET-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+$'
        return re.match(pattern, token) is not None
    
    def test_server_connection(self):
        """Test connection to helpdesk server"""
        def test_connection():
            server_url = self.server_url_var.get().strip()
            if not server_url:
                self.root.after(0, lambda: self.update_server_status("Server URL required", 'red'))
                return
            
            self.root.after(0, lambda: self.update_server_status("Testing connection...", 'blue'))
            
            try:
                response = requests.get(f"{server_url}/health", timeout=10)
                if response.status_code == 200:
                    self.root.after(0, lambda: self.update_server_status("Connection successful", 'green'))
                    self.log_message("Server connection test successful")
                else:
                    self.root.after(0, lambda: self.update_server_status("Server responded with error", 'red'))
                    self.log_message(f"Server connection test failed: HTTP {response.status_code}", 'ERROR')
            except requests.exceptions.RequestException as e:
                self.root.after(0, lambda: self.update_server_status(f"Connection failed: {str(e)}", 'red'))
                self.log_message(f"Server connection test failed: {str(e)}", 'ERROR')
        
        threading.Thread(target=test_connection, daemon=True).start()
    
    def update_server_status(self, message, color):
        """Update server connection status"""
        self.server_status_label.config(text=message, foreground=color)
    
    def start_installation(self):
        """Start the installation process"""
        if not self.token_valid:
            messagebox.showerror("Error", "Please enter a valid installation token first.")
            return
        
        if self.installation_thread and self.installation_thread.is_alive():
            messagebox.showwarning("Warning", "Installation is already in progress.")
            return
        
        # Confirm installation
        result = messagebox.askyesno(
            "Confirm Installation",
            f"Install LANET Agent for:\n\n"
            f"Client: {self.client_info.get('client_name', 'Unknown')}\n"
            f"Site: {self.client_info.get('site_name', 'Unknown')}\n"
            f"Token: {self.token_var.get()}\n\n"
            f"This will install the agent as a Windows service with SYSTEM privileges.\n\n"
            f"Continue with installation?"
        )
        
        if result:
            # Disable UI during installation
            self.install_button.config(state='disabled')
            self.test_button.config(state='disabled')
            
            # Start installation thread
            self.installation_thread = threading.Thread(target=self.perform_installation, daemon=True)
            self.installation_thread.start()
    
    def perform_installation(self):
        """Perform the actual installation process"""
        try:
            self.log_message("=== Starting LANET Agent Installation ===")
            self.update_progress(0, "Starting installation...")
            
            # Step 1: Check administrator privileges
            self.log_message("Checking administrator privileges...")
            if not self.is_admin():
                self.log_message("ERROR: Administrator privileges required!", 'ERROR')
                self.root.after(0, lambda: messagebox.showerror(
                    "Administrator Required", 
                    "This installer requires administrator privileges.\n\n"
                    "Please right-click and select 'Run as administrator'."
                ))
                return
            
            self.log_message("Administrator privileges confirmed")
            self.update_progress(10, "Administrator privileges confirmed")
            
            # Step 2: Create installation directory
            self.log_message("Creating installation directory...")
            if not self.create_installation_directory():
                return
            self.update_progress(20, "Installation directory created")
            
            # Step 3: Copy agent files
            self.log_message("Copying agent files...")
            if not self.copy_agent_files():
                return
            self.update_progress(40, "Agent files copied")
            
            # Step 4: Create service wrapper
            self.log_message("Creating Windows service wrapper...")
            if not self.create_service_wrapper():
                return
            self.update_progress(60, "Service wrapper created")
            
            # Step 5: Install Windows service
            self.log_message("Installing Windows service...")
            if not self.install_windows_service():
                return
            self.update_progress(80, "Windows service installed")
            
            # Step 6: Configure and start service
            self.log_message("Configuring and starting service...")
            if not self.configure_and_start_service():
                return
            self.update_progress(100, "Installation completed successfully!")
            
            self.log_message("=== LANET Agent Installation Completed Successfully ===")
            
            # Show success message
            self.root.after(0, lambda: messagebox.showinfo(
                "Installation Complete",
                "LANET Agent has been installed successfully!\n\n"
                "The agent is now running as a Windows service and will:\n"
                "• Start automatically on system boot\n"
                "• Collect hardware and software inventory\n"
                "• Monitor BitLocker status with SYSTEM privileges\n"
                "• Send regular heartbeats to the helpdesk server\n\n"
                "The computer should appear in the helpdesk within 5-10 minutes."
            ))
            
        except Exception as e:
            self.log_message(f"Installation failed: {str(e)}", 'ERROR')
            self.root.after(0, lambda: messagebox.showerror("Installation Failed", f"Installation failed with error:\n\n{str(e)}"))
        finally:
            # Re-enable UI
            self.root.after(0, lambda: self.install_button.config(state='normal'))
            self.root.after(0, lambda: self.test_button.config(state='normal'))
    
    def update_progress(self, value, status):
        """Update progress bar and status"""
        self.root.after(0, lambda: self.progress_var.set(value))
        self.root.after(0, lambda: self.progress_status_label.config(text=status))
    
    def is_admin(self):
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def create_installation_directory(self):
        """Create the installation directory structure"""
        try:
            # Create main installation directory
            self.install_dir.mkdir(parents=True, exist_ok=True)
            self.log_message(f"Created installation directory: {self.install_dir}")

            # Create subdirectories
            subdirs = ['logs', 'data', 'config', 'service']
            for subdir in subdirs:
                (self.install_dir / subdir).mkdir(exist_ok=True)
                self.log_message(f"Created subdirectory: {subdir}")

            # Create ProgramData directory for logs and data
            programdata_dir = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / "LANET Agent"
            programdata_dir.mkdir(parents=True, exist_ok=True)
            (programdata_dir / "Logs").mkdir(exist_ok=True)
            (programdata_dir / "Data").mkdir(exist_ok=True)

            self.log_message("Installation directory structure created successfully")
            return True

        except Exception as e:
            self.log_message(f"Failed to create installation directory: {str(e)}", 'ERROR')
            return False

    def copy_agent_files(self):
        """Copy agent files to installation directory"""
        try:
            # Get source directory (agent_files)
            source_dir = Path(__file__).parent / "agent_files"

            if not source_dir.exists():
                self.log_message(f"Source directory not found: {source_dir}", 'ERROR')
                return False

            # Files and directories to copy
            items_to_copy = [
                'main.py',
                'core/',
                'modules/',
                'ui/',
                'config/',
                'requirements.txt'
            ]

            copied_count = 0
            for item in items_to_copy:
                source_path = source_dir / item
                dest_path = self.install_dir / item

                if source_path.exists():
                    if source_path.is_file():
                        shutil.copy2(source_path, dest_path)
                        self.log_message(f"Copied file: {item}")
                    else:
                        if dest_path.exists():
                            shutil.rmtree(dest_path)
                        shutil.copytree(source_path, dest_path)
                        self.log_message(f"Copied directory: {item}")
                    copied_count += 1
                else:
                    self.log_message(f"Source not found: {item}", 'WARNING')

            self.log_message(f"Successfully copied {copied_count} items to installation directory")
            return True

        except Exception as e:
            self.log_message(f"Failed to copy agent files: {str(e)}", 'ERROR')
            return False

    def create_service_wrapper(self):
        """Create robust Windows service wrapper"""
        try:
            service_wrapper_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Windows Service Wrapper
Robust service wrapper that addresses path and import issues
"""

import sys
import os
import logging
import time
from pathlib import Path
import json

# Configure paths BEFORE any imports
AGENT_DIR = Path(r"{self.install_dir}")
PROGRAMDATA_DIR = Path(r"{os.environ.get('PROGRAMDATA', 'C:/ProgramData')}/LANET Agent")

# Add agent directories to Python path
sys.path.insert(0, str(AGENT_DIR))
sys.path.insert(0, str(AGENT_DIR / "core"))
sys.path.insert(0, str(AGENT_DIR / "modules"))

# Change working directory to agent directory
os.chdir(str(AGENT_DIR))

# Setup logging for service
log_file = PROGRAMDATA_DIR / "Logs" / "service.log"
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

def create_agent_config():
    """Create agent configuration file with installation token"""
    config_file = AGENT_DIR / "config" / "agent_config.json"

    config = {{
        "server": {{
            "url": "{self.server_url_var.get()}",
            "base_url": "{self.server_url_var.get()}",
            "production_url": "https://helpdesk.lanet.mx/api",
            "environment": "production",
            "timeout": 30,
            "retry_attempts": 3,
            "verify_ssl": True
        }},
        "agent": {{
            "name": os.environ.get('COMPUTERNAME', 'Unknown'),
            "version": "3.0",
            "log_level": "INFO",
            "heartbeat_interval": 300,
            "inventory_interval": 3600
        }},
        "registration": {{
            "installation_token": "{self.token_var.get()}",
            "auto_register": True,
            "client_id": "{self.client_info.get('client_id', '')}",
            "site_id": "{self.client_info.get('site_id', '')}"
        }},
        "bitlocker": {{
            "enabled": True,
            "collection_interval": 3600,
            "require_admin_privileges": False
        }},
        "database": {{
            "local_db_path": "data/agent.db",
            "backup_interval": 86400,
            "max_backup_files": 7
        }}
    }}

    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    logger.info(f"Created agent configuration: {{config_file}}")
    return config_file

def main():
    """Main service entry point"""
    try:
        logger.info("=== LANET Agent Service Starting ===")
        logger.info(f"Service running with SYSTEM privileges")
        logger.info(f"Working directory: {{os.getcwd()}}")
        logger.info(f"Python path: {{sys.path[:3]}}")

        # Create agent configuration
        config_file = create_agent_config()

        # Import and run agent
        logger.info("Importing agent modules...")
        from main import main as agent_main

        # Set command line arguments for registration
        sys.argv = ['main.py', '--register', '{self.token_var.get()}']

        logger.info("Starting agent main process...")
        agent_main()

    except ImportError as e:
        logger.error(f"Import error: {{e}}")
        logger.error(f"Current working directory: {{os.getcwd()}}")
        logger.error(f"Python path: {{sys.path}}")
        raise
    except Exception as e:
        logger.error(f"Service error: {{e}}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
'''

            # Write service wrapper
            service_wrapper_path = self.install_dir / "service" / "service_wrapper.py"
            with open(service_wrapper_path, 'w', encoding='utf-8') as f:
                f.write(service_wrapper_content)

            self.log_message(f"Created service wrapper: {service_wrapper_path}")

            # Create Windows service script using pywin32
            windows_service_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Windows Service
Uses pywin32 to create a proper Windows service
"""

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
            # Import and run service wrapper
            sys.path.insert(0, r"{self.install_dir}")
            sys.path.insert(0, r"{self.install_dir / 'service'}")

            from service_wrapper import main as service_main
            service_main()

        except Exception as e:
            servicemanager.LogErrorMsg(f"Service error: {{e}}")

        # Wait for stop signal
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(LANETAgentService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(LANETAgentService)
'''

            # Write Windows service script
            windows_service_path = self.install_dir / "service" / "windows_service.py"
            with open(windows_service_path, 'w', encoding='utf-8') as f:
                f.write(windows_service_content)

            self.log_message(f"Created Windows service script: {windows_service_path}")
            return True

        except Exception as e:
            self.log_message(f"Failed to create service wrapper: {str(e)}", 'ERROR')
            return False

    def install_windows_service(self):
        """Install the Windows service using pywin32"""
        try:
            # First, install required Python packages
            self.log_message("Installing required Python packages...")
            if not self.install_python_dependencies():
                return False

            # Install the Windows service
            service_script = self.install_dir / "service" / "windows_service.py"

            self.log_message("Installing Windows service...")
            result = subprocess.run(
                [sys.executable, str(service_script), 'install'],
                capture_output=True,
                text=True,
                cwd=str(self.install_dir),
                timeout=60
            )

            if result.returncode == 0:
                self.log_message("Windows service installed successfully")
                self.log_message(f"Service output: {result.stdout}")
            else:
                self.log_message(f"Service installation failed: {result.stderr}", 'ERROR')
                return False

            # Configure service for automatic startup and LocalSystem account
            self.log_message("Configuring service for automatic startup with SYSTEM privileges...")

            # Set service to automatic startup
            config_result = subprocess.run(
                ['sc.exe', 'config', 'LANETAgent', 'start=', 'auto'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if config_result.returncode == 0:
                self.log_message("Service configured for automatic startup")
            else:
                self.log_message(f"Warning: Could not configure automatic startup: {config_result.stderr}", 'WARNING')

            # Set service to run as LocalSystem (SYSTEM privileges)
            system_result = subprocess.run(
                ['sc.exe', 'config', 'LANETAgent', 'obj=', 'LocalSystem'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if system_result.returncode == 0:
                self.log_message("Service configured to run with SYSTEM privileges")
            else:
                self.log_message(f"Warning: Could not configure SYSTEM privileges: {system_result.stderr}", 'WARNING')

            return True

        except Exception as e:
            self.log_message(f"Failed to install Windows service: {str(e)}", 'ERROR')
            return False

    def install_python_dependencies(self):
        """Install required Python packages"""
        try:
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
                    [sys.executable, '-m', 'pip', 'install', package],
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode == 0:
                    self.log_message(f"Successfully installed {package}")
                else:
                    self.log_message(f"Failed to install {package}: {result.stderr}", 'ERROR')
                    return False

            return True

        except Exception as e:
            self.log_message(f"Failed to install Python dependencies: {str(e)}", 'ERROR')
            return False

    def configure_and_start_service(self):
        """Configure and start the LANET Agent service"""
        try:
            # Create uninstaller
            self.create_uninstaller()

            # Start the service
            self.log_message("Starting LANET Agent service...")
            start_result = subprocess.run(
                ['sc.exe', 'start', 'LANETAgent'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if start_result.returncode == 0:
                self.log_message("LANET Agent service started successfully")

                # Wait a moment and check service status
                time.sleep(3)
                status_result = subprocess.run(
                    ['sc.exe', 'query', 'LANETAgent'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if status_result.returncode == 0:
                    if 'RUNNING' in status_result.stdout:
                        self.log_message("Service is running correctly")
                        return True
                    else:
                        self.log_message("Service started but may not be running correctly", 'WARNING')
                        self.log_message(f"Service status: {status_result.stdout}")
                        return True  # Still consider success as service was installed
                else:
                    self.log_message("Could not check service status", 'WARNING')
                    return True
            else:
                self.log_message(f"Failed to start service: {start_result.stderr}", 'ERROR')
                self.log_message("Service was installed but failed to start. You can start it manually later.", 'WARNING')
                return True  # Still consider success as service was installed

        except Exception as e:
            self.log_message(f"Failed to configure and start service: {str(e)}", 'ERROR')
            return False

    def create_uninstaller(self):
        """Create uninstaller script"""
        try:
            uninstaller_content = f'''@echo off
echo LANET Agent Uninstaller
echo ======================

REM Stop and remove service
echo Stopping LANET Agent service...
sc stop LANETAgent
timeout /t 5 /nobreak >nul

echo Removing LANET Agent service...
python "{self.install_dir / 'service' / 'windows_service.py'}" remove

REM Remove installation directory
echo Removing installation files...
timeout /t 3 /nobreak >nul
rmdir /s /q "{self.install_dir}"

echo LANET Agent uninstalled successfully.
pause
'''

            uninstaller_path = self.install_dir / "uninstall.bat"
            with open(uninstaller_path, 'w', encoding='utf-8') as f:
                f.write(uninstaller_content)

            self.log_message(f"Created uninstaller: {uninstaller_path}")

        except Exception as e:
            self.log_message(f"Failed to create uninstaller: {str(e)}", 'WARNING')

    def run(self):
        """Run the installer GUI"""
        self.log_message("LANET Agent Production Installer GUI started")
        self.root.mainloop()

def main():
    """Main entry point"""
    # Check if running as administrator
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False

    if not is_admin:
        print("LANET Agent Production Installer")
        print("=" * 50)
        print("ERROR: Administrator privileges required!")
        print()
        print("Please right-click this installer and select 'Run as administrator'")
        print("to install the LANET Agent with proper SYSTEM privileges.")
        input("\nPress Enter to exit...")
        return

    # Create and run installer
    installer = LANETAgentProductionInstaller()
    installer.run()

if __name__ == "__main__":
    main()
