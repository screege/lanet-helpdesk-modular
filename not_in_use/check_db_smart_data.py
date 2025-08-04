#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check what SMART data is stored in the database
"""

import psycopg2
import json

def check_db_smart_data():
    """Check what SMART data is stored in the database"""
    try:
        print("🔍 Checking database SMART data...")
        
        conn = psycopg2.connect(
            host='localhost',
            database='lanet_helpdesk',
            user='postgres', 
            password='Poikl55+*'
        )
        
        cursor = conn.cursor()
        
        # Get the latest inventory snapshot
        print("\n📦 Latest inventory snapshot:")
        cursor.execute("""
            SELECT hardware_summary, created_at
            FROM assets_inventory_snapshots 
            WHERE asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        if result:
            hardware_summary, created_at = result
            print(f"Created: {created_at}")
            
            if hardware_summary and 'disks' in hardware_summary:
                disks = hardware_summary['disks']
                print(f"\n💿 Found {len(disks)} disks in database:")
                
                for i, disk in enumerate(disks):
                    print(f"\n  Disk {i+1}:")
                    print(f"    Device: {disk.get('device', 'Unknown')}")
                    print(f"    Model: {disk.get('model', 'Unknown')}")
                    print(f"    Health Status: '{disk.get('health_status', 'NOT_SET')}'")
                    print(f"    SMART Status: '{disk.get('smart_status', 'NOT_SET')}'")
                    print(f"    Interface: {disk.get('interface_type', 'Unknown')}")
                    print(f"    Temperature: {disk.get('temperature', 'Unknown')}")
                    
                    # Show all keys for debugging
                    print(f"    All keys: {list(disk.keys())}")
            else:
                print("❌ No disk data found in hardware_summary")
        else:
            print("❌ No inventory snapshot found")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_db_smart_data()
