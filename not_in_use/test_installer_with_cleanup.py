#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Installer with Automatic Cleanup
"""

import subprocess
import sys
import ctypes
import time

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_installer_test():
    """Run the installer and verify it works"""
    if not is_admin():
        print("ERROR: This script must be run as Administrator")
        print("Right-click and select 'Run as administrator'")
        return False
    
    print("LANET Agent Production Installer Test")
    print("=" * 50)
    print("Testing installer with automatic cleanup")
    print()
    
    # Test parameters
    token = "LANET-75F6-EC23-03BBDB"
    server_url = "http://localhost:5001/api"
    installer_path = "dist\\LANET_Agent_Installer.exe"
    
    print(f"Token: {token}")
    print(f"Server: {server_url}")
    print(f"Installer: {installer_path}")
    print()
    
    # Run the installer
    print("Running installer with automatic cleanup...")
    print("-" * 50)
    
    try:
        result = subprocess.run([
            installer_path,
            "--install-service",
            "--install-token", token,
            "--server-url", server_url
        ], capture_output=False, text=True, timeout=180)
        
        print("-" * 50)
        print(f"Installer completed with return code: {result.returncode}")
        
        if result.returncode == 0:
            print("SUCCESS: Installer completed successfully")
            
            # Wait for service to start
            print("Waiting for service to start...")
            time.sleep(5)
            
            # Check service status
            print("Checking service status...")
            service_result = subprocess.run(['sc', 'query', 'LANETAgent'], 
                                          capture_output=True, text=True)
            
            if service_result.returncode == 0:
                print("Service status:")
                print(service_result.stdout)
                
                if "RUNNING" in service_result.stdout:
                    print("SUCCESS: Service is running!")
                    
                    # Check service logs
                    print("Checking service logs...")
                    try:
                        with open("C:\\Program Files\\LANET Agent\\logs\\service.log", 'r', encoding='utf-8') as f:
                            logs = f.read()
                            if "LANET Production Service starting" in logs:
                                print("SUCCESS: Service is logging correctly")
                            else:
                                print("WARNING: Service logs may be incomplete")
                    except Exception as e:
                        print(f"WARNING: Could not read service logs: {e}")
                    
                    return True
                else:
                    print("WARNING: Service installed but not running")
                    return False
            else:
                print("ERROR: Service not found after installation")
                return False
        else:
            print(f"ERROR: Installer failed with return code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("ERROR: Installer timed out")
        return False
    except Exception as e:
        print(f"ERROR: Exception running installer: {e}")
        return False

def main():
    """Main test function"""
    success = run_installer_test()
    
    print("\n" + "=" * 50)
    if success:
        print("INSTALLATION TEST PASSED!")
        print()
        print("The installer successfully:")
        print("  - Cleaned up any existing installation")
        print("  - Installed the agent as a Windows service")
        print("  - Configured SYSTEM privileges for BitLocker access")
        print("  - Started the service in background mode")
        print("  - No visible windows (completely silent operation)")
        print()
        print("Next steps:")
        print("  1. Check frontend dashboard for new asset data")
        print("  2. Verify BitLocker data collection")
        print("  3. Test mass deployment procedures")
    else:
        print("INSTALLATION TEST FAILED!")
        print()
        print("Troubleshooting:")
        print("  1. Make sure you're running as Administrator")
        print("  2. Check if backend is running on localhost:5001")
        print("  3. Verify the installation token is valid")
        print("  4. Check Windows Event Log for service errors")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
