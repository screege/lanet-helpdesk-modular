#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Security Utilities
Security-related utility functions
"""

import re
import html
import secrets
import hashlib
import base64
import os
from cryptography.fernet import Fernet
from typing import Dict, List, Any, Optional
from functools import wraps
from flask import request, g, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

class SecurityUtils:
    """Utility class for security operations"""
    
    # XSS prevention patterns
    XSS_PATTERNS = [
        re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),
        re.compile(r'<iframe[^>]*>.*?</iframe>', re.IGNORECASE | re.DOTALL),
        re.compile(r'<object[^>]*>.*?</object>', re.IGNORECASE | re.DOTALL),
        re.compile(r'<embed[^>]*>', re.IGNORECASE),
    ]
    
    @staticmethod
    def sanitize_input(value: str) -> str:
        """Sanitize input to prevent XSS attacks"""
        if not value or not isinstance(value, str):
            return ''
        
        # HTML escape
        sanitized = html.escape(value)
        
        # Remove potentially dangerous patterns
        for pattern in SecurityUtils.XSS_PATTERNS:
            sanitized = pattern.sub('', sanitized)
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary values"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = SecurityUtils.sanitize_input(value)
            elif isinstance(value, dict):
                sanitized[key] = SecurityUtils.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    SecurityUtils.sanitize_input(item) if isinstance(item, str) 
                    else SecurityUtils.sanitize_dict(item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def _get_encryption_key() -> bytes:
        """Get or generate encryption key for sensitive data"""
        # In production, this should be stored securely (environment variable, key management service)
        # For now, we'll use a derived key from JWT secret
        try:
            jwt_secret = current_app.config.get('JWT_SECRET_KEY', 'default-secret-key')
            # Derive a 32-byte key from JWT secret
            key = hashlib.sha256(jwt_secret.encode()).digest()
            return base64.urlsafe_b64encode(key)
        except Exception:
            # Fallback key (should not be used in production)
            return base64.urlsafe_b64encode(b'default-encryption-key-32-bytes!')

    @staticmethod
    def encrypt_password(password: str) -> str:
        """Encrypt password for storage (for email passwords, etc.)"""
        try:
            if not password:
                return ''

            key = SecurityUtils._get_encryption_key()
            fernet = Fernet(key)
            encrypted = fernet.encrypt(password.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted).decode('utf-8')
        except Exception as e:
            current_app.logger.error(f"Password encryption failed: {e}")
            raise

    @staticmethod
    def decrypt_password(encrypted_password: str) -> str:
        """Decrypt password for use"""
        try:
            if not encrypted_password:
                return ''

            key = SecurityUtils._get_encryption_key()
            fernet = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode('utf-8'))
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            current_app.logger.error(f"Password decryption failed: {e}")
            raise
    
    @staticmethod
    def hash_file_content(content: bytes) -> str:
        """Generate SHA-256 hash of file content"""
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """Check if filename is safe (no path traversal)"""
        if not filename:
            return False
        
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            return False
        
        # Check for hidden files
        if filename.startswith('.'):
            return False
        
        # Check for reserved names (Windows)
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        name_without_ext = filename.split('.')[0].upper()
        if name_without_ext in reserved_names:
            return False
        
        return True
    
    @staticmethod
    def get_allowed_file_extensions() -> List[str]:
        """Get list of allowed file extensions"""
        return [
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'txt', 'rtf', 'csv',
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff',
            'zip', 'rar', '7z',
            'mp4', 'avi', 'mov', 'wmv',
            'mp3', 'wav', 'ogg'
        ]
    
    @staticmethod
    def is_allowed_file_type(filename: str) -> bool:
        """Check if file type is allowed"""
        if not filename:
            return False
        
        extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        return extension in SecurityUtils.get_allowed_file_extensions()
    
    @staticmethod
    def validate_file_upload(file) -> Dict[str, Any]:
        """Validate uploaded file"""
        errors = []
        
        if not file:
            errors.append('No file provided')
            return {'valid': False, 'errors': errors}
        
        if not file.filename:
            errors.append('No filename provided')
            return {'valid': False, 'errors': errors}
        
        # Check filename safety
        if not SecurityUtils.is_safe_filename(file.filename):
            errors.append('Unsafe filename')
        
        # Check file type
        if not SecurityUtils.is_allowed_file_type(file.filename):
            errors.append('File type not allowed')
        
        # Check file size (10MB limit)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            errors.append('File size exceeds 10MB limit')
        
        if file_size == 0:
            errors.append('File is empty')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'size': file_size
        }

def require_role(allowed_roles: List[str]):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                claims = get_jwt()
                user_role = claims.get('role')
                
                if not user_role or user_role not in allowed_roles:
                    return current_app.response_manager.forbidden(
                        f"Access denied. Required roles: {', '.join(allowed_roles)}"
                    )
                
                return f(*args, **kwargs)
            except Exception as e:
                current_app.logger.error(f"Role check failed: {e}")
                return current_app.response_manager.unauthorized()
        
        return decorated_function
    return decorator

def require_client_access(client_id_param: str = 'client_id'):
    """Decorator to require access to specific client"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                claims = get_jwt()
                user_role = claims.get('role')
                user_client_id = claims.get('client_id')
                
                # Get target client ID from request
                target_client_id = None
                if client_id_param in kwargs:
                    target_client_id = kwargs[client_id_param]
                elif request.json and client_id_param in request.json:
                    target_client_id = request.json[client_id_param]
                elif request.args.get(client_id_param):
                    target_client_id = request.args.get(client_id_param)
                
                # Check access
                if not current_app.auth_manager.can_access_client(
                    user_role, user_client_id, target_client_id
                ):
                    return current_app.response_manager.forbidden(
                        "Access denied to this client"
                    )
                
                return f(*args, **kwargs)
            except Exception as e:
                current_app.logger.error(f"Client access check failed: {e}")
                return current_app.response_manager.unauthorized()
        
        return decorated_function
    return decorator

def require_site_access(site_id_param: str = 'site_id'):
    """Decorator to require access to specific site"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                claims = get_jwt()
                user_role = claims.get('role')
                user_client_id = claims.get('client_id')
                user_site_ids = claims.get('site_ids', [])
                
                # Get target site ID from request
                target_site_id = None
                if site_id_param in kwargs:
                    target_site_id = kwargs[site_id_param]
                elif request.json and site_id_param in request.json:
                    target_site_id = request.json[site_id_param]
                elif request.args.get(site_id_param):
                    target_site_id = request.args.get(site_id_param)
                
                # Check access
                if not current_app.auth_manager.can_access_site(
                    user_role, user_client_id, user_site_ids, target_site_id
                ):
                    return current_app.response_manager.forbidden(
                        "Access denied to this site"
                    )
                
                return f(*args, **kwargs)
            except Exception as e:
                current_app.logger.error(f"Site access check failed: {e}")
                return current_app.response_manager.unauthorized()
        
        return decorated_function
    return decorator

def log_user_action(action: str, resource_type: str = None, resource_id: str = None):
    """Decorator to log user actions for audit trail"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Execute the function
                result = f(*args, **kwargs)
                
                # Log the action if user is authenticated
                if hasattr(g, 'current_user_id') and g.current_user_id:
                    audit_data = {
                        'user_id': g.current_user_id,
                        'action': action,
                        'table_name': resource_type,
                        'record_id': resource_id or kwargs.get('id'),
                        'ip_address': request.remote_addr,
                        'user_agent': request.headers.get('User-Agent', '')[:500],
                        'details': f"{request.method} {request.path}"
                    }
                    
                    current_app.db_manager.execute_insert('audit_log', audit_data)
                
                return result
            except Exception as e:
                current_app.logger.error(f"Action logging failed: {e}")
                return f(*args, **kwargs)  # Continue even if logging fails
        
        return decorated_function
    return decorator
