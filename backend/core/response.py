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
    
    def bad_request(self, message: str = "Bad request") -> tuple:
        """Create a bad request response"""
        return self.error(message, 400)

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

        # Handle phone number mapping: if affected_person_phone is empty, use affected_person_contact
        if not safe_ticket.get('affected_person_phone') and safe_ticket.get('affected_person_contact'):
            safe_ticket['affected_person_phone'] = safe_ticket['affected_person_contact']

        # Convert datetime objects to ISO format
        datetime_fields = [
            'created_at', 'updated_at', 'assigned_at',
            'resolved_at', 'closed_at', 'approved_at'
        ]
        for field in datetime_fields:
            if field in safe_ticket and safe_ticket[field]:
                safe_ticket[field] = safe_ticket[field].isoformat()

        return safe_ticket

    def format_comment_data(self, comment: Dict) -> Dict:
        """Format comment data for API response"""
        if not comment:
            return None

        safe_comment = comment.copy()

        # Convert datetime objects to ISO format
        datetime_fields = ['created_at', 'updated_at']
        for field in datetime_fields:
            if field in safe_comment and safe_comment[field]:
                safe_comment[field] = safe_comment[field].isoformat()

        return safe_comment

    def format_activity_data(self, activity: Dict) -> Dict:
        """Format activity data for API response"""
        if not activity:
            return None

        safe_activity = activity.copy()

        # Convert datetime objects to ISO format
        if 'created_at' in safe_activity and safe_activity['created_at']:
            safe_activity['created_at'] = safe_activity['created_at'].isoformat()

        return safe_activity

    def format_attachment_data(self, attachment: Dict) -> Dict:
        """Format attachment data for API response"""
        if not attachment:
            return None

        safe_attachment = attachment.copy()

        # Convert datetime objects to ISO format
        if 'created_at' in safe_attachment and safe_attachment['created_at']:
            safe_attachment['created_at'] = safe_attachment['created_at'].isoformat()

        # Format file size for display
        if 'file_size' in safe_attachment and safe_attachment['file_size']:
            size_bytes = safe_attachment['file_size']
            if size_bytes < 1024:
                safe_attachment['file_size_display'] = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                safe_attachment['file_size_display'] = f"{size_bytes / 1024:.1f} KB"
            else:
                safe_attachment['file_size_display'] = f"{size_bytes / (1024 * 1024):.1f} MB"

        return safe_attachment

    def format_category_data(self, category: Dict) -> Dict:
        """Format category data for API response"""
        if not category:
            return None

        safe_category = category.copy()

        # Convert datetime objects to ISO format
        datetime_fields = ['created_at', 'updated_at']
        for field in datetime_fields:
            if field in safe_category and safe_category[field]:
                safe_category[field] = safe_category[field].isoformat()

        return safe_category

    def format_email_config_data(self, config: Dict) -> Dict:
        """Format email configuration data for API response"""
        if not config:
            return None

        safe_config = config.copy()

        # Remove sensitive data
        sensitive_fields = ['smtp_password_encrypted', 'imap_password_encrypted']
        for field in sensitive_fields:
            if field in safe_config:
                safe_config[field] = '***' if safe_config[field] else None

        # Convert datetime objects to ISO format
        datetime_fields = ['created_at', 'updated_at']
        for field in datetime_fields:
            if field in safe_config and safe_config[field]:
                safe_config[field] = safe_config[field].isoformat()

        return safe_config

    def format_email_queue_data(self, queue_item: Dict) -> Dict:
        """Format email queue data for API response"""
        if not queue_item:
            return None

        safe_item = queue_item.copy()

        # Convert datetime objects to ISO format
        datetime_fields = ['created_at', 'updated_at', 'sent_at', 'next_attempt_at']
        for field in datetime_fields:
            if field in safe_item and safe_item[field]:
                safe_item[field] = safe_item[field].isoformat()

        return safe_item

    def format_sla_policy_data(self, policy: Dict) -> Dict:
        """Format SLA policy data for API response"""
        if not policy:
            return None

        safe_policy = policy.copy()

        # Convert datetime objects to ISO format
        datetime_fields = ['created_at', 'updated_at']
        for field in datetime_fields:
            if field in safe_policy and safe_policy[field]:
                safe_policy[field] = safe_policy[field].isoformat()

        # Parse escalation levels JSON
        if 'escalation_levels' in safe_policy and safe_policy['escalation_levels']:
            try:
                import json
                safe_policy['escalation_levels'] = json.loads(safe_policy['escalation_levels'])
            except:
                safe_policy['escalation_levels'] = []

        return safe_policy

    def format_sla_tracking_data(self, tracking: Dict) -> Dict:
        """Format SLA tracking data for API response"""
        if not tracking:
            return None

        safe_tracking = tracking.copy()

        # Convert datetime objects to ISO format
        datetime_fields = [
            'response_deadline', 'resolution_deadline', 'first_response_at',
            'resolved_at', 'response_breached_at', 'resolution_breached_at',
            'last_escalation_at', 'created_at', 'updated_at'
        ]
        for field in datetime_fields:
            if field in safe_tracking and safe_tracking[field]:
                safe_tracking[field] = safe_tracking[field].isoformat()

        return safe_tracking

    def format_sla_breach_data(self, breach: Dict) -> Dict:
        """Format SLA breach data for API response"""
        if not breach:
            return None

        safe_breach = breach.copy()

        # Convert datetime objects to ISO format
        datetime_fields = ['response_deadline', 'resolution_deadline', 'created_at']
        for field in datetime_fields:
            if field in safe_breach and safe_breach[field]:
                safe_breach[field] = safe_breach[field].isoformat()

        return safe_breach

    def format_sla_warning_data(self, warning: Dict) -> Dict:
        """Format SLA warning data for API response"""
        if not warning:
            return None

        safe_warning = warning.copy()

        # Convert datetime objects to ISO format
        datetime_fields = ['response_deadline', 'resolution_deadline']
        for field in datetime_fields:
            if field in safe_warning and safe_warning[field]:
                safe_warning[field] = safe_warning[field].isoformat()

        return safe_warning
