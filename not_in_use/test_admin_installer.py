#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test LANET Agent Installer with Administrator Privileges
"""

import subprocess
import time
import psycopg2
import uuid
import ctypes
from datetime import datetime, timedelta
from pathlib import Path

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_test_token():
    """Create a test installation token"""
    print("🎫 Creating test installation token...")
    
    try:
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()
        
        # Get a client and site for the token
        cur.execute("""
            SELECT c.client_id, s.site_id, c.name as client_name, s.name as site_name
            FROM clients c
            JOIN sites s ON c.client_id = s.client_id
            LIMIT 1
        """)
        
        result = cur.fetchone()
        if not result:
            print("❌ No clients/sites found in database")
            return None
        
        client_id, site_id, client_name, site_name = result
        
        # Generate token
        token_value = f"LANET-ADMIN-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:6].upper()}"
        
        # Get a user ID for created_by
        cur.execute("SELECT user_id FROM users WHERE role = 'superadmin' LIMIT 1")
        user_result = cur.fetchone()
        created_by = user_result[0] if user_result else None
        
        # Create token
        cur.execute("""
            INSERT INTO agent_installation_tokens (
                token_id, token_value, client_id, site_id, 
                is_active, expires_at, created_by, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(uuid.uuid4()),
            token_value,
            client_id,
            site_id,
            True,
            datetime.now() + timedelta(days=30),
            created_by,
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Test token created: {token_value}")
        print(f"   Client: {client_name}")
        print(f"   Site: {site_name}")
        
        return token_value
        
    except Exception as e:
        print(f"❌ Error creating test token: {e}")
        return None

def cleanup_existing():
    """Clean up any existing installation"""
    print("🧹 Cleaning up existing installation...")
    
    try:
        subprocess.run(['sc.exe', 'stop', 'LANETAgent'], capture_output=True)
        subprocess.run(['sc.exe', 'delete', 'LANETAgent'], capture_output=True)
        
        install_dir = Path("C:/Program Files/LANET Agent")
        if install_dir.exists():
            import shutil
            shutil.rmtree(install_dir)
        
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

def test_installer(token):
    """Test the installer"""
    print("🔧 Testing installer...")
    
    installer_path = Path("production_installer/dist/LANET_Agent_Installer.exe")
    if not installer_path.exists():
        print(f"❌ Installer not found: {installer_path}")
        return False
    
    cmd = [
        str(installer_path),
        '--silent',
        '--token', token,
        '--server-url', 'http://localhost:5001/api'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            print("✅ Installation completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ Installation failed with exit code: {result.returncode}")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Installation timed out")
        return False
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def check_service():
    """Check service status"""
    print("🔍 Checking service status...")
    
    try:
        result = subprocess.run(['sc.exe', 'query', 'LANETAgent'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Service is installed")
            
            if "RUNNING" in result.stdout:
                print("✅ Service is running")
                return True
            else:
                print("⚠️ Service not running, attempting to start...")
                start_result = subprocess.run(['sc.exe', 'start', 'LANETAgent'], 
                                            capture_output=True, text=True)
                
                if start_result.returncode == 0:
                    print("✅ Service started")
                    time.sleep(15)
                    return True
                else:
                    print(f"❌ Failed to start service: {start_result.stderr}")
                    return False
        else:
            print("❌ Service not installed")
            return False
            
    except Exception as e:
        print(f"❌ Service check error: {e}")
        return False

def check_database():
    """Check if agent appears in database"""
    print("📊 Checking database for agent data...")
    
    try:
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()
        
        cur.execute('''
            SELECT asset_id, name, last_seen
            FROM assets 
            WHERE last_seen > NOW() - INTERVAL '15 minutes'
            ORDER BY last_seen DESC
            LIMIT 3
        ''')
        
        assets = cur.fetchall()
        if assets:
            print(f"✅ Found {len(assets)} recent assets:")
            for asset in assets:
                print(f"  📱 {asset[1]} - {asset[2]}")
            conn.close()
            return True
        else:
            print("⚠️ No recent assets found")
            conn.close()
            return False
        
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

def check_logs():
    """Check log files"""
    print("📝 Checking log files...")
    
    log_dirs = [
        Path("C:/Program Files/LANET Agent/logs"),
        Path("C:/ProgramData/LANET Agent/Logs")
    ]
    
    for log_dir in log_dirs:
        if log_dir.exists():
            log_files = list(log_dir.glob("*.log"))
            if log_files:
                print(f"✅ Found logs in {log_dir}:")
                for log_file in log_files:
                    size = log_file.stat().st_size
                    print(f"  📄 {log_file.name} ({size} bytes)")
                return True
    
    print("⚠️ No log files found")
    return False

def main():
    """Main test function"""
    print("🧪 LANET Agent Administrator Test")
    print("=" * 50)
    
    if not is_admin():
        print("❌ Must run as Administrator!")
        print("Right-click and select 'Run as Administrator'")
        return False
    
    print("✅ Running as Administrator")
    print()
    
    # Create test token
    token = create_test_token()
    if not token:
        return False
    print()
    
    # Cleanup
    cleanup_existing()
    print()
    
    # Test installation
    if not test_installer(token):
        return False
    print()
    
    # Check service
    if not check_service():
        return False
    print()
    
    # Wait for agent to start
    print("⏳ Waiting 45 seconds for agent to initialize...")
    time.sleep(45)
    
    # Check database
    db_ok = check_database()
    print()
    
    # Check logs
    logs_ok = check_logs()
    print()
    
    # Results
    print("=" * 50)
    print("🏁 TEST RESULTS")
    print("=" * 50)
    
    tests = {
        "Administrator": True,
        "Token Creation": True,
        "Installation": True,
        "Service": True,
        "Database": db_ok,
        "Logs": logs_ok
    }
    
    for test, result in tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test:<15}: {status}")
    
    all_passed = all(tests.values())
    
    print()
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("The installer works correctly as Administrator!")
    else:
        print("⚠️ Some tests failed - check logs for details")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
