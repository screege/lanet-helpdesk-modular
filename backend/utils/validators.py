#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Validation Utilities
Input validation and sanitization functions
"""

import re
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

class ValidationUtils:
    """Utility class for input validation"""
    
    # Regular expressions for validation
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_REGEX = re.compile(r'^\+?[\d\s\-\(\)]{10,15}$')
    RFC_REGEX = re.compile(r'^[A-Z&Ñ]{3,4}[0-9]{6}[A-Z0-9]{3}$')
    POSTAL_CODE_REGEX = re.compile(r'^\d{5}$')
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        return bool(ValidationUtils.EMAIL_REGEX.match(email.strip()))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        if not phone or not isinstance(phone, str):
            return False
        return bool(ValidationUtils.PHONE_REGEX.match(phone.strip()))
    
    @staticmethod
    def validate_rfc(rfc: str) -> bool:
        """Validate Mexican RFC format"""
        if not rfc or not isinstance(rfc, str):
            return False
        return bool(ValidationUtils.RFC_REGEX.match(rfc.strip().upper()))
    
    @staticmethod
    def validate_postal_code(postal_code: str) -> bool:
        """Validate Mexican postal code format"""
        if not postal_code or not isinstance(postal_code, str):
            return False
        return bool(ValidationUtils.POSTAL_CODE_REGEX.match(postal_code.strip()))
    
    @staticmethod
    def validate_uuid(value: str) -> bool:
        """Validate UUID format"""
        if not value or not isinstance(value, str):
            return False
        try:
            uuid.UUID(value)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        
        if not password or not isinstance(password, str):
            return {'valid': False, 'errors': ['Password is required']}
        
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', password):
            errors.append('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Password must contain at least one special character')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: List[str]) -> Dict[str, str]:
        """Validate that required fields are present and not empty"""
        errors = {}
        
        for field in required_fields:
            if field not in data:
                errors[field] = f'{field} is required'
            elif not data[field] or (isinstance(data[field], str) and not data[field].strip()):
                errors[field] = f'{field} cannot be empty'
        
        return errors
    
    @staticmethod
    def validate_user_data(data: Dict, is_update: bool = False) -> Dict[str, str]:
        """Validate user creation/update data"""
        errors = {}
        
        # Required fields for creation
        if not is_update:
            required_fields = ['name', 'email', 'role']
            if 'password' not in data:
                required_fields.append('password')
            errors.update(ValidationUtils.validate_required_fields(data, required_fields))
        
        # Email validation
        if 'email' in data and data['email']:
            if not ValidationUtils.validate_email(data['email']):
                errors['email'] = 'Invalid email format'
        
        # Password validation (only if provided)
        if 'password' in data and data['password']:
            password_validation = ValidationUtils.validate_password(data['password'])
            if not password_validation['valid']:
                errors['password'] = '; '.join(password_validation['errors'])
        
        # Role validation
        valid_roles = ['superadmin', 'admin', 'technician', 'client_admin', 'solicitante']
        if 'role' in data and data['role'] not in valid_roles:
            errors['role'] = f'Role must be one of: {", ".join(valid_roles)}'
        
        # Phone validation (optional)
        if 'phone' in data and data['phone']:
            if not ValidationUtils.validate_phone(data['phone']):
                errors['phone'] = 'Invalid phone number format'
        
        # Client ID validation for client users
        if 'role' in data and data['role'] in ['client_admin', 'solicitante']:
            if 'client_id' not in data or not data['client_id']:
                errors['client_id'] = 'Client ID is required for client users'
            elif not ValidationUtils.validate_uuid(data['client_id']):
                errors['client_id'] = 'Invalid client ID format'
        
        return errors
    
    @staticmethod
    def validate_client_data(data: Dict, is_update: bool = False) -> Dict[str, str]:
        """Validate client creation/update data"""
        errors = {}
        
        # Required fields for creation
        if not is_update:
            required_fields = ['name', 'email']
            errors.update(ValidationUtils.validate_required_fields(data, required_fields))
        
        # Email validation
        if 'email' in data and data['email']:
            if not ValidationUtils.validate_email(data['email']):
                errors['email'] = 'Invalid email format'
        
        # RFC validation (optional)
        if 'rfc' in data and data['rfc']:
            if not ValidationUtils.validate_rfc(data['rfc']):
                errors['rfc'] = 'Invalid RFC format'
        
        # Phone validation (optional)
        if 'phone' in data and data['phone']:
            if not ValidationUtils.validate_phone(data['phone']):
                errors['phone'] = 'Invalid phone number format'
        
        # Postal code validation (optional)
        if 'postal_code' in data and data['postal_code']:
            if not ValidationUtils.validate_postal_code(data['postal_code']):
                errors['postal_code'] = 'Invalid postal code format (must be 5 digits)'
        
        return errors
    
    @staticmethod
    def validate_site_data(data: Dict, is_update: bool = False) -> Dict[str, str]:
        """Validate site creation/update data"""
        errors = {}
        
        # Required fields for creation
        if not is_update:
            required_fields = ['client_id', 'name', 'address', 'city', 'state', 'postal_code']
            errors.update(ValidationUtils.validate_required_fields(data, required_fields))
        
        # Client ID validation
        if 'client_id' in data and data['client_id']:
            if not ValidationUtils.validate_uuid(data['client_id']):
                errors['client_id'] = 'Invalid client ID format'
        
        # Postal code validation
        if 'postal_code' in data and data['postal_code']:
            if not ValidationUtils.validate_postal_code(data['postal_code']):
                errors['postal_code'] = 'Invalid postal code format (must be 5 digits)'
        
        # Latitude/longitude validation (optional)
        if 'latitude' in data and data['latitude'] is not None:
            try:
                lat = float(data['latitude'])
                if not -90 <= lat <= 90:
                    errors['latitude'] = 'Latitude must be between -90 and 90'
            except (ValueError, TypeError):
                errors['latitude'] = 'Invalid latitude format'
        
        if 'longitude' in data and data['longitude'] is not None:
            try:
                lng = float(data['longitude'])
                if not -180 <= lng <= 180:
                    errors['longitude'] = 'Longitude must be between -180 and 180'
            except (ValueError, TypeError):
                errors['longitude'] = 'Invalid longitude format'
        
        return errors
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = None) -> str:
        """Sanitize string input"""
        if not value or not isinstance(value, str):
            return ''
        
        # Strip whitespace and normalize
        sanitized = value.strip()
        
        # Truncate if max_length specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_pagination(page: Any, per_page: Any) -> Dict[str, Any]:
        """Validate pagination parameters"""
        errors = {}
        
        try:
            page = int(page) if page else 1
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
            errors['page'] = 'Invalid page number'
        
        try:
            per_page = int(per_page) if per_page else 20
            if per_page < 1:
                per_page = 20
            elif per_page > 100:
                per_page = 100
        except (ValueError, TypeError):
            per_page = 20
            errors['per_page'] = 'Invalid per_page value'
        
        return {
            'page': page,
            'per_page': per_page,
            'errors': errors
        }
