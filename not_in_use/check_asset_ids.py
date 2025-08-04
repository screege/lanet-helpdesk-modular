#!/usr/bin/env python3
"""
Check asset IDs in database
"""
import sys
sys.path.append('backend')

def check_database():
    """Check database for asset IDs"""
    try:
        import psycopg2
        
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="lanet_helpdesk",
            user="postgres",
            password="Poikl55+*"
        )
        
        cursor = conn.cursor()
        
        # Check bitlocker_keys table
        print("🔍 Checking bitlocker_keys table...")
        cursor.execute("SELECT asset_id, volume_letter, protection_status FROM bitlocker_keys")
        results = cursor.fetchall()
        
        print(f"📊 Found {len(results)} BitLocker records:")
        for asset_id, volume, status in results:
            print(f"  Asset: {asset_id}")
            print(f"  Volume: {volume} - {status}")
            print()
        
        # Check if our test asset exists
        test_asset = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
        cursor.execute("SELECT COUNT(*) FROM bitlocker_keys WHERE asset_id = %s", (test_asset,))
        count = cursor.fetchone()[0]
        print(f"🔍 Test asset {test_asset}: {count} records")
        
        # Check assets table to see what assets exist
        print("\n🔍 Checking assets table...")
        cursor.execute("SELECT id, hostname FROM assets LIMIT 5")
        assets = cursor.fetchall()
        
        print(f"📊 Found {len(assets)} assets:")
        for asset_id, hostname in assets:
            print(f"  {asset_id} - {hostname}")
        
        cursor.close()
        conn.close()
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == '__main__':
    check_database()
