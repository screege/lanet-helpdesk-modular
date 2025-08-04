#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Force BitLocker Heartbeat
Force the agent to send a full heartbeat with BitLocker data
"""

import sys
import subprocess
import requests
import json
import psycopg2

def force_heartbeat_with_bitlocker():
    """Force the agent to send a heartbeat with BitLocker data"""
    print("🔐 Forcing LANET Agent to Send BitLocker Data")
    print("=" * 60)
    
    try:
        # Force a full heartbeat from the running agent
        print("1. Forcing full heartbeat from running agent...")
        
        result = subprocess.run([
            sys.executable, '-c', '''
import sys
sys.path.insert(0, "C:/Program Files/LANET Agent")

from core.config_manager import ConfigManager
from modules.heartbeat import HeartbeatModule
from core.database import DatabaseManager

print("Initializing heartbeat module...")
config_manager = ConfigManager("C:/Program Files/LANET Agent/config/agent_config.json")
database = DatabaseManager("C:/Program Files/LANET Agent/data/agent.db")

heartbeat = HeartbeatModule(config_manager, database)

# Force a full heartbeat (TIER 2) with BitLocker data
print("Forcing full heartbeat with BitLocker data...")

# Override the should_send_full_inventory to force TIER 2
heartbeat._last_full_heartbeat = None  # Force full heartbeat

success = heartbeat.send_heartbeat()
print(f"Heartbeat result: {success}")
'''
        ], capture_output=True, text=True, timeout=120)
        
        print("Return code:", result.returncode)
        print("Output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Heartbeat sent successfully")
        else:
            print("❌ Heartbeat failed")
            return False
        
        # Wait a moment for backend to process
        print("\n2. Waiting for backend to process data...")
        import time
        time.sleep(5)
        
        # Check if BitLocker data appeared in backend
        print("\n3. Checking backend for BitLocker data...")
        return check_backend_bitlocker_data()
        
    except Exception as e:
        print(f"❌ Error forcing heartbeat: {e}")
        return False

def check_backend_bitlocker_data():
    """Check if BitLocker data appeared in the backend"""
    try:
        # Get asset ID from database
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()
        
        # Check bitlocker_keys table
        cur.execute("""
            SELECT bk.asset_id, bk.volume_letter, bk.recovery_key, bk.created_at,
                   a.name as asset_name
            FROM bitlocker_keys bk
            JOIN assets a ON bk.asset_id = a.asset_id
            ORDER BY bk.created_at DESC
            LIMIT 5
        """)
        
        bitlocker_results = cur.fetchall()
        
        print(f"BitLocker keys in database: {len(bitlocker_results)}")
        
        if bitlocker_results:
            print("✅ BitLocker data found in database:")
            for row in bitlocker_results:
                asset_id, volume, key, created, asset_name = row
                print(f"  Asset: {asset_name}")
                print(f"  Volume: {volume}")
                print(f"  Key: {key}")
                print(f"  Created: {created}")
                print("  ---")
        else:
            print("❌ No BitLocker data in database")
        
        # Also check assets table for recent updates
        cur.execute("""
            SELECT asset_id, name, last_seen, specifications
            FROM assets
            WHERE last_seen > NOW() - INTERVAL '10 minutes'
            ORDER BY last_seen DESC
        """)
        
        recent_assets = cur.fetchall()
        print(f"\nRecent asset updates: {len(recent_assets)}")
        
        for asset in recent_assets:
            asset_id, name, last_seen, specs = asset
            print(f"  Asset: {name} (last seen: {last_seen})")
            
            # Check if specifications contain BitLocker data
            if specs and 'bitlocker' in str(specs).lower():
                print("    ✅ Contains BitLocker data in specifications")
            else:
                print("    ❌ No BitLocker data in specifications")
        
        conn.close()
        
        return len(bitlocker_results) > 0
        
    except Exception as e:
        print(f"❌ Error checking backend data: {e}")
        return False

def test_api_endpoint():
    """Test the API endpoint for BitLocker data"""
    print("\n4. Testing API endpoint...")
    
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
        
        # Get asset ID
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()
        cur.execute("SELECT asset_id FROM assets ORDER BY last_seen DESC LIMIT 1")
        result = cur.fetchone()
        conn.close()
        
        if not result:
            print("❌ No assets found")
            return False
        
        asset_id = result[0]
        
        # Test BitLocker endpoint
        response = requests.get(f'http://localhost:5001/api/bitlocker/{asset_id}', headers=headers)
        
        print(f"API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            volumes = data.get('data', {}).get('volumes', [])
            
            if volumes:
                print(f"✅ API returned {len(volumes)} BitLocker volumes")
                for volume in volumes:
                    print(f"  Volume {volume.get('volume_letter')}: {volume.get('protection_status')}")
                return True
            else:
                print("❌ API returned no BitLocker volumes")
                return False
        else:
            print(f"❌ API error: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

def main():
    """Main function"""
    print("🔐 LANET Agent BitLocker Heartbeat Force")
    print("=" * 60)
    
    # Force heartbeat
    heartbeat_success = force_heartbeat_with_bitlocker()
    
    # Test API
    api_success = test_api_endpoint()
    
    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    
    print(f"Heartbeat sent: {'✅ SUCCESS' if heartbeat_success else '❌ FAILED'}")
    print(f"API endpoint: {'✅ SUCCESS' if api_success else '❌ FAILED'}")
    
    if heartbeat_success and api_success:
        print("\n🎉 SUCCESS: BitLocker data is now in the backend!")
        print("Check the frontend dashboard for BitLocker information.")
    elif heartbeat_success and not api_success:
        print("\n⚠️ PARTIAL: Heartbeat sent but API not showing data yet")
        print("Data may still be processing. Check again in a few minutes.")
    else:
        print("\n❌ FAILED: BitLocker data transmission failed")
        print("Check agent logs and backend connectivity.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
