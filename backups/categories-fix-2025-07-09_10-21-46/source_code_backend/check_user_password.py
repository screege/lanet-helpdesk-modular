#!/usr/bin/env python3
"""
Check user password in database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def check_user_password():
    """Check user password in database"""
    app = create_app()
    
    with app.app_context():
        print("🔍 CHECKING USER PASSWORDS")
        print("=" * 60)
        
        # Get user info
        users = app.db_manager.execute_query("""
            SELECT email, password_hash, role, is_active
            FROM users 
            WHERE email IN ('ba@lanet.mx', 'admin@test.com', 'test@test.com')
            ORDER BY email
        """)
        
        print("Users in database:")
        for user in users:
            print(f"  Email: {user['email']}")
            print(f"  Role: {user['role']}")
            print(f"  Active: {user['is_active']}")
            print(f"  Password hash: {user['password_hash'][:50]}...")
            print()
        
        # Test password verification
        print("Testing password verification...")
        
        if users:
            test_user = users[0]  # Use first user
            
            # Test common passwords
            test_passwords = ['admin123', '123456', 'password', 'admin', 'test']
            
            import bcrypt
            
            for password in test_passwords:
                try:
                    is_valid = bcrypt.checkpw(
                        password.encode('utf-8'), 
                        test_user['password_hash'].encode('utf-8')
                    )
                    print(f"  Password '{password}': {'✅ VALID' if is_valid else '❌ Invalid'}")
                except Exception as e:
                    print(f"  Password '{password}': ❌ Error - {e}")
        
        # Also check if backend is running
        print(f"\nChecking if backend is accessible...")
        
        try:
            import requests
            response = requests.get('http://localhost:5001/api/health', timeout=5)
            print(f"Backend health check: {response.status_code}")
        except Exception as e:
            print(f"❌ Backend not accessible: {e}")

if __name__ == '__main__':
    check_user_password()
