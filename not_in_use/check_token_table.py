#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Token Table Structure
"""

import psycopg2

def check_token_table():
    try:
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()
        
        # Check table structure
        cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'agent_installation_tokens'
        ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print('agent_installation_tokens columns:')
        for col, dtype, nullable in columns:
            print(f'  {col}: {dtype} ({nullable})')
        
        # Check if there's a sequence
        cur.execute("""
        SELECT pg_get_serial_sequence('agent_installation_tokens', column_name) as seq
        FROM information_schema.columns 
        WHERE table_name = 'agent_installation_tokens'
        AND pg_get_serial_sequence('agent_installation_tokens', column_name) IS NOT NULL
        """)
        
        sequences = cur.fetchall()
        print(f'\nSequences: {sequences}')
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_token_table()
