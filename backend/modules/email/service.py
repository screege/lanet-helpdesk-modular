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
            current_app.logger.info(f"Testing SMTP connection to {config['smtp_host']}:{config['smtp_port']}")

            # Check if password is encrypted
            if not config.get('smtp_password_encrypted'):
                current_app.logger.error("SMTP password not encrypted or missing")
                return False

            # Decrypt password
            from utils.security import SecurityUtils
            smtp_password = SecurityUtils.decrypt_password(config['smtp_password_encrypted'])
            current_app.logger.info(f"Password decrypted successfully, length: {len(smtp_password) if smtp_password else 0}")

            if config['smtp_use_ssl']:
                self.smtp_connection = smtplib.SMTP_SSL(config['smtp_host'], config['smtp_port'])
            else:
                self.smtp_connection = smtplib.SMTP(config['smtp_host'], config['smtp_port'])
                if config['smtp_use_tls']:
                    self.smtp_connection.starttls()

            self.smtp_connection.login(config['smtp_username'], smtp_password)
            current_app.logger.info("SMTP connection successful")
            return True
        except Exception as e:
            current_app.logger.error(f"SMTP connection error: {e}")
            import traceback
            current_app.logger.error(f"SMTP traceback: {traceback.format_exc()}")
            return False
    
    def connect_imap(self, config: Dict) -> bool:
        """Connect to IMAP server"""
        try:
            # Decrypt password
            from utils.security import SecurityUtils
            imap_password = SecurityUtils.decrypt_password(config['imap_password_encrypted'])

            if config['imap_use_ssl']:
                self.imap_connection = imaplib.IMAP4_SSL(config['imap_host'], config['imap_port'])
            else:
                self.imap_connection = imaplib.IMAP4(config['imap_host'], config['imap_port'])

            self.imap_connection.login(config['imap_username'], imap_password)
            return True
        except Exception as e:
            current_app.logger.error(f"IMAP connection error: {e}")
            return False

    def send_test_email(self, config: Dict, to_email: str) -> tuple[bool, str]:
        """Send a test email using the specified configuration"""
        try:
            current_app.logger.info(f"Sending test email to {to_email}")

            # Check if password is encrypted
            if not config.get('smtp_password_encrypted'):
                return False, "SMTP password not configured"

            # Decrypt password
            from utils.security import SecurityUtils
            smtp_password = SecurityUtils.decrypt_password(config['smtp_password_encrypted'])

            if not smtp_password:
                return False, "Failed to decrypt SMTP password"

            # Create SMTP connection
            if config['smtp_use_ssl']:
                server = smtplib.SMTP_SSL(config['smtp_host'], config['smtp_port'])
            else:
                server = smtplib.SMTP(config['smtp_host'], config['smtp_port'])
                if config['smtp_use_tls']:
                    server.starttls()

            # Login to SMTP server
            server.login(config['smtp_username'], smtp_password)

            # Create test email message
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from datetime import datetime

            msg = MIMEMultipart()
            msg['From'] = config['smtp_username']
            msg['To'] = to_email
            msg['Subject'] = f"Email de Prueba - LANET Helpdesk - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # Email body
            body = f"""
¡Hola!

Este es un email de prueba enviado desde LANET Helpdesk V3.

Detalles de la configuración:
- Servidor SMTP: {config['smtp_host']}:{config['smtp_port']}
- Usuario: {config['smtp_username']}
- Seguridad: {'SSL' if config['smtp_use_ssl'] else 'TLS' if config['smtp_use_tls'] else 'Ninguna'}
- Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Si recibes este email, la configuración SMTP está funcionando correctamente.

Saludos,
LANET Helpdesk V3
            """

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Send email
            text = msg.as_string()
            server.sendmail(config['smtp_username'], to_email, text)
            server.quit()

            current_app.logger.info(f"Test email sent successfully to {to_email}")
            return True, f"Email enviado exitosamente a {to_email}"

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Error de autenticación SMTP: {str(e)}"
            current_app.logger.error(error_msg)
            return False, error_msg
        except smtplib.SMTPConnectError as e:
            error_msg = f"Error de conexión SMTP: {str(e)}"
            current_app.logger.error(error_msg)
            return False, error_msg
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Destinatario rechazado: {str(e)}"
            current_app.logger.error(error_msg)
            return False, error_msg
        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"Servidor SMTP desconectado: {str(e)}"
            current_app.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error enviando email: {str(e)}"
            current_app.logger.error(error_msg)
            import traceback
            current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
            return False, error_msg
    
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
        """Fetch and parse a single email with attachments"""
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
                'body_html': '',
                'attachments': []
            }

            # Extract body and attachments
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get('Content-Disposition', ''))

                    if content_type == 'text/plain' and 'attachment' not in content_disposition:
                        email_data['body_text'] = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif content_type == 'text/html' and 'attachment' not in content_disposition:
                        email_data['body_html'] = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif 'attachment' in content_disposition:
                        # Process attachment
                        filename = part.get_filename()
                        if filename:
                            attachment_data = {
                                'filename': filename,
                                'content_type': content_type,
                                'content': part.get_payload(decode=True),
                                'size': len(part.get_payload(decode=True)) if part.get_payload(decode=True) else 0
                            }
                            email_data['attachments'].append(attachment_data)
            else:
                email_data['body_text'] = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')

            return email_data

        except Exception as e:
            current_app.logger.error(f"Error fetching email: {e}")
            return None

    def process_email_attachments(self, attachments: List[Dict], ticket_id: str) -> List[str]:
        """Process email attachments and save as ticket attachments"""
        try:
            import os
            import uuid
            from werkzeug.utils import secure_filename

            saved_attachments = []

            # Get system configuration for file limits
            max_size_query = "SELECT config_value FROM system_config WHERE config_key = 'max_attachment_size_mb'"
            max_size_result = current_app.db_manager.execute_query(max_size_query, fetch='one')
            max_size_mb = int(max_size_result['config_value']) if max_size_result else 10
            max_size_bytes = max_size_mb * 1024 * 1024

            # Get allowed file types
            allowed_types_query = "SELECT config_value FROM system_config WHERE config_key = 'allowed_attachment_types'"
            allowed_types_result = current_app.db_manager.execute_query(allowed_types_query, fetch='one')
            allowed_extensions = allowed_types_result['config_value'].split(',') if allowed_types_result else ['.pdf', '.png', '.jpg', '.jpeg', '.docx', '.xlsx', '.txt']

            for attachment in attachments:
                try:
                    # Validate file size
                    if attachment['size'] > max_size_bytes:
                        current_app.logger.warning(f"Attachment {attachment['filename']} too large: {attachment['size']} bytes")
                        continue

                    # Validate file type
                    filename = secure_filename(attachment['filename'])
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext not in allowed_extensions:
                        current_app.logger.warning(f"Attachment {filename} has disallowed extension: {file_ext}")
                        continue

                    # Generate unique filename
                    unique_filename = f"{uuid.uuid4()}_{filename}"

                    # Create upload directory if it doesn't exist
                    upload_dir = os.path.join(os.getcwd(), 'uploads', 'tickets')
                    os.makedirs(upload_dir, exist_ok=True)

                    # Save file
                    file_path = os.path.join(upload_dir, unique_filename)
                    with open(file_path, 'wb') as f:
                        f.write(attachment['content'])

                    # Save attachment record to database
                    attachment_data = {
                        'attachment_id': str(uuid.uuid4()),
                        'ticket_id': ticket_id,
                        'filename': filename,
                        'file_path': f"uploads/tickets/{unique_filename}",
                        'file_size': attachment['size'],
                        'content_type': attachment['content_type'],
                        'uploaded_by': None,  # Email system
                        'uploaded_via': 'email',
                        'created_at': 'CURRENT_TIMESTAMP'
                    }

                    current_app.db_manager.execute_insert('file_attachments', attachment_data)
                    saved_attachments.append(unique_filename)

                    current_app.logger.info(f"Email attachment saved: {filename} -> {unique_filename}")

                except Exception as e:
                    current_app.logger.error(f"Error processing attachment {attachment.get('filename', 'unknown')}: {e}")
                    continue

            return saved_attachments

        except Exception as e:
            current_app.logger.error(f"Error processing email attachments: {e}")
            return []
    
    def process_incoming_email(self, email_data: Dict, config: Dict) -> Optional[str]:
        """Process incoming email and create/update ticket with enhanced threading"""
        try:
            # Enhance email data with threading information
            enhanced_email_data = self.enhance_email_threading(email_data)

            # Log the incoming email
            log_data = {
                'config_id': config['config_id'],
                'message_id': enhanced_email_data['message_id'],
                'from_email': enhanced_email_data['from_email'],
                'to_email': enhanced_email_data['to_email'],
                'subject': enhanced_email_data['subject'],
                'body_text': enhanced_email_data['body_text'],
                'body_html': enhanced_email_data['body_html'],
                'processing_status': 'pending'
            }

            log_id = current_app.db_manager.execute_insert('email_processing_log', log_data, returning='log_id')

            # Check if this is a reply to existing ticket using enhanced extraction
            ticket_number = self._extract_ticket_number(
                enhanced_email_data['subject'],
                config.get('ticket_number_regex')
            )

            if ticket_number:
                # This is a reply to existing ticket
                ticket_id = self._add_email_comment_to_ticket(ticket_number, enhanced_email_data)
                action = 'added_comment'
            else:
                # This is a new ticket
                ticket_id = self._create_ticket_from_email(enhanced_email_data, config)
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
    
    def _extract_ticket_number(self, subject: str, regex_pattern: str = None) -> Optional[str]:
        """Extract ticket number from email subject with enhanced parsing"""
        try:
            # Default patterns for ticket number extraction
            default_patterns = [
                r'\[#?([A-Z]+-\d+)\]',  # [#TKT-123456] or [TKT-123456]
                r'#([A-Z]+-\d+)',       # #TKT-123456
                r'([A-Z]+-\d+)',        # TKT-123456
                r'\[(\d+)\]',           # [123456]
                r'#(\d+)',              # #123456
            ]

            # Use custom pattern if provided, otherwise try default patterns
            patterns = [regex_pattern] if regex_pattern else default_patterns

            for pattern in patterns:
                match = re.search(pattern, subject, re.IGNORECASE)
                if match:
                    ticket_number = match.group(1)
                    current_app.logger.info(f"Extracted ticket number: {ticket_number} from subject: {subject}")
                    return ticket_number

            # Try to extract from common email reply patterns
            reply_patterns = [
                r'Re:\s*.*?([A-Z]+-\d+)',
                r'RE:\s*.*?([A-Z]+-\d+)',
                r'Fwd:\s*.*?([A-Z]+-\d+)',
                r'FWD:\s*.*?([A-Z]+-\d+)',
            ]

            for pattern in reply_patterns:
                match = re.search(pattern, subject, re.IGNORECASE)
                if match:
                    ticket_number = match.group(1)
                    current_app.logger.info(f"Extracted ticket number from reply: {ticket_number} from subject: {subject}")
                    return ticket_number

            return None

        except Exception as e:
            current_app.logger.error(f"Error extracting ticket number from subject '{subject}': {e}")
            return None

    def enhance_email_threading(self, email_data: Dict) -> Dict:
        """Enhance email data with threading information"""
        try:
            enhanced_data = email_data.copy()

            # Extract In-Reply-To and References headers for better threading
            enhanced_data['in_reply_to'] = email_data.get('in_reply_to', '')
            enhanced_data['references'] = email_data.get('references', '')

            # Clean and normalize subject for better matching
            subject = email_data.get('subject', '')

            # Remove common reply prefixes
            clean_subject = re.sub(r'^(Re:|RE:|Fwd:|FWD:|Fw:)\s*', '', subject, flags=re.IGNORECASE).strip()
            enhanced_data['clean_subject'] = clean_subject

            # Extract conversation thread ID if present
            thread_id = self._extract_thread_id(email_data)
            if thread_id:
                enhanced_data['thread_id'] = thread_id

            # Determine if this is likely a reply or forward
            enhanced_data['is_reply'] = bool(re.match(r'^(Re:|RE:)', subject, re.IGNORECASE))
            enhanced_data['is_forward'] = bool(re.match(r'^(Fwd:|FWD:|Fw:)', subject, re.IGNORECASE))

            return enhanced_data

        except Exception as e:
            current_app.logger.error(f"Error enhancing email threading: {e}")
            return email_data

    def _extract_thread_id(self, email_data: Dict) -> Optional[str]:
        """Extract thread ID from email headers"""
        try:
            # Try to get thread ID from various headers
            thread_sources = [
                email_data.get('thread_topic', ''),
                email_data.get('thread_index', ''),
                email_data.get('message_id', ''),
            ]

            for source in thread_sources:
                if source:
                    # Generate a consistent thread ID
                    import hashlib
                    return hashlib.md5(source.encode()).hexdigest()[:16]

            return None

        except Exception:
            return None
    
    def validate_sender_email(self, sender_email: str) -> Optional[Dict]:
        """Validate sender email against client allowed emails and return client info"""
        try:
            # Clean the sender email
            sender_email = sender_email.lower().strip()
            sender_domain = '@' + sender_email.split('@')[1] if '@' in sender_email else ''

            # Query clients with allowed_emails that match sender
            query = """
            SELECT client_id, name, allowed_emails
            FROM clients
            WHERE is_active = true
            AND (
                %s = ANY(allowed_emails) OR  -- Exact email match
                %s = ANY(allowed_emails)     -- Domain match
            )
            LIMIT 1
            """

            client = current_app.db_manager.execute_query(
                query,
                (sender_email, sender_domain),
                fetch='one'
            )

            if client:
                current_app.logger.info(f"Email validation successful: {sender_email} -> {client['name']}")
                return client
            else:
                current_app.logger.warning(f"Email validation failed: {sender_email} not in any client's allowed_emails")
                return None

        except Exception as e:
            current_app.logger.error(f"Error validating sender email {sender_email}: {e}")
            return None

    def log_email_rejection(self, email_data: Dict, reason: str, config: Dict):
        """Log rejected email to audit log"""
        try:
            audit_data = {
                'user_id': None,  # System action
                'action': 'email_rejected',
                'table_name': 'email_processing_log',
                'record_id': None,
                'old_values': None,
                'new_values': {
                    'from_email': email_data['from_email'],
                    'to_email': email_data['to_email'],
                    'subject': email_data['subject'],
                    'rejection_reason': reason,
                    'config_id': config['config_id'],
                    'message_id': email_data['message_id']
                },
                'timestamp': 'CURRENT_TIMESTAMP'
            }

            current_app.db_manager.execute_insert('audit_log', audit_data)
            current_app.logger.warning(f"Email rejected and logged: {email_data['from_email']} - {reason}")

        except Exception as e:
            current_app.logger.error(f"Error logging email rejection: {e}")

    def _create_ticket_from_email(self, email_data: Dict, config: Dict) -> Optional[str]:
        """Create new ticket from email with security validation"""
        try:
            # Extract sender name and email
            from_email = email_data['from_email']
            sender_name = from_email.split('<')[0].strip() if '<' in from_email else from_email
            sender_email = from_email.split('<')[1].replace('>', '').strip() if '<' in from_email else from_email

            # SECURITY VALIDATION: Check if sender is authorized
            authorized_client = self.validate_sender_email(sender_email)
            if not authorized_client:
                # Log rejection and return None (no ticket created)
                self.log_email_rejection(
                    email_data,
                    f"Sender email {sender_email} not in any client's allowed_emails",
                    config
                )
                return None

            # Import here to avoid circular imports
            from modules.tickets.service import TicketsService

            tickets_service = TicketsService()

            # Use the validated client_id instead of default
            ticket_data = {
                'client_id': authorized_client['client_id'],
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

            # Create ticket with validated client
            ticket_id = tickets_service.create_ticket(ticket_data, created_by_email=sender_email)

            if ticket_id:
                current_app.logger.info(f"Ticket created from authorized email: {ticket_id} from {sender_email}")

                # Process email attachments if any
                if email_data.get('attachments'):
                    saved_attachments = self.process_email_attachments(email_data['attachments'], ticket_id)
                    if saved_attachments:
                        current_app.logger.info(f"Processed {len(saved_attachments)} attachments for ticket {ticket_id}")

            return ticket_id

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

    def get_template_by_type(self, template_type: str) -> Optional[Dict]:
        """Get email template by type"""
        try:
            query = """
            SELECT template_id, name, subject_template, body_template, is_html, available_variables
            FROM email_templates
            WHERE template_type = %s AND is_active = true
            ORDER BY is_default DESC, created_at DESC
            LIMIT 1
            """

            template = current_app.db_manager.execute_query(query, (template_type,), fetch='one')
            return template

        except Exception as e:
            current_app.logger.error(f"Error getting template by type {template_type}: {e}")
            return None

    def send_template_email(self, template_id: str, to_email: str, variables: Dict,
                          ticket_id: str = None, priority: int = 2) -> bool:
        """Send email using template with variable substitution"""
        try:
            # Get template
            template = current_app.db_manager.execute_query(
                "SELECT * FROM email_templates WHERE template_id = %s AND is_active = true",
                (template_id,),
                fetch='one'
            )

            if not template:
                current_app.logger.error(f"Template {template_id} not found or inactive")
                return False

            # Replace variables in subject and body
            subject = template['subject_template']
            body = template['body_template']

            for variable, value in variables.items():
                placeholder = f"{{{{{variable}}}}}"
                subject = subject.replace(placeholder, str(value))
                body = body.replace(placeholder, str(value))

            # Get default email configuration
            config = self.get_default_config()
            if not config:
                current_app.logger.error("No default email configuration found")
                return False

            # Queue email for sending
            return self.queue_email(
                config=config,
                to_email=to_email,
                subject=subject,
                body_text=body if not template['is_html'] else None,
                body_html=body if template['is_html'] else None,
                ticket_id=ticket_id,
                priority=priority
            )

        except Exception as e:
            current_app.logger.error(f"Error sending template email: {e}")
            return False

    def queue_email(self, config: Dict, to_email: str, subject: str,
                   body_text: str = None, body_html: str = None,
                   cc_emails: List[str] = None, bcc_emails: List[str] = None,
                   ticket_id: str = None, user_id: str = None, priority: int = 2) -> bool:
        """Queue email for sending"""
        try:
            queue_data = {
                'config_id': config['config_id'],
                'to_email': to_email,
                'cc_emails': cc_emails,
                'bcc_emails': bcc_emails,
                'subject': subject,
                'body_text': body_text,
                'body_html': body_html,
                'ticket_id': ticket_id,
                'user_id': user_id,
                'status': 'pending',
                'priority': priority,
                'attempts': 0,
                'max_attempts': 3,
                'next_attempt_at': 'CURRENT_TIMESTAMP'
            }

            result = current_app.db_manager.execute_insert('email_queue', queue_data)
            return bool(result)

        except Exception as e:
            current_app.logger.error(f"Error queuing email: {e}")
            return False

    def process_queue_item(self, queue_id: str) -> bool:
        """Process a single email queue item"""
        try:
            # Get queue item
            queue_item = current_app.db_manager.execute_query(
                "SELECT * FROM email_queue WHERE queue_id = %s",
                (queue_id,),
                fetch='one'
            )

            if not queue_item or queue_item['status'] != 'pending':
                return False

            # Get email configuration
            config = self.get_config_by_id(queue_item['config_id'])
            if not config:
                self._mark_queue_item_failed(queue_id, "Email configuration not found")
                return False

            # Update status to sending
            current_app.db_manager.execute_update(
                'email_queue',
                {'status': 'sending', 'attempts': queue_item['attempts'] + 1},
                'queue_id = %s',
                (queue_id,)
            )

            # Send email
            success = self.send_email(
                config=config,
                to_email=queue_item['to_email'],
                subject=queue_item['subject'],
                body_text=queue_item['body_text'],
                body_html=queue_item['body_html'],
                cc_emails=queue_item.get('cc_emails'),
                bcc_emails=queue_item.get('bcc_emails')
            )

            if success:
                # Mark as sent
                current_app.db_manager.execute_update(
                    'email_queue',
                    {'status': 'sent', 'sent_at': 'CURRENT_TIMESTAMP'},
                    'queue_id = %s',
                    (queue_id,)
                )
                return True
            else:
                # Mark as failed or retry
                if queue_item['attempts'] + 1 >= queue_item['max_attempts']:
                    self._mark_queue_item_failed(queue_id, "Maximum retry attempts reached")
                else:
                    # Schedule retry
                    from datetime import datetime, timedelta
                    next_attempt = datetime.now() + timedelta(minutes=5 * (queue_item['attempts'] + 1))
                    current_app.db_manager.execute_update(
                        'email_queue',
                        {
                            'status': 'pending',
                            'next_attempt_at': next_attempt,
                            'error_message': 'Send failed, will retry'
                        },
                        'queue_id = %s',
                        (queue_id,)
                    )
                return False

        except Exception as e:
            current_app.logger.error(f"Error processing queue item {queue_id}: {e}")
            self._mark_queue_item_failed(queue_id, str(e))
            return False

    def _mark_queue_item_failed(self, queue_id: str, error_message: str):
        """Mark queue item as failed"""
        try:
            current_app.db_manager.execute_update(
                'email_queue',
                {
                    'status': 'failed',
                    'error_message': error_message
                },
                'queue_id = %s',
                (queue_id,)
            )
        except Exception as e:
            current_app.logger.error(f"Error marking queue item as failed: {e}")

    def disconnect_imap(self):
        """Disconnect from IMAP server"""
        if self.imap_connection:
            try:
                self.imap_connection.close()
                self.imap_connection.logout()
            except:
                pass
            finally:
                self.imap_connection = None

    def check_and_process_emails(self, config: Dict) -> Dict:
        """Check for new emails and process them into tickets"""
        try:
            current_app.logger.info(f"🔧 EMAIL SERVICE: Starting email check for config: {config.get('name')}")

            # Connect to IMAP
            if not self.connect_imap(config):
                raise Exception("Failed to connect to IMAP server")

            # Select inbox folder
            folder = config.get('imap_folder', 'INBOX')
            current_app.logger.info(f"🔧 EMAIL SERVICE: Selecting folder: {folder}")
            self.imap_connection.select(folder)

            # Search for unread emails
            current_app.logger.info("🔧 EMAIL SERVICE: Searching for unread emails")
            status, messages = self.imap_connection.search(None, 'UNSEEN')

            if status != 'OK':
                raise Exception(f"Failed to search emails: {status}")

            message_ids = messages[0].split()
            emails_found = len(message_ids)
            tickets_created = 0

            current_app.logger.info(f"🔧 EMAIL SERVICE: Found {emails_found} unread emails")

            # Process each email (limit to 10 for safety)
            for msg_id in message_ids[:10]:
                try:
                    current_app.logger.info(f"🔧 EMAIL SERVICE: Processing email ID: {msg_id}")

                    # Fetch email
                    status, msg_data = self.imap_connection.fetch(msg_id, '(RFC822)')
                    if status != 'OK':
                        current_app.logger.error(f"Failed to fetch email {msg_id}: {status}")
                        continue

                    # Parse email
                    import email
                    email_message = email.message_from_bytes(msg_data[0][1])

                    # Extract email details
                    from_email = email_message.get('From', '')
                    subject = email_message.get('Subject', 'Sin asunto')

                    current_app.logger.info(f"🔧 EMAIL SERVICE: Email from: {from_email}, subject: {subject}")

                    # Get email body
                    body = self._extract_email_body(email_message)

                    # Create ticket from email (simplified for now)
                    ticket_created = self._create_ticket_from_email(from_email, subject, body, config)

                    if ticket_created:
                        tickets_created += 1
                        current_app.logger.info(f"🔧 EMAIL SERVICE: Created ticket from email {msg_id}")

                        # Mark email as read
                        self.imap_connection.store(msg_id, '+FLAGS', '\\Seen')

                except Exception as e:
                    current_app.logger.error(f"🔧 EMAIL SERVICE: Error processing email {msg_id}: {e}")
                    continue

            # Disconnect
            self.disconnect_imap()

            result = {
                'emails_found': emails_found,
                'tickets_created': tickets_created
            }

            current_app.logger.info(f"🔧 EMAIL SERVICE: Email check completed: {result}")
            return result

        except Exception as e:
            current_app.logger.error(f"🔧 EMAIL SERVICE: Error in check_and_process_emails: {e}")
            self.disconnect_imap()
            raise e

    def _extract_email_body(self, email_message) -> str:
        """Extract text body from email message"""
        try:
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    elif part.get_content_type() == "text/html" and not body:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')

            return body[:5000]  # Limit body length
        except Exception as e:
            current_app.logger.error(f"Error extracting email body: {e}")
            return "Error extracting email content"

    def _create_ticket_from_email(self, from_email: str, subject: str, body: str, config: Dict) -> bool:
        """Create a ticket from email (simplified implementation)"""
        try:
            current_app.logger.info(f"🔧 EMAIL SERVICE: Creating ticket from email: {from_email}")

            # For now, just log the email details
            # In a full implementation, this would:
            # 1. Validate sender against authorized domains
            # 2. Extract client/site information
            # 3. Create ticket in database
            # 4. Send confirmation email

            current_app.logger.info(f"🔧 EMAIL SERVICE: Would create ticket - From: {from_email}, Subject: {subject}")
            current_app.logger.info(f"🔧 EMAIL SERVICE: Body preview: {body[:200]}...")

            # Return True to simulate successful ticket creation
            return True

        except Exception as e:
            current_app.logger.error(f"🔧 EMAIL SERVICE: Error creating ticket from email: {e}")
            return False

# Global email service instance
email_service = EmailService()
