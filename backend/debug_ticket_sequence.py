#!/usr/bin/env python3
"""
Debug ticket number sequence generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def debug_ticket_sequence():
    """Debug ticket number sequence generation"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Debugging Ticket Number Sequence")
        print("=" * 50)
        
        try:
            # Test 1: Check if sequence exists
            print("1. Checking if ticket_number_seq exists...")
            
            sequence_check = app.db_manager.execute_query("""
                SELECT sequence_name, start_value, increment
                FROM information_schema.sequences
                WHERE sequence_name = 'ticket_number_seq'
            """, fetch='one')
            
            if sequence_check:
                print(f"✅ Sequence exists: {sequence_check['sequence_name']}")
                print(f"   Start value: {sequence_check['start_value']}")
                print(f"   Increment: {sequence_check['increment']}")
            else:
                print("❌ Sequence does not exist!")
                return
            
            # Test 2: Check if function exists
            print("\n2. Checking if generate_ticket_number function exists...")
            
            function_check = app.db_manager.execute_query("""
                SELECT routine_name, routine_definition
                FROM information_schema.routines 
                WHERE routine_name = 'generate_ticket_number'
                AND routine_type = 'FUNCTION'
            """, fetch='one')
            
            if function_check:
                print(f"✅ Function exists: {function_check['routine_name']}")
            else:
                print("❌ Function does not exist!")
                return
            
            # Test 3: Try to call the function directly
            print("\n3. Testing generate_ticket_number() function...")
            
            try:
                result = app.db_manager.execute_query("""
                    SELECT generate_ticket_number() as ticket_number
                """, fetch='one')
                
                if result:
                    print(f"✅ Function call successful: {result['ticket_number']}")
                else:
                    print("❌ Function returned no result")
                    
            except Exception as e:
                print(f"❌ Function call failed: {e}")
                
                # Test 4: Try direct sequence access
                print("\n4. Testing direct sequence access...")
                
                try:
                    direct_result = app.db_manager.execute_query("""
                        SELECT 'TKT-' || LPAD(nextval('ticket_number_seq')::TEXT, 6, '0') as ticket_number
                    """, fetch='one')
                    
                    if direct_result:
                        print(f"✅ Direct sequence access successful: {direct_result['ticket_number']}")
                    else:
                        print("❌ Direct sequence access failed")
                        
                except Exception as e2:
                    print(f"❌ Direct sequence access failed: {e2}")
            
            # Test 5: Check current sequence value
            print("\n5. Checking current sequence value...")
            
            try:
                seq_value = app.db_manager.execute_query("""
                    SELECT currval('ticket_number_seq') as current_value
                """, fetch='one')
                
                if seq_value:
                    print(f"✅ Current sequence value: {seq_value['current_value']}")

                    # Check if value is too high for integer
                    if seq_value['current_value'] > 2147483647:
                        print(f"❌ Sequence value {seq_value['current_value']} exceeds integer limit!")
                        print("   This is causing the overflow error")
                        
                        # Reset sequence to a reasonable value
                        print("\n6. Resetting sequence to reasonable value...")
                        app.db_manager.execute_query("""
                            SELECT setval('ticket_number_seq', 1, false)
                        """, fetch='one')
                        print("✅ Sequence reset to 1")
                        
                        # Test again
                        test_result = app.db_manager.execute_query("""
                            SELECT 'TKT-' || LPAD(nextval('ticket_number_seq')::TEXT, 6, '0') as ticket_number
                        """, fetch='one')
                        
                        if test_result:
                            print(f"✅ After reset: {test_result['ticket_number']}")
                        
                else:
                    print("❌ Could not get sequence value")
                    
            except Exception as e:
                print(f"❌ Error checking sequence value: {e}")
            
        except Exception as e:
            print(f"❌ Error debugging ticket sequence: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_ticket_sequence()
