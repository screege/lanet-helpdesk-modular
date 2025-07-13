#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - User Password Fix Utility
Fix bcrypt hash corruption issues and reset user passwords
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import DatabaseManager
from core.auth import AuthManager

def fix_user_passwords():
    """Fix corrupted password hashes for all users"""
    
    # Initialize managers
    db = DatabaseManager('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
    auth = AuthManager(db)
    
    # Default passwords for different roles
    default_passwords = {
        'superadmin': 'TestAdmin123!',
        'admin': 'TestAdmin123!', 
        'technician': 'TestTech123!',
        'client_admin': 'Poikl55+*',
        'solicitante': 'Poikl55+*'
    }
    
    print("🔧 Fixing user password hashes...")
    
    # Get all users
    users = db.execute_query("SELECT user_id, email, role, name FROM users WHERE is_active = true")
    
    for user in users:
        email = user['email']
        role = user['role']
        name = user['name']
        
        # Get default password for role
        password = default_passwords.get(role, 'Poikl55+*')
        
        # Generate proper hash using AuthManager
        try:
            password_hash = auth.hash_password(password)
            
            # Update using database manager (prevents corruption)
            result = db.execute_update(
                'users',
                {'password_hash': password_hash},
                'user_id = %s',
                (user['user_id'],)
            )
            
            if result:
                print(f"✅ Fixed: {email} ({role}) - Password: {password}")
            else:
                print(f"❌ Failed: {email}")
                
        except Exception as e:
            print(f"❌ Error fixing {email}: {e}")
    
    print("\n🎉 Password fix completed!")
    print("\n📋 Default Passwords by Role:")
    for role, pwd in default_passwords.items():
        print(f"   {role}: {pwd}")

def create_test_users():
    """Create additional test users for testing"""
    
    db = DatabaseManager('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
    auth = AuthManager(db)
    
    test_users = [
        {
            'name': 'Técnico de Prueba',
            'email': 'tech@test.com',
            'password': 'TestTech123!',
            'role': 'technician',
            'client_id': None
        },
        {
            'name': 'Admin de Prueba', 
            'email': 'admin@test.com',
            'password': 'TestAdmin123!',
            'role': 'admin',
            'client_id': None
        }
    ]
    
    print("\n👥 Creating test users...")
    
    for user_data in test_users:
        # Check if user exists
        existing = db.get_user_by_email(user_data['email'])
        if existing:
            print(f"⚠️  User {user_data['email']} already exists")
            continue
            
        try:
            # Hash password properly
            password_hash = auth.hash_password(user_data['password'])
            
            # Create user data
            import uuid
            from datetime import datetime
            
            user_record = {
                'user_id': str(uuid.uuid4()),
                'client_id': user_data['client_id'],
                'name': user_data['name'],
                'email': user_data['email'],
                'password_hash': password_hash,
                'role': user_data['role'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'created_by': '770e8400-e29b-41d4-a716-446655440001'  # ba@lanet.mx
            }
            
            # Insert user
            result = db.execute_insert('users', user_record)
            
            if result:
                print(f"✅ Created: {user_data['email']} ({user_data['role']}) - Password: {user_data['password']}")
            else:
                print(f"❌ Failed to create: {user_data['email']}")
                
        except Exception as e:
            print(f"❌ Error creating {user_data['email']}: {e}")

if __name__ == '__main__':
    print("🚀 LANET Helpdesk V3 - User Password Fix Utility")
    print("=" * 60)
    
    # Fix existing users
    fix_user_passwords()
    
    # Create test users
    create_test_users()
    
    print("\n✅ All operations completed!")
