#!/usr/bin/env python3
"""
Test real BitLocker data collection and send to backend
"""
import subprocess
import json
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

def get_real_bitlocker_data():
    """Get real BitLocker data from the system using PowerShell"""
    print("🔍 Collecting real BitLocker data from your system...")
    
    try:
        # PowerShell command to get BitLocker information
        ps_command = """
        Get-BitLockerVolume | ForEach-Object {
            $volume = $_
            $recoveryKeys = $volume.KeyProtector | Where-Object { $_.KeyProtectorType -eq 'RecoveryPassword' }
            
            [PSCustomObject]@{
                MountPoint = $volume.MountPoint
                VolumeLabel = if ($volume.VolumeLabel) { $volume.VolumeLabel } else { "Local Disk" }
                ProtectionStatus = $volume.ProtectionStatus.ToString()
                EncryptionMethod = $volume.EncryptionMethod.ToString()
                VolumeStatus = $volume.VolumeStatus.ToString()
                EncryptionPercentage = $volume.EncryptionPercentage
                KeyProtectorCount = $volume.KeyProtector.Count
                RecoveryKeyId = if ($recoveryKeys) { $recoveryKeys[0].KeyProtectorId } else { $null }
                RecoveryPassword = if ($recoveryKeys) { $recoveryKeys[0].RecoveryPassword } else { $null }
            }
        } | ConvertTo-Json -Depth 3
        """
        
        # Execute PowerShell command
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            # Parse JSON output
            bitlocker_data = json.loads(result.stdout)
            
            # Handle single volume (not array)
            if isinstance(bitlocker_data, dict):
                bitlocker_data = [bitlocker_data]
            
            print(f"✅ Found {len(bitlocker_data)} BitLocker volume(s)")
            
            for i, volume in enumerate(bitlocker_data):
                print(f"  Volume {i+1}: {volume.get('MountPoint')} - {volume.get('ProtectionStatus')}")
                if volume.get('RecoveryPassword'):
                    print(f"    Recovery Key: {volume.get('RecoveryPassword')[:20]}...")
            
            return bitlocker_data
        else:
            print("⚠️ No BitLocker volumes found or BitLocker not available")
            return []
            
    except subprocess.CalledProcessError as e:
        print(f"❌ PowerShell command failed: {e}")
        print(f"   Error output: {e.stderr}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse PowerShell output: {e}")
        print(f"   Raw output: {result.stdout}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

def send_bitlocker_to_backend(bitlocker_data):
    """Send real BitLocker data to backend"""
    print("\n🔍 Sending real BitLocker data to backend...")
    
    if not bitlocker_data:
        print("❌ No BitLocker data to send")
        return False
    
    try:
        # Login first
        login_data = {'email': 'ba@lanet.mx', 'password': 'TestAdmin123!'}
        login_response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token = login_response.json()['data']['access_token']
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # Prepare data for backend
        asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
        
        volumes = []
        for volume in bitlocker_data:
            volume_data = {
                'volume_letter': volume.get('MountPoint', 'C:'),
                'volume_label': volume.get('VolumeLabel', 'Local Disk'),
                'protection_status': volume.get('ProtectionStatus', 'Unknown'),
                'encryption_method': volume.get('EncryptionMethod', 'Unknown'),
                'key_protector_type': 'RecoveryPassword' if volume.get('RecoveryPassword') else 'Unknown',
                'recovery_key_id': volume.get('RecoveryKeyId'),
                'recovery_key': volume.get('RecoveryPassword')
            }
            volumes.append(volume_data)
        
        payload = {'volumes': volumes}
        
        print(f"📤 Sending {len(volumes)} volume(s) to backend...")
        
        # Send to backend
        response = requests.post(
            f'http://localhost:5001/api/bitlocker/{asset_id}/update',
            headers=headers,
            json=payload
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Real BitLocker data sent successfully!")
            print(f"📊 Response: {response.json()}")
            return True
        else:
            print(f"❌ Failed to send data: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending data: {e}")
        return False

def test_bitlocker_retrieval():
    """Test retrieving BitLocker data from backend"""
    print("\n🔍 Testing BitLocker data retrieval...")
    
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
            
            return True
        else:
            print(f"❌ Failed to retrieve data: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving data: {e}")
        return False

def main():
    print("🚀 Real BitLocker Test - LANET Helpdesk V3")
    print("=" * 60)
    
    # Check if we have the encryption key
    encryption_key = os.environ.get('BITLOCKER_ENCRYPTION_KEY')
    print(f"🔑 Encryption key available: {'YES' if encryption_key else 'NO'}")
    
    # Step 1: Collect real BitLocker data
    bitlocker_data = get_real_bitlocker_data()
    
    # Step 2: Send to backend
    send_success = False
    if bitlocker_data:
        send_success = send_bitlocker_to_backend(bitlocker_data)
    
    # Step 3: Test retrieval
    retrieve_success = test_bitlocker_retrieval()
    
    print("\n" + "=" * 60)
    print("📋 REAL BITLOCKER TEST SUMMARY:")
    print(f"✅ Data Collection: {'SUCCESS' if bitlocker_data else 'NO DATA'}")
    print(f"✅ Send to Backend: {'SUCCESS' if send_success else 'FAILED'}")
    print(f"✅ Retrieve from Backend: {'SUCCESS' if retrieve_success else 'FAILED'}")
    
    if bitlocker_data and send_success and retrieve_success:
        print("\n🎉 COMPLETE SUCCESS! Real BitLocker data is working end-to-end!")
    elif bitlocker_data and send_success:
        print("\n⚠️ Partial success - data sent but retrieval failed (backend restart needed)")
    else:
        print("\n❌ Issues detected - check the output above for details")

if __name__ == '__main__':
    main()
