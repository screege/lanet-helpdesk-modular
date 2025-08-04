#!/usr/bin/env python3
"""
Simple BitLocker debug - test database and decryption directly
"""
import psycopg2
import os
from cryptography.fernet import Fernet

def test_database_connection():
    """Test database connection and query"""
    print("🔍 Testing database connection...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="lanet_helpdesk",
            user="postgres",
            password="Poikl55+*"
        )
        
        cursor = conn.cursor()
        
        # Test BitLocker query
        asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
        query = """
            SELECT 
                id,
                volume_letter,
                volume_label,
                protection_status,
                encryption_method,
                key_protector_type,
                recovery_key_id,
                recovery_key_encrypted,
                created_at,
                updated_at
            FROM bitlocker_keys
            WHERE asset_id = %s
            ORDER BY volume_letter
        """
        
        cursor.execute(query, (asset_id,))
        results = cursor.fetchall()
        
        print(f"✅ Database connection successful")
        print(f"📊 Found {len(results)} BitLocker volumes")
        
        for i, row in enumerate(results):
            print(f"  Volume {i+1}:")
            print(f"    Letter: {row[1]}")
            print(f"    Label: {row[2]}")
            print(f"    Status: {row[3]}")
            print(f"    Method: {row[4]}")
            print(f"    Protector: {row[5]}")
            print(f"    Key ID: {row[6]}")
            print(f"    Encrypted Key Length: {len(row[7]) if row[7] else 0}")
            print(f"    Created: {row[8]}")
        
        cursor.close()
        conn.close()
        
        return results
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None

def test_decryption(encrypted_key):
    """Test decryption of BitLocker key"""
    print("\n🔍 Testing decryption...")
    
    if not encrypted_key:
        print("❌ No encrypted key to test")
        return None
    
    try:
        # Try to get the encryption key from environment or config
        encryption_key = os.environ.get('BITLOCKER_ENCRYPTION_KEY', 'default-key-for-development-only')
        
        print(f"✅ Using encryption key: {encryption_key}")

        # Use the same logic as backend/utils/encryption.py
        import base64
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

        # Derive a proper key from the key material (same as backend)
        salt = b'lanet_helpdesk_salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
        fernet = Fernet(key)
        # Decode the base64 encoded data first (same as backend)
        decoded_data = base64.urlsafe_b64decode(encrypted_key.encode('utf-8'))
        decrypted = fernet.decrypt(decoded_data)
        decrypted_str = decrypted.decode('utf-8')
        
        print(f"✅ Decryption successful: {decrypted_str}")
        return decrypted_str
        
    except Exception as e:
        print(f"❌ Decryption error: {e}")
        return None

def test_backend_endpoint_simulation():
    """Simulate the backend endpoint logic"""
    print("\n🔍 Simulating backend endpoint logic...")
    
    try:
        # Step 1: Database query
        results = test_database_connection()
        
        if not results:
            print("❌ No data from database")
            return {"error": "No BitLocker data found"}
        
        # Step 2: Process results
        volumes = []
        for row in results:
            volume_data = {
                'id': row[0],
                'volume_letter': row[1],
                'volume_label': row[2],
                'protection_status': row[3],
                'encryption_method': row[4],
                'key_protector_type': row[5],
                'recovery_key_id': row[6],
                'created_at': row[8].isoformat() if row[8] else None,
                'updated_at': row[9].isoformat() if row[9] else None
            }
            
            # Step 3: Try to decrypt recovery key
            if row[7]:  # recovery_key_encrypted
                decrypted_key = test_decryption(row[7])
                if decrypted_key:
                    volume_data['recovery_key'] = decrypted_key
                else:
                    volume_data['recovery_key'] = "DECRYPTION_FAILED"
            else:
                volume_data['recovery_key'] = None
            
            volumes.append(volume_data)
        
        result = {
            'success': True,
            'data': {
                'asset_id': 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd',
                'volumes': volumes,
                'total_volumes': len(volumes)
            }
        }
        
        print(f"✅ Endpoint simulation successful")
        print(f"📊 Result: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ Endpoint simulation error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def main():
    print("🚀 Simple BitLocker Debug")
    print("=" * 50)
    
    # Test 1: Database connection and query
    db_results = test_database_connection()
    
    # Test 2: Decryption (if we have data)
    if db_results and db_results[0][7]:  # If there's encrypted data
        test_decryption(db_results[0][7])
    
    # Test 3: Full endpoint simulation
    endpoint_result = test_backend_endpoint_simulation()
    
    print("\n" + "=" * 50)
    print("📋 DEBUG SUMMARY:")
    print(f"✅ Database Query: {'SUCCESS' if db_results else 'FAILED'}")
    print(f"✅ Endpoint Simulation: {'SUCCESS' if endpoint_result.get('success') else 'FAILED'}")
    
    if endpoint_result.get('error'):
        print(f"❌ Error: {endpoint_result['error']}")

if __name__ == '__main__':
    main()
