#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Auth Module Routes
Authentication endpoints: login, logout, password reset, token refresh
"""

from flask import Blueprint, request, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils.validators import ValidationUtils
from utils.security import SecurityUtils, log_user_action

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User authentication endpoint"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return current_app.response_manager.error('Request body required', 400)
        
        # Sanitize input
        data = SecurityUtils.sanitize_dict(data)
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return current_app.response_manager.error('Email and password are required', 400)
        
        # Validate email format
        if not ValidationUtils.validate_email(data['email']):
            return current_app.response_manager.error('Invalid email format', 400)
        
        # Authenticate user
        user = current_app.auth_manager.authenticate_user(
            data['email'].lower().strip(),
            data['password']
        )
        
        if not user:
            return current_app.response_manager.error('Invalid credentials', 401)
        
        # Create tokens
        tokens = current_app.auth_manager.create_tokens(user)
        
        # Format user data for response
        user_data = current_app.response_manager.format_user_data(user)
        
        # Log successful login
        current_app.logger.info(f"User logged in: {user['email']}")
        
        return current_app.response_manager.success({
            'user': user_data,
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token']
        }, 'Login successful')
        
    except Exception as e:
        current_app.logger.error(f"Login error: {e}")
        return current_app.response_manager.server_error('Login failed')

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint"""
    try:
        user_id = get_jwt_identity()
        
        # In a production environment, you would add the token to a blacklist
        # For now, we'll just log the logout
        current_app.logger.info(f"User logged out: {user_id}")
        
        return current_app.response_manager.success(None, 'Logout successful')
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {e}")
        return current_app.response_manager.server_error('Logout failed')

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Get user data
        user = current_app.db_manager.execute_query(
            "SELECT * FROM users WHERE user_id = %s AND is_active = true",
            (user_id,),
            fetch='one'
        )
        
        if not user:
            return current_app.response_manager.error('User not found', 404)
        
        # Create new tokens
        tokens = current_app.auth_manager.create_tokens(user)
        
        return current_app.response_manager.success({
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token']
        }, 'Token refreshed successfully')
        
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {e}")
        return current_app.response_manager.server_error('Token refresh failed')

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        user_id = get_jwt_identity()
        
        # Get user data
        user = current_app.db_manager.execute_query(
            "SELECT * FROM users WHERE user_id = %s AND is_active = true",
            (user_id,),
            fetch='one'
        )
        
        if not user:
            return current_app.response_manager.error('User not found', 404)
        
        # Format user data
        user_data = current_app.response_manager.format_user_data(user)
        
        return current_app.response_manager.success(user_data)
        
    except Exception as e:
        current_app.logger.error(f"Get current user error: {e}")
        return current_app.response_manager.server_error('Failed to get user information')

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return current_app.response_manager.error('Request body required', 400)
        
        # Sanitize input
        data = SecurityUtils.sanitize_dict(data)
        
        # Validate email
        email = data.get('email', '').lower().strip()
        if not email or not ValidationUtils.validate_email(email):
            return current_app.response_manager.error('Valid email is required', 400)
        
        # Get user
        user = current_app.db_manager.get_user_by_email(email)
        
        # Always return success to prevent email enumeration
        if user:
            try:
                # Generate reset token
                token = current_app.auth_manager.generate_password_reset_token(user['user_id'])
                
                # In a real application, you would send an email here
                # For now, we'll just log it (remove in production)
                current_app.logger.info(f"Password reset token for {email}: {token}")
                
                # TODO: Send email with reset link
                # reset_url = f"http://localhost:5173/reset-password?token={token}"
                # send_password_reset_email(user['email'], user['name'], reset_url)
                
            except Exception as e:
                current_app.logger.error(f"Password reset token generation failed: {e}")
        
        return current_app.response_manager.success(
            None, 
            'If the email exists, a password reset link has been sent'
        )
        
    except Exception as e:
        current_app.logger.error(f"Forgot password error: {e}")
        return current_app.response_manager.server_error('Password reset request failed')

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return current_app.response_manager.error('Request body required', 400)
        
        # Sanitize input
        data = SecurityUtils.sanitize_dict(data)
        
        # Validate required fields
        token = data.get('token', '').strip()
        new_password = data.get('password', '')
        
        if not token:
            return current_app.response_manager.error('Reset token is required', 400)
        
        if not new_password:
            return current_app.response_manager.error('New password is required', 400)
        
        # Validate password strength
        password_validation = ValidationUtils.validate_password(new_password)
        if not password_validation['valid']:
            return current_app.response_manager.validation_error({
                'password': '; '.join(password_validation['errors'])
            })
        
        # Reset password
        success = current_app.auth_manager.reset_password(token, new_password)
        
        if not success:
            return current_app.response_manager.error('Invalid or expired reset token', 400)
        
        current_app.logger.info(f"Password reset successful for token: {token[:8]}...")
        
        return current_app.response_manager.success(
            None, 
            'Password reset successful'
        )
        
    except Exception as e:
        current_app.logger.error(f"Password reset error: {e}")
        return current_app.response_manager.server_error('Password reset failed')

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@log_user_action('change_password', 'users')
def change_password():
    """Change user password (authenticated)"""
    try:
        user_id = get_jwt_identity()
        
        # Get request data
        data = request.get_json()
        if not data:
            return current_app.response_manager.error('Request body required', 400)
        
        # Sanitize input
        data = SecurityUtils.sanitize_dict(data)
        
        # Validate required fields
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return current_app.response_manager.error(
                'Current password and new password are required', 400
            )
        
        # Get user
        user = current_app.db_manager.execute_query(
            "SELECT password_hash FROM users WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )
        
        if not user:
            return current_app.response_manager.error('User not found', 404)
        
        # Verify current password
        if not current_app.auth_manager.verify_password(current_password, user['password_hash']):
            return current_app.response_manager.error('Current password is incorrect', 400)
        
        # Validate new password strength
        password_validation = ValidationUtils.validate_password(new_password)
        if not password_validation['valid']:
            return current_app.response_manager.validation_error({
                'new_password': '; '.join(password_validation['errors'])
            })
        
        # Hash new password
        new_password_hash = current_app.auth_manager.hash_password(new_password)
        
        # Update password
        rows_updated = current_app.db_manager.execute_update(
            'users',
            {'password_hash': new_password_hash},
            'user_id = %s',
            (user_id,)
        )
        
        if rows_updated == 0:
            return current_app.response_manager.error('Failed to update password', 500)
        
        current_app.logger.info(f"Password changed for user: {user_id}")
        
        return current_app.response_manager.success(
            None, 
            'Password changed successfully'
        )
        
    except Exception as e:
        current_app.logger.error(f"Change password error: {e}")
        return current_app.response_manager.server_error('Password change failed')
