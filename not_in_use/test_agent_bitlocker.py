#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test BitLocker Collection from Running Agent
"""

import sys
import subprocess
import requests
import json

def test_agent_bitlocker_collection():
    """Test if the running agent is collecting BitLocker data"""
    print("🔍 Testing BitLocker Collection from Running Agent")
    print("=" * 60)
    
    try:
        # Test BitLocker collection directly
        print("1. Testing direct BitLocker collection...")
        
        result = subprocess.run([
            sys.executable, '-c', '''
import sys
sys.path.insert(0, "C:/Program Files/LANET Agent")

from modules.bitlocker import BitLockerCollector
import json

collector = BitLockerCollector()
bitlocker_info = collector.get_bitlocker_info()

print("BitLocker Collection Result:")
print(json.dumps(bitlocker_info, indent=2, default=str))
'''
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Direct BitLocker collection successful")
            print("Output:")
            print(result.stdout)
        else:
            print("❌ Direct BitLocker collection failed")
            print("Error:", result.stderr)
            return False
        
        # Test monitoring module BitLocker integration
        print("\n2. Testing monitoring module BitLocker integration...")
        
        result = subprocess.run([
            sys.executable, '-c', '''
import sys
sys.path.insert(0, "C:/Program Files/LANET Agent")

from core.config_manager import ConfigManager
from modules.monitoring import MonitoringModule
from core.database import DatabaseManager
import json

config_manager = ConfigManager("C:/Program Files/LANET Agent/config/agent_config.json")
database = DatabaseManager("C:/Program Files/LANET Agent/data/agent.db")
monitoring = MonitoringModule(config_manager, database)

bitlocker_info = monitoring.get_bitlocker_info()

print("Monitoring BitLocker Result:")
print(json.dumps(bitlocker_info, indent=2, default=str))
'''
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Monitoring module BitLocker integration successful")
            print("Output:")
            print(result.stdout)
        else:
            print("❌ Monitoring module BitLocker integration failed")
            print("Error:", result.stderr)
            return False
        
        # Test if BitLocker data is included in heartbeat
        print("\n3. Testing BitLocker data in heartbeat...")
        
        result = subprocess.run([
            sys.executable, '-c', '''
import sys
sys.path.insert(0, "C:/Program Files/LANET Agent")

from core.config_manager import ConfigManager
from modules.monitoring import MonitoringModule
from core.database import DatabaseManager
import json

config_manager = ConfigManager("C:/Program Files/LANET Agent/config/agent_config.json")
database = DatabaseManager("C:/Program Files/LANET Agent/data/agent.db")
monitoring = MonitoringModule(config_manager, database)

# Get full system status (what gets sent in heartbeat)
status = monitoring.get_system_status()

print("System Status (Heartbeat Data):")
print(json.dumps(status, indent=2, default=str))

# Check if BitLocker is included
if 'hardware_inventory' in status and 'bitlocker' in status['hardware_inventory']:
    print("\\n✅ BitLocker data IS included in heartbeat")
    bitlocker_data = status['hardware_inventory']['bitlocker']
    print(f"BitLocker volumes: {len(bitlocker_data.get('volumes', []))}")
    print(f"Protected volumes: {bitlocker_data.get('protected_volumes', 0)}")
else:
    print("\\n❌ BitLocker data NOT included in heartbeat")
'''
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Heartbeat BitLocker test successful")
            print("Output:")
            print(result.stdout)
        else:
            print("❌ Heartbeat BitLocker test failed")
            print("Error:", result.stderr)
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_backend_bitlocker_endpoint():
    """Test if the backend BitLocker endpoint is working"""
    print("\n🌐 Testing Backend BitLocker Endpoint")
    print("=" * 50)
    
    try:
        # Login to get token
        login_response = requests.post('http://localhost:5001/api/auth/login', json={
            'email': 'ba@lanet.mx',
            'password': 'TestAdmin123!'
        })
        
        if login_response.status_code != 200:
            print("❌ Login failed")
            return False
        
        token = login_response.json()['data']['access_token']
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # Get asset ID from database
        import psycopg2
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()
        cur.execute("SELECT asset_id FROM assets ORDER BY last_seen DESC LIMIT 1")
        result = cur.fetchone()
        conn.close()
        
        if not result:
            print("❌ No assets found in database")
            return False
        
        asset_id = result[0]
        print(f"Testing with asset ID: {asset_id}")
        
        # Test BitLocker endpoint
        response = requests.get(f'http://localhost:5001/api/bitlocker/{asset_id}', headers=headers)
        
        print(f"BitLocker endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ BitLocker endpoint working")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check if there's BitLocker data
            if data.get('data', {}).get('volumes'):
                print("✅ BitLocker data found in backend")
                return True
            else:
                print("⚠️ No BitLocker data in backend yet")
                return False
        else:
            print(f"❌ BitLocker endpoint failed: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def main():
    """Main test function"""
    print("🔐 LANET Agent BitLocker Collection Test")
    print("=" * 60)
    
    # Test agent collection
    collection_works = test_agent_bitlocker_collection()
    
    # Test backend endpoint
    backend_works = test_backend_bitlocker_endpoint()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    print(f"Agent BitLocker Collection: {'✅ WORKING' if collection_works else '❌ FAILED'}")
    print(f"Backend BitLocker Endpoint: {'✅ WORKING' if backend_works else '❌ FAILED'}")
    
    if collection_works and not backend_works:
        print("\n🔍 DIAGNOSIS: Agent can collect BitLocker data but it's not reaching the backend")
        print("Possible issues:")
        print("  1. Agent is not sending BitLocker data in heartbeat")
        print("  2. Backend is not processing BitLocker data from heartbeat")
        print("  3. BitLocker data is not being stored in database")
    elif not collection_works:
        print("\n🔍 DIAGNOSIS: Agent cannot collect BitLocker data")
        print("Possible issues:")
        print("  1. BitLocker not available on this system")
        print("  2. Agent lacks SYSTEM privileges")
        print("  3. PowerShell execution blocked")
    elif collection_works and backend_works:
        print("\n🎉 SUCCESS: BitLocker collection is working end-to-end!")
    else:
        print("\n❌ FAILURE: Both agent and backend have issues")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
