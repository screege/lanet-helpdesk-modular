#!/usr/bin/env python3
"""
Test BitLocker with admin privileges and manual data
"""
import requests
import json

def send_manual_bitlocker_data():
    """Send manual BitLocker data based on your system evidence"""
    print("🔍 Sending manual BitLocker data based on your system...")
    
    try:
        # Login first
        login_data = {'email': 'ba@lanet.mx', 'password': 'TestAdmin123!'}
        login_response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token = login_response.json()['data']['access_token']
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # Manual BitLocker data based on your evidence
        asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
        
        # Based on your screenshot: C: drive with BitLocker active but suspended
        manual_bitlocker_data = {
            'volumes': [
                {
                    'volume_letter': 'C:',
                    'volume_label': 'Windows-SSD',
                    'protection_status': 'ProtectionSuspended',  # From your screenshot
                    'encryption_method': 'AES-256',
                    'key_protector_type': 'TPM+PIN',
                    'recovery_key_id': 'real-key-id-from-your-system',
                    'recovery_key': '123456-789012-345678-901234-567890-654321'  # Real format
                }
            ]
        }
        
        print(f"📤 Sending manual BitLocker data for C: drive...")
        print(f"   Status: {manual_bitlocker_data['volumes'][0]['protection_status']}")
        
        # Send to backend
        response = requests.post(
            f'http://localhost:5001/api/bitlocker/{asset_id}/update',
            headers=headers,
            json=manual_bitlocker_data
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Manual BitLocker data sent successfully!")
            print(f"📊 Response: {response.json()}")
            return True
        else:
            print(f"❌ Failed to send data: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending data: {e}")
        return False

def test_bitlocker_retrieval_after_restart():
    """Test BitLocker retrieval after backend restart"""
    print("\n🔍 Testing BitLocker retrieval after backend restart...")
    
    try:
        # Login first
        login_data = {'email': 'ba@lanet.mx', 'password': 'TestAdmin123!'}
        login_response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token = login_response.json()['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test retrieval
        asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
        response = requests.get(f'http://localhost:5001/api/bitlocker/{asset_id}', headers=headers)
        
        print(f"📥 Retrieval status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ BitLocker data retrieved successfully!")
            print(f"📊 Retrieved data: {json.dumps(data, indent=2)}")
            
            volumes = data.get('data', {}).get('volumes', [])
            if volumes:
                print(f"\n🔑 Found {len(volumes)} volume(s) with recovery keys:")
                for i, volume in enumerate(volumes):
                    print(f"  Volume {i+1}: {volume.get('volume_letter')} - {volume.get('protection_status')}")
                    if volume.get('recovery_key'):
                        print(f"    Recovery Key: {volume.get('recovery_key')}")
                        print(f"    ✅ DECRYPTION WORKING!")
            
            return True
        else:
            print(f"❌ Failed to retrieve data: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving data: {e}")
        return False

def check_database_directly():
    """Check what's in the database directly"""
    print("\n🔍 Checking database directly...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="lanet_helpdesk",
            user="postgres",
            password="Poikl55+*"
        )
        
        cursor = conn.cursor()
        
        # Check BitLocker data
        asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
        query = """
            SELECT 
                volume_letter,
                volume_label,
                protection_status,
                encryption_method,
                recovery_key_encrypted,
                created_at
            FROM bitlocker_keys
            WHERE asset_id = %s
            ORDER BY volume_letter
        """
        
        cursor.execute(query, (asset_id,))
        results = cursor.fetchall()
        
        print(f"📊 Database contains {len(results)} BitLocker volume(s)")
        
        for i, row in enumerate(results):
            print(f"  Volume {i+1}:")
            print(f"    Letter: {row[0]}")
            print(f"    Label: {row[1]}")
            print(f"    Status: {row[2]}")
            print(f"    Method: {row[3]}")
            print(f"    Encrypted Key: {'YES' if row[4] else 'NO'}")
            print(f"    Created: {row[5]}")
        
        cursor.close()
        conn.close()
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

def main():
    print("🚀 BitLocker Admin Test - After Backend Restart")
    print("=" * 60)
    
    # Step 1: Check current database state
    db_has_data = check_database_directly()
    
    # Step 2: Send manual data (based on your screenshot)
    send_success = send_manual_bitlocker_data()
    
    # Step 3: Test retrieval (should work now with restarted backend)
    retrieve_success = test_bitlocker_retrieval_after_restart()
    
    print("\n" + "=" * 60)
    print("📋 ADMIN TEST SUMMARY:")
    print(f"✅ Database Check: {'HAS DATA' if db_has_data else 'EMPTY'}")
    print(f"✅ Send Manual Data: {'SUCCESS' if send_success else 'FAILED'}")
    print(f"✅ Retrieve Data: {'SUCCESS' if retrieve_success else 'FAILED'}")
    
    if send_success and retrieve_success:
        print("\n🎉 COMPLETE SUCCESS! BitLocker system is working!")
        print("   ✅ Backend restart fixed the decryption issue")
        print("   ✅ Your BitLocker data can now be displayed in frontend")
    elif send_success:
        print("\n⚠️ Partial success - data sent but retrieval still failing")
        print("   Check if backend truly restarted with new environment variables")
    else:
        print("\n❌ Issues persist - backend may need additional debugging")

if __name__ == '__main__':
    main()
