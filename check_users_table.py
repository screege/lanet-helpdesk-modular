#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check the users table structure
"""

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from core.database import DatabaseManager

def check_users_structure():
    """Check the actual structure of the users table"""
    try:
        db_manager = DatabaseManager('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        
        print("🔍 CHECKING USERS TABLE STRUCTURE")
        print("=" * 60)
        
        # Get table structure
        structure_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'users'
        ORDER BY ordinal_position
        """
        
        columns = db_manager.execute_query(structure_query)
        
        if columns:
            print("📋 Users table columns:")
            for col in columns:
                print(f"   {col['column_name']} ({col['data_type']}) - Nullable: {col['is_nullable']}")
        
        # Get sample user data
        print(f"\n📊 Sample users data:")
        sample_query = "SELECT * FROM users LIMIT 3"
        users = db_manager.execute_query(sample_query)
        
        if users:
            for user in users:
                print(f"   User ID: {user.get('user_id', 'N/A')}")
                print(f"   Email: {user.get('email', 'N/A')}")
                print(f"   Name fields: {[k for k in user.keys() if 'name' in k.lower()]}")
                print(f"   All fields: {list(user.keys())}")
                print()
        
    except Exception as e:
        print(f"❌ Error checking users structure: {e}")

if __name__ == "__main__":
    check_users_structure()
