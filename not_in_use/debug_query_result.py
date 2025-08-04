#!/usr/bin/env python3
"""
Debug query result format
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Add backend to path
sys.path.append('backend')

def debug_query_result():
    """Debug what the query actually returns"""
    print("🔍 Debugging query result format...")
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
            
            # Test the exact query from BitLocker endpoint
            query = """
                SELECT 
                    bk.id,
                    bk.volume_letter,
                    bk.volume_label,
                    bk.protection_status,
                    bk.encryption_method,
                    bk.key_protector_type,
                    bk.recovery_key_id,
                    bk.recovery_key_encrypted,
                    bk.created_at,
                    bk.updated_at,
                    bk.last_verified_at
                FROM bitlocker_keys bk
                WHERE bk.asset_id = %s
                ORDER BY bk.volume_letter
            """
            
            result = app.db_manager.execute_query(query, (asset_id,), fetch='all')
            
            print(f"📊 Query returned: {type(result)}")
            print(f"📊 Result length: {len(result) if result else 0}")
            
            if result:
                first_row = result[0]
                print(f"📊 First row type: {type(first_row)}")
                print(f"📊 First row content: {first_row}")
                
                # Try different ways to access the data
                print("\n🔍 Trying different access methods:")
                
                try:
                    print(f"  row[0]: {first_row[0]}")
                    print(f"  row[1]: {first_row[1]}")
                except Exception as e:
                    print(f"  ❌ Index access failed: {e}")
                
                try:
                    if hasattr(first_row, 'keys'):
                        print(f"  Keys: {list(first_row.keys())}")
                except Exception as e:
                    print(f"  ❌ Keys access failed: {e}")
                
                try:
                    if isinstance(first_row, dict):
                        print(f"  Dict access - id: {first_row.get('id')}")
                        print(f"  Dict access - volume_letter: {first_row.get('volume_letter')}")
                except Exception as e:
                    print(f"  ❌ Dict access failed: {e}")
                
                # Try to iterate
                try:
                    print(f"  Iteration:")
                    for i, item in enumerate(first_row):
                        print(f"    [{i}]: {item}")
                        if i > 5:  # Limit output
                            break
                except Exception as e:
                    print(f"  ❌ Iteration failed: {e}")
            
            return True
            
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_psycopg2():
    """Test with direct psycopg2 to compare"""
    print("\n🔍 Testing with direct psycopg2...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="lanet_helpdesk",
            user="postgres",
            password="Poikl55+*"
        )
        
        cursor = conn.cursor()
        
        asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
        query = """
            SELECT 
                bk.id,
                bk.volume_letter,
                bk.volume_label,
                bk.protection_status
            FROM bitlocker_keys bk
            WHERE bk.asset_id = %s
            ORDER BY bk.volume_letter
        """
        
        cursor.execute(query, (asset_id,))
        result = cursor.fetchall()
        
        print(f"📊 Direct psycopg2 result: {type(result)}")
        print(f"📊 Result length: {len(result) if result else 0}")
        
        if result:
            first_row = result[0]
            print(f"📊 First row type: {type(first_row)}")
            print(f"📊 First row content: {first_row}")
            
            print(f"  row[0]: {first_row[0]}")
            print(f"  row[1]: {first_row[1]}")
            print(f"  row[2]: {first_row[2]}")
            print(f"  row[3]: {first_row[3]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Direct psycopg2 error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Query Result Debug")
    print("=" * 50)
    
    # Test 1: App db_manager
    app_success = debug_query_result()
    
    # Test 2: Direct psycopg2
    direct_success = test_direct_psycopg2()
    
    print("\n" + "=" * 50)
    print("📋 DEBUG SUMMARY:")
    print(f"✅ App DB Manager: {'SUCCESS' if app_success else 'FAILED'}")
    print(f"✅ Direct psycopg2: {'SUCCESS' if direct_success else 'FAILED'}")

if __name__ == '__main__':
    main()
