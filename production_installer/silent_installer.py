#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Silent Installer
Command-line installer for mass deployment via GPO/SCCM/RMM
"""

import os
import sys
import subprocess
import shutil
import json
import time
import ctypes
import psycopg2
from pathlib import Path
from datetime import datetime
import logging

class SilentInstaller:
    """Silent installer for LANET Agent with enterprise deployment support"""
    
    # Exit codes for enterprise deployment
    EXIT_SUCCESS = 0
    EXIT_GENERAL_ERROR = 1
    EXIT_INVALID_TOKEN = 2
    EXIT_NETWORK_ERROR = 3
    EXIT_PERMISSION_ERROR = 4
    EXIT_ALREADY_INSTALLED = 5
    
    def __init__(self, token, server_url, install_dir=None):
        self.token = token
        self.server_url = server_url or "https://helpdesk.lanet.mx/api"
        self.install_dir = Path(install_dir) if install_dir else Path("C:/Program Files/LANET Agent")
        
        self.setup_logging()
        self.client_info = None
        
    def setup_logging(self):
        """Setup comprehensive logging for silent installation"""
        log_dir = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / "LANET Agent" / "Logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"silent_install_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('LANETSilentInstaller')
        self.logger.info("LANET Agent Silent Installer started")
        self.logger.info(f"Token: {self.token[:10]}..." if self.token else "No token provided")
        self.logger.info(f"Server URL: {self.server_url}")
        self.logger.info(f"Install Directory: {self.install_dir}")
    
    def install(self):
        """Perform silent installation"""
        try:
            self.logger.info("Starting silent installation...")
            
            # Pre-installation checks
            if not self.pre_installation_checks():
                return self.EXIT_PERMISSION_ERROR
            
            # Validate token
            if not self.validate_token():
                return self.EXIT_INVALID_TOKEN
            
            # Check if already installed
            if self.is_already_installed():
                self.logger.info("LANET Agent already installed - performing upgrade")
            
            # Perform installation steps
            self.cleanup_existing_installation()
            self.create_installation_directory()
            self.copy_agent_files()
            self.create_configuration()
            self.install_windows_service()
            self.start_service()
            
            self.logger.info("✅ Silent installation completed successfully")
            return self.EXIT_SUCCESS
            
        except Exception as e:
            self.logger.error(f"❌ Silent installation failed: {e}")
            return self.EXIT_GENERAL_ERROR
    
    def pre_installation_checks(self):
        """Perform pre-installation system checks"""
        self.logger.info("Performing pre-installation checks...")
        
        # Check administrator privileges
        if not self.is_admin():
            self.logger.error("Administrator privileges required")
            return False
        
        # Check Windows version
        if not self.check_windows_version():
            self.logger.error("Unsupported Windows version")
            return False
        
        # Check disk space (minimum 100MB)
        if not self.check_disk_space():
            self.logger.error("Insufficient disk space")
            return False
        
        # Check network connectivity
        if not self.check_network_connectivity():
            self.logger.error("Network connectivity check failed")
            return False
        
        self.logger.info("✅ Pre-installation checks passed")
        return True
    
    def is_admin(self):
        """Check if running as administrator"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def check_windows_version(self):
        """Check if Windows version is supported"""
        try:
            import platform
            version = platform.version()
            # Windows 10 and 11 are supported
            major_version = int(version.split('.')[0])
            return major_version >= 10
        except:
            return True  # Assume supported if can't determine
    
    def check_disk_space(self):
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.install_dir.parent)
            free_mb = free // (1024 * 1024)
            return free_mb >= 100  # Minimum 100MB
        except:
            return True  # Assume sufficient if can't determine
    
    def check_network_connectivity(self):
        """Check network connectivity to server"""
        try:
            import requests
            response = requests.get(f"{self.server_url}/health", timeout=10)
            return response.status_code == 200
        except:
            # If health endpoint doesn't exist, try basic connectivity
            try:
                import socket
                from urllib.parse import urlparse
                parsed = urlparse(self.server_url)
                host = parsed.hostname or 'localhost'
                port = parsed.port or (443 if parsed.scheme == 'https' else 80)
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()
                return result == 0
            except:
                return False
    
    def validate_token(self):
        """Validate installation token against database"""
        if not self.token:
            self.logger.error("No installation token provided")
            return False
        
        self.logger.info("Validating installation token...")
        
        try:
            # Connect to database (try localhost first, then remote)
            conn = None
            try:
                conn = psycopg2.connect(
                    host='localhost',
                    port='5432',
                    database='lanet_helpdesk',
                    user='postgres',
                    password='Poikl55+*',
                    connect_timeout=5
                )
            except:
                # If localhost fails, try to extract host from server URL
                from urllib.parse import urlparse
                parsed = urlparse(self.server_url)
                if parsed.hostname and parsed.hostname != 'localhost':
                    conn = psycopg2.connect(
                        host=parsed.hostname,
                        port='5432',
                        database='lanet_helpdesk',
                        user='postgres',
                        password='Poikl55+*',
                        connect_timeout=10
                    )
                else:
                    raise Exception("Cannot connect to database")
            
            cur = conn.cursor()
            
            # Validate token
            cur.execute("""
                SELECT t.token_id, t.client_id, t.site_id, t.is_active, t.expires_at,
                       c.name as client_name, s.name as site_name
                FROM agent_installation_tokens t
                JOIN clients c ON t.client_id = c.client_id
                JOIN sites s ON t.site_id = s.site_id
                WHERE t.token_value = %s
            """, (self.token,))
            
            result = cur.fetchone()
            conn.close()
            
            if not result:
                self.logger.error("Invalid installation token")
                return False
            
            token_id, client_id, site_id, is_active, expires_at, client_name, site_name = result
            
            if not is_active:
                self.logger.error("Installation token is inactive")
                return False
            
            if expires_at and expires_at < datetime.now():
                self.logger.error("Installation token has expired")
                return False
            
            self.client_info = {
                'token_id': token_id,
                'client_id': client_id,
                'site_id': site_id,
                'client_name': client_name,
                'site_name': site_name
            }
            
            self.logger.info(f"✅ Token validated - Client: {client_name}, Site: {site_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Token validation failed: {e}")
            return False
    
    def is_already_installed(self):
        """Check if LANET Agent is already installed"""
        try:
            # Check if service exists
            result = subprocess.run(['sc.exe', 'query', 'LANETAgent'], 
                                   capture_output=True, text=True)
            service_exists = result.returncode == 0
            
            # Check if installation directory exists
            dir_exists = self.install_dir.exists()
            
            return service_exists or dir_exists
            
        except:
            return False
    
    def cleanup_existing_installation(self):
        """Clean up existing LANET Agent installation"""
        self.logger.info("Cleaning up existing installation...")
        
        try:
            # Stop service
            subprocess.run(['sc.exe', 'stop', 'LANETAgent'], capture_output=True)
            self.logger.info("Stopped existing service")
            
            # Remove service
            subprocess.run(['sc.exe', 'delete', 'LANETAgent'], capture_output=True)
            self.logger.info("Removed existing service")
            
            # Kill processes
            subprocess.run(['taskkill', '/F', '/IM', 'LANET_Agent.exe'], capture_output=True)
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
            
            # Wait for processes to terminate
            time.sleep(3)
            
            # Remove directory
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir)
                self.logger.info("Removed existing installation directory")
            
        except Exception as e:
            self.logger.warning(f"Cleanup warning: {e}")
    
    def create_installation_directory(self):
        """Create installation directory structure"""
        self.logger.info("Creating installation directory structure...")
        
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
        
        self.logger.info("✅ Installation directories created")
    
    def copy_agent_files(self):
        """Copy agent files to installation directory"""
        self.logger.info("Copying agent files...")
        
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
                    self.logger.info(f"Copied: {src_name}")
                else:
                    if dst_path.exists():
                        shutil.rmtree(dst_path)
                    shutil.copytree(src_path, dst_path)
                    self.logger.info(f"Copied directory: {src_name}")
            else:
                self.logger.warning(f"Source file not found: {src_name}")
        
        self.logger.info("✅ Agent files copied")
    
    def create_configuration(self):
        """Create agent configuration"""
        self.logger.info("Creating agent configuration...")
        
        config = {
            "server": {
                "url": self.server_url,
                "base_url": self.server_url,
                "production_url": self.server_url,
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
                "installation_token": self.token,
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
        
        self.logger.info("✅ Configuration created")
    
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
                self.logger.info(f"Found Python at: {path}")
                return path

        # If we can't find Python, this is a critical error
        self.logger.error("Could not find Python executable")
        return None

    def install_windows_service(self):
        """Install as Windows service with proper SYSTEM privileges"""
        self.logger.info("Installing Windows service...")

        # Create robust service runner script
        service_runner = f'''
import sys
import os
import time
import logging
from pathlib import Path

def setup_service_environment():
    """Setup proper service environment"""
    # Set working directory and path
    install_dir = Path(r"{self.install_dir}")
    os.chdir(str(install_dir))
    sys.path.insert(0, str(install_dir))

    # Set service mode environment variables
    os.environ['LANET_SERVICE_MODE'] = '1'
    os.environ['LANET_NO_UI'] = '1'
    os.environ['LANET_AUTO_REGISTER'] = '1'

    return install_dir

def setup_service_logging(install_dir):
    """Setup logging with SYSTEM privileges"""
    # Use ProgramData for logs (SYSTEM has write access)
    log_dir = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / "LANET Agent" / "Logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Also create logs in install dir as backup
    install_log_dir = install_dir / "logs"
    install_log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'agent_service.log', encoding='utf-8'),
            logging.FileHandler(install_log_dir / 'agent_service.log', encoding='utf-8'),
        ]
    )

    return logging.getLogger('LANETAgentService')

def run_agent_service():
    """Run the LANET Agent in service mode"""
    install_dir = None
    logger = None

    try:
        # Setup environment
        install_dir = setup_service_environment()
        logger = setup_service_logging(install_dir)

        logger.info("LANET Agent Service starting...")
        logger.info(f"Install directory: {{install_dir}}")
        logger.info(f"Working directory: {{os.getcwd()}}")
        logger.info("Service mode environment configured")

        # Import main agent
        from main import main as agent_main

        logger.info("Starting main agent in service mode...")

        # Run the main agent
        agent_main()

    except Exception as e:
        if logger:
            logger.error(f"Service error: {{e}}", exc_info=True)
        else:
            # Fallback logging if logger setup failed
            error_log = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / "LANET Agent" / "Logs" / "service_error.log"
            error_log.parent.mkdir(parents=True, exist_ok=True)
            with open(error_log, 'a', encoding='utf-8') as f:
                f.write(f"{{time.strftime('%Y-%m-%d %H:%M:%S')}} - CRITICAL ERROR: {{e}}\\n")

        # Wait before exit to prevent rapid restart
        time.sleep(10)

if __name__ == "__main__":
    run_agent_service()
'''

        # Write service runner
        service_file = self.install_dir / "run_agent_service.py"
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write(service_runner)

        self.logger.info("Service runner script created")

        # Remove any existing service first
        subprocess.run(['sc.exe', 'stop', 'LANETAgent'], capture_output=True)
        subprocess.run(['sc.exe', 'delete', 'LANETAgent'], capture_output=True)
        time.sleep(2)  # Wait for cleanup

        # Find the correct Python executable
        python_exe = self.find_python_executable()
        if not python_exe:
            raise Exception("Could not find Python executable")

        # Install service using sc.exe with proper configuration
        service_cmd = f'"{python_exe}" "{service_file}"'
        self.logger.info(f"Service command: {service_cmd}")

        result = subprocess.run([
            'sc.exe', 'create', 'LANETAgent',
            'binPath=', service_cmd,
            'start=', 'auto',
            'obj=', 'LocalSystem',
            'DisplayName=', 'LANET Helpdesk Agent',
            'depend=', 'Tcpip'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            self.logger.info("Windows service created successfully")

            # Configure service properties
            subprocess.run([
                'sc.exe', 'description', 'LANETAgent',
                'LANET Helpdesk Agent - Professional MSP monitoring and BitLocker recovery key collection'
            ], capture_output=True)

            # Set service failure recovery
            subprocess.run([
                'sc.exe', 'failure', 'LANETAgent',
                'reset=', '86400',
                'actions=', 'restart/10000/restart/30000/restart/60000'
            ], capture_output=True)

            # Set service to delayed auto start for better reliability
            subprocess.run([
                'sc.exe', 'config', 'LANETAgent', 'start=', 'delayed-auto'
            ], capture_output=True)

            self.logger.info("✅ Service configuration completed")
        else:
            raise Exception(f"Service creation failed: {result.stderr}")
    
    def start_service(self):
        """Start the Windows service"""
        self.logger.info("Starting LANET Agent service...")
        
        result = subprocess.run(['sc.exe', 'start', 'LANETAgent'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            self.logger.info("✅ Service started successfully")
        else:
            self.logger.warning(f"Service start warning: {result.stderr}")

def main():
    """Main function for silent installer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LANET Agent Silent Installer')
    parser.add_argument('--token', required=True, help='Installation token')
    parser.add_argument('--server-url', default='https://helpdesk.lanet.mx/api', help='Server URL')
    parser.add_argument('--install-dir', help='Installation directory')
    
    args = parser.parse_args()
    
    installer = SilentInstaller(args.token, args.server_url, args.install_dir)
    exit_code = installer.install()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
