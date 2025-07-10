#!/usr/bin/env python3
"""
Fix database schema issues for ticket creation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def fix_database_schema():
    """Fix database schema issues"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Fixing Database Schema Issues")
        print("=" * 50)
        
        try:
            # Check if affected_person_contact column exists
            print("1. Checking tickets table schema...")
            
            column_check = app.db_manager.execute_query("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'tickets' 
                AND column_name = 'affected_person_contact'
            """, fetch='one')
            
            if not column_check:
                print("❌ Missing affected_person_contact column. Adding it...")

                # Add the missing column
                app.db_manager.execute_query("""
                    ALTER TABLE tickets
                    ADD COLUMN affected_person_contact VARCHAR(255) NOT NULL DEFAULT 'No especificado'
                """, fetch='none')

                # Remove the default after adding
                app.db_manager.execute_query("""
                    ALTER TABLE tickets
                    ALTER COLUMN affected_person_contact DROP DEFAULT
                """, fetch='none')

                print("✅ Added affected_person_contact column")
            else:
                print("✅ affected_person_contact column exists")
            
            # Check if ticket number sequence exists
            print("\n2. Checking ticket number sequence...")
            
            sequence_check = app.db_manager.execute_query("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_name = 'ticket_number_seq'
            """, fetch='one')
            
            if not sequence_check:
                print("❌ Missing ticket_number_seq sequence. Creating it...")

                # Create the sequence
                app.db_manager.execute_query("""
                    CREATE SEQUENCE ticket_number_seq START 1
                """, fetch='none')

                print("✅ Created ticket_number_seq sequence")
            else:
                print("✅ ticket_number_seq sequence exists")
            
            # Check if generate_ticket_number function exists
            print("\n3. Checking ticket number generation function...")
            
            function_check = app.db_manager.execute_query("""
                SELECT routine_name 
                FROM information_schema.routines 
                WHERE routine_name = 'generate_ticket_number'
                AND routine_type = 'FUNCTION'
            """, fetch='one')
            
            if not function_check:
                print("❌ Missing generate_ticket_number function. Creating it...")

                # Create the function
                app.db_manager.execute_query("""
                    CREATE OR REPLACE FUNCTION generate_ticket_number()
                    RETURNS VARCHAR(20) AS $$
                    BEGIN
                        RETURN 'TKT-' || LPAD(nextval('ticket_number_seq')::TEXT, 6, '0');
                    END;
                    $$ LANGUAGE plpgsql;
                """, fetch='none')

                print("✅ Created generate_ticket_number function")
            else:
                print("✅ generate_ticket_number function exists")
            
            # Test the ticket number generation
            print("\n4. Testing ticket number generation...")
            
            test_result = app.db_manager.execute_query("""
                SELECT generate_ticket_number() as ticket_number
            """, fetch='one')
            
            if test_result:
                print(f"✅ Ticket number generation test successful: {test_result['ticket_number']}")
            else:
                print("❌ Ticket number generation test failed")
            
            # Check current sequence value and reset if too high
            print("\n5. Checking sequence value...")
            
            seq_value = app.db_manager.execute_query("""
                SELECT last_value FROM ticket_number_seq
            """, fetch='one')
            
            if seq_value and seq_value['last_value'] > 999999:
                print(f"❌ Sequence value too high: {seq_value['last_value']}. Resetting...")

                # Reset sequence to a reasonable value
                app.db_manager.execute_query("""
                    SELECT setval('ticket_number_seq', 1, false)
                """, fetch='one')

                print("✅ Reset sequence to start from 1")
            else:
                print(f"✅ Sequence value is reasonable: {seq_value['last_value'] if seq_value else 'Not set'}")
            
            print("\n🎉 Database schema fixes completed successfully!")
            
        except Exception as e:
            print(f"❌ Error fixing database schema: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_database_schema()
