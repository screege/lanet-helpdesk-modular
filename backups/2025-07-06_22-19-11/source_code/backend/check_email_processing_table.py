#!/usr/bin/env python3
"""
Check email processing table structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def check_email_processing_table():
    """Check email processing table structure"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Checking Email Processing Table Structure")
        print("=" * 60)
        
        # Check if table exists and its structure
        table_info = app.db_manager.execute_query("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'email_processing_log'
            ORDER BY ordinal_position
        """)
        
        if table_info:
            print(f"✅ email_processing_log table exists with {len(table_info)} columns:")
            for col in table_info:
                print(f"   {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        else:
            print(f"❌ email_processing_log table does not exist")
            return
        
        # Check recent entries
        print(f"\n📊 Recent Email Processing Log Entries:")
        print("-" * 40)
        
        try:
            recent_logs = app.db_manager.execute_query("""
                SELECT * FROM email_processing_log 
                ORDER BY created_at DESC 
                LIMIT 3
            """)
            
            if recent_logs:
                for i, log in enumerate(recent_logs, 1):
                    print(f"{i}. Log Entry:")
                    for key, value in log.items():
                        print(f"   {key}: {value}")
                    print()
            else:
                print("No entries found in email_processing_log")
                
        except Exception as e:
            print(f"❌ Error querying email_processing_log: {e}")
        
        # Check auto_delete_processed setting
        print(f"🔧 Email Configuration Settings:")
        print("-" * 40)
        
        config = app.db_manager.execute_query("""
            SELECT name, auto_delete_processed, enable_email_to_ticket
            FROM email_configurations 
            WHERE is_active = true
        """, fetch='one')
        
        if config:
            print(f"Configuration: {config['name']}")
            print(f"Auto Delete Processed: {config['auto_delete_processed']}")
            print(f"Email to Ticket Enabled: {config['enable_email_to_ticket']}")
            
            if not config['auto_delete_processed']:
                print(f"\n⚠️ ISSUE FOUND: auto_delete_processed is FALSE")
                print(f"   This means emails are NOT being deleted after processing")
                print(f"   They are only being marked as read")
                
                # Fix it
                print(f"\n🔧 Fixing auto_delete_processed setting...")
                app.db_manager.execute_query("""
                    UPDATE email_configurations 
                    SET auto_delete_processed = true 
                    WHERE is_active = true
                """, fetch='none')
                print(f"✅ auto_delete_processed set to TRUE")
            else:
                print(f"✅ auto_delete_processed is correctly set to TRUE")

if __name__ == '__main__':
    check_email_processing_table()
