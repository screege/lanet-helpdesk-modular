#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test LANET Agent Installer as Administrator
"""

import subprocess
import time
import ctypes
import sys
from pathlib import Path

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def cleanup_existing():
    """Clean up existing installation"""
    print("🧹 Cleaning up existing installation...")
    
    try:
        # Stop and remove service
        subprocess.run(['sc.exe', 'stop', 'LANETAgent'], capture_output=True)
        subprocess.run(['sc.exe', 'delete', 'LANETAgent'], capture_output=True)
        
        # Remove installation directory
        install_dir = Path("C:/Program Files/LANET Agent")
        if install_dir.exists():
            import shutil
            shutil.rmtree(install_dir)
            print("✅ Installation directory removed")
        
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

def test_installer():
    """Test the installer"""
    print("🔧 Testing LANET Agent Installer v2...")
    
    installer_path = Path("production_installer/dist/LANET_Agent_Installer_v2.exe")
    if not installer_path.exists():
        print(f"❌ Installer not found: {installer_path}")
        return False
    
    # Test with the token we created
    token = "LANET-TEST-PROD-94DA44"
    
    cmd = [
        str(installer_path),
        '--silent',
        '--token', token,
        '--server-url', 'http://localhost:5001/api'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print("⏳ Installing...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        print(f"Exit code: {result.returncode}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Installation completed successfully")
            return True
        else:
            print(f"❌ Installation failed with exit code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Installation timed out")
        return False
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def check_service():
    """Check if service was created and is running"""
    print("🔍 Checking service status...")
    
    try:
        # Check if service exists
        result = subprocess.run(['sc.exe', 'query', 'LANETAgent'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Service exists")
            print(f"Service status:\n{result.stdout}")
            
            if "RUNNING" in result.stdout:
                print("✅ Service is running")
                return True
            elif "STOPPED" in result.stdout:
                print("⚠️ Service exists but is stopped")
                
                # Try to start it
                print("🚀 Attempting to start service...")
                start_result = subprocess.run(['sc.exe', 'start', 'LANETAgent'], 
                                            capture_output=True, text=True)
                
                if start_result.returncode == 0:
                    print("✅ Service started successfully")
                    time.sleep(10)
                    
                    # Check status again
                    status_result = subprocess.run(['sc.exe', 'query', 'LANETAgent'], 
                                                 capture_output=True, text=True)
                    
                    if "RUNNING" in status_result.stdout:
                        print("✅ Service is now running")
                        return True
                    else:
                        print("⚠️ Service started but not running properly")
                        return False
                else:
                    print(f"❌ Failed to start service: {start_result.stderr}")
                    return False
            else:
                print("⚠️ Service in unknown state")
                return False
        else:
            print("❌ Service does not exist")
            return False
            
    except Exception as e:
        print(f"❌ Error checking service: {e}")
        return False

def check_logs():
    """Check if logs are being created"""
    print("📝 Checking log files...")
    
    log_locations = [
        Path("C:/Program Files/LANET Agent/logs"),
        Path("C:/ProgramData/LANET Agent/Logs")
    ]
    
    found_logs = False
    
    for log_dir in log_locations:
        if log_dir.exists():
            log_files = list(log_dir.glob("*.log"))
            if log_files:
                print(f"✅ Found logs in {log_dir}:")
                for log_file in log_files:
                    size = log_file.stat().st_size
                    print(f"  📄 {log_file.name} ({size} bytes)")
                    
                    # Show last few lines
                    if size > 0:
                        try:
                            with open(log_file, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                if lines:
                                    print(f"  Last entries:")
                                    for line in lines[-3:]:
                                        print(f"    {line.strip()}")
                        except:
                            pass
                            
                found_logs = True
    
    if not found_logs:
        print("⚠️ No log files found")
    
    return found_logs

def main():
    """Main test function"""
    print("🧪 LANET Agent Installer v2 Test")
    print("=" * 50)
    
    if not is_admin():
        print("❌ This test must be run as Administrator")
        print("Right-click and select 'Run as Administrator'")
        return False
    
    print("✅ Running as Administrator")
    print()
    
    # Cleanup existing installation
    cleanup_existing()
    print()
    
    # Test installer
    if not test_installer():
        print("❌ Installer test failed")
        return False
    print()
    
    # Check service
    service_ok = check_service()
    print()
    
    # Wait a bit for agent to initialize
    print("⏳ Waiting 30 seconds for agent to initialize...")
    time.sleep(30)
    
    # Check logs
    logs_ok = check_logs()
    print()
    
    # Summary
    print("=" * 50)
    print("🏁 TEST RESULTS")
    print("=" * 50)
    
    results = {
        "Installation": True,
        "Service": service_ok,
        "Logs": logs_ok
    }
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test:<15}: {status}")
    
    all_passed = all(results.values())
    
    print()
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("The installer is working correctly!")
    else:
        print("⚠️ Some tests failed")
        print("Check the details above for issues")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
