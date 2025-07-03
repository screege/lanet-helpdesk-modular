"""
LANET Helpdesk V3 - Intelligent Email-to-Ticket Routing Service
Phase 3: Email Domain Authorization & Client Mapping
"""

import re
import time
from typing import Dict, List, Optional, Tuple
from flask import current_app
from flask import current_app


class EmailRoutingService:
    """Service for intelligent email-to-ticket routing based on sender authorization"""
    
    def __init__(self):
        self.routing_cache = {}  # Cache for routing rules
        self.cache_ttl = 300  # 5 minutes cache TTL
        
    def route_email_to_client_site(self, sender_email: str, sender_name: str = None) -> Dict:
        """
        Route incoming email to appropriate client and site based on authorization rules
        
        Returns:
        {
            'client_id': UUID or None,
            'site_id': UUID or None,
            'routing_decision': 'exact_match'|'domain_match'|'fallback'|'unauthorized',
            'routing_confidence': float (0.0-1.0),
            'matched_rule_id': UUID or None,
            'priority': 'baja'|'media'|'alta'|'critica'
        }
        """
        start_time = time.time()
        
        try:
            current_app.logger.info(f"🔧 EMAIL ROUTING: Starting routing for {sender_email}")
            
            # Extract domain from email
            sender_domain = self._extract_domain(sender_email)
            if not sender_domain:
                return self._create_unauthorized_routing(sender_email, "Invalid email format")
            
            current_app.logger.info(f"🔧 EMAIL ROUTING: Extracted domain: {sender_domain}")
            
            # Step 1: Try exact email match first (highest priority)
            current_app.logger.info(f"🔧 EMAIL ROUTING: Step 1 - Checking exact email match for {sender_email}")
            exact_match = self._find_exact_email_match(sender_email)
            current_app.logger.info(f"🔧 EMAIL ROUTING: Exact match result: {exact_match}")
            if exact_match:
                result = self._create_routing_result(
                    exact_match, 'exact_match', 1.0, sender_email, sender_domain
                )
                self._log_routing_decision(result, start_time)
                return result
            
            # Step 2: Try domain match
            current_app.logger.info(f"🔧 EMAIL ROUTING: Step 2 - Checking domain match for {sender_domain}")
            domain_match = self._find_domain_match(sender_domain)
            current_app.logger.info(f"🔧 EMAIL ROUTING: Domain match result: {domain_match}")
            if domain_match:
                result = self._create_routing_result(
                    domain_match, 'domain_match', 0.8, sender_email, sender_domain
                )
                self._log_routing_decision(result, start_time)
                return result
            
            # Step 3: Try pattern matching (advanced rules)
            pattern_match = self._find_pattern_match(sender_email)
            if pattern_match:
                result = self._create_routing_result(
                    pattern_match, 'pattern_match', 0.6, sender_email, sender_domain
                )
                self._log_routing_decision(result, start_time)
                return result
            
            # Step 4: Unauthorized email - route to unknown sender client
            result = self._create_unauthorized_routing(sender_email, "No matching authorization rules")
            self._log_routing_decision(result, start_time)
            return result
            
        except Exception as e:
            import traceback
            error_details = f"Error: {str(e)}, Type: {type(e).__name__}, Traceback: {traceback.format_exc()}"
            current_app.logger.error(f"🔧 EMAIL ROUTING: Error routing email {sender_email}: {error_details}")

            # Provide more detailed error message
            error_msg = str(e) if str(e) else f"Unknown {type(e).__name__} error"
            return self._create_unauthorized_routing(sender_email, f"Routing error: {error_msg}")
    
    def _extract_domain(self, email: str) -> Optional[str]:
        """Extract domain from email address"""
        try:
            if '@' not in email:
                return None
            domain = email.split('@')[1].lower().strip()
            return f"@{domain}"
        except:
            return None
    
    def _find_exact_email_match(self, sender_email: str) -> Optional[Dict]:
        """Find exact email match in site authorized emails"""
        try:
            current_app.logger.info(f"🔧 EMAIL ROUTING: Getting database connection for exact match")
            with current_app.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            s.site_id,
                            s.client_id,
                            c.name as client_name,
                            s.name as site_name,
                            c.default_priority,
                            err.rule_id,
                            err.priority as rule_priority
                        FROM sites s
                        JOIN clients c ON s.client_id = c.client_id
                        LEFT JOIN email_routing_rules err ON s.site_id = err.site_id 
                            AND err.rule_type = 'email' 
                            AND err.rule_value = %s 
                            AND err.is_active = true
                        WHERE s.is_active = true 
                            AND c.is_active = true
                            AND s.site_email_routing_enabled = true
                            AND c.email_routing_enabled = true
                            AND (
                                %s = ANY(s.authorized_emails) 
                                OR err.rule_id IS NOT NULL
                            )
                        ORDER BY err.priority ASC NULLS LAST, s.is_primary_site DESC
                        LIMIT 1
                    """, (sender_email.lower(), sender_email.lower()))
                    
                    result = cursor.fetchone()
                    if result:
                        return {
                            'site_id': result['site_id'],
                            'client_id': result['client_id'],
                            'client_name': result['client_name'],
                            'site_name': result['site_name'],
                            'priority': result['default_priority'] or 'media',
                            'rule_id': result['rule_id'],
                            'rule_priority': result['rule_priority']
                        }
                    return None
                    
        except Exception as e:
            current_app.logger.error(f"Error finding exact email match: {e}")
            return None
    
    def _find_domain_match(self, sender_domain: str) -> Optional[Dict]:
        """Find domain match in client authorized domains"""
        try:
            with current_app.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            c.client_id,
                            c.name as client_name,
                            c.default_priority,
                            s.site_id,
                            s.name as site_name,
                            s.is_primary_site,
                            err.rule_id,
                            err.priority as rule_priority
                        FROM clients c
                        LEFT JOIN email_routing_rules err ON c.client_id = err.client_id 
                            AND err.rule_type = 'domain' 
                            AND err.rule_value = %s 
                            AND err.is_active = true
                        LEFT JOIN sites s ON c.client_id = s.client_id 
                            AND s.is_active = true
                            AND s.site_email_routing_enabled = true
                        WHERE c.is_active = true 
                            AND c.email_routing_enabled = true
                            AND (
                                %s = ANY(c.authorized_domains) 
                                OR err.rule_id IS NOT NULL
                            )
                        ORDER BY 
                            err.priority ASC NULLS LAST,
                            s.is_primary_site DESC NULLS LAST,
                            s.created_at ASC
                        LIMIT 1
                    """, (sender_domain.lower(), sender_domain.lower()))
                    
                    result = cursor.fetchone()
                    if result:
                        return {
                            'client_id': result['client_id'],
                            'client_name': result['client_name'],
                            'priority': result['default_priority'] or 'media',
                            'site_id': result['site_id'],  # May be None if no sites
                            'site_name': result['site_name'],
                            'is_primary_site': result['is_primary_site'],
                            'rule_id': result['rule_id'],
                            'rule_priority': result['rule_priority']
                        }
                    return None
                    
        except Exception as e:
            current_app.logger.error(f"Error finding domain match: {e}")
            return None
    
    def _find_pattern_match(self, sender_email: str) -> Optional[Dict]:
        """Find pattern match using regex rules"""
        try:
            with current_app.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            err.rule_id,
                            err.rule_value,
                            err.client_id,
                            err.site_id,
                            err.priority,
                            c.name as client_name,
                            c.default_priority,
                            s.name as site_name
                        FROM email_routing_rules err
                        JOIN clients c ON err.client_id = c.client_id
                        LEFT JOIN sites s ON err.site_id = s.site_id
                        WHERE err.rule_type = 'pattern' 
                            AND err.is_active = true
                            AND c.is_active = true
                            AND c.email_routing_enabled = true
                        ORDER BY err.priority ASC
                    """)
                    
                    for row in cursor.fetchall():
                        try:
                            if re.match(row['rule_value'], sender_email, re.IGNORECASE):
                                return {
                                    'rule_id': row['rule_id'],
                                    'client_id': row['client_id'],
                                    'site_id': row['site_id'],
                                    'client_name': row['client_name'],
                                    'site_name': row['site_name'],
                                    'priority': row['default_priority'] or 'media',
                                    'rule_priority': row['priority']
                                }
                        except re.error:
                            current_app.logger.warning(f"Invalid regex pattern in rule {row['rule_id']}: {row['rule_value']}")
                            continue
                    
                    return None
                    
        except Exception as e:
            current_app.logger.error(f"Error finding pattern match: {e}")
            return None
    
    def _create_routing_result(self, match_data: Dict, decision: str, confidence: float, 
                             sender_email: str, sender_domain: str) -> Dict:
        """Create standardized routing result"""
        return {
            'client_id': match_data.get('client_id'),
            'site_id': match_data.get('site_id'),
            'routing_decision': decision,
            'routing_confidence': confidence,
            'matched_rule_id': match_data.get('rule_id'),
            'priority': match_data.get('priority', 'media'),
            'client_name': match_data.get('client_name'),
            'site_name': match_data.get('site_name'),
            'sender_email': sender_email,
            'sender_domain': sender_domain
        }
    
    def _create_unauthorized_routing(self, sender_email: str, reason: str) -> Dict:
        """Create routing result for unauthorized emails"""
        try:
            # Get unknown sender client from configuration
            with current_app.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT ec.unknown_sender_client_id, c.name, c.default_priority
                        FROM email_configurations ec
                        LEFT JOIN clients c ON ec.unknown_sender_client_id = c.client_id
                        WHERE ec.is_active = true
                        LIMIT 1
                    """)
                    
                    result = cursor.fetchone()
                    if result and result['unknown_sender_client_id']:
                        return {
                            'client_id': result['unknown_sender_client_id'],
                            'site_id': None,  # No specific site for unauthorized emails
                            'routing_decision': 'unauthorized',
                            'routing_confidence': 0.0,
                            'matched_rule_id': None,
                            'priority': 'media',  # Default priority for unauthorized
                            'client_name': result['name'] or 'Unknown Sender',
                            'site_name': None,
                            'sender_email': sender_email,
                            'sender_domain': self._extract_domain(sender_email),
                            'reason': reason
                        }
            
            # Fallback if no unknown sender client configured
            return {
                'client_id': None,
                'site_id': None,
                'routing_decision': 'unauthorized',
                'routing_confidence': 0.0,
                'matched_rule_id': None,
                'priority': 'media',
                'client_name': 'Unknown Sender',
                'site_name': None,
                'sender_email': sender_email,
                'sender_domain': self._extract_domain(sender_email),
                'reason': reason
            }
            
        except Exception as e:
            current_app.logger.error(f"Error creating unauthorized routing: {e}")
            return {
                'client_id': None,
                'site_id': None,
                'routing_decision': 'error',
                'routing_confidence': 0.0,
                'matched_rule_id': None,
                'priority': 'media',
                'client_name': 'System Error',
                'site_name': None,
                'sender_email': sender_email,
                'sender_domain': self._extract_domain(sender_email),
                'reason': f"Routing error: {str(e)}"
            }
    
    def _log_routing_decision(self, routing_result: Dict, start_time: float):
        """Log routing decision for analysis and debugging"""
        try:
            processing_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            
            with current_app.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO email_routing_log (
                            email_message_id, sender_email, sender_domain, matched_rule_id,
                            routed_client_id, routed_site_id, routing_decision, routing_confidence,
                            processing_time_ms
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        f"routing-test-{int(time.time())}",  # Temporary message ID
                        routing_result.get('sender_email'),
                        routing_result.get('sender_domain'),
                        routing_result.get('matched_rule_id'),
                        routing_result.get('client_id'),
                        routing_result.get('site_id'),
                        routing_result.get('routing_decision'),
                        routing_result.get('routing_confidence'),
                        processing_time
                    ))
                    conn.commit()
                    
        except Exception as e:
            current_app.logger.error(f"Error logging routing decision: {e}")


# Global routing service instance
email_routing_service = EmailRoutingService()
