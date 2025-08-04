#!/usr/bin/env python3
"""
Test BitLocker endpoint within Flask context
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Add backend to path
sys.path.append('backend')

def test_flask_bitlocker_endpoint():
    """Test BitLocker endpoint within Flask app context"""
    print("🔍 Testing BitLocker endpoint in Flask context...")
    
    try:
        # Import Flask app
        from app import create_app
        
        # Create app
        app = create_app()
        
        with app.app_context():
            # Import the database manager
            from utils.encryption import decrypt_data
            
            # Test database query directly
            asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
            query = """
                SELECT 
                    id, volume_letter, volume_label, protection_status,
                    encryption_method, key_protector_type, recovery_key_id,
                    recovery_key_encrypted, created_at, updated_at
                FROM bitlocker_keys
                WHERE asset_id = %s
                ORDER BY volume_letter
            """
            
            result = app.db_manager.execute_query(query, (asset_id,), fetch='all')
            
            if not result:
                print("❌ No BitLocker data found in database")
                return False
            
            print(f"✅ Found {len(result)} BitLocker volume(s)")
            
            # Test decryption within Flask context
            for i, row in enumerate(result):
                print(f"\n  Volume {i+1}:")
                print(f"    Letter: {row[1]}")
                print(f"    Label: {row[2]}")
                print(f"    Status: {row[3]}")
                
                if row[7]:  # recovery_key_encrypted
                    try:
                        decrypted_key = decrypt_data(row[7])
                        print(f"    ✅ Decrypted Key: {decrypted_key}")
                    except Exception as e:
                        print(f"    ❌ Decryption failed: {e}")
                        return False
                else:
                    print(f"    ⚠️ No encrypted key")
            
            print("\n✅ Flask context decryption successful!")
            return True
            
    except Exception as e:
        print(f"❌ Flask context test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_actual_endpoint_call():
    """Test the actual endpoint call with proper authentication"""
    print("\n🔍 Testing actual endpoint call...")
    
    try:
        import requests
        
        # Login first
        login_data = {'email': 'ba@lanet.mx', 'password': 'TestAdmin123!'}
        login_response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token = login_response.json()['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test BitLocker endpoint
        asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
        response = requests.get(f'http://localhost:5001/api/bitlocker/{asset_id}', headers=headers)
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📊 Response text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint call successful!")
            
            volumes = data.get('data', {}).get('volumes', [])
            if volumes:
                for i, volume in enumerate(volumes):
                    print(f"  Volume {i+1}: {volume.get('volume_letter')} - {volume.get('protection_status')}")
                    if volume.get('recovery_key'):
                        print(f"    Recovery Key: {volume.get('recovery_key')}")
            
            return True
        else:
            print(f"❌ Endpoint call failed")
            return False
            
    except Exception as e:
        print(f"❌ Endpoint test error: {e}")
        return False

def check_backend_logs():
    """Check recent backend logs for errors"""
    print("\n🔍 Checking recent backend activity...")
    
    try:
        # Check if there are recent log files
        log_files = ['backend/logs/app.log', 'backend/app.log']
        
        for log_file in log_files:
            if os.path.exists(log_file):
                print(f"📄 Checking {log_file}...")
                
                # Read last few lines
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                if lines:
                    print(f"   Last log entry: {lines[-1].strip()}")
                    
                    # Look for recent BitLocker related errors
                    recent_lines = lines[-20:] if len(lines) > 20 else lines
                    bitlocker_errors = [line for line in recent_lines if 'bitlocker' in line.lower() or 'decrypt' in line.lower()]
                    
                    if bitlocker_errors:
                        print("   Recent BitLocker/decrypt errors:")
                        for error in bitlocker_errors[-3:]:  # Last 3 errors
                            print(f"     {error.strip()}")
                    else:
                        print("   No recent BitLocker/decrypt errors found")
                else:
                    print("   Log file is empty")
                break
        else:
            print("❌ No log files found")
            
    except Exception as e:
        print(f"❌ Log check error: {e}")

def main():
    print("🚀 Flask Context BitLocker Test")
    print("=" * 50)
    
    # Test 1: Flask context
    flask_success = test_flask_bitlocker_endpoint()
    
    # Test 2: Actual endpoint
    endpoint_success = test_actual_endpoint_call()
    
    # Test 3: Check logs
    check_backend_logs()
    
    print("\n" + "=" * 50)
    print("📋 FLASK CONTEXT TEST SUMMARY:")
    print(f"✅ Flask Context: {'SUCCESS' if flask_success else 'FAILED'}")
    print(f"✅ Endpoint Call: {'SUCCESS' if endpoint_success else 'FAILED'}")
    
    if flask_success and endpoint_success:
        print("\n🎉 COMPLETE SUCCESS! BitLocker endpoint is working!")
        print("   The backend restart successfully loaded the encryption key")
    elif flask_success:
        print("\n⚠️ Flask context works but endpoint fails")
        print("   There may be an issue with the HTTP endpoint logic")
    else:
        print("\n❌ Issues in Flask context - deeper debugging needed")

if __name__ == '__main__':
    main()
