#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Encryption utilities for sensitive data like BitLocker keys
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Global encryption key (in production, this should be from environment variables)
_encryption_key = None

def _get_encryption_key():
    """Get or generate encryption key"""
    global _encryption_key
    
    if _encryption_key is None:
        # In production, use environment variable
        key_material = os.environ.get('BITLOCKER_ENCRYPTION_KEY', 'default-key-for-development-only')
        
        # Derive a proper key from the key material
        salt = b'lanet_helpdesk_salt'  # In production, use a random salt stored securely
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_material.encode()))
        _encryption_key = Fernet(key)
    
    return _encryption_key

def encrypt_data(data):
    """Encrypt sensitive data"""
    if not data:
        return None
    
    try:
        fernet = _get_encryption_key()
        encrypted_data = fernet.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    except Exception as e:
        raise Exception(f"Encryption failed: {e}")

def decrypt_data(encrypted_data):
    """Decrypt sensitive data"""
    if not encrypted_data:
        return None
    
    try:
        fernet = _get_encryption_key()
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
        decrypted_data = fernet.decrypt(decoded_data)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        raise Exception(f"Decryption failed: {e}")

def is_encrypted(data):
    """Check if data appears to be encrypted"""
    if not data or not isinstance(data, str):
        return False
    
    try:
        # Try to decode as base64
        base64.urlsafe_b64decode(data.encode('utf-8'))
        return True
    except:
        return False
