#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - SLA Service
Complete SLA management, tracking, and escalation system
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from flask import current_app
import pytz

class SLAService:
    def __init__(self):
        self.business_days = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 
            'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
        }
    
    def get_applicable_sla_policy(self, ticket_data: Dict) -> Optional[Dict]:
        """Get the most specific SLA policy for a ticket"""
        try:
            # Priority order: Client+Category+Priority > Client+Priority > Category+Priority > Priority > Default
            queries = [
                # Most specific: Client + Category + Priority
                """
                SELECT * FROM sla_policies 
                WHERE client_id = %s AND category_id = %s AND priority = %s AND is_active = true
                ORDER BY created_at DESC LIMIT 1
                """,
                # Client + Priority
                """
                SELECT * FROM sla_policies 
                WHERE client_id = %s AND category_id IS NULL AND priority = %s AND is_active = true
                ORDER BY created_at DESC LIMIT 1
                """,
                # Category + Priority
                """
                SELECT * FROM sla_policies 
                WHERE client_id IS NULL AND category_id = %s AND priority = %s AND is_active = true
                ORDER BY created_at DESC LIMIT 1
                """,
                # Priority only
                """
                SELECT * FROM sla_policies 
                WHERE client_id IS NULL AND category_id IS NULL AND priority = %s AND is_active = true
                ORDER BY created_at DESC LIMIT 1
                """,
                # Default policy
                """
                SELECT * FROM sla_policies 
                WHERE is_default = true AND is_active = true
                ORDER BY created_at DESC LIMIT 1
                """
            ]
            
            params_sets = [
                (ticket_data.get('client_id'), ticket_data.get('category_id'), ticket_data.get('priority')),
                (ticket_data.get('client_id'), ticket_data.get('priority')),
                (ticket_data.get('category_id'), ticket_data.get('priority')),
                (ticket_data.get('priority'),),
                ()
            ]
            
            for query, params in zip(queries, params_sets):
                policy = current_app.db_manager.execute_query(query, params, fetch='one')
                if policy:
                    return policy
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error getting SLA policy: {e}")
            return None
    
    def create_sla_tracking(self, ticket_id: str, ticket_data: Dict) -> bool:
        """Create SLA tracking for a new ticket"""
        try:
            # Get applicable SLA policy
            policy = self.get_applicable_sla_policy(ticket_data)
            if not policy:
                current_app.logger.warning(f"No SLA policy found for ticket {ticket_id}")
                return False
            
            # Calculate deadlines
            created_at = ticket_data.get('created_at', datetime.now())
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            response_deadline = self._calculate_deadline(
                created_at, 
                policy['response_time_hours'],
                policy
            )
            
            resolution_deadline = self._calculate_deadline(
                created_at,
                policy['resolution_time_hours'],
                policy
            )
            
            # Create tracking record
            tracking_data = {
                'ticket_id': ticket_id,
                'policy_id': policy['policy_id'],
                'response_deadline': response_deadline,
                'resolution_deadline': resolution_deadline,
                'response_status': 'pending',
                'resolution_status': 'pending',
                'escalation_level': 0
            }
            
            current_app.db_manager.execute_insert('sla_tracking', tracking_data)
            
            current_app.logger.info(f"SLA tracking created for ticket {ticket_id} with policy {policy['name']}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error creating SLA tracking: {e}")
            return False
    
    def update_sla_on_first_response(self, ticket_id: str) -> bool:
        """Update SLA tracking when first response is made"""
        try:
            now = datetime.now()
            
            # Update tracking
            update_data = {
                'first_response_at': now,
                'response_status': 'met'
            }
            
            current_app.db_manager.execute_update(
                'sla_tracking',
                update_data,
                'ticket_id = %s AND response_status = %s',
                (ticket_id, 'pending')
            )
            
            current_app.logger.info(f"SLA response updated for ticket {ticket_id}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error updating SLA response: {e}")
            return False
    
    def update_sla_on_resolution(self, ticket_id: str) -> bool:
        """Update SLA tracking when ticket is resolved"""
        try:
            now = datetime.now()
            
            # Update tracking
            update_data = {
                'resolved_at': now,
                'resolution_status': 'met',
                'updated_at': 'CURRENT_TIMESTAMP'
            }
            
            current_app.db_manager.execute_update(
                'sla_tracking',
                update_data,
                'ticket_id = %s AND resolution_status = %s',
                (ticket_id, 'pending')
            )
            
            current_app.logger.info(f"SLA resolution updated for ticket {ticket_id}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error updating SLA resolution: {e}")
            return False
    
    def check_sla_breaches(self) -> List[Dict]:
        """Check for SLA breaches and warnings"""
        try:
            now = datetime.now()
            breaches = []
            
            # Check response SLA breaches
            response_breaches = current_app.db_manager.execute_query("""
                SELECT st.tracking_id, st.ticket_id, st.response_deadline, st.escalation_level,
                       t.ticket_number, t.subject, t.priority, t.assigned_to,
                       sp.name as policy_name, sp.escalation_enabled, sp.escalation_levels
                FROM sla_tracking st
                JOIN tickets t ON st.ticket_id = t.ticket_id
                JOIN sla_policies sp ON st.policy_id = sp.policy_id
                WHERE st.response_status = 'pending' 
                AND st.response_deadline < %s
                AND t.status NOT IN ('resuelto', 'cerrado')
            """, (now,))
            
            for breach in (response_breaches or []):
                # Mark as breached
                current_app.db_manager.execute_update(
                    'sla_tracking',
                    {
                        'response_status': 'breached',
                        'response_breached_at': now,
                        'updated_at': 'CURRENT_TIMESTAMP'
                    },
                    'tracking_id = %s',
                    (breach['tracking_id'],)
                )
                
                breach['breach_type'] = 'response'
                breaches.append(breach)
            
            # Check resolution SLA breaches
            resolution_breaches = current_app.db_manager.execute_query("""
                SELECT st.tracking_id, st.ticket_id, st.resolution_deadline, st.escalation_level,
                       t.ticket_number, t.subject, t.priority, t.assigned_to,
                       sp.name as policy_name, sp.escalation_enabled, sp.escalation_levels
                FROM sla_tracking st
                JOIN tickets t ON st.ticket_id = t.ticket_id
                JOIN sla_policies sp ON st.policy_id = sp.policy_id
                WHERE st.resolution_status = 'pending' 
                AND st.resolution_deadline < %s
                AND t.status NOT IN ('resuelto', 'cerrado')
            """, (now,))
            
            for breach in (resolution_breaches or []):
                # Mark as breached
                current_app.db_manager.execute_update(
                    'sla_tracking',
                    {
                        'resolution_status': 'breached',
                        'resolution_breached_at': now,
                        'updated_at': 'CURRENT_TIMESTAMP'
                    },
                    'tracking_id = %s',
                    (breach['tracking_id'],)
                )
                
                breach['breach_type'] = 'resolution'
                breaches.append(breach)
            
            return breaches
            
        except Exception as e:
            current_app.logger.error(f"Error checking SLA breaches: {e}")
            return []
    
    def check_sla_warnings(self, warning_hours: int = 2) -> List[Dict]:
        """Check for upcoming SLA breaches (warnings)"""
        try:
            warning_time = datetime.now() + timedelta(hours=warning_hours)
            warnings = []
            
            # Check response warnings
            response_warnings = current_app.db_manager.execute_query("""
                SELECT st.tracking_id, st.ticket_id, st.response_deadline,
                       t.ticket_number, t.subject, t.priority, t.assigned_to,
                       sp.name as policy_name
                FROM sla_tracking st
                JOIN tickets t ON st.ticket_id = t.ticket_id
                JOIN sla_policies sp ON st.policy_id = sp.policy_id
                WHERE st.response_status = 'pending' 
                AND st.response_deadline BETWEEN %s AND %s
                AND t.status NOT IN ('resuelto', 'cerrado')
            """, (datetime.now(), warning_time))
            
            for warning in (response_warnings or []):
                warning['warning_type'] = 'response'
                warnings.append(warning)
            
            # Check resolution warnings
            resolution_warnings = current_app.db_manager.execute_query("""
                SELECT st.tracking_id, st.ticket_id, st.resolution_deadline,
                       t.ticket_number, t.subject, t.priority, t.assigned_to,
                       sp.name as policy_name
                FROM sla_tracking st
                JOIN tickets t ON st.ticket_id = t.ticket_id
                JOIN sla_policies sp ON st.policy_id = sp.policy_id
                WHERE st.resolution_status = 'pending' 
                AND st.resolution_deadline BETWEEN %s AND %s
                AND t.status NOT IN ('resuelto', 'cerrado')
            """, (datetime.now(), warning_time))
            
            for warning in (resolution_warnings or []):
                warning['warning_type'] = 'resolution'
                warnings.append(warning)
            
            return warnings
            
        except Exception as e:
            current_app.logger.error(f"Error checking SLA warnings: {e}")
            return []
    
    def process_escalations(self) -> int:
        """Process SLA escalations"""
        try:
            breaches = self.check_sla_breaches()
            escalated = 0
            
            for breach in breaches:
                if breach.get('escalation_enabled') and breach.get('escalation_levels'):
                    try:
                        escalation_levels = json.loads(breach['escalation_levels'])
                        current_level = breach['escalation_level']
                        
                        # Find next escalation level
                        next_escalation = None
                        for level_config in escalation_levels:
                            if level_config['level'] > current_level:
                                next_escalation = level_config
                                break
                        
                        if next_escalation:
                            # Check if enough time has passed for escalation
                            breach_time = breach.get('response_breached_at') or breach.get('resolution_breached_at')
                            if breach_time:
                                hours_since_breach = (datetime.now() - breach_time).total_seconds() / 3600
                                
                                if hours_since_breach >= next_escalation.get('hours', 0):
                                    # Escalate
                                    self._escalate_ticket(breach, next_escalation)
                                    escalated += 1
                    
                    except Exception as e:
                        current_app.logger.error(f"Error processing escalation for ticket {breach['ticket_id']}: {e}")
            
            return escalated
            
        except Exception as e:
            current_app.logger.error(f"Error processing escalations: {e}")
            return 0
    
    def _calculate_deadline(self, start_time: datetime, hours: int, policy: Dict) -> datetime:
        """Calculate SLA deadline considering business hours"""
        try:
            if not policy['business_hours_only']:
                # 24/7 SLA
                return start_time + timedelta(hours=hours)
            
            # Business hours SLA
            timezone = pytz.timezone(policy['timezone'])
            current_time = start_time.astimezone(timezone)
            
            business_start = policy['business_start_hour']
            business_end = policy['business_end_hour']
            business_days = policy['business_days']
            
            remaining_hours = hours
            
            while remaining_hours > 0:
                # Check if current day is a business day
                day_name = current_time.strftime('%A').lower()
                
                if day_name in business_days:
                    # It's a business day
                    if current_time.hour < business_start:
                        # Before business hours, jump to start
                        current_time = current_time.replace(hour=business_start, minute=0, second=0)
                    elif current_time.hour >= business_end:
                        # After business hours, jump to next business day
                        current_time = current_time + timedelta(days=1)
                        current_time = current_time.replace(hour=business_start, minute=0, second=0)
                        continue
                    
                    # Calculate hours available today
                    hours_until_end = business_end - current_time.hour - (current_time.minute / 60)
                    
                    if remaining_hours <= hours_until_end:
                        # Can finish today
                        current_time = current_time + timedelta(hours=remaining_hours)
                        remaining_hours = 0
                    else:
                        # Need to continue tomorrow
                        remaining_hours -= hours_until_end
                        current_time = current_time + timedelta(days=1)
                        current_time = current_time.replace(hour=business_start, minute=0, second=0)
                else:
                    # Not a business day, jump to next day
                    current_time = current_time + timedelta(days=1)
                    current_time = current_time.replace(hour=business_start, minute=0, second=0)
            
            return current_time.astimezone(pytz.UTC)
            
        except Exception as e:
            current_app.logger.error(f"Error calculating deadline: {e}")
            # Fallback to simple calculation
            return start_time + timedelta(hours=hours)
    
    def _escalate_ticket(self, breach: Dict, escalation_config: Dict):
        """Escalate a ticket according to escalation configuration"""
        try:
            # Update escalation level
            current_app.db_manager.execute_update(
                'sla_tracking',
                {
                    'escalation_level': escalation_config['level'],
                    'last_escalation_at': 'CURRENT_TIMESTAMP',
                    'updated_at': 'CURRENT_TIMESTAMP'
                },
                'tracking_id = %s',
                (breach['tracking_id'],)
            )
            
            # Send escalation notifications
            from modules.notifications.service import notifications_service
            
            additional_data = {
                'escalation_level': escalation_config['level'],
                'breach_type': breach['breach_type'],
                'policy_name': breach['policy_name']
            }
            
            notifications_service.send_ticket_notification(
                'sla_breach', 
                breach['ticket_id'], 
                additional_data
            )
            
            current_app.logger.info(f"Escalated ticket {breach['ticket_number']} to level {escalation_config['level']}")
            
        except Exception as e:
            current_app.logger.error(f"Error escalating ticket: {e}")

    def send_sla_breach_notification(self, breach_data: Dict) -> bool:
        """Send SLA breach notification using the new email system"""
        try:
            # Get ticket details
            ticket = current_app.db_manager.execute_query(
                """
                SELECT t.*, c.name as client_name, u.email as assigned_email, u.name as assigned_name,
                       s.name as site_name
                FROM tickets t
                JOIN clients c ON t.client_id = c.client_id
                LEFT JOIN users u ON t.assigned_to = u.user_id
                LEFT JOIN sites s ON t.site_id = s.site_id
                WHERE t.ticket_id = %s
                """,
                (breach_data['ticket_id'],),
                fetch='one'
            )

            if not ticket:
                return False

            # Get notification recipients
            recipients = self._get_breach_notification_recipients(breach_data, ticket)

            # Get SLA breach email template
            from modules.email.service import email_service
            template = email_service.get_template_by_type('sla_breach')

            if not template:
                current_app.logger.warning("No SLA breach email template found")
                return False

            # Prepare template variables
            template_variables = {
                'ticket_number': ticket['ticket_number'],
                'client_name': ticket['client_name'],
                'site_name': ticket.get('site_name', 'N/A'),
                'subject': ticket['subject'],
                'priority': ticket['priority'],
                'breach_type': breach_data['breach_type'],
                'time_elapsed': self._calculate_time_elapsed(breach_data),
                'assigned_name': ticket.get('assigned_name', 'No asignado'),
                'escalation_level': breach_data.get('escalation_level', 0),
                'deadline': breach_data.get('deadline', '').strftime('%d/%m/%Y %H:%M') if breach_data.get('deadline') else 'N/A'
            }

            # Send notifications
            success_count = 0
            for recipient in recipients:
                try:
                    # Create notification record
                    notification_data = {
                        'user_id': recipient.get('user_id'),
                        'ticket_id': breach_data['ticket_id'],
                        'type': 'sla_breach',
                        'title': f'SLA Breach: {ticket["ticket_number"]}',
                        'message': f'SLA {breach_data["breach_type"]} breach for ticket {ticket["ticket_number"]}',
                        'data': {
                            'breach_type': breach_data['breach_type'],
                            'deadline': breach_data.get('deadline'),
                            'escalation_level': breach_data.get('escalation_level', 0)
                        }
                    }

                    current_app.db_manager.execute_insert('notifications', notification_data)

                    # Send email if recipient has email
                    if recipient.get('email'):
                        success = email_service.send_template_email(
                            template_id=template['template_id'],
                            to_email=recipient['email'],
                            variables=template_variables,
                            ticket_id=breach_data['ticket_id']
                        )
                        if success:
                            success_count += 1

                except Exception as e:
                    current_app.logger.error(f"Error sending breach notification to {recipient}: {e}")
                    continue

            current_app.logger.info(f"Sent SLA breach notifications to {success_count} recipients for ticket {ticket['ticket_number']}")
            return success_count > 0

        except Exception as e:
            current_app.logger.error(f"Error sending SLA breach notification: {e}")
            return False

    def _get_breach_notification_recipients(self, breach_data: Dict, ticket: Dict) -> List[Dict]:
        """Get list of recipients for SLA breach notifications"""
        try:
            recipients = []

            # Add assigned technician
            if ticket.get('assigned_to') and ticket.get('assigned_email'):
                recipients.append({
                    'user_id': ticket['assigned_to'],
                    'email': ticket['assigned_email'],
                    'name': ticket.get('assigned_name', 'Technician')
                })

            # Add superadmins and admins
            admin_users = current_app.db_manager.execute_query(
                """
                SELECT user_id, email, name
                FROM users
                WHERE role IN ('superadmin', 'admin')
                AND is_active = true
                AND email IS NOT NULL
                """
            )

            for admin in (admin_users or []):
                recipients.append({
                    'user_id': admin['user_id'],
                    'email': admin['email'],
                    'name': admin['name']
                })

            # Add client contacts if configured
            if breach_data.get('escalation_level', 0) >= 2:  # High escalation level
                client_contacts = current_app.db_manager.execute_query(
                    """
                    SELECT email, name
                    FROM users
                    WHERE client_id = %s
                    AND role = 'client_admin'
                    AND is_active = true
                    AND email IS NOT NULL
                    """,
                    (ticket['client_id'],)
                )

                for contact in (client_contacts or []):
                    recipients.append({
                        'user_id': None,  # External contact
                        'email': contact['email'],
                        'name': contact['name']
                    })

            return recipients

        except Exception as e:
            current_app.logger.error(f"Error getting breach notification recipients: {e}")
            return []

    def _calculate_time_elapsed(self, breach_data: Dict) -> str:
        """Calculate human-readable time elapsed since deadline"""
        try:
            if not breach_data.get('deadline'):
                return 'N/A'

            deadline = breach_data['deadline']
            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))

            now = datetime.now(deadline.tzinfo) if deadline.tzinfo else datetime.now()
            elapsed = now - deadline

            if elapsed.days > 0:
                return f"{elapsed.days} días, {elapsed.seconds // 3600} horas"
            elif elapsed.seconds >= 3600:
                return f"{elapsed.seconds // 3600} horas, {(elapsed.seconds % 3600) // 60} minutos"
            else:
                return f"{elapsed.seconds // 60} minutos"

        except Exception as e:
            current_app.logger.error(f"Error calculating time elapsed: {e}")
            return 'N/A'

    def calculate_business_hours(self, start_time: datetime, end_time: datetime,
                               business_start: int = 8, business_end: int = 17,
                               business_days: List[int] = None) -> float:
        """Calculate business hours between two datetime objects"""
        try:
            if business_days is None:
                business_days = [0, 1, 2, 3, 4]  # Monday to Friday

            if start_time >= end_time:
                return 0.0

            total_hours = 0.0
            current_time = start_time

            while current_time.date() <= end_time.date():
                # Check if current day is a business day
                if current_time.weekday() in business_days:
                    # Calculate business hours for this day
                    day_start = current_time.replace(hour=business_start, minute=0, second=0, microsecond=0)
                    day_end = current_time.replace(hour=business_end, minute=0, second=0, microsecond=0)

                    # Adjust for start and end times
                    if current_time.date() == start_time.date():
                        day_start = max(day_start, start_time)
                    if current_time.date() == end_time.date():
                        day_end = min(day_end, end_time)

                    # Calculate hours for this day
                    if day_start < day_end:
                        day_hours = (day_end - day_start).total_seconds() / 3600
                        total_hours += day_hours

                # Move to next day
                current_time = (current_time + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

            return total_hours

        except Exception as e:
            current_app.logger.error(f"Error calculating business hours: {e}")
            return 0.0

    def run_sla_monitor(self) -> Dict[str, int]:
        """Run SLA monitoring - check breaches, warnings, and process escalations"""
        try:
            current_app.logger.info("🔍 SLA Monitor: Starting SLA monitoring cycle")

            results = {
                'breaches_found': 0,
                'warnings_found': 0,
                'escalations_processed': 0,
                'notifications_sent': 0
            }

            # Check for SLA breaches
            breaches = self.check_sla_breaches()
            results['breaches_found'] = len(breaches)

            if breaches:
                current_app.logger.warning(f"🚨 SLA Monitor: Found {len(breaches)} SLA breaches")
                for breach in breaches:
                    # Send breach notification
                    if self.send_sla_breach_notification(breach):
                        results['notifications_sent'] += 1

            # Check for SLA warnings
            warnings = self.check_sla_warnings(warning_hours=2)
            results['warnings_found'] = len(warnings)

            if warnings:
                current_app.logger.info(f"⚠️ SLA Monitor: Found {len(warnings)} SLA warnings")

            # Process escalations
            escalations = self.process_escalations()
            results['escalations_processed'] = escalations

            if escalations > 0:
                current_app.logger.info(f"📈 SLA Monitor: Processed {escalations} escalations")

            current_app.logger.info(f"✅ SLA Monitor: Completed monitoring cycle - {results}")
            return results

        except Exception as e:
            current_app.logger.error(f"❌ SLA Monitor: Error in monitoring cycle: {e}")
            return {'error': str(e)}

    def create_sla_policy(self, data: Dict) -> Optional[str]:
        """Create a new SLA policy"""
        try:
            import uuid
            policy_id = str(uuid.uuid4())

            query = """
            INSERT INTO sla_policies (
                policy_id, name, description, priority,
                response_time_hours, resolution_time_hours,
                business_hours_only, escalation_enabled, escalation_levels,
                client_id, category_id, is_active, is_default
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            params = (
                policy_id,
                data['name'],
                data.get('description'),
                data['priority'],
                data['response_time_hours'],
                data['resolution_time_hours'],
                data.get('business_hours_only', True),
                data.get('escalation_enabled', False),
                json.dumps(data.get('escalation_levels', 1)),  # Convert to JSON
                data.get('client_id') if data.get('client_id') else None,
                data.get('category_id') if data.get('category_id') else None,
                data.get('is_active', True),
                False  # New policies are not default by default
            )

            current_app.db_manager.execute_query(query, params, fetch='none')
            current_app.logger.info(f"Created SLA policy: {data['name']} (ID: {policy_id})")
            return policy_id

        except Exception as e:
            current_app.logger.error(f"Error creating SLA policy: {e}")
            return None

    def update_sla_policy(self, policy_id: str, data: Dict) -> bool:
        """Update an existing SLA policy"""
        try:
            # Build dynamic update query
            update_fields = []
            params = []

            if 'name' in data:
                update_fields.append("name = %s")
                params.append(data['name'])
            if 'description' in data:
                update_fields.append("description = %s")
                params.append(data['description'])
            if 'priority' in data:
                update_fields.append("priority = %s")
                params.append(data['priority'])
            if 'response_time_hours' in data:
                update_fields.append("response_time_hours = %s")
                params.append(data['response_time_hours'])
            if 'resolution_time_hours' in data:
                update_fields.append("resolution_time_hours = %s")
                params.append(data['resolution_time_hours'])
            if 'business_hours_only' in data:
                update_fields.append("business_hours_only = %s")
                params.append(data['business_hours_only'])
            if 'escalation_enabled' in data:
                update_fields.append("escalation_enabled = %s")
                params.append(data['escalation_enabled'])
            if 'escalation_levels' in data:
                update_fields.append("escalation_levels = %s")
                params.append(json.dumps(data['escalation_levels']))
            if 'client_id' in data:
                update_fields.append("client_id = %s")
                params.append(data['client_id'] if data['client_id'] else None)
            if 'category_id' in data:
                update_fields.append("category_id = %s")
                params.append(data['category_id'] if data['category_id'] else None)
            if 'is_active' in data:
                update_fields.append("is_active = %s")
                params.append(data['is_active'])

            if not update_fields:
                return False

            update_fields.append("updated_at = NOW()")
            params.append(policy_id)

            query = f"""
            UPDATE sla_policies
            SET {', '.join(update_fields)}
            WHERE policy_id = %s
            """

            current_app.db_manager.execute_query(query, params, fetch='none')
            current_app.logger.info(f"Updated SLA policy: {policy_id}")
            return True

        except Exception as e:
            current_app.logger.error(f"Error updating SLA policy: {e}")
            return False

    def delete_sla_policy(self, policy_id: str) -> bool:
        """Delete an SLA policy"""
        try:
            # Check if policy is default
            check_query = "SELECT is_default FROM sla_policies WHERE policy_id = %s"
            policy = current_app.db_manager.execute_query(check_query, (policy_id,), fetch='one')

            if policy and policy['is_default']:
                current_app.logger.warning(f"Cannot delete default SLA policy: {policy_id}")
                return False

            # Delete the policy
            query = "DELETE FROM sla_policies WHERE policy_id = %s"
            current_app.db_manager.execute_query(query, (policy_id,), fetch='none')
            current_app.logger.info(f"Deleted SLA policy: {policy_id}")
            return True

        except Exception as e:
            current_app.logger.error(f"Error deleting SLA policy: {e}")
            return False

    def set_default_policy(self, policy_id: str) -> bool:
        """Set an SLA policy as default"""
        try:
            # First, unset all other default policies
            current_app.db_manager.execute_query(
                "UPDATE sla_policies SET is_default = false WHERE is_default = true",
                fetch='none'
            )

            # Set the new default policy
            query = "UPDATE sla_policies SET is_default = true WHERE policy_id = %s"
            current_app.db_manager.execute_query(query, (policy_id,), fetch='none')
            current_app.logger.info(f"Set default SLA policy: {policy_id}")
            return True

        except Exception as e:
            current_app.logger.error(f"Error setting default SLA policy: {e}")
            return False

# Global SLA service instance
sla_service = SLAService()
