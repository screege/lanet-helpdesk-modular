#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Fix Demo Users
Create proper demo users with correct roles and client assignments
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import DatabaseManager
from core.auth import AuthManager

def fix_demo_users():
    """Fix demo users according to blueprint requirements"""
    
    # Initialize managers
    db = DatabaseManager('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
    auth = AuthManager(db)
    
    print("🔧 Fixing demo users according to blueprint...")
    
    # Get client IDs
    industrias_tebi = db.execute_query(
        "SELECT client_id FROM clients WHERE name = 'Industrias Tebi'",
        fetch='one'
    )
    
    if not industrias_tebi:
        print("❌ Industrias Tebi client not found!")
        return
    
    tebi_client_id = industrias_tebi['client_id']
    
    # Demo users according to blueprint (4 roles only)
    demo_users = [
        {
            'email': 'ba@lanet.mx',
            'name': 'Bruno Administrador',
            'password': 'TestAdmin123!',
            'role': 'superadmin',
            'client_id': None,
            'description': 'Super Administrador del Sistema'
        },
        {
            'email': 'tech@test.com',
            'name': 'María González',
            'password': 'TestTech123!',
            'role': 'technician', 
            'client_id': None,
            'description': 'Técnico de Soporte'
        },
        {
            'email': 'prueba@prueba.com',
            'name': 'Carlos Tebi Admin',
            'password': 'Poikl55+*',
            'role': 'client_admin',
            'client_id': tebi_client_id,
            'description': 'Administrador de Industrias Tebi'
        },
        {
            'email': 'prueba3@prueba.com',
            'name': 'Ana Tebi Usuario',
            'password': 'Poikl55+*',
            'role': 'solicitante',
            'client_id': tebi_client_id,
            'description': 'Usuario Solicitante de Industrias Tebi'
        }
    ]
    
    print("\n👥 Creating/Updating demo users...")
    
    for user_data in demo_users:
        email = user_data['email']
        
        # Check if user exists
        existing = db.execute_query(
            "SELECT user_id, email, role FROM users WHERE email = %s",
            (email,),
            fetch='one'
        )
        
        # Generate proper password hash
        password_hash = auth.hash_password(user_data['password'])
        
        if existing:
            # Update existing user
            update_data = {
                'name': user_data['name'],
                'password_hash': password_hash,
                'role': user_data['role'],
                'client_id': user_data['client_id'],
                'is_active': True
            }
            
            result = db.execute_update(
                'users',
                update_data,
                'email = %s',
                (email,)
            )
            
            if result:
                print(f"✅ Updated: {email} ({user_data['role']}) - {user_data['description']}")
            else:
                print(f"❌ Failed to update: {email}")
        else:
            # Create new user
            import uuid
            from datetime import datetime
            
            user_record = {
                'user_id': str(uuid.uuid4()),
                'client_id': user_data['client_id'],
                'name': user_data['name'],
                'email': email,
                'password_hash': password_hash,
                'role': user_data['role'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'created_by': '770e8400-e29b-41d4-a716-446655440001'  # ba@lanet.mx
            }
            
            result = db.execute_insert('users', user_record)
            
            if result:
                print(f"✅ Created: {email} ({user_data['role']}) - {user_data['description']}")
            else:
                print(f"❌ Failed to create: {email}")
    
    print("\n🗑️ Removing invalid roles...")
    
    # Remove 'admin' role users (not in blueprint)
    admin_users = db.execute_query(
        "SELECT user_id, email FROM users WHERE role = 'admin'",
    )
    
    for admin_user in admin_users:
        # Convert admin to superadmin or deactivate
        if admin_user['email'] == 'admin@test.com':
            db.execute_update(
                'users',
                {'is_active': False},
                'user_id = %s',
                (admin_user['user_id'],)
            )
            print(f"🔒 Deactivated admin user: {admin_user['email']}")
    
    print("\n📋 Final Demo Credentials:")
    print("=" * 60)
    print("🔑 SUPERADMIN:")
    print("   Email: ba@lanet.mx")
    print("   Password: TestAdmin123!")
    print("   Role: Super Administrador")
    print("")
    print("🔧 TECHNICIAN:")
    print("   Email: tech@test.com") 
    print("   Password: TestTech123!")
    print("   Role: Técnico")
    print("")
    print("👔 CLIENT ADMIN:")
    print("   Email: prueba@prueba.com")
    print("   Password: Poikl55+*")
    print("   Role: Admin Cliente (Industrias Tebi)")
    print("")
    print("👤 SOLICITANTE:")
    print("   Email: prueba3@prueba.com")
    print("   Password: Poikl55+*")
    print("   Role: Solicitante (Industrias Tebi)")
    print("=" * 60)

def update_frontend_login_form():
    """Update frontend login form with correct demo credentials"""
    
    print("\n🎨 Updating frontend login form...")
    
    # The login form should have these 4 demo buttons
    demo_credentials = [
        {
            'label': 'Super Admin',
            'email': 'ba@lanet.mx',
            'password': 'TestAdmin123!',
            'role': 'superadmin'
        },
        {
            'label': 'Técnico',
            'email': 'tech@test.com', 
            'password': 'TestTech123!',
            'role': 'technician'
        },
        {
            'label': 'Admin Cliente',
            'email': 'prueba@prueba.com',
            'password': 'Poikl55+*',
            'role': 'client_admin'
        },
        {
            'label': 'Solicitante',
            'email': 'prueba3@prueba.com',
            'password': 'Poikl55+*',
            'role': 'solicitante'
        }
    ]
    
    print("✅ Frontend should show these 4 demo login buttons:")
    for cred in demo_credentials:
        print(f"   [{cred['label']}] {cred['email']} / {cred['password']}")

if __name__ == '__main__':
    print("🚀 LANET Helpdesk V3 - Demo Users Fix")
    print("=" * 60)
    
    # Fix demo users
    fix_demo_users()
    
    # Update frontend info
    update_frontend_login_form()
    
    print("\n✅ Demo users fix completed!")
    print("🌐 Test login at: http://localhost:5173")
