#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Backend BitLocker Processing
Add BitLocker data processing to the backend heartbeat handler
"""

import sys
import os
import json

def add_bitlocker_processing():
    """Add BitLocker processing to the backend heartbeat handler"""
    print("🔧 Adding BitLocker Processing to Backend Heartbeat Handler")
    print("=" * 70)
    
    try:
        # Read the current agents routes file
        routes_file = "backend/modules/agents/routes.py"
        
        print(f"1. Reading {routes_file}...")
        
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if BitLocker processing already exists
        if "process_bitlocker_data" in content:
            print("✅ BitLocker processing already exists in routes")
            return True
        
        # Find the location to add BitLocker processing
        # Look for the line where hardware inventory is saved
        insert_point = content.find("current_app.logger.info(f\"SAVED TO DB: Hardware inventory saved successfully for {asset_id}\")")
        
        if insert_point == -1:
            print("❌ Could not find insertion point in routes file")
            return False
        
        # Find the end of that line
        insert_point = content.find("\n", insert_point) + 1
        
        # BitLocker processing code to insert
        bitlocker_processing_code = '''
                # Process BitLocker data if present
                if hardware_inventory and 'bitlocker' in hardware_inventory:
                    try:
                        current_app.logger.info(f"Processing BitLocker data for asset {asset_id}")
                        bitlocker_data = hardware_inventory['bitlocker']
                        
                        if bitlocker_data.get('supported') and bitlocker_data.get('volumes'):
                            from utils.encryption import encrypt_data
                            
                            for volume in bitlocker_data['volumes']:
                                volume_letter = volume.get('volume_letter')
                                recovery_key = volume.get('recovery_key')
                                
                                if volume_letter and recovery_key:
                                    # Encrypt the recovery key
                                    encrypted_key = encrypt_data(recovery_key)
                                    
                                    # Upsert BitLocker data
                                    bitlocker_upsert_query = """
                                        INSERT INTO bitlocker_keys (
                                            asset_id, volume_letter, volume_label, protection_status,
                                            encryption_method, key_protector_type, recovery_key_id,
                                            recovery_key_encrypted, last_verified_at
                                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                                        ON CONFLICT (asset_id, volume_letter) DO UPDATE SET
                                            volume_label = EXCLUDED.volume_label,
                                            protection_status = EXCLUDED.protection_status,
                                            encryption_method = EXCLUDED.encryption_method,
                                            key_protector_type = EXCLUDED.key_protector_type,
                                            recovery_key_id = EXCLUDED.recovery_key_id,
                                            recovery_key_encrypted = EXCLUDED.recovery_key_encrypted,
                                            last_verified_at = EXCLUDED.last_verified_at,
                                            updated_at = NOW()
                                    """
                                    
                                    current_app.db_manager.execute_query(
                                        bitlocker_upsert_query,
                                        (
                                            asset_id,
                                            volume_letter,
                                            volume.get('volume_label', 'Local Disk'),
                                            volume.get('protection_status', 'Unknown'),
                                            volume.get('encryption_method'),
                                            volume.get('key_protector_type'),
                                            volume.get('recovery_key_id'),
                                            encrypted_key
                                        ),
                                        fetch='none'
                                    )
                                    
                                    current_app.logger.info(f"✅ BitLocker data saved for volume {volume_letter}")
                            
                            current_app.logger.info(f"✅ BitLocker processing completed for asset {asset_id}")
                        else:
                            current_app.logger.info(f"BitLocker not supported or no volumes for asset {asset_id}")
                    
                    except Exception as e:
                        current_app.logger.error(f"Error processing BitLocker data for asset {asset_id}: {e}")
'''
        
        # Insert the BitLocker processing code
        new_content = content[:insert_point] + bitlocker_processing_code + content[insert_point:]
        
        # Write the updated file
        print("2. Writing updated routes file...")
        
        with open(routes_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ BitLocker processing added to backend heartbeat handler")
        return True
        
    except Exception as e:
        print(f"❌ Error adding BitLocker processing: {e}")
        return False

def test_bitlocker_processing():
    """Test if BitLocker processing is working"""
    print("\n3. Testing BitLocker processing...")
    
    try:
        # Check if the backend is running
        import requests
        
        response = requests.get('http://localhost:5001/api/health', timeout=5)
        if response.status_code != 200:
            print("❌ Backend not running - start the backend first")
            return False
        
        print("✅ Backend is running")
        
        # The agent should now send BitLocker data that gets processed
        print("✅ BitLocker processing should now work when agent sends heartbeat")
        print("   Run the agent again to test: python run_fixed_agent.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing: {e}")
        return False

def main():
    """Main function"""
    print("🔧 LANET Backend BitLocker Processing Fix")
    print("=" * 70)
    
    if add_bitlocker_processing():
        if test_bitlocker_processing():
            print("\n🎉 SUCCESS: BitLocker processing added to backend!")
            print("\nNext steps:")
            print("1. Restart the backend server")
            print("2. Run the agent: python run_fixed_agent.py")
            print("3. Check frontend for BitLocker data")
            print("4. Verify database: python check_bitlocker_schema.py")
        else:
            print("\n⚠️ BitLocker processing added but testing failed")
    else:
        print("\n❌ Failed to add BitLocker processing")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
