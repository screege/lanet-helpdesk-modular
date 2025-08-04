#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Production Installer - GUI Interface
Professional Windows installer with real-time token validation
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

class LANETAgentInstaller:
    """Professional LANET Agent Installer with GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_logging()

        # Installation parameters (initialize BEFORE setup_ui)
        self.token_var = tk.StringVar()
        self.server_url_var = tk.StringVar(value="http://localhost:5001/api")  # Default to local for development
        self.install_dir = Path("C:/Program Files/LANET Agent")

        # Validation state
        self.token_valid = False
        self.client_info = None
        self.installation_thread = None
        self.validation_thread = None

        # Setup UI after variables are initialized
        self.setup_ui()

        # Bind token validation
        self.token_var.trace('w', self.on_token_change)
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / "LANET Agent" / "Logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"installer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('LANETInstaller')
        self.logger.info("LANET Agent Installer started")
    
    def setup_ui(self):
        """Setup professional GUI interface"""
        self.root.title("LANET Agent Installer")
        self.root.geometry("600x700")  # Increased height to show all elements
        self.root.resizable(True, True)  # Allow resizing
        
        # Set icon (if available)
        try:
            self.root.iconbitmap("assets/lanet_icon.ico")
        except:
            pass
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="LANET Helpdesk Agent", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        subtitle_label = ttk.Label(header_frame, text="Professional MSP Agent Installation", 
                                  font=('Arial', 10))
        subtitle_label.grid(row=1, column=0, sticky=tk.W)
        
        # Token input section
        token_frame = ttk.LabelFrame(main_frame, text="Installation Token", padding="10")
        token_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(token_frame, text="Enter your installation token:").grid(row=0, column=0, sticky=tk.W)
        
        token_entry_frame = ttk.Frame(token_frame)
        token_entry_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.token_entry = ttk.Entry(token_entry_frame, textvariable=self.token_var, 
                                    font=('Consolas', 10), width=40)
        self.token_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Validation indicator
        self.validation_label = ttk.Label(token_entry_frame, text="", font=('Arial', 10))
        self.validation_label.grid(row=0, column=1, padx=(10, 0))
        
        # Client info display
        self.client_info_label = ttk.Label(token_frame, text="", font=('Arial', 9), 
                                          foreground='blue')
        self.client_info_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        # Server URL section
        server_frame = ttk.LabelFrame(main_frame, text="Server Configuration", padding="10")
        server_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(server_frame, text="Server URL:").grid(row=0, column=0, sticky=tk.W)
        
        server_entry = ttk.Entry(server_frame, textvariable=self.server_url_var, 
                                font=('Consolas', 9), width=50)
        server_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Installation options
        options_frame = ttk.LabelFrame(main_frame, text="Installation Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.cleanup_var = tk.BooleanVar(value=True)
        cleanup_check = ttk.Checkbutton(options_frame, text="Clean up existing installation", 
                                       variable=self.cleanup_var)
        cleanup_check.grid(row=0, column=0, sticky=tk.W)
        
        self.autostart_var = tk.BooleanVar(value=True)
        autostart_check = ttk.Checkbutton(options_frame, text="Start service automatically", 
                                         variable=self.autostart_var)
        autostart_check.grid(row=1, column=0, sticky=tk.W)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Installation Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_var = tk.StringVar(value="Ready to install")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Installation Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=70, 
                                                 font=('Consolas', 8))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.install_button = ttk.Button(button_frame, text="Install Agent", 
                                        command=self.start_installation, state='disabled')
        self.install_button.grid(row=0, column=0, padx=(0, 10))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", 
                                       command=self.cancel_installation)
        self.cancel_button.grid(row=0, column=1, padx=(0, 10))
        
        self.close_button = ttk.Button(button_frame, text="Close", 
                                      command=self.root.quit)
        self.close_button.grid(row=0, column=2)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Center window
        self.center_window()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def log_message(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        self.logger.info(message)
    
    def update_progress(self, value, message):
        """Update progress bar and message"""
        self.progress_bar['value'] = value
        self.progress_var.set(message)
        self.root.update_idletasks()
    
    def on_token_change(self, *args):
        """Handle token input change"""
        token = self.token_var.get().strip()
        
        if len(token) < 10:
            self.validation_label.config(text="", foreground='black')
            self.client_info_label.config(text="")
            self.install_button.config(state='disabled')
            self.token_valid = False
            return
        
        # Start validation in background
        if self.validation_thread and self.validation_thread.is_alive():
            return  # Already validating
        
        self.validation_thread = threading.Thread(target=self.validate_token, args=(token,))
        self.validation_thread.daemon = True
        self.validation_thread.start()
    
    def validate_token(self, token):
        """Validate token against database"""
        try:
            self.root.after(0, lambda: self.validation_label.config(text="Validating...", foreground='orange'))
            
            # Connect to database
            conn = psycopg2.connect(
                host='localhost',
                port='5432',
                database='lanet_helpdesk',
                user='postgres',
                password='Poikl55+*'
            )
            
            cur = conn.cursor()
            
            # Validate token
            cur.execute("""
                SELECT t.token_id, t.client_id, t.site_id, t.is_active, t.expires_at,
                       c.name as client_name, s.name as site_name
                FROM agent_installation_tokens t
                JOIN clients c ON t.client_id = c.client_id
                JOIN sites s ON t.site_id = s.site_id
                WHERE t.token_value = %s
            """, (token,))
            
            result = cur.fetchone()
            conn.close()
            
            if result:
                token_id, client_id, site_id, is_active, expires_at, client_name, site_name = result
                
                if not is_active:
                    self.root.after(0, lambda: self.validation_label.config(text="✗ Inactive", foreground='red'))
                    self.root.after(0, lambda: self.client_info_label.config(text="Token is inactive"))
                    self.token_valid = False
                elif expires_at and expires_at < datetime.now():
                    self.root.after(0, lambda: self.validation_label.config(text="✗ Expired", foreground='red'))
                    self.root.after(0, lambda: self.client_info_label.config(text="Token has expired"))
                    self.token_valid = False
                else:
                    self.root.after(0, lambda: self.validation_label.config(text="✓ Valid", foreground='green'))
                    self.root.after(0, lambda: self.client_info_label.config(text=f"Client: {client_name} | Site: {site_name}"))
                    self.token_valid = True
                    self.client_info = {
                        'token_id': token_id,
                        'client_id': client_id,
                        'site_id': site_id,
                        'client_name': client_name,
                        'site_name': site_name
                    }
            else:
                self.root.after(0, lambda: self.validation_label.config(text="✗ Invalid", foreground='red'))
                self.root.after(0, lambda: self.client_info_label.config(text="Token not found"))
                self.token_valid = False
            
            # Update install button state
            self.root.after(0, lambda: self.install_button.config(
                state='normal' if self.token_valid else 'disabled'
            ))
            
        except Exception as e:
            self.logger.error(f"Token validation error: {e}")
            self.root.after(0, lambda: self.validation_label.config(text="✗ Error", foreground='red'))
            self.root.after(0, lambda: self.client_info_label.config(text="Validation failed - check connection"))
            self.token_valid = False
    
    def start_installation(self):
        """Start the installation process"""
        if not self.token_valid:
            messagebox.showerror("Error", "Please enter a valid installation token")
            return
        
        if not self.is_admin():
            messagebox.showerror("Error", "Administrator privileges required.\nPlease run as Administrator.")
            return
        
        # Disable UI during installation
        self.install_button.config(state='disabled')
        self.token_entry.config(state='disabled')
        
        # Start installation in background thread
        self.installation_thread = threading.Thread(target=self.perform_installation)
        self.installation_thread.daemon = True
        self.installation_thread.start()
    
    def is_admin(self):
        """Check if running as administrator"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def perform_installation(self):
        """Perform the actual installation"""
        try:
            self.log_message("Starting LANET Agent installation...")
            self.update_progress(0, "Initializing installation...")
            
            # Step 1: Cleanup existing installation
            if self.cleanup_var.get():
                self.update_progress(10, "Cleaning up existing installation...")
                self.cleanup_existing_installation()
            
            # Step 2: Create installation directory
            self.update_progress(20, "Creating installation directory...")
            self.create_installation_directory()
            
            # Step 3: Copy agent files
            self.update_progress(30, "Copying agent files...")
            self.copy_agent_files()
            
            # Step 4: Create configuration
            self.update_progress(50, "Creating configuration...")
            self.create_configuration()
            
            # Step 5: Install Windows service
            self.update_progress(70, "Installing Windows service...")
            self.install_windows_service()
            
            # Step 6: Start service
            if self.autostart_var.get():
                self.update_progress(90, "Starting service...")
                self.start_service()
            
            # Step 7: Complete
            self.update_progress(100, "Installation completed successfully!")
            self.log_message("✅ LANET Agent installed successfully!")
            
            # Show success dialog
            self.root.after(0, lambda: messagebox.showinfo(
                "Installation Complete", 
                f"LANET Agent has been installed successfully!\n\n"
                f"Client: {self.client_info['client_name']}\n"
                f"Site: {self.client_info['site_name']}\n\n"
                f"The agent is now running and will appear in your dashboard shortly."
            ))
            
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            self.log_message(f"❌ Installation failed: {e}")
            self.update_progress(0, "Installation failed")
            
            self.root.after(0, lambda: messagebox.showerror(
                "Installation Failed", 
                f"Installation failed with error:\n\n{str(e)}\n\n"
                f"Please check the installation log for details."
            ))
        
        finally:
            # Re-enable UI
            self.root.after(0, lambda: self.install_button.config(state='normal' if self.token_valid else 'disabled'))
            self.root.after(0, lambda: self.token_entry.config(state='normal'))
    
    def cleanup_existing_installation(self):
        """Clean up existing LANET Agent installation"""
        self.log_message("Cleaning up existing installation...")
        
        try:
            # Stop service
            subprocess.run(['sc.exe', 'stop', 'LANETAgent'], capture_output=True)
            self.log_message("Stopped existing service")
            
            # Remove service
            subprocess.run(['sc.exe', 'delete', 'LANETAgent'], capture_output=True)
            self.log_message("Removed existing service")
            
            # Kill processes
            subprocess.run(['taskkill', '/F', '/IM', 'LANET_Agent.exe'], capture_output=True)
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
            
            # Wait for processes to terminate
            time.sleep(2)
            
            # Remove directory
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir)
                self.log_message("Removed existing installation directory")
            
        except Exception as e:
            self.log_message(f"Cleanup warning: {e}")
    
    def create_installation_directory(self):
        """Create installation directory structure"""
        self.log_message("Creating installation directory...")
        
        directories = [
            self.install_dir,
            self.install_dir / "logs",
            self.install_dir / "data",
            self.install_dir / "config",
            self.install_dir / "core",
            self.install_dir / "modules",
            self.install_dir / "ui",
            self.install_dir / "service"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.log_message("Installation directories created")
    
    def copy_agent_files(self):
        """Copy agent files to installation directory"""
        self.log_message("Copying agent files...")
        
        # Get the directory where this installer is running from
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            source_dir = Path(sys._MEIPASS) / "agent_files"
        else:
            # Running as script
            source_dir = Path(__file__).parent.parent / "lanet_agent"
        
        if not source_dir.exists():
            raise Exception(f"Agent source files not found at: {source_dir}")
        
        # Copy files
        files_to_copy = [
            ("main.py", "main.py"),
            ("core", "core"),
            ("modules", "modules"),
            ("ui", "ui"),
            ("service", "service")
        ]
        
        for src_name, dst_name in files_to_copy:
            src_path = source_dir / src_name
            dst_path = self.install_dir / dst_name
            
            if src_path.exists():
                if src_path.is_file():
                    shutil.copy2(src_path, dst_path)
                    self.log_message(f"Copied: {src_name}")
                else:
                    if dst_path.exists():
                        shutil.rmtree(dst_path)
                    shutil.copytree(src_path, dst_path)
                    self.log_message(f"Copied directory: {src_name}")
            else:
                self.log_message(f"Warning: {src_name} not found")
    
    def create_configuration(self):
        """Create agent configuration"""
        self.log_message("Creating agent configuration...")
        
        config = {
            "server": {
                "url": self.server_url_var.get(),
                "base_url": self.server_url_var.get(),
                "production_url": self.server_url_var.get(),
                "timeout": 30,
                "retry_attempts": 3,
                "verify_ssl": True,
                "environment": "production"
            },
            "agent": {
                "name": os.environ.get('COMPUTERNAME', 'Unknown'),
                "version": "3.0",
                "log_level": "INFO",
                "heartbeat_interval": 300,
                "inventory_interval": 3600
            },
            "registration": {
                "installation_token": self.token_var.get().strip(),
                "auto_register": True,
                "client_id": str(self.client_info['client_id']),
                "site_id": str(self.client_info['site_id'])
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
        
        config_path = self.install_dir / "config" / "agent_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.log_message("Configuration created successfully")
    
    def find_python_executable(self):
        """Find the correct Python executable"""
        import shutil

        # Try common Python locations
        python_paths = [
            shutil.which('python'),
            shutil.which('python.exe'),
            'C:\\Python310\\python.exe',
            'C:\\Python39\\python.exe',
            'C:\\Python311\\python.exe',
            'C:\\Python312\\python.exe',
        ]

        for path in python_paths:
            if path and Path(path).exists():
                self.log_message(f"Found Python at: {path}")
                return path

        # If we can't find Python, this is a critical error
        self.log_message("❌ Could not find Python executable")
        return None

    def install_windows_service(self):
        """Install as Windows service with proper SYSTEM privileges and immediate startup"""
        self.log_message("Installing Windows service...")

        # Create simple, reliable service runner that actually works
        service_runner = f'''
import sys
import os
import time
import logging
from pathlib import Path

# Setup environment immediately
install_dir = Path(r"{self.install_dir}")
os.chdir(str(install_dir))
sys.path.insert(0, str(install_dir))

# Set service mode environment variables
os.environ['LANET_SERVICE_MODE'] = '1'
os.environ['LANET_NO_UI'] = '1'
os.environ['LANET_AUTO_REGISTER'] = '1'

# Setup logging
log_dir = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / "LANET Agent" / "Logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'simple_service.log', encoding='utf-8'),
    ]
)

logger = logging.getLogger('LANETSimpleService')

def main():
    """Simple service main function"""
    try:
        logger.info("LANET Simple Service starting...")
        logger.info(f"Working directory: {{os.getcwd()}}")
        logger.info("Environment configured for service mode")

        # Import and run main agent directly
        logger.info("Importing main agent...")
        from main import main as agent_main

        logger.info("Starting agent main function...")
        agent_main()

    except Exception as e:
        logger.error(f"Service error: {{e}}", exc_info=True)
        # Wait before exit to prevent rapid restart
        time.sleep(10)

if __name__ == "__main__":
    main()
'''

        # Write simple service runner
        service_file = self.install_dir / "simple_service.py"
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write(service_runner)

        self.log_message("Simple service runner created")

        # Remove any existing service first
        self.log_message("Removing any existing service...")
        subprocess.run(['sc.exe', 'stop', 'LANETAgent'], capture_output=True)
        subprocess.run(['sc.exe', 'delete', 'LANETAgent'], capture_output=True)
        time.sleep(3)  # Wait for cleanup

        # Find the correct Python executable
        python_exe = self.find_python_executable()
        if not python_exe:
            raise Exception("Could not find Python executable")

        # Create service command
        service_cmd = f'"{python_exe}" "{service_file}"'

        self.log_message(f"Creating service with command: {service_cmd}")
        self.log_message(f"Python executable: {python_exe}")

        # Install service with minimal configuration first
        result = subprocess.run([
            'sc.exe', 'create', 'LANETAgent',
            'binPath=', service_cmd,
            'start=', 'demand',  # Manual start for testing
            'obj=', 'LocalSystem',
            'DisplayName=', 'LANET Helpdesk Agent'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            self.log_message("✅ Windows service created successfully")

            # Set service description
            subprocess.run([
                'sc.exe', 'description', 'LANETAgent',
                'LANET Helpdesk Agent - MSP monitoring and BitLocker collection'
            ], capture_output=True)

            self.log_message("Service description set")

        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            self.log_message(f"❌ Service creation failed: {error_msg}")
            raise Exception(f"Service creation failed: {error_msg}")
    
    def start_service(self):
        """Start the Windows service with comprehensive testing"""
        if not self.autostart_var.get():
            self.log_message("Auto-start disabled, skipping service start")
            return

        self.log_message("Testing service startup...")

        # First, try to start the service
        result = subprocess.run(['sc.exe', 'start', 'LANETAgent'],
                               capture_output=True, text=True)

        if result.returncode == 0:
            self.log_message("✅ Service start command successful")

            # Wait for service to initialize
            self.log_message("Waiting 15 seconds for service to initialize...")
            time.sleep(15)

            # Check service status
            status_result = subprocess.run(['sc.exe', 'query', 'LANETAgent'],
                                         capture_output=True, text=True)

            if status_result.returncode == 0 and "RUNNING" in status_result.stdout:
                self.log_message("✅ Service is running successfully")

                # Set service to auto start after successful test
                auto_result = subprocess.run([
                    'sc.exe', 'config', 'LANETAgent', 'start=', 'auto'
                ], capture_output=True, text=True)

                if auto_result.returncode == 0:
                    self.log_message("✅ Service configured for automatic startup")
                else:
                    self.log_message("⚠️ Could not set auto-start")

                # Check for log files
                log_dir = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / "LANET Agent" / "Logs"
                if log_dir.exists():
                    log_files = list(log_dir.glob("*.log"))
                    if log_files:
                        self.log_message("✅ Service is creating log files")

                        # Show last log entry
                        try:
                            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
                            with open(latest_log, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                if lines:
                                    self.log_message(f"Latest log: {lines[-1].strip()}")
                        except:
                            pass
                    else:
                        self.log_message("⚠️ No log files created yet")

            else:
                self.log_message("⚠️ Service started but not running properly")
                self.log_message("Checking service logs...")

                # Check Windows Event Log
                event_result = subprocess.run([
                    'powershell', '-Command',
                    'Get-WinEvent -LogName System -MaxEvents 2 | Where-Object {$_.Id -eq 7000 -or $_.Id -eq 7034} | Select-Object Message'
                ], capture_output=True, text=True)

                if event_result.returncode == 0 and event_result.stdout.strip():
                    self.log_message(f"Service error: {event_result.stdout}")

        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            self.log_message(f"❌ Service start failed: {error_msg}")

            # Don't fail installation, just warn
            self.log_message("⚠️ Service installed but not started")
            self.log_message("You can start it manually from Windows Services")
    
    def cancel_installation(self):
        """Cancel the installation"""
        if self.installation_thread and self.installation_thread.is_alive():
            # Installation is running, ask for confirmation
            if messagebox.askyesno("Cancel Installation", 
                                  "Installation is in progress. Are you sure you want to cancel?"):
                self.root.quit()
        else:
            self.root.quit()
    
    def run(self):
        """Run the installer GUI"""
        self.root.mainloop()

def main():
    """Main installer function"""
    import argparse

    parser = argparse.ArgumentParser(description='LANET Agent Installer')
    parser.add_argument('--silent', action='store_true', help='Silent installation mode')
    parser.add_argument('--token', help='Installation token')
    parser.add_argument('--server-url', default='https://helpdesk.lanet.mx/api', help='Server URL')
    parser.add_argument('--install-dir', help='Installation directory')

    args = parser.parse_args()

    if args.silent:
        # Silent installation mode
        from .silent_installer import SilentInstaller
        installer = SilentInstaller(args.token, args.server_url, args.install_dir)
        exit_code = installer.install()
        sys.exit(exit_code)
    else:
        # GUI installation mode
        try:
            installer = LANETAgentInstaller()
            installer.run()
        except Exception as e:
            messagebox.showerror("Installer Error", f"Failed to start installer: {e}")

if __name__ == "__main__":
    main()
