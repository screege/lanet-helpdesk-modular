#!/usr/bin/env python3
"""
Check email authorization data structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def check_email_auth_data():
    """Check email authorization data structure"""
    app = create_app()
    
    with app.app_context():
        print("🔍 CHECKING EMAIL AUTHORIZATION DATA STRUCTURE")
        print("=" * 60)
        
        # Check sites table structure
        print("1. Checking sites table structure...")
        
        sites_columns = app.db_manager.execute_query("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'sites' 
            AND column_name LIKE '%email%'
            ORDER BY column_name
        """)
        
        print("Sites email-related columns:")
        for col in sites_columns:
            print(f"  {col['column_name']}: {col['data_type']}")
        
        # Check clients table structure
        print("\n2. Checking clients table structure...")
        
        clients_columns = app.db_manager.execute_query("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'clients' 
            AND column_name LIKE '%domain%'
            ORDER BY column_name
        """)
        
        print("Clients domain-related columns:")
        for col in clients_columns:
            print(f"  {col['column_name']}: {col['data_type']}")
        
        # Check actual data in sites
        print("\n3. Checking actual sites data...")
        
        sites_data = app.db_manager.execute_query("""
            SELECT c.name as client_name, s.name as site_name, s.authorized_emails
            FROM clients c
            JOIN sites s ON c.client_id = s.client_id
            WHERE c.is_active = true AND s.is_active = true
            LIMIT 5
        """)
        
        print("Sample sites data:")
        for site in sites_data:
            print(f"  Client: {site['client_name']}")
            print(f"  Site: {site['site_name']}")
            print(f"  Authorized emails: {site['authorized_emails']} (type: {type(site['authorized_emails'])})")
            print()
        
        # Check actual data in clients
        print("4. Checking actual clients data...")
        
        clients_data = app.db_manager.execute_query("""
            SELECT name, authorized_domains
            FROM clients
            WHERE is_active = true
            LIMIT 5
        """)
        
        print("Sample clients data:")
        for client in clients_data:
            print(f"  Client: {client['name']}")
            print(f"  Authorized domains: {client['authorized_domains']} (type: {type(client['authorized_domains'])})")
            print()
        
        # Test email validation with a known email
        print("5. Testing email validation...")
        
        from modules.email.service import EmailService
        email_service = EmailService()
        
        # Test with a few common emails
        test_emails = [
            'contacto@cafemexico.mx',
            'ba@lanet.mx',
            'screege@hotmail.com',
            'test@example.com'
        ]
        
        for test_email in test_emails:
            try:
                result = email_service.validate_sender_email(test_email)
                print(f"  {test_email}: {result}")
            except Exception as e:
                print(f"  {test_email}: ERROR - {e}")

if __name__ == '__main__':
    check_email_auth_data()
