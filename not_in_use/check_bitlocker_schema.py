#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check BitLocker Database Schema
"""

import psycopg2

def check_schema():
    """Check the BitLocker database schema"""
    try:
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()

        # Check bitlocker_keys table structure
        cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'bitlocker_keys'
        ORDER BY ordinal_position
        """)

        columns = cur.fetchall()
        print('BitLocker table columns:')
        for col, dtype in columns:
            print(f'  {col}: {dtype}')

        # Check if table has any data
        cur.execute('SELECT COUNT(*) FROM bitlocker_keys')
        count = cur.fetchone()[0]
        print(f'\nBitLocker records: {count}')

        # Check recent assets
        cur.execute("""
        SELECT asset_id, name, last_seen 
        FROM assets 
        WHERE last_seen > NOW() - INTERVAL '1 hour'
        ORDER BY last_seen DESC
        """)
        
        assets = cur.fetchall()
        print(f'\nRecent assets: {len(assets)}')
        for asset_id, name, last_seen in assets:
            print(f'  {name}: {last_seen}')

        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
