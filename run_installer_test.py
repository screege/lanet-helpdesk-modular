#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run Installer Test - Test the production installer
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

def run_installer():
    """Run the installer with test parameters"""
    if not is_admin():
        print("❌ This script must be run as Administrator")
        print("   Right-click and select 'Run as administrator'")
        return False
    
    print("🚀 Testing LANET Agent Production Installer")
    print("=" * 50)
    
    # Test parameters
    token = "LANET-75F6-EC23-03BBDB"
    server_url = "http://localhost:5001/api"
    installer_path = "dist\\LANET_Agent_Installer.exe"
    
    print(f"🔑 Token: {token}")
    print(f"🌐 Server: {server_url}")
    print(f"📦 Installer: {installer_path}")
    print()
    
    # Run the installer
    print("🔧 Running installer...")
    
    try:
        result = subprocess.run([
            installer_path,
            "--install-service",
            "--install-token", token,
            "--server-url", server_url
        ], capture_output=True, text=True, timeout=120)
        
        print("📋 Installer Output:")
        print("-" * 30)
        print(result.stdout)
        
        if result.stderr:
            print("📋 Installer Errors:")
            print("-" * 30)
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Installer completed successfully")
            
            # Wait a moment for service to start
            print("⏳ Waiting for service to start...")
            time.sleep(5)
            
            # Check service status
            service_result = subprocess.run(['sc', 'query', 'LANETAgent'], 
                                          capture_output=True, text=True)
            
            if service_result.returncode == 0:
                print("✅ Service status:")
                print(service_result.stdout)
                
                if "RUNNING" in service_result.stdout:
                    print("🎉 Service is running successfully!")
                    return True
                else:
                    print("⚠️ Service installed but not running")
                    return False
            else:
                print("❌ Service not found")
                return False
        else:
            print(f"❌ Installer failed with return code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Installer timed out")
        return False
    except Exception as e:
        print(f"❌ Error running installer: {e}")
        return False

def main():
    """Main test function"""
    success = run_installer()
    
    if success:
        print("\n🎉 INSTALLATION TEST SUCCESSFUL!")
        print("📋 Next steps:")
        print("   1. Check service logs: type \"C:\\Program Files\\LANET Agent\\logs\\service.log\"")
        print("   2. Run verification: python test_production_installer.py")
        print("   3. Check frontend for new asset data")
    else:
        print("\n❌ INSTALLATION TEST FAILED!")
        print("📋 Troubleshooting:")
        print("   1. Make sure you're running as Administrator")
        print("   2. Check if backend is running on localhost:5001")
        print("   3. Verify token is valid")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
