#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check user credentials in database
"""

import psycopg2

def check_user_credentials():
    """Check user credentials"""
    try:
        print("🔍 Checking user credentials...")
        
        conn = psycopg2.connect(
            host='localhost',
            database='lanet_helpdesk',
            user='postgres', 
            password='Poikl55+*'
        )
        
        cursor = conn.cursor()
        
        # Get all users with their emails and roles
        cursor.execute("""
            SELECT email, role, name, client_id, is_active
            FROM users 
            ORDER BY role, email
        """)
        
        users = cursor.fetchall()
        print(f"\n👥 Found {len(users)} users:")
        
        for email, role, name, client_id, is_active in users:
            status = "✅ Active" if is_active else "❌ Inactive"
            print(f"  - {email} ({role}) - {name} - {status}")
            if client_id:
                print(f"    Client ID: {client_id}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_user_credentials()
