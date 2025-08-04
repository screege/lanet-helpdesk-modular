#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Production Installer - Main Entry Point
Handles both GUI and silent installation modes
"""

import sys
import os
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='LANET Agent Production Installer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  GUI Mode (default):
    LANET_Agent_Installer.exe
    
  Silent Mode:
    LANET_Agent_Installer.exe --silent --token "LANET-75F6-EC23-03BBDB" --server-url "https://helpdesk.lanet.mx/api"
    
  Silent Mode with custom directory:
    LANET_Agent_Installer.exe --silent --token "LANET-XXXX-XXXX-XXXXXX" --install-dir "D:\\LANET Agent"

Exit Codes (Silent Mode):
  0 - Success
  1 - General error
  2 - Invalid token
  3 - Network error
  4 - Permission error
  5 - Already installed (upgrade performed)
        '''
    )
    
    # Installation mode
    parser.add_argument('--silent', action='store_true', 
                       help='Run in silent mode for automated deployment')
    
    # Installation parameters
    parser.add_argument('--token', 
                       help='Installation token (required for silent mode)')
    parser.add_argument('--server-url', 
                       default='https://helpdesk.lanet.mx/api',
                       help='Server URL (default: https://helpdesk.lanet.mx/api)')
    parser.add_argument('--install-dir', 
                       help='Installation directory (default: C:\\Program Files\\LANET Agent)')
    
    # Additional options
    parser.add_argument('--no-cleanup', action='store_true',
                       help='Skip cleanup of existing installation')
    parser.add_argument('--no-autostart', action='store_true',
                       help='Do not start service automatically after installation')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    
    # Version and help
    parser.add_argument('--version', action='version', version='LANET Agent Installer 3.0')
    
    return parser.parse_args()

def validate_silent_mode_args(args):
    """Validate arguments for silent mode"""
    if args.silent and not args.token:
        print("ERROR: --token is required for silent mode installation")
        print("Use --help for usage information")
        return False
    
    if args.token and len(args.token.strip()) < 10:
        print("ERROR: Invalid token format")
        return False
    
    return True

def run_gui_installer():
    """Run the GUI installer"""
    try:
        from installer_gui import LANETAgentInstaller
        installer = LANETAgentInstaller()
        installer.run()
        return 0
    except ImportError as e:
        print(f"ERROR: Failed to import GUI installer: {e}")
        print("GUI components may not be available in this build")
        return 1
    except Exception as e:
        print(f"ERROR: GUI installer failed: {e}")
        return 1

def run_silent_installer(args):
    """Run the silent installer"""
    try:
        from silent_installer import SilentInstaller
        
        installer = SilentInstaller(
            token=args.token,
            server_url=args.server_url,
            install_dir=args.install_dir
        )
        
        # Set additional options
        installer.cleanup_existing = not args.no_cleanup
        installer.autostart_service = not args.no_autostart
        installer.log_level = args.log_level
        
        return installer.install()
        
    except ImportError as e:
        print(f"ERROR: Failed to import silent installer: {e}")
        return 1
    except Exception as e:
        print(f"ERROR: Silent installer failed: {e}")
        return 1

def check_system_requirements():
    """Check basic system requirements"""
    import platform
    
    # Check Windows version
    if platform.system() != 'Windows':
        print("ERROR: LANET Agent is only supported on Windows")
        return False
    
    # Check Python version (if running as script)
    if not getattr(sys, 'frozen', False):
        if sys.version_info < (3, 7):
            print("ERROR: Python 3.7 or higher is required")
            return False
    
    return True

def setup_logging(log_level):
    """Setup basic logging for main installer"""
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger('LANETMainInstaller')
    logger.info(f"LANET Agent Installer starting (log level: {log_level})")
    
    return logger

def print_banner():
    """Print installer banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    LANET Agent Installer                    ║
║                     Version 3.0                             ║
║                                                              ║
║  Professional MSP Agent with BitLocker Recovery Key         ║
║  Collection and Real-time System Monitoring                 ║
║                                                              ║
║  © 2025 Lanet Systems - All Rights Reserved                 ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def main():
    """Main installer entry point"""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Setup logging
        logger = setup_logging(args.log_level)
        
        # Print banner for GUI mode or verbose silent mode
        if not args.silent or args.log_level == 'DEBUG':
            print_banner()
        
        # Check system requirements
        if not check_system_requirements():
            return 1
        
        # Validate arguments for silent mode
        if not validate_silent_mode_args(args):
            return 2
        
        # Log installation mode
        mode = "Silent" if args.silent else "GUI"
        logger.info(f"Starting {mode} installation mode")
        
        if args.silent:
            logger.info(f"Token: {args.token[:10]}..." if args.token else "No token")
            logger.info(f"Server URL: {args.server_url}")
            logger.info(f"Install Directory: {args.install_dir or 'Default'}")
        
        # Run appropriate installer
        if args.silent:
            exit_code = run_silent_installer(args)
        else:
            exit_code = run_gui_installer()
        
        # Log completion
        if exit_code == 0:
            logger.info("Installation completed successfully")
        else:
            logger.error(f"Installation failed with exit code: {exit_code}")
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user")
        return 1
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
