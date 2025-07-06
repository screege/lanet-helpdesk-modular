#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Notifications Service
Complete notification system for ticket events
"""

from typing import Dict, List, Optional
from flask import current_app
from modules.email.service import email_service

class NotificationsService:
    def __init__(self):
        self.notification_types = {
            'ticket_created': {
                'template_type': 'ticket_created',
                'recipients': ['client', 'assigned_technician', 'admins'],
                'priority': 3
            },
            'ticket_assigned': {
                'template_type': 'ticket_assigned',
                'recipients': ['client', 'assigned_technician', 'admins'],
                'priority': 2
            },
            'ticket_status_changed': {
                'template_type': 'ticket_updated',
                'recipients': ['client', 'assigned_technician'],
                'priority': 3
            },
            'ticket_commented': {
                'template_type': 'ticket_commented',
                'recipients': ['client', 'assigned_technician', 'admins'],
                'priority': 4
            },
            'ticket_resolved': {
                'template_type': 'ticket_resolved',
                'recipients': ['client', 'assigned_technician', 'admins'],
                'priority': 2
            },
            'ticket_closed': {
                'template_type': 'ticket_closed',
                'recipients': ['client'],
                'priority': 3
            },
            'sla_warning': {
                'template_type': 'sla_warning',
                'recipients': ['assigned_technician', 'admins'],
                'priority': 1
            },
            'sla_breach': {
                'template_type': 'sla_breach',
                'recipients': ['assigned_technician', 'admins', 'client'],
                'priority': 1
            }
        }
    
    def send_ticket_notification(self, notification_type: str, ticket_id: str,
                                additional_data: Dict = None) -> bool:
        """Send notification for ticket event"""
        try:
            current_app.logger.info(f"🔔 NOTIFICATION: Starting {notification_type} for ticket {ticket_id}")

            if notification_type not in self.notification_types:
                current_app.logger.warning(f"❌ NOTIFICATION: Unknown notification type: {notification_type}")
                return False

            # Get ticket details
            ticket = self._get_ticket_details(ticket_id)
            if not ticket:
                current_app.logger.error(f"❌ NOTIFICATION: Ticket not found: {ticket_id}")
                return False

            current_app.logger.info(f"🔔 NOTIFICATION: Found ticket {ticket['ticket_number']}")

            notification_config = self.notification_types[notification_type]

            # Get email template
            template = self._get_email_template(notification_config['template_type'])
            if not template:
                current_app.logger.warning(f"❌ NOTIFICATION: No template found for: {notification_config['template_type']}")
                return False

            # Get recipients
            recipients = self._get_notification_recipients(
                ticket,
                notification_config['recipients'],
                additional_data
            )

            if not recipients:
                current_app.logger.info(f"⚠️ NOTIFICATION: No recipients for notification: {notification_type}")
                return True

            current_app.logger.info(f"🔔 NOTIFICATION: Found {len(recipients)} recipients: {[r['email'] for r in recipients]}")

            # Prepare template variables
            template_vars = self._prepare_template_variables(ticket, additional_data)

            # Send notifications
            success_count = 0
            for recipient in recipients:
                if self._send_email_notification(
                    recipient, template, template_vars,
                    notification_config['priority'], ticket_id
                ):
                    success_count += 1

            current_app.logger.info(
                f"✅ NOTIFICATION: Sent {success_count}/{len(recipients)} notifications for {notification_type}"
            )
            return success_count > 0
            
        except Exception as e:
            current_app.logger.error(f"Error sending ticket notification: {e}")
            return False
    
    def _get_ticket_details(self, ticket_id: str) -> Optional[Dict]:
        """Get complete ticket details for notifications"""
        try:
            query = """
            SELECT t.ticket_id, t.ticket_number, t.subject, t.description, t.priority,
                   t.status, t.created_at, t.updated_at, t.assigned_at, t.resolved_at,
                   t.affected_person, t.affected_person_phone, t.notification_email, t.additional_emails,
                   t.client_id, c.name as client_name, c.email as client_email,
                   s.name as site_name, s.address as site_address,
                   cat.name as category_name,
                   creator.name as created_by_name, creator.email as created_by_email,
                   assignee.name as assigned_to_name, assignee.email as assigned_to_email
            FROM tickets t
            LEFT JOIN clients c ON t.client_id = c.client_id
            LEFT JOIN sites s ON t.site_id = s.site_id
            LEFT JOIN categories cat ON t.category_id = cat.category_id
            LEFT JOIN users creator ON t.created_by = creator.user_id
            LEFT JOIN users assignee ON t.assigned_to = assignee.user_id
            WHERE t.ticket_id = %s
            """
            
            return current_app.db_manager.execute_query(query, (ticket_id,), fetch='one')
            
        except Exception as e:
            current_app.logger.error(f"Error getting ticket details: {e}")
            return None
    
    def _get_email_template(self, template_type: str) -> Optional[Dict]:
        """Get email template by type"""
        try:
            query = """
            SELECT * FROM email_templates
            WHERE template_type = %s AND is_active = true
            ORDER BY is_default DESC, created_at DESC
            LIMIT 1
            """

            template = current_app.db_manager.execute_query(query, (template_type,), fetch='one')
            if template:
                current_app.logger.info(f"🔔 NOTIFICATION: Found template for {template_type}: {template['name']}")
            else:
                current_app.logger.warning(f"🔔 NOTIFICATION: No template found for {template_type}")
            return template

        except Exception as e:
            current_app.logger.error(f"❌ NOTIFICATION: Error getting email template: {e}")
            return None
    
    def _get_notification_recipients(self, ticket: Dict, recipient_types: List[str], 
                                   additional_data: Dict = None) -> List[Dict]:
        """Get list of notification recipients"""
        recipients = []
        
        try:
            for recipient_type in recipient_types:
                if recipient_type == 'client':
                    # Add notification email recipient (new field)
                    notification_email = ticket.get('notification_email')
                    if notification_email:
                        recipients.append({
                            'email': notification_email,
                            'name': ticket['affected_person'],
                            'type': 'affected_person'
                        })

                    # Also add additional emails
                    additional_emails = ticket.get('additional_emails', [])
                    if additional_emails:
                        for email in additional_emails:
                            if email and email.strip():
                                recipients.append({
                                    'email': email.strip(),
                                    'name': ticket['affected_person'],
                                    'type': 'additional_contact'
                                })

                    # Add client admin if different
                    if ticket.get('client_email') and ticket['client_email'] != notification_email:
                        recipients.append({
                            'email': ticket['client_email'],
                            'name': ticket['client_name'],
                            'type': 'client_admin'
                        })

                    # CRITICAL FIX: Add all solicitante users for this client
                    client_id = ticket.get('client_id')
                    if client_id:
                        solicitante_query = """
                        SELECT email, name FROM users
                        WHERE client_id = %s AND role = 'solicitante' AND is_active = true
                        """
                        solicitante_users = current_app.db_manager.execute_query(solicitante_query, (client_id,))
                        current_app.logger.info(f"🔔 NOTIFICATION: Found {len(solicitante_users or [])} solicitante users for client {client_id}")

                        for user in (solicitante_users or []):
                            recipients.append({
                                'email': user['email'],
                                'name': user['name'],
                                'type': 'solicitante'
                            })
                            current_app.logger.info(f"🔔 NOTIFICATION: Added solicitante recipient: {user['email']}")
                
                elif recipient_type == 'assigned_technician':
                    if ticket['assigned_to_email']:
                        recipients.append({
                            'email': ticket['assigned_to_email'],
                            'name': ticket['assigned_to_name'],
                            'type': 'technician'
                        })
                
                elif recipient_type == 'admins':
                    # Get admin and technician users (both should receive notifications)
                    admin_query = """
                    SELECT email, name FROM users
                    WHERE role IN ('admin', 'superadmin', 'technician') AND is_active = true
                    """
                    admins = current_app.db_manager.execute_query(admin_query)
                    current_app.logger.info(f"🔔 NOTIFICATION: Found {len(admins or [])} admin/technician users")

                    for admin in (admins or []):
                        recipients.append({
                            'email': admin['email'],
                            'name': admin['name'],
                            'type': 'admin'
                        })
                        current_app.logger.info(f"🔔 NOTIFICATION: Added admin recipient: {admin['email']}")
            
            # Remove duplicates based on email
            unique_recipients = []
            seen_emails = set()
            
            for recipient in recipients:
                if recipient['email'] not in seen_emails:
                    unique_recipients.append(recipient)
                    seen_emails.add(recipient['email'])
            
            return unique_recipients
            
        except Exception as e:
            current_app.logger.error(f"Error getting notification recipients: {e}")
            return []
    
    def _prepare_template_variables(self, ticket: Dict, additional_data: Dict = None) -> Dict:
        """Prepare variables for email template"""
        variables = {
            'ticket_number': ticket['ticket_number'],
            'ticket_id': ticket['ticket_id'],
            'subject': ticket['subject'],
            'description': ticket['description'],
            'priority': ticket['priority'].title() if ticket['priority'] else 'Media',
            'status': ticket['status'].replace('_', ' ').title() if ticket['status'] else 'Nuevo',
            'client_name': ticket['client_name'] or 'Cliente',
            'site_name': ticket['site_name'] or 'Sitio',
            'category_name': ticket['category_name'] or 'Sin categoría',
            'affected_person': ticket['affected_person'] or 'Usuario',
            'affected_person_phone': ticket.get('affected_person_phone') or '',
            'notification_email': ticket.get('notification_email') or '',
            'created_by_name': ticket['created_by_name'] or 'Sistema',
            'assigned_to_name': ticket['assigned_to_name'] or 'Sin asignar',
            'assigned_to_email': ticket['assigned_to_email'] or '',
            'created_at': ticket['created_at'].strftime('%d/%m/%Y %H:%M') if ticket['created_at'] else '',
            'updated_at': ticket['updated_at'].strftime('%d/%m/%Y %H:%M') if ticket['updated_at'] else '',
            'assigned_at': ticket['assigned_at'].strftime('%d/%m/%Y %H:%M') if ticket['assigned_at'] else '',
            'resolved_at': ticket['resolved_at'].strftime('%d/%m/%Y %H:%M') if ticket['resolved_at'] else ''
        }
        
        # Add additional data if provided
        if additional_data:
            variables.update(additional_data)
        
        return variables
    
    def _send_email_notification(self, recipient: Dict, template: Dict,
                               variables: Dict, priority: int, ticket_id: str) -> bool:
        """Send email notification to recipient"""
        try:
            # Replace template variables
            subject = self._replace_template_variables(template['subject_template'], variables)
            body = self._replace_template_variables(template['body_template'], variables)

            current_app.logger.info(f"🔔 NOTIFICATION: Queueing email to {recipient['email']} - {subject}")

            # Get email configuration
            from modules.email.service import email_service
            config = email_service.get_default_config()
            if not config:
                current_app.logger.error("🔔 NOTIFICATION: No email configuration found")
                return False

            # Queue email directly in database
            queue_data = {
                'config_id': config['config_id'],
                'to_email': recipient['email'],
                'subject': subject,
                'body_html': body,
                'ticket_id': ticket_id,
                'priority': priority,
                'status': 'pending'
            }

            current_app.db_manager.execute_insert('email_queue', queue_data)
            current_app.logger.info(f"✅ NOTIFICATION: Email queued successfully to {recipient['email']}")
            return True

        except Exception as e:
            current_app.logger.error(f"❌ NOTIFICATION: Error sending email notification: {e}")
            import traceback
            current_app.logger.error(f"❌ NOTIFICATION: Traceback: {traceback.format_exc()}")
            return False
    
    def _replace_template_variables(self, template: str, variables: Dict) -> str:
        """Replace template variables with actual values"""
        try:
            for key, value in variables.items():
                template = template.replace(f'{{{{{key}}}}}', str(value or ''))
            return template
        except Exception:
            return template
    
    def send_sla_warning(self, ticket_id: str, sla_type: str, time_remaining: int) -> bool:
        """Send SLA warning notification"""
        additional_data = {
            'sla_type': sla_type,
            'time_remaining': f"{time_remaining} horas",
            'urgency_level': 'warning'
        }
        
        return self.send_ticket_notification('sla_warning', ticket_id, additional_data)
    
    def send_sla_breach(self, ticket_id: str, sla_type: str, time_overdue: int) -> bool:
        """Send SLA breach notification"""
        additional_data = {
            'sla_type': sla_type,
            'time_overdue': f"{time_overdue} horas",
            'urgency_level': 'critical'
        }
        
        return self.send_ticket_notification('sla_breach', ticket_id, additional_data)

# Global notifications service instance
notifications_service = NotificationsService()
