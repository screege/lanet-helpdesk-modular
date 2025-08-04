#!/usr/bin/env python3
"""
Debug the decrypt_data function directly
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Add backend to path
sys.path.append('backend')

def test_decrypt_function():
    """Test the decrypt_data function directly"""
    print("🔍 Testing decrypt_data function...")
    
    try:
        # Import the function
        from utils.encryption import decrypt_data, encrypt_data
        
        # Test encryption/decryption cycle
        test_key = "123456-789012-345678-901234-567890-654321"
        print(f"🔑 Test key: {test_key}")
        
        # Test encryption
        encrypted = encrypt_data(test_key)
        print(f"✅ Encryption successful: {encrypted[:50]}...")
        
        # Test decryption
        decrypted = decrypt_data(encrypted)
        print(f"✅ Decryption successful: {decrypted}")
        
        if decrypted == test_key:
            print("✅ Round-trip successful!")
            return True, encrypted
        else:
            print("❌ Round-trip failed!")
            return False, None
            
    except Exception as e:
        print(f"❌ Error in decrypt function: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_database_decryption():
    """Test decryption of actual database data"""
    print("\n🔍 Testing decryption of database data...")
    
    try:
        import psycopg2
        from utils.encryption import decrypt_data
        
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="lanet_helpdesk",
            user="postgres",
            password="Poikl55+*"
        )
        
        cursor = conn.cursor()
        
        # Get encrypted data from database
        asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
        query = """
            SELECT volume_letter, recovery_key_encrypted
            FROM bitlocker_keys
            WHERE asset_id = %s AND recovery_key_encrypted IS NOT NULL
            LIMIT 1
        """
        
        cursor.execute(query, (asset_id,))
        result = cursor.fetchone()
        
        if result:
            volume_letter, encrypted_key = result
            print(f"📊 Found encrypted key for volume {volume_letter}")
            print(f"   Encrypted length: {len(encrypted_key)}")
            
            # Try to decrypt
            try:
                decrypted_key = decrypt_data(encrypted_key)
                print(f"✅ Decryption successful: {decrypted_key}")
                return True
            except Exception as e:
                print(f"❌ Decryption failed: {e}")
                return False
        else:
            print("❌ No encrypted keys found in database")
            return False
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database decryption test error: {e}")
        return False

def test_environment_variables():
    """Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    # Check environment variables
    bitlocker_key = os.environ.get('BITLOCKER_ENCRYPTION_KEY')
    jwt_key = os.environ.get('JWT_SECRET_KEY')
    
    print(f"🔑 BITLOCKER_ENCRYPTION_KEY: {'SET' if bitlocker_key else 'NOT_SET'}")
    print(f"🔑 JWT_SECRET_KEY: {'SET' if jwt_key else 'NOT_SET'}")
    
    if bitlocker_key:
        print(f"   Value: {bitlocker_key}")
        return True
    else:
        print("❌ BITLOCKER_ENCRYPTION_KEY not found!")
        return False

def main():
    print("🚀 Decrypt Function Debug")
    print("=" * 50)
    
    # Test 1: Environment variables
    env_success = test_environment_variables()
    
    # Test 2: Decrypt function
    decrypt_success, test_encrypted = test_decrypt_function()
    
    # Test 3: Database decryption
    db_decrypt_success = test_database_decryption()
    
    print("\n" + "=" * 50)
    print("📋 DECRYPT DEBUG SUMMARY:")
    print(f"✅ Environment Variables: {'SUCCESS' if env_success else 'FAILED'}")
    print(f"✅ Decrypt Function: {'SUCCESS' if decrypt_success else 'FAILED'}")
    print(f"✅ Database Decryption: {'SUCCESS' if db_decrypt_success else 'FAILED'}")
    
    if env_success and decrypt_success and db_decrypt_success:
        print("\n🎉 All decryption tests passed!")
        print("   The issue may be in the Flask app context or endpoint logic")
    elif env_success and decrypt_success:
        print("\n⚠️ Function works but database decryption fails")
        print("   Database may have data encrypted with different key")
    else:
        print("\n❌ Fundamental decryption issues detected")

if __name__ == '__main__':
    main()
