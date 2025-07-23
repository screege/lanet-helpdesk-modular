#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify tiered heartbeat system is working
"""

import psycopg2
import json
from datetime import datetime

def verify_tiered_system():
    """Verify the tiered heartbeat system"""
    try:
        print("🔍 Verifying tiered heartbeat system...")
        
        conn = psycopg2.connect(
            host='localhost',
            database='lanet_helpdesk',
            user='postgres', 
            password='Poikl55+*'
        )
        
        cursor = conn.cursor()
        
        # Check optimized status table
        print("\n📊 Checking assets_status_optimized table...")
        cursor.execute("""
            SELECT asset_id, agent_status, cpu_percent, memory_percent, 
                   disk_percent, last_seen, last_heartbeat 
            FROM assets_status_optimized 
            ORDER BY last_seen DESC LIMIT 1
        """)
        
        result = cursor.fetchone()
        if result:
            asset_id, status, cpu, memory, disk, last_seen, last_heartbeat = result
            print(f"✅ Latest status update:")
            print(f"  Asset ID: {asset_id}")
            print(f"  Status: {status}")
            print(f"  CPU: {cpu}%")
            print(f"  Memory: {memory}%") 
            print(f"  Disk: {disk}%")
            print(f"  Last seen: {last_seen}")
            print(f"  Last heartbeat: {last_heartbeat}")
        else:
            print("❌ No data in assets_status_optimized table")
        
        # Check inventory snapshots
        print("\n📦 Checking assets_inventory_snapshots table...")
        cursor.execute("SELECT COUNT(*) FROM assets_inventory_snapshots")
        count = cursor.fetchone()[0]
        print(f"✅ Inventory snapshots: {count} records")
        
        if count > 0:
            cursor.execute("""
                SELECT asset_id, version, created_at, inventory_hash
                FROM assets_inventory_snapshots 
                ORDER BY created_at DESC LIMIT 1
            """)
            result = cursor.fetchone()
            if result:
                asset_id, version, created_at, inv_hash = result
                print(f"  Latest snapshot:")
                print(f"    Asset ID: {asset_id}")
                print(f"    Version: {version}")
                print(f"    Created: {created_at}")
                print(f"    Hash: {inv_hash[:16]}...")
        
        # Check data size comparison
        print("\n📈 Data size analysis...")
        
        # Old system size (from main assets table)
        cursor.execute("""
            SELECT LENGTH(specifications::text) as old_size
            FROM assets 
            WHERE specifications IS NOT NULL
            ORDER BY last_seen DESC LIMIT 1
        """)
        result = cursor.fetchone()
        old_size = result[0] if result else 0
        
        # New system size (status only)
        new_status_size = 271  # From the heartbeat log
        
        print(f"  Old heartbeat size: ~{old_size} characters")
        print(f"  New status heartbeat: {new_status_size} characters")
        if old_size > 0:
            reduction = ((old_size - new_status_size) / old_size) * 100
            print(f"  📉 Size reduction: {reduction:.1f}%")
        
        # Calculate daily data savings for 2000 assets
        old_daily = (old_size * 288 * 2000) / (1024 * 1024)  # MB
        new_daily = (new_status_size * 288 * 2000 + 14000 * 2000) / (1024 * 1024)  # MB
        
        print(f"\n🌍 Projected daily data usage (2000 assets):")
        print(f"  Old system: {old_daily:.1f} MB/day")
        print(f"  New system: {new_daily:.1f} MB/day")
        print(f"  💾 Daily savings: {old_daily - new_daily:.1f} MB")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Tiered heartbeat system verification completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying system: {e}")
        return False

if __name__ == "__main__":
    verify_tiered_system()
