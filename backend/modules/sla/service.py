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
                'response_status': 'met',
                'updated_at': 'CURRENT_TIMESTAMP'
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

# Global SLA service instance
sla_service = SLAService()
