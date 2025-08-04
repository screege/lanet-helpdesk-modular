#!/usr/bin/env python3
"""
Quick test script to verify LANET Agent installation
"""

import os
import subprocess
from pathlib import Path
import requests
import time

def test_installation():
    """Test the installation status"""
    print("🔍 Testing LANET Agent Installation")
    print("=" * 40)
    
    # Check installation directory
    install_dir = Path("C:/Program Files/LANET Agent")
    if install_dir.exists():
        print("✅ Installation directory exists")
        files = list(install_dir.glob("*"))
        for file in files:
            print(f"   📁 {file.name}")
    else:
        print("❌ Installation directory not found")
        return False
    
    # Check service status
    try:
        result = subprocess.run(['sc', 'query', 'LANETAgent'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Service exists")
            if "RUNNING" in result.stdout:
                print("✅ Service is running")
            else:
                print("⚠️  Service is stopped")
        else:
            print("❌ Service not found")
    except Exception as e:
        print(f"❌ Service check failed: {e}")
    
    # Check service configuration
    try:
        result = subprocess.run(['sc', 'qc', 'LANETAgent'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Service configuration:")
            lines = result.stdout.split('\n')
            for line in lines:
                if 'BINARY_PATH_NAME' in line or 'NOMBRE_RUTA_BINARIO' in line:
                    print(f"   🔧 {line.strip()}")
        else:
            print("❌ Could not get service configuration")
    except Exception as e:
        print(f"❌ Service config check failed: {e}")
    
    # Test backend connectivity
    try:
        response = requests.get("http://localhost:5001/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is accessible")
        else:
            print(f"⚠️  Backend returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
    
    # Check logs
    log_dir = Path("C:/ProgramData/LANET Agent/Logs")
    if log_dir.exists():
        print("✅ Log directory exists")
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            print(f"   📄 Latest log: {latest_log.name}")
            
            # Read latest log
            try:
                with open(latest_log, 'r') as f:
                    content = f.read()
                    if content.strip():
                        print("   📝 Log content (last 5 lines):")
                        lines = content.strip().split('\n')
                        for line in lines[-5:]:
                            print(f"      {line}")
                    else:
                        print("   📝 Log file is empty")
            except Exception as e:
                print(f"   ❌ Could not read log: {e}")
        else:
            print("   ⚠️  No log files found")
    else:
        print("❌ Log directory not found")
    
    print("\n" + "=" * 40)
    print("Test completed")

if __name__ == "__main__":
    test_installation()
