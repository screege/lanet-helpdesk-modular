#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Response Manager
Standardized API response formatting
"""

from flask import jsonify
from typing import Any, Dict, Optional
import logging

class ResponseManager:
    """Centralized response management for consistent API responses"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def success(self, data: Any = None, message: str = None, status_code: int = 200) -> tuple:
        """Create a successful response"""
        response = {
            'success': True,
            'data': data
        }
        
        if message:
            response['message'] = message
            
        return jsonify(response), status_code
    
    def error(self, message: str, status_code: int = 400, details: Dict = None) -> tuple:
        """Create an error response"""
        response = {
            'success': False,
            'error': message
        }
        
        if details:
            response['details'] = details
            
        # Log error for debugging
        if status_code >= 500:
            self.logger.error(f"Server error: {message}")
        elif status_code >= 400:
            self.logger.warning(f"Client error: {message}")
            
        return jsonify(response), status_code
    
    def validation_error(self, errors: Dict[str, str]) -> tuple:
        """Create a validation error response"""
        return self.error(
            message="Validation failed",
            status_code=400,
            details={'validation_errors': errors}
        )
    
    def unauthorized(self, message: str = "Unauthorized access") -> tuple:
        """Create an unauthorized response"""
        return self.error(message, 401)
    
    def forbidden(self, message: str = "Access forbidden") -> tuple:
        """Create a forbidden response"""
        return self.error(message, 403)
    
    def not_found(self, resource: str = "Resource") -> tuple:
        """Create a not found response"""
        return self.error(f"{resource} not found", 404)
    
    def conflict(self, message: str) -> tuple:
        """Create a conflict response"""
        return self.error(message, 409)
    
    def server_error(self, message: str = "Internal server error") -> tuple:
        """Create a server error response"""
        return self.error(message, 500)
    
    def created(self, data: Any = None, message: str = "Resource created successfully") -> tuple:
        """Create a resource created response"""
        return self.success(data, message, 201)
    
    def updated(self, data: Any = None, message: str = "Resource updated successfully") -> tuple:
        """Create a resource updated response"""
        return self.success(data, message, 200)
    
    def deleted(self, message: str = "Resource deleted successfully") -> tuple:
        """Create a resource deleted response"""
        return self.success(None, message, 200)
    
    def paginated(self, data: list, page: int, per_page: int, total: int, message: str = None) -> tuple:
        """Create a paginated response"""
        total_pages = (total + per_page - 1) // per_page
        
        response_data = {
            'items': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
        
        return self.success(response_data, message)
    
    def format_user_data(self, user: Dict) -> Dict:
        """Format user data for API response (remove sensitive fields)"""
        if not user:
            return None
            
        safe_user = user.copy()
        # Remove sensitive fields
        safe_user.pop('password_hash', None)
        
        # Convert datetime objects to ISO format
        for field in ['created_at', 'updated_at', 'last_login']:
            if field in safe_user and safe_user[field]:
                safe_user[field] = safe_user[field].isoformat()
                
        return safe_user
    
    def format_client_data(self, client: Dict) -> Dict:
        """Format client data for API response"""
        if not client:
            return None
            
        safe_client = client.copy()
        
        # Convert datetime objects to ISO format
        for field in ['created_at', 'updated_at']:
            if field in safe_client and safe_client[field]:
                safe_client[field] = safe_client[field].isoformat()
                
        return safe_client

    def format_site_data(self, site: Dict) -> Dict:
        """Format site data for API response"""
        if not site:
            return None

        safe_site = site.copy()

        # Format datetime fields
        for field in ['created_at', 'updated_at']:
            if field in safe_site and safe_site[field]:
                safe_site[field] = safe_site[field].isoformat()

        return safe_site

    def format_ticket_data(self, ticket: Dict) -> Dict:
        """Format ticket data for API response"""
        if not ticket:
            return None
            
        safe_ticket = ticket.copy()
        
        # Convert datetime objects to ISO format
        datetime_fields = [
            'created_at', 'updated_at', 'assigned_at', 
            'resolved_at', 'closed_at', 'approved_at'
        ]
        for field in datetime_fields:
            if field in safe_ticket and safe_ticket[field]:
                safe_ticket[field] = safe_ticket[field].isoformat()
                
        return safe_ticket
