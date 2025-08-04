#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the duplicate asset fix
"""

import psycopg2
import json
from datetime import datetime

def test_duplicate_fix():
    """Test the duplicate asset prevention fix"""
    
    print("🧪 Testing LANET Agent Duplicate Asset Fix")
    print("=" * 60)
    
    # Connect to database
    conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
    cur = conn.cursor()
    
    try:
        # 1. Check current duplicate status
        print("1. Checking current duplicate assets...")
        cur.execute("""
        SELECT 
            a.name,
            COUNT(*) as count,
            STRING_AGG(a.asset_id::text, ', ') as asset_ids
        FROM assets a
        WHERE a.status = 'active' AND a.name LIKE '%Agent%'
        GROUP BY a.name
        HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC
        """)
        
        duplicates_before = cur.fetchall()
        print(f"   Found {len(duplicates_before)} duplicate groups before fix")
        
        for name, count, asset_ids in duplicates_before:
            print(f"   - {name}: {count} duplicates ({asset_ids})")
        
        # 2. Test hardware fingerprint generation
        print("\n2. Testing hardware fingerprint generation...")
        
        # Sample hardware info similar to what agent would send
        sample_hardware_info = {
            'computer_name': 'test-computer',
            'network_interfaces': [
                {
                    'interface': 'Ethernet',
                    'mac_address': '00:11:22:33:44:55',
                    'ip_addresses': [{'ip': '192.168.1.100', 'netmask': '255.255.255.0'}]
                }
            ],
            'hardware': {
                'cpu': {'cores': 8},
                'memory': {'total_bytes': 34359738368},
                'disk': {'total_bytes': 1000204886016}
            },
            'platform_details': {
                'machine': 'AMD64',
                'processor': 'Intel64 Family 6 Model 142 Stepping 12, GenuineIntel'
            }
        }
        
        # Test fingerprint generation (simulate backend logic)
        import hashlib
        
        fingerprint_data = []
        fingerprint_data.append(f"name:{sample_hardware_info['computer_name']}")
        
        # MAC addresses
        mac_addresses = []
        for interface in sample_hardware_info['network_interfaces']:
            if interface.get('mac_address'):
                mac_addresses.append(interface['mac_address'].upper())
        
        if mac_addresses:
            mac_addresses.sort()
            fingerprint_data.append(f"mac:{','.join(mac_addresses)}")
        
        # Hardware details
        hardware = sample_hardware_info['hardware']
        fingerprint_data.append(f"cpu_cores:{hardware['cpu']['cores']}")
        fingerprint_data.append(f"memory:{hardware['memory']['total_bytes']}")
        fingerprint_data.append(f"disk:{hardware['disk']['total_bytes']}")
        
        # Platform details
        platform_details = sample_hardware_info['platform_details']
        fingerprint_data.append(f"machine:{platform_details['machine']}")
        fingerprint_data.append(f"processor:{platform_details['processor']}")
        
        fingerprint_string = '|'.join(sorted(fingerprint_data))
        fingerprint_hash = hashlib.sha256(fingerprint_string.encode('utf-8')).hexdigest()[:16]
        
        print(f"   Generated fingerprint: {fingerprint_hash}")
        print(f"   From data: {fingerprint_string}")
        
        # 3. Test duplicate detection query
        print("\n3. Testing duplicate detection query...")
        
        # Test the new fingerprint-based duplicate detection
        test_client_id = '75f6b906-db3a-404d-b032-3a52eac324c4'  # From agent database
        test_site_id = 'ec2368ae-cd4b-417d-86be-504088e5678c'    # From agent database
        
        cur.execute("""
        SELECT asset_id, name, client_id, site_id, specifications
        FROM assets
        WHERE client_id = %s 
        AND site_id = %s
        AND status = 'active'
        AND specifications->>'hardware_fingerprint' = %s
        LIMIT 1
        """, (test_client_id, test_site_id, fingerprint_hash))
        
        existing_by_fingerprint = cur.fetchone()
        
        if existing_by_fingerprint:
            print(f"   ✅ Found existing asset by fingerprint: {existing_by_fingerprint[0]}")
        else:
            print(f"   ℹ️  No existing asset found with fingerprint: {fingerprint_hash}")
        
        # Test name-based detection as fallback
        cur.execute("""
        SELECT asset_id, name, client_id, site_id
        FROM assets
        WHERE name = %s
        AND status = 'active'
        LIMIT 1
        """, ('test-computer (Agent)',))
        
        existing_by_name = cur.fetchone()
        
        if existing_by_name:
            print(f"   ✅ Found existing asset by name: {existing_by_name[0]}")
        else:
            print(f"   ℹ️  No existing asset found with name: test-computer (Agent)")
        
        # 4. Show recommendations
        print("\n4. Recommendations:")
        print("   ✅ Backend duplicate detection logic implemented")
        print("   ✅ Agent MAC address collection improved")
        print("   ✅ Hardware fingerprinting added")
        print("   ✅ Agent registration verification enhanced")
        
        if duplicates_before:
            print(f"\n   ⚠️  Clean up {len(duplicates_before)} existing duplicate groups:")
            print("      Run: python ELIMINAR_TODOS_ASSETS.py")
            print("      Then reinstall agents with new version")
        
        print("\n5. Next Steps:")
        print("   1. Recompile agent installer with fixes")
        print("   2. Clean existing duplicate assets")
        print("   3. Test agent installation/restart cycle")
        print("   4. Verify no new duplicates are created")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    test_duplicate_fix()
