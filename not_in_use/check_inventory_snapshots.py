#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check what's stored in assets_inventory_snapshots table
"""

import psycopg2
import json

def check_inventory_snapshots():
    """Check what's stored in assets_inventory_snapshots table"""
    try:
        print("🔍 Checking assets_inventory_snapshots table...")
        
        conn = psycopg2.connect(
            host='localhost',
            database='lanet_helpdesk',
            user='postgres', 
            password='Poikl55+*'
        )
        
        cursor = conn.cursor()
        
        # Get the latest inventory snapshot
        print("\n📦 Latest inventory snapshots:")
        cursor.execute("""
            SELECT asset_id, hardware_summary, created_at, version
            FROM assets_inventory_snapshots 
            WHERE asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
            ORDER BY created_at DESC
            LIMIT 3
        """)
        
        results = cursor.fetchall()
        if results:
            for i, (asset_id, hardware_summary, created_at, version) in enumerate(results):
                print(f"\n--- Snapshot {i+1} ---")
                print(f"Asset ID: {asset_id}")
                print(f"Created: {created_at}")
                print(f"Version: {version}")
                
                if hardware_summary:
                    print(f"Hardware summary keys: {list(hardware_summary.keys())}")
                    
                    if 'disks' in hardware_summary:
                        disks = hardware_summary['disks']
                        print(f"\n💿 Found {len(disks)} disks:")
                        
                        for j, disk in enumerate(disks):
                            print(f"\n  Disk {j+1}:")
                            print(f"    Device: {disk.get('device', 'Unknown')}")
                            print(f"    Model: {disk.get('model', 'Unknown')}")
                            print(f"    Health Status: '{disk.get('health_status', 'NOT_SET')}'")
                            print(f"    SMART Status: '{disk.get('smart_status', 'NOT_SET')}'")
                            print(f"    Interface: {disk.get('interface_type', 'Unknown')}")
                            print(f"    Temperature: {disk.get('temperature', 'Unknown')}")
                            print(f"    Physical Size: {disk.get('physical_size_gb', 'Unknown')}")
                            
                            # Show all keys for debugging
                            print(f"    All keys: {list(disk.keys())}")
                    else:
                        print("❌ No disk data found in hardware_summary")
                else:
                    print("❌ No hardware_summary found")
        else:
            print("❌ No inventory snapshots found")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_inventory_snapshots()
