#!/usr/bin/env python3
"""
Check what data is really in the database
"""
import psycopg2

def check_database_data():
    """Check what data is really in the database"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='lanet_helpdesk',
            user='postgres',
            password='Poikl55+*'
        )
        
        cursor = conn.cursor()
        
        # Check BitLocker data with timestamps
        print('🔍 BitLocker data in database:')
        cursor.execute('''
            SELECT asset_id, volume_letter, protection_status, 
                   recovery_key_encrypted, created_at, updated_at
            FROM bitlocker_keys 
            ORDER BY created_at DESC
        ''')
        
        results = cursor.fetchall()
        if results:
            for row in results:
                print(f'Asset: {row[0]}')
                print(f'Volume: {row[1]} - {row[2]}')
                print(f'Created: {row[4]}')
                print(f'Updated: {row[5]}')
                print(f'Key encrypted: {"YES" if row[3] else "NO"}')
                print('---')
        else:
            print('No BitLocker data found')
        
        # Check SMART data
        print('\n🔍 SMART data in database:')
        cursor.execute('SELECT COUNT(*) FROM smart_data')
        smart_count = cursor.fetchone()[0]
        print(f'SMART records: {smart_count}')
        
        if smart_count > 0:
            cursor.execute('SELECT asset_id, created_at FROM smart_data ORDER BY created_at DESC LIMIT 3')
            smart_results = cursor.fetchall()
            for row in smart_results:
                print(f'Asset: {row[0]}, Created: {row[1]}')
        
        # Check when was the last heartbeat
        print('\n🔍 Last heartbeat data:')
        cursor.execute('''
            SELECT asset_id, last_seen, status 
            FROM assets 
            WHERE last_seen IS NOT NULL 
            ORDER BY last_seen DESC 
            LIMIT 5
        ''')
        
        heartbeat_results = cursor.fetchall()
        if heartbeat_results:
            for row in heartbeat_results:
                print(f'Asset: {row[0]}, Last seen: {row[1]}, Status: {row[2]}')
        else:
            print('No heartbeat data found')
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == '__main__':
    check_database_data()
