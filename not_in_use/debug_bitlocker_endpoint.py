#!/usr/bin/env python3
"""
Debug BitLocker endpoint directly
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def test_bitlocker_endpoint_directly():
    """Test BitLocker endpoint directly without HTTP"""
    print("🔍 Testing BitLocker endpoint directly...")
    
    try:
        # Import the BitLocker module
        from backend.modules.bitlocker.routes import get_bitlocker_info
        from backend.core.database import DatabaseManager
        from backend.core.response_manager import ResponseManager
        
        # Create a minimal Flask app for testing
        app = Flask(__name__)
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
        
        jwt = JWTManager(app)
        
        # Initialize database and response manager
        db_manager = DatabaseManager()
        response_manager = ResponseManager()
        
        app.db_manager = db_manager
        app.response_manager = response_manager
        
        with app.app_context():
            # Create a test JWT token
            token = create_access_token(
                identity='ba@lanet.mx',
                additional_claims={
                    'role': 'superadmin',
                    'client_id': None,
                    'site_ids': [],
                    'email': 'ba@lanet.mx'
                }
            )
            
            print(f"✅ Test token created: {token[:50]}...")
            
            # Test the function directly
            asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
            
            # Mock the JWT context
            from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
            
            # This is tricky - we need to mock the JWT context
            print("⚠️ Direct function testing requires JWT context mocking")
            print("Let's test the database query directly instead...")
            
            # Test database query directly
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
            
            result = db_manager.execute_query(query, (asset_id,), fetch='all')
            print(f"📊 Database query result: {result}")
            
            if result:
                print(f"✅ Found {len(result)} BitLocker volumes")
                for i, row in enumerate(result):
                    print(f"  Volume {i+1}: {row[1]} - {row[3]} - Encrypted key length: {len(row[7]) if row[7] else 0}")
            else:
                print("❌ No BitLocker volumes found in database")
                
            # Test decryption
            if result and result[0][7]:  # If there's an encrypted key
                from backend.utils.encryption import decrypt_data
                try:
                    decrypted = decrypt_data(result[0][7])
                    print(f"✅ Decryption successful: {decrypted}")
                except Exception as e:
                    print(f"❌ Decryption failed: {e}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_access_function():
    """Test the user access function"""
    print("\n🔍 Testing user access function...")
    
    try:
        from backend.modules.bitlocker.routes import _user_has_asset_access
        from backend.core.database import DatabaseManager
        
        # Create a minimal Flask app for testing
        app = Flask(__name__)
        db_manager = DatabaseManager()
        app.db_manager = db_manager
        
        with app.app_context():
            current_user = {
                'role': 'superadmin',
                'client_id': None,
                'site_ids': [],
                'email': 'ba@lanet.mx',
                'sub': 'ba@lanet.mx'
            }
            
            asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
            
            has_access = _user_has_asset_access(current_user, asset_id)
            print(f"✅ User access check: {has_access}")
            
            return has_access
            
    except Exception as e:
        print(f"❌ Error testing user access: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 BitLocker Endpoint Debug")
    print("=" * 50)
    
    # Test 1: User access function
    access_success = test_user_access_function()
    
    # Test 2: Direct endpoint testing
    endpoint_success = test_bitlocker_endpoint_directly()
    
    print("\n" + "=" * 50)
    print("📋 DEBUG SUMMARY:")
    print(f"✅ User Access: {'SUCCESS' if access_success else 'FAILED'}")
    print(f"✅ Endpoint Test: {'SUCCESS' if endpoint_success else 'FAILED'}")

if __name__ == '__main__':
    main()
