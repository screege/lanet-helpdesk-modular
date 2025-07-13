#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to update user passwords with proper bcrypt hashes
"""

import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DATABASE_URL = "postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk"

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def update_user_password(email, password):
    """Update user password in database"""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        password_hash = hash_password(password)
        
        cur.execute(
            "UPDATE users SET password_hash = %s WHERE email = %s",
            (password_hash, email)
        )
        
        if cur.rowcount > 0:
            print(f"Updated password for {email}")
        else:
            print(f"User {email} not found")
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error updating password for {email}: {e}")

if __name__ == "__main__":
    # Update test user passwords
    users = [
        ("ba@lanet.mx", "TestAdmin123!"),
        ("admin@test.com", "TestAdmin123!"),
        ("tech@test.com", "TestAdmin123!"),
        ("carlos.tech@lanet.mx", "TestAdmin123!"),
        ("prueba@prueba.com", "TestAdmin123!"),
        ("admin@disenonono.com", "TestAdmin123!"),
        ("admin@tecnicoaguila.mx", "TestAdmin123!"),
        ("prueba3@prueba.com", "TestAdmin123!"),
        ("usuario@disenonono.com", "TestAdmin123!"),
        ("usuario@solucionfacil.com.mx", "TestAdmin123!")
    ]
    
    for email, password in users:
        update_user_password(email, password)
    
    print("Password update completed!")
