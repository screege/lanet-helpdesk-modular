#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Email Service
Complete email-to-ticket and notification system
"""

import smtplib
import imaplib
import email
import re
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from flask import current_app

class EmailService:
    def __init__(self):
        self.smtp_connection = None
        self.imap_connection = None
        
    def get_default_config(self):
        """Get default email configuration"""
        try:
            query = """
            SELECT * FROM email_configurations 
            WHERE is_default = true AND is_active = true 
            LIMIT 1
            """
            return current_app.db_manager.execute_query(query, fetch='one')
        except Exception as e:
            current_app.logger.error(f"Error getting default email config: {e}")
            return None
    
    def get_config_by_id(self, config_id: str):
        """Get email configuration by ID"""
        try:
            query = "SELECT * FROM email_configurations WHERE config_id = %s AND is_active = true"
            return current_app.db_manager.execute_query(query, (config_id,), fetch='one')
        except Exception as e:
            current_app.logger.error(f"Error getting email config: {e}")
            return None
    
    def connect_smtp(self, config: Dict) -> bool:
        """Connect to SMTP server"""
        try:
            if config['smtp_use_ssl']:
                self.smtp_connection = smtplib.SMTP_SSL(config['smtp_host'], config['smtp_port'])
            else:
                self.smtp_connection = smtplib.SMTP(config['smtp_host'], config['smtp_port'])
                if config['smtp_use_tls']:
                    self.smtp_connection.starttls()
            
            self.smtp_connection.login(config['smtp_username'], config['smtp_password_encrypted'])
            return True
        except Exception as e:
            current_app.logger.error(f"SMTP connection error: {e}")
            return False
    
    def connect_imap(self, config: Dict) -> bool:
        """Connect to IMAP server"""
        try:
            if config['imap_use_ssl']:
                self.imap_connection = imaplib.IMAP4_SSL(config['imap_host'], config['imap_port'])
            else:
                self.imap_connection = imaplib.IMAP4(config['imap_host'], config['imap_port'])
            
            self.imap_connection.login(config['imap_username'], config['imap_password_encrypted'])
            return True
        except Exception as e:
            current_app.logger.error(f"IMAP connection error: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   cc_emails: List[str] = None, bcc_emails: List[str] = None,
                   is_html: bool = True, config_id: str = None) -> bool:
        """Send email using configured SMTP"""
        try:
            config = self.get_config_by_id(config_id) if config_id else self.get_default_config()
            if not config:
                current_app.logger.error("No email configuration found")
                return False
            
            if not self.connect_smtp(config):
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = config['smtp_username']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Send email
            recipients = [to_email]
            if cc_emails:
                recipients.extend(cc_emails)
            if bcc_emails:
                recipients.extend(bcc_emails)
            
            self.smtp_connection.send_message(msg, to_addrs=recipients)
            self.smtp_connection.quit()
            
            current_app.logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error sending email: {e}")
            return False
    
    def queue_email(self, to_email: str, subject: str, body: str,
                    cc_emails: List[str] = None, bcc_emails: List[str] = None,
                    ticket_id: str = None, user_id: str = None,
                    priority: int = 5, config_id: str = None) -> bool:
        """Queue email for background processing"""
        try:
            config = self.get_config_by_id(config_id) if config_id else self.get_default_config()
            if not config:
                return False
            
            queue_data = {
                'config_id': config['config_id'],
                'to_email': to_email,
                'cc_emails': cc_emails,
                'bcc_emails': bcc_emails,
                'subject': subject,
                'body_html': body,
                'ticket_id': ticket_id,
                'user_id': user_id,
                'priority': priority,
                'status': 'pending'
            }
            
            current_app.db_manager.execute_insert('email_queue', queue_data)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error queueing email: {e}")
            return False
    
    def process_email_queue(self, limit: int = 10) -> int:
        """Process pending emails in queue"""
        try:
            # Get pending emails ordered by priority and creation time
            query = """
            SELECT * FROM email_queue 
            WHERE status = 'pending' AND next_attempt_at <= CURRENT_TIMESTAMP
            ORDER BY priority ASC, created_at ASC
            LIMIT %s
            """
            
            pending_emails = current_app.db_manager.execute_query(query, (limit,))
            processed = 0
            
            for email_item in (pending_emails or []):
                if self._process_single_email(email_item):
                    processed += 1
            
            return processed
            
        except Exception as e:
            current_app.logger.error(f"Error processing email queue: {e}")
            return 0
    
    def _process_single_email(self, email_item: Dict) -> bool:
        """Process a single email from queue"""
        try:
            # Update status to sending
            current_app.db_manager.execute_update(
                'email_queue',
                {'status': 'sending', 'updated_at': 'CURRENT_TIMESTAMP'},
                'queue_id = %s',
                (email_item['queue_id'],)
            )
            
            # Send email
            success = self.send_email(
                to_email=email_item['to_email'],
                subject=email_item['subject'],
                body=email_item['body_html'] or email_item['body_text'],
                cc_emails=email_item['cc_emails'],
                bcc_emails=email_item['bcc_emails'],
                is_html=bool(email_item['body_html']),
                config_id=email_item['config_id']
            )
            
            if success:
                # Mark as sent
                current_app.db_manager.execute_update(
                    'email_queue',
                    {
                        'status': 'sent',
                        'sent_at': 'CURRENT_TIMESTAMP',
                        'updated_at': 'CURRENT_TIMESTAMP'
                    },
                    'queue_id = %s',
                    (email_item['queue_id'],)
                )
                return True
            else:
                # Mark as failed and schedule retry
                attempts = email_item['attempts'] + 1
                max_attempts = email_item['max_attempts']
                
                if attempts >= max_attempts:
                    status = 'failed'
                    next_attempt = None
                else:
                    status = 'pending'
                    # Exponential backoff: 5min, 15min, 45min
                    delay_minutes = 5 * (3 ** (attempts - 1))
                    next_attempt = datetime.now() + timedelta(minutes=delay_minutes)
                
                current_app.db_manager.execute_update(
                    'email_queue',
                    {
                        'status': status,
                        'attempts': attempts,
                        'next_attempt_at': next_attempt,
                        'error_message': 'Failed to send email',
                        'updated_at': 'CURRENT_TIMESTAMP'
                    },
                    'queue_id = %s',
                    (email_item['queue_id'],)
                )
                return False
                
        except Exception as e:
            current_app.logger.error(f"Error processing single email: {e}")
            return False
    
    def check_incoming_emails(self, config_id: str = None) -> List[Dict]:
        """Check for new incoming emails"""
        try:
            config = self.get_config_by_id(config_id) if config_id else self.get_default_config()
            if not config or not config['enable_email_to_ticket']:
                return []
            
            if not self.connect_imap(config):
                return []
            
            # Select inbox
            self.imap_connection.select(config['imap_folder'])
            
            # Search for unread emails
            status, messages = self.imap_connection.search(None, 'UNSEEN')
            
            if status != 'OK':
                return []
            
            email_ids = messages[0].split()
            processed_emails = []
            
            for email_id in email_ids[-10:]:  # Process last 10 unread emails
                email_data = self._fetch_email(email_id, config)
                if email_data:
                    processed_emails.append(email_data)
            
            self.imap_connection.close()
            self.imap_connection.logout()
            
            return processed_emails
            
        except Exception as e:
            current_app.logger.error(f"Error checking incoming emails: {e}")
            return []
    
    def _fetch_email(self, email_id: bytes, config: Dict) -> Optional[Dict]:
        """Fetch and parse a single email"""
        try:
            status, msg_data = self.imap_connection.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                return None
            
            email_message = email.message_from_bytes(msg_data[0][1])
            
            # Extract email data
            email_data = {
                'message_id': email_message.get('Message-ID', ''),
                'from_email': email_message.get('From', ''),
                'to_email': email_message.get('To', ''),
                'subject': email_message.get('Subject', ''),
                'date': email_message.get('Date', ''),
                'body_text': '',
                'body_html': ''
            }
            
            # Extract body
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        email_data['body_text'] = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif content_type == 'text/html':
                        email_data['body_html'] = part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                email_data['body_text'] = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            return email_data
            
        except Exception as e:
            current_app.logger.error(f"Error fetching email: {e}")
            return None
    
    def process_incoming_email(self, email_data: Dict, config: Dict) -> Optional[str]:
        """Process incoming email and create/update ticket"""
        try:
            # Log the incoming email
            log_data = {
                'config_id': config['config_id'],
                'message_id': email_data['message_id'],
                'from_email': email_data['from_email'],
                'to_email': email_data['to_email'],
                'subject': email_data['subject'],
                'body_text': email_data['body_text'],
                'body_html': email_data['body_html'],
                'processing_status': 'pending'
            }
            
            log_id = current_app.db_manager.execute_insert('email_processing_log', log_data, returning='log_id')
            
            # Check if this is a reply to existing ticket
            ticket_number = self._extract_ticket_number(email_data['subject'], config['ticket_number_regex'])
            
            if ticket_number:
                # This is a reply to existing ticket
                ticket_id = self._add_email_comment_to_ticket(ticket_number, email_data)
                action = 'added_comment'
            else:
                # This is a new ticket
                ticket_id = self._create_ticket_from_email(email_data, config)
                action = 'created_ticket'
            
            if ticket_id:
                # Update processing log
                current_app.db_manager.execute_update(
                    'email_processing_log',
                    {
                        'processing_status': 'processed',
                        'ticket_id': ticket_id,
                        'action_taken': action,
                        'processed_at': 'CURRENT_TIMESTAMP'
                    },
                    'log_id = %s',
                    (log_id['log_id'],)
                )
                
                # Send auto-response if it's a new ticket
                if action == 'created_ticket':
                    self._send_auto_response(email_data, ticket_id, config)
                
                return ticket_id
            else:
                # Update processing log with error
                current_app.db_manager.execute_update(
                    'email_processing_log',
                    {
                        'processing_status': 'failed',
                        'error_message': 'Failed to create/update ticket',
                        'processed_at': 'CURRENT_TIMESTAMP'
                    },
                    'log_id = %s',
                    (log_id['log_id'],)
                )
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error processing incoming email: {e}")
            return None
    
    def _extract_ticket_number(self, subject: str, regex_pattern: str) -> Optional[str]:
        """Extract ticket number from email subject"""
        try:
            match = re.search(regex_pattern, subject)
            return match.group(1) if match else None
        except Exception:
            return None
    
    def _create_ticket_from_email(self, email_data: Dict, config: Dict) -> Optional[str]:
        """Create new ticket from email"""
        try:
            # Import here to avoid circular imports
            from modules.tickets.service import TicketsService
            
            tickets_service = TicketsService()
            
            # Extract sender name and email
            from_email = email_data['from_email']
            sender_name = from_email.split('<')[0].strip() if '<' in from_email else from_email
            sender_email = from_email.split('<')[1].replace('>', '').strip() if '<' in from_email else from_email
            
            ticket_data = {
                'client_id': config['default_client_id'],
                'category_id': config['default_category_id'],
                'subject': email_data['subject'],
                'description': email_data['body_text'] or email_data['body_html'],
                'priority': config['default_priority'],
                'affected_person': sender_name,
                'affected_person_contact': sender_email,
                'channel': 'email',
                'is_email_originated': True,
                'from_email': sender_email,
                'email_message_id': email_data['message_id']
            }
            
            # Auto-assign if configured
            if config['auto_assign_to']:
                ticket_data['assigned_to'] = config['auto_assign_to']
            
            return tickets_service.create_ticket(ticket_data, created_by_email=sender_email)
            
        except Exception as e:
            current_app.logger.error(f"Error creating ticket from email: {e}")
            return None
    
    def _add_email_comment_to_ticket(self, ticket_number: str, email_data: Dict) -> Optional[str]:
        """Add email as comment to existing ticket"""
        try:
            # Get ticket by number
            query = "SELECT ticket_id FROM tickets WHERE ticket_number = %s"
            ticket = current_app.db_manager.execute_query(query, (ticket_number,), fetch='one')
            
            if not ticket:
                return None
            
            # Add comment
            comment_data = {
                'ticket_id': ticket['ticket_id'],
                'comment': email_data['body_text'] or email_data['body_html'],
                'is_internal': False,
                'created_by_email': email_data['from_email']
            }
            
            current_app.db_manager.execute_insert('ticket_comments', comment_data)
            return ticket['ticket_id']
            
        except Exception as e:
            current_app.logger.error(f"Error adding email comment: {e}")
            return None
    
    def _send_auto_response(self, email_data: Dict, ticket_id: str, config: Dict):
        """Send auto-response for new ticket"""
        try:
            # Get ticket details
            query = """
            SELECT t.ticket_number, t.subject, c.name as client_name
            FROM tickets t
            LEFT JOIN clients c ON t.client_id = c.client_id
            WHERE t.ticket_id = %s
            """
            ticket = current_app.db_manager.execute_query(query, (ticket_id,), fetch='one')
            
            if not ticket:
                return
            
            # Get auto-response template
            template_query = """
            SELECT * FROM email_templates 
            WHERE template_type = 'auto_response' AND is_active = true AND is_default = true
            LIMIT 1
            """
            template = current_app.db_manager.execute_query(template_query, fetch='one')
            
            if not template:
                return
            
            # Prepare template variables
            variables = {
                'sender_name': email_data['from_email'].split('<')[0].strip(),
                'ticket_number': ticket['ticket_number'],
                'subject': ticket['subject'],
                'original_subject': email_data['subject'],
                'client_name': ticket['client_name'] or 'Cliente'
            }
            
            # Replace variables in template
            subject = self._replace_template_variables(template['subject'], variables)
            body = self._replace_template_variables(template['body'], variables)
            
            # Queue auto-response
            self.queue_email(
                to_email=email_data['from_email'],
                subject=subject,
                body=body,
                ticket_id=ticket_id,
                priority=1,  # High priority for auto-responses
                config_id=config['config_id']
            )
            
        except Exception as e:
            current_app.logger.error(f"Error sending auto-response: {e}")
    
    def _replace_template_variables(self, template: str, variables: Dict) -> str:
        """Replace template variables with actual values"""
        try:
            for key, value in variables.items():
                template = template.replace(f'{{{{{key}}}}}', str(value or ''))
            return template
        except Exception:
            return template

# Global email service instance
email_service = EmailService()
