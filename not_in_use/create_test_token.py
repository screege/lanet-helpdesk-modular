#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Test Token for Production Installer Testing
"""

import psycopg2
import uuid
from datetime import datetime, timedelta

def create_test_token():
    """Create a test installation token"""
    try:
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()
        
        # Get a client and site for the token
        cur.execute("""
            SELECT c.client_id, s.site_id, c.name as client_name, s.name as site_name
            FROM clients c
            JOIN sites s ON c.client_id = s.client_id
            LIMIT 1
        """)
        
        result = cur.fetchone()
        if not result:
            print("No clients/sites found in database")
            return None
        
        client_id, site_id, client_name, site_name = result
        
        # Generate token
        token_value = f"LANET-TEST-PROD-{uuid.uuid4().hex[:6].upper()}"
        
        # Get a user ID for created_by
        cur.execute("SELECT user_id FROM users WHERE role = 'superadmin' LIMIT 1")
        user_result = cur.fetchone()
        created_by = user_result[0] if user_result else None

        # Create token
        cur.execute("""
            INSERT INTO agent_installation_tokens (
                token_id, token_value, client_id, site_id,
                is_active, expires_at, created_by, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(uuid.uuid4()),
            token_value,
            client_id,
            site_id,
            True,
            datetime.now() + timedelta(days=30),
            created_by,
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Test token created: {token_value}")
        print(f"   Client: {client_name}")
        print(f"   Site: {site_name}")
        
        return token_value
        
    except Exception as e:
        print(f"Error creating test token: {e}")
        return None

if __name__ == "__main__":
    token = create_test_token()
    if token:
        print(f"\nUse this token to test the installer:")
        print(f'dist\\LANET_Agent_Installer.exe --silent --token "{token}" --server-url "http://localhost:5001/api"')
