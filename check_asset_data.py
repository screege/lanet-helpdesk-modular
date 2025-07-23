#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check what data is stored for the asset
"""

import psycopg2
import json

def check_asset_data():
    """Check what data is stored for the asset"""
    try:
        print("🔍 Checking asset data in database...")
        
        conn = psycopg2.connect(
            host='localhost',
            database='lanet_helpdesk',
            user='postgres', 
            password='Poikl55+*'
        )
        
        cursor = conn.cursor()
        
        # Get asset data from main table
        print("\n📊 Main asset data:")
        cursor.execute("""
            SELECT asset_id, name, specifications 
            FROM assets 
            WHERE name LIKE '%benny%'
        """)
        
        result = cursor.fetchone()
        if result:
            asset_id, name, specs = result
            print(f"Asset: {name}")
            print(f"ID: {asset_id}")
            
            if specs:
                print(f"\n📋 Specifications keys: {list(specs.keys())}")
                
                # Check hardware info
                if 'hardware_info' in specs:
                    hw = specs['hardware_info']
                    print(f"\n🔧 Hardware info keys: {list(hw.keys())}")
                    
                    # Memory info
                    if 'memory' in hw:
                        print(f"💾 Memory: {hw['memory']}")
                    
                    # Disk info
                    if 'disks' in hw:
                        print(f"💿 Disks: {len(hw['disks'])} found")
                        for i, disk in enumerate(hw['disks']):
                            print(f"  Disk {i+1}: {disk.get('device', 'Unknown')} - Health: {disk.get('health_status', 'Unknown')}")
                
                # Check system metrics
                if 'system_metrics' in specs:
                    metrics = specs['system_metrics']
                    print(f"\n📈 System metrics: {metrics}")
        
        # Check optimized status table
        print("\n📊 Optimized status data:")
        cursor.execute("""
            SELECT cpu_percent, memory_percent, disk_percent, last_seen
            FROM assets_status_optimized 
            WHERE asset_id = %s
        """, (asset_id,))
        
        status_result = cursor.fetchone()
        if status_result:
            cpu, memory, disk, last_seen = status_result
            print(f"CPU: {cpu}%, Memory: {memory}%, Disk: {disk}%")
            print(f"Last seen: {last_seen}")
        
        # Check inventory snapshots
        print("\n📦 Inventory snapshots:")
        cursor.execute("""
            SELECT hardware_summary, software_summary, created_at
            FROM assets_inventory_snapshots 
            WHERE asset_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (asset_id,))
        
        inventory_result = cursor.fetchone()
        if inventory_result:
            hw_summary, sw_summary, created_at = inventory_result
            print(f"Created: {created_at}")
            if hw_summary:
                print(f"Hardware summary keys: {list(hw_summary.keys())}")
                if 'memory' in hw_summary:
                    print(f"Memory data: {hw_summary['memory']}")
                if 'disks' in hw_summary:
                    print(f"Disk data: {len(hw_summary['disks'])} disks")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_asset_data()
