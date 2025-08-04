#!/usr/bin/env python3
"""
Test asset access function specifically
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Add backend to path
sys.path.append('backend')

def test_asset_access_function():
    """Test the _user_has_asset_access function directly"""
    print("🔍 Testing asset access function...")
    
    try:
        # Import Flask app
        from app import create_app
        
        # Create app
        app = create_app()
        
        with app.app_context():
            # Import the function
            from modules.bitlocker.routes import _user_has_asset_access
            
            # Test with superadmin user
            superadmin_user = {
                'role': 'superadmin',
                'client_id': None,
                'site_ids': [],
                'email': 'ba@lanet.mx',
                'sub': 'some-user-id'
            }
            
            asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
            
            print(f"🔍 Testing access for superadmin to asset {asset_id}")
            has_access = _user_has_asset_access(superadmin_user, asset_id)
            print(f"  Result: {has_access}")
            
            if has_access:
                print("✅ Superadmin access test passed")
                return True
            else:
                print("❌ Superadmin access test failed")
                return False
            
    except Exception as e:
        print(f"❌ Error testing asset access: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_query_directly():
    """Test the database query used in asset access"""
    print("\n🔍 Testing database query directly...")
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
            
            # Test the exact query from the function
            query = """
                SELECT 1 FROM assets 
                WHERE asset_id = %s
            """
            
            result = app.db_manager.execute_query(query, (asset_id,), fetch='one')
            print(f"  Query result: {result}")
            
            if result:
                print("✅ Database query test passed")
                return True
            else:
                print("❌ Database query test failed - asset not found")
                
                # Check what assets exist
                print("\n🔍 Available assets:")
                assets_query = "SELECT asset_id, name FROM assets LIMIT 5"
                assets = app.db_manager.execute_query(assets_query, fetch='all')
                for asset in assets:
                    print(f"  {asset[0]} - {asset[1]}")
                
                return False
            
    except Exception as e:
        print(f"❌ Database query error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bitlocker_query_directly():
    """Test the BitLocker query directly"""
    print("\n🔍 Testing BitLocker query directly...")
    
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
            print(f"  BitLocker query result: {len(result) if result else 0} rows")
            
            if result:
                print("✅ BitLocker query test passed")
                for i, row in enumerate(result):
                    print(f"    Volume {i+1}: {row[1]} - {row[3]}")
                return True
            else:
                print("❌ BitLocker query test failed - no data found")
                return False
            
    except Exception as e:
        print(f"❌ BitLocker query error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Asset Access Test")
    print("=" * 50)
    
    # Test 1: Asset access function
    access_success = test_asset_access_function()
    
    # Test 2: Database query
    db_success = test_database_query_directly()
    
    # Test 3: BitLocker query
    bitlocker_success = test_bitlocker_query_directly()
    
    print("\n" + "=" * 50)
    print("📋 ASSET ACCESS TEST SUMMARY:")
    print(f"✅ Asset Access Function: {'SUCCESS' if access_success else 'FAILED'}")
    print(f"✅ Database Query: {'SUCCESS' if db_success else 'FAILED'}")
    print(f"✅ BitLocker Query: {'SUCCESS' if bitlocker_success else 'FAILED'}")
    
    if access_success and db_success and bitlocker_success:
        print("\n🎉 All tests passed! The issue is elsewhere.")
    else:
        print("\n❌ Some tests failed - this explains the 500 error")

if __name__ == '__main__':
    main()
