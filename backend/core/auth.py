#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Authentication Manager
Handles JWT tokens, password hashing, and user authentication
"""

import bcrypt
import secrets
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from typing import Dict, Optional, List
import logging

class AuthManager:
    """Centralized authentication management"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Password hashing failed: {e}")
            raise
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            self.logger.error(f"Password verification failed: {e}")
            return False
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user with email and password"""
        try:
            # Get user from database
            user = self.db.get_user_by_email(email)
            if not user:
                self.logger.warning(f"Authentication failed: user not found for email {email}")
                return None
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                self.logger.warning(f"Authentication failed: invalid password for email {email}")
                return None
            
            # Check if user is active
            if not user['is_active']:
                self.logger.warning(f"Authentication failed: inactive user {email}")
                return None
            
            # Update last login
            self.db.execute_update(
                'users',
                {'last_login': datetime.utcnow()},
                'user_id = %s',
                (user['user_id'],)
            )
            
            self.logger.info(f"User authenticated successfully: {email}")
            return user
            
        except Exception as e:
            self.logger.error(f"Authentication error for {email}: {e}")
            return None
    
    def create_tokens(self, user: Dict) -> Dict[str, str]:
        """Create JWT access and refresh tokens"""
        try:
            # Get user's site assignments
            user_sites = self.db.get_user_sites(user['user_id'])
            site_ids = [site['site_id'] for site in user_sites]
            
            # Prepare additional claims
            additional_claims = {
                'role': user['role'],
                'client_id': user['client_id'],
                'site_ids': site_ids,
                'name': user['name'],
                'email': user['email']
            }
            
            # Create tokens
            access_token = create_access_token(
                identity=str(user['user_id']),
                additional_claims=additional_claims
            )
            
            refresh_token = create_refresh_token(
                identity=str(user['user_id']),
                additional_claims=additional_claims
            )
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
        except Exception as e:
            self.logger.error(f"Token creation failed: {e}")
            raise
    
    def generate_password_reset_token(self, user_id: str) -> str:
        """Generate a password reset token"""
        try:
            # Generate secure token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(minutes=15)  # 15 minutes expiry
            
            # Store token in database
            self.db.execute_insert(
                'password_reset_tokens',
                {
                    'user_id': user_id,
                    'token': token,
                    'expires_at': expires_at
                }
            )
            
            self.logger.info(f"Password reset token generated for user {user_id}")
            return token
            
        except Exception as e:
            self.logger.error(f"Password reset token generation failed: {e}")
            raise
    
    def validate_password_reset_token(self, token: str) -> Optional[str]:
        """Validate password reset token and return user_id"""
        try:
            query = """
            SELECT user_id FROM password_reset_tokens 
            WHERE token = %s AND expires_at > %s AND used = false
            """
            result = self.db.execute_query(
                query, 
                (token, datetime.utcnow()), 
                fetch='one'
            )
            
            if result:
                return result['user_id']
            return None
            
        except Exception as e:
            self.logger.error(f"Password reset token validation failed: {e}")
            return None
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password using token"""
        try:
            # Validate token
            user_id = self.validate_password_reset_token(token)
            if not user_id:
                return False
            
            # Hash new password
            password_hash = self.hash_password(new_password)
            
            # Update password
            rows_updated = self.db.execute_update(
                'users',
                {'password_hash': password_hash, 'updated_at': datetime.utcnow()},
                'user_id = %s',
                (user_id,)
            )
            
            if rows_updated > 0:
                # Mark token as used
                self.db.execute_update(
                    'password_reset_tokens',
                    {'used': True, 'used_at': datetime.utcnow()},
                    'token = %s',
                    (token,)
                )
                
                self.logger.info(f"Password reset successful for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Password reset failed: {e}")
            return False
    
    def check_role_permission(self, user_role: str, required_roles: List[str]) -> bool:
        """Check if user role has required permissions"""
        role_hierarchy = {
            'superadmin': 5,
            'admin': 4,
            'technician': 3,
            'client_admin': 2,
            'solicitante': 1
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_levels = [role_hierarchy.get(role, 0) for role in required_roles]
        
        return user_level >= max(required_levels) if required_levels else False
    
    def can_access_client(self, user_role: str, user_client_id: str, target_client_id: str) -> bool:
        """Check if user can access specific client data"""
        # Superadmin, admin, and technician can access all clients
        if user_role in ['superadmin', 'admin', 'technician']:
            return True
        
        # Client users can only access their own client
        return user_client_id == target_client_id
    
    def can_access_site(self, user_role: str, user_client_id: str, user_site_ids: List[str], target_site_id: str) -> bool:
        """Check if user can access specific site data"""
        # Superadmin, admin, and technician can access all sites
        if user_role in ['superadmin', 'admin', 'technician']:
            return True
        
        # Client admin can access all sites in their client
        if user_role == 'client_admin':
            # Need to verify site belongs to user's client
            query = "SELECT client_id FROM sites WHERE site_id = %s"
            result = self.db.execute_query(query, (target_site_id,), fetch='one')
            return result and result['client_id'] == user_client_id
        
        # Solicitante can only access assigned sites
        return target_site_id in user_site_ids
