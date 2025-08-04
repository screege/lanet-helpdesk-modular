#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Database Schema
"""

import psycopg2

def check_schema():
    try:
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()
        
        # Check all tables
        cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        print(f'Database tables ({len(tables)}):')
        for table in tables:
            print(f'  {table[0]}')
        
        # Check for token-related tables
        token_tables = [t[0] for t in tables if 'token' in t[0].lower()]
        print(f'\nToken-related tables: {token_tables}')
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
