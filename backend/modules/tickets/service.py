#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Tickets Module Service
Complete ticket lifecycle management with MSP workflow
Workflow: Client → Site → User → Ticket → Assignment → Resolution
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from core.database import DatabaseManager
from core.auth import AuthManager
import logging

class TicketService:
    """Service class for complete ticket lifecycle management"""
    
    def __init__(self, db_manager: DatabaseManager, auth_manager: AuthManager):
        self.db = db_manager
        self.auth = auth_manager
        self.logger = logging.getLogger(__name__)

    def _get_system_config(self, config_key: str, default_value: str = None) -> str:
        """Get system configuration value"""
        try:
            query = "SELECT config_value FROM system_config WHERE config_key = %s"
            result = self.db.execute_query(query, (config_key,), fetch='one')
            return result['config_value'] if result else default_value
        except Exception as e:
            self.logger.error(f"Error getting system config {config_key}: {e}")
            return default_value
    
    def get_all_tickets(self, page: int = 1, per_page: int = 20, filters: Dict = None) -> Dict[str, Any]:
        """Get all tickets with pagination, search, and filters"""
        try:
            # Build filter conditions
            where_conditions = ["t.is_active = true"]
            params = []
            
            if filters:
                # Client filter
                if filters.get('client_id'):
                    where_conditions.append("t.client_id = %s")
                    params.append(filters['client_id'])
                
                # Status filter
                if filters.get('status'):
                    where_conditions.append("t.status = %s")
                    params.append(filters['status'])
                
                # Priority filter
                if filters.get('priority'):
                    where_conditions.append("t.priority = %s")
                    params.append(filters['priority'])
                
                # Assigned to filter
                if filters.get('assigned_to'):
                    where_conditions.append("t.assigned_to = %s")
                    params.append(filters['assigned_to'])
                
                # Search filter
                if filters.get('search'):
                    where_conditions.append("(t.subject ILIKE %s OR t.description ILIKE %s OR t.ticket_number ILIKE %s)")
                    search_term = f"%{filters['search']}%"
                    params.extend([search_term, search_term, search_term])
            
            where_clause = " AND ".join(where_conditions)

            # Handle sorting
            sort_by = filters.get('sort_by', 'created_at') if filters else 'created_at'
            sort_order = filters.get('sort_order', 'desc') if filters else 'desc'

            # Validate sort fields to prevent SQL injection
            valid_sort_fields = {
                'ticket_number': 'CAST(SUBSTRING(t.ticket_number FROM \'TKT-([0-9]+)\') AS BIGINT)',
                'client_name': 'c.name',
                'subject': 't.subject',
                'status': 't.status',
                'priority': 't.priority',
                'created_at': 't.created_at',
                'updated_at': 't.updated_at'
            }

            sort_field = valid_sort_fields.get(sort_by, 't.created_at')
            sort_direction = 'ASC' if sort_order.lower() == 'asc' else 'DESC'

            # Get total count
            count_query = f"""
            SELECT COUNT(*) as total
            FROM tickets t
            WHERE {where_clause}
            """
            total_result = self.db.execute_query(count_query, tuple(params), fetch='one')
            total = total_result['total'] if total_result else 0

            # Calculate offset
            offset = (page - 1) * per_page

            # Get tickets with related data
            query = f"""
            SELECT t.ticket_id, t.ticket_number, t.client_id, t.site_id, t.asset_id,
                   t.created_by, t.assigned_to, t.subject, t.description, t.affected_person,
                   t.affected_person_phone, t.affected_person_contact, t.notification_email, t.additional_emails, t.priority, t.category_id,
                   t.status, t.channel, t.is_email_originated, t.from_email,
                   t.email_message_id, t.email_thread_id, t.approval_status,
                   t.approved_by, t.approved_at, t.created_at, t.updated_at,
                   t.assigned_at, t.resolved_at, t.closed_at, t.resolution_notes,
                   c.name as client_name,
                   s.name as site_name,
                   cat.name as category_name,
                   creator.name as created_by_name,
                   assignee.name as assigned_to_name
            FROM tickets t
            LEFT JOIN clients c ON t.client_id = c.client_id
            LEFT JOIN sites s ON t.site_id = s.site_id
            LEFT JOIN categories cat ON t.category_id = cat.category_id
            LEFT JOIN users creator ON t.created_by = creator.user_id
            LEFT JOIN users assignee ON t.assigned_to = assignee.user_id
            WHERE {where_clause}
            ORDER BY {sort_field} {sort_direction}
            LIMIT %s OFFSET %s
            """
            
            final_params = params + [per_page, offset]
            tickets = self.db.execute_query(query, tuple(final_params))
            
            return {
                'tickets': tickets or [],
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            self.logger.error(f"Error getting tickets: {e}")
            raise
    
    def get_ticket_by_id(self, ticket_id: str) -> Optional[Dict]:
        """Get ticket by ID with complete information"""
        try:
            if not self.db.validate_uuid(ticket_id):
                return None
                
            query = """
            SELECT t.ticket_id, t.ticket_number, t.client_id, t.site_id, t.asset_id,
                   t.created_by, t.assigned_to, t.subject, t.description, t.affected_person,
                   t.affected_person_phone, t.affected_person_contact, t.notification_email, t.additional_emails, t.priority, t.category_id,
                   t.status, t.channel, t.is_email_originated, t.from_email,
                   t.email_message_id, t.email_thread_id, t.approval_status,
                   t.approved_by, t.approved_at, t.created_at, t.updated_at,
                   t.assigned_at, t.resolved_at, t.closed_at, t.resolution_notes,
                   c.name as client_name,
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
            
            return self.db.execute_query(query, (ticket_id,), fetch='one')
            
        except Exception as e:
            self.logger.error(f"Error getting ticket {ticket_id}: {e}")
            raise
    
    def create_ticket(self, ticket_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Create a new ticket with MSP workflow validation"""
        try:
            # Validate required fields
            required_fields = ['client_id', 'site_id', 'subject', 'description', 'affected_person', 'affected_person_contact', 'priority']
            for field in required_fields:
                if field not in ticket_data or not ticket_data[field]:
                    return {'success': False, 'errors': {field: f'{field} is required'}}
            
            # Validate client exists and is active
            client = self.db.execute_query(
                "SELECT client_id, name FROM clients WHERE client_id = %s AND is_active = true",
                (ticket_data['client_id'],),
                fetch='one'
            )
            if not client:
                return {'success': False, 'errors': {'client_id': 'Invalid or inactive client'}}
            
            # Validate site exists and belongs to client
            site = self.db.execute_query(
                "SELECT site_id, name FROM sites WHERE site_id = %s AND client_id = %s AND is_active = true",
                (ticket_data['site_id'], ticket_data['client_id']),
                fetch='one'
            )
            if not site:
                return {'success': False, 'errors': {'site_id': 'Invalid site or site does not belong to client'}}
            
            # Validate priority
            valid_priorities = ['baja', 'media', 'alta', 'critica']
            if ticket_data['priority'] not in valid_priorities:
                return {'success': False, 'errors': {'priority': 'Invalid priority level'}}
            
            # Validate category if provided
            if ticket_data.get('category_id'):
                category = self.db.execute_query(
                    "SELECT category_id FROM categories WHERE category_id = %s AND is_active = true",
                    (ticket_data['category_id'],),
                    fetch='one'
                )
                if not category:
                    return {'success': False, 'errors': {'category_id': 'Invalid category'}}
            
            # Generate ticket number
            ticket_number = self._generate_ticket_number()
            
            # Prepare ticket data for insertion
            new_ticket_data = {
                'ticket_id': str(uuid.uuid4()),
                'ticket_number': ticket_number,
                'client_id': ticket_data['client_id'],
                'site_id': ticket_data['site_id'],
                'asset_id': ticket_data.get('asset_id'),
                'created_by': created_by,
                'assigned_to': ticket_data.get('assigned_to'),
                'subject': ticket_data['subject'].strip(),
                'description': ticket_data['description'].strip(),
                'affected_person': ticket_data['affected_person'].strip(),
                'affected_person_contact': ticket_data['affected_person_contact'].strip(),
                'additional_emails': ticket_data.get('additional_emails', []),
                'priority': ticket_data['priority'],
                'category_id': ticket_data.get('category_id'),
                'status': 'nuevo',
                'channel': ticket_data.get('channel', 'portal'),
                'is_email_originated': ticket_data.get('is_email_originated', False),
                'from_email': ticket_data.get('from_email'),
                'email_message_id': ticket_data.get('email_message_id'),
                'email_thread_id': ticket_data.get('email_thread_id'),
                'approval_status': 'pendiente'
                # Note: created_at and updated_at will use DEFAULT CURRENT_TIMESTAMP from PostgreSQL
                # which respects the database timezone (America/Mexico_City)
            }

            # Auto-assignment logic: assign to available technician if not explicitly assigned
            if not new_ticket_data['assigned_to']:
                auto_assigned_technician = self._get_auto_assignment_technician(ticket_data['client_id'], ticket_data['priority'])
                if auto_assigned_technician:
                    new_ticket_data['assigned_to'] = auto_assigned_technician
                    self.logger.info(f"Auto-assigned ticket {ticket_number} to technician {auto_assigned_technician}")
            
            # Auto-assign if assigned_to is provided
            if new_ticket_data['assigned_to']:
                new_ticket_data['status'] = 'en_proceso'
                # Note: assigned_at will be set by database trigger or explicit update later
                # to maintain timezone consistency
            
            # Insert ticket
            result = self.db.execute_insert(
                'tickets',
                new_ticket_data,
                returning='ticket_id, ticket_number, subject, status, created_at'
            )
            
            if result:
                # Create initial activity log
                self._create_activity_log(
                    result['ticket_id'],
                    created_by,
                    'created',
                    f"Ticket creado: {result['subject']}"
                )
                
                # Create SLA tracking
                try:
                    from modules.sla.service import sla_service
                    sla_service.create_sla_tracking(result['ticket_id'], new_ticket_data)
                except Exception as e:
                    self.logger.warning(f"Failed to create SLA tracking: {e}")

                # Send notification for ticket creation
                try:
                    from modules.notifications.service import notifications_service
                    notifications_service.send_ticket_notification('ticket_created', result['ticket_id'])
                except Exception as e:
                    self.logger.warning(f"Failed to send ticket creation notification: {e}")

                self.logger.info(f"Ticket created successfully: {result['ticket_number']}")
                return {'success': True, 'ticket': result}
            else:
                return {'success': False, 'errors': {'general': 'Failed to create ticket'}}
                
        except Exception as e:
            self.logger.error(f"Error creating ticket: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}
    
    def _generate_ticket_number(self) -> str:
        """Generate unique ticket number using PostgreSQL sequence"""
        try:
            # Use the PostgreSQL function to generate ticket number
            result = self.db.execute_query(
                "SELECT generate_ticket_number() as ticket_number",
                fetch='one'
            )

            if result and result['ticket_number']:
                return result['ticket_number']
            else:
                # Fallback: use sequence directly
                result = self.db.execute_query(
                    "SELECT 'TKT-' || LPAD(nextval('ticket_number_seq')::TEXT, 6, '0') as ticket_number",
                    fetch='one'
                )
                return result['ticket_number'] if result else f"TKT-{str(uuid.uuid4())[:8].upper()}"

        except Exception as e:
            self.logger.error(f"Error generating ticket number: {e}")
            # Final fallback to UUID-based number
            return f"TKT-{str(uuid.uuid4())[:8].upper()}"

    def _get_auto_assignment_technician(self, client_id: str, priority: str) -> Optional[str]:
        """Get technician for auto-assignment using round-robin algorithm"""
        try:
            # Get available technicians (superadmin, admin, technician roles)
            technicians_query = """
            SELECT user_id, name, email, role
            FROM users
            WHERE role IN ('superadmin', 'admin', 'technician')
            AND is_active = true
            ORDER BY role DESC, name ASC
            """

            technicians = self.db.execute_query(technicians_query)

            if not technicians:
                self.logger.warning("No available technicians found for auto-assignment")
                return None

            # For now, use simple round-robin: get technician with least assigned tickets
            # This can be enhanced later with more sophisticated algorithms
            assignment_query = """
            SELECT u.user_id, u.name, COUNT(t.ticket_id) as ticket_count
            FROM users u
            LEFT JOIN tickets t ON u.user_id = t.assigned_to
                AND t.status NOT IN ('cerrado', 'resuelto')
            WHERE u.role IN ('superadmin', 'admin', 'technician')
            AND u.is_active = true
            GROUP BY u.user_id, u.name
            ORDER BY ticket_count ASC, u.name ASC
            LIMIT 1
            """

            selected_technician = self.db.execute_query(assignment_query, fetch='one')

            if selected_technician:
                self.logger.info(f"Auto-assignment: Selected {selected_technician['name']} (current tickets: {selected_technician['ticket_count']})")
                return selected_technician['user_id']

            # Fallback: return first available technician
            return technicians[0]['user_id']

        except Exception as e:
            self.logger.error(f"Error in auto-assignment logic: {e}")
            return None
    
    def _create_activity_log(self, ticket_id: str, user_id: str, action: str, description: str):
        """Create activity log entry"""
        try:
            activity_data = {
                'activity_id': str(uuid.uuid4()),
                'ticket_id': ticket_id,
                'user_id': user_id,
                'action': action,
                'description': description,
                'created_at': datetime.utcnow()
            }
            
            self.db.execute_insert('ticket_activities', activity_data)
            
        except Exception as e:
            self.logger.error(f"Error creating activity log: {e}")
            # Don't fail the main operation for logging errors

    def update_ticket(self, ticket_id: str, ticket_data: Dict[str, Any], updated_by: str) -> Dict[str, Any]:
        """Update an existing ticket"""
        try:
            # Validate ticket ID
            if not self.db.validate_uuid(ticket_id):
                return {'success': False, 'errors': {'ticket_id': 'Invalid ticket ID'}}

            # Check if ticket exists
            existing_ticket = self.get_ticket_by_id(ticket_id)
            if not existing_ticket:
                return {'success': False, 'errors': {'ticket_id': 'Ticket not found'}}

            # Prepare update data
            # Note: updated_at will be handled by PostgreSQL trigger (update_updated_at_column)
            # which uses CURRENT_TIMESTAMP and respects the database timezone
            update_data = {}
            changes = []

            # Handle status changes
            if 'status' in ticket_data and ticket_data['status'] != existing_ticket['status']:
                valid_statuses = ['nuevo', 'asignado', 'en_proceso', 'espera_cliente', 'resuelto', 'cerrado', 'cancelado', 'pendiente_aprobacion', 'reabierto']
                if ticket_data['status'] not in valid_statuses:
                    return {'success': False, 'errors': {'status': 'Invalid status'}}

                update_data['status'] = ticket_data['status']
                changes.append(f"Estado cambiado de '{existing_ticket['status']}' a '{ticket_data['status']}'")

                # Handle status-specific updates
                if ticket_data['status'] == 'resuelto':
                    update_data['resolved_at'] = datetime.utcnow()
                    # Require resolution notes when resolving
                    if 'resolution_notes' not in ticket_data or not ticket_data['resolution_notes']:
                        return {'success': False, 'errors': {'resolution_notes': 'Se requieren notas de resolución'}}

                    # HISTORIAL REAL: Crear entrada en tabla de resoluciones
                    resolution_text = ticket_data['resolution_notes'].strip()

                    # Insertar en historial de resoluciones
                    try:
                        resolution_data = {
                            'ticket_id': ticket_id,
                            'resolution_notes': resolution_text,
                            'resolved_by': updated_by,
                            'resolved_at': datetime.utcnow(),
                            'created_at': datetime.utcnow()
                        }

                        result = self.db.execute_insert('ticket_resolutions', resolution_data)
                        if result:
                            self.logger.info(f"Resolution added to history for ticket {ticket_id}")
                        else:
                            self.logger.error(f"Failed to insert resolution for ticket {ticket_id}")
                    except Exception as e:
                        self.logger.error(f"Error adding resolution to history: {e}")
                        # Continuar sin fallar el proceso principal

                    # NO actualizar resolution_notes - Solo usar historial
                    # update_data['resolution_notes'] = resolution_text  # COMENTADO PARA MANTENER HISTORIAL

                    # Check if auto-close is enabled
                    auto_close_enabled = self._get_system_config('auto_close_resolved_tickets', 'false').lower() == 'true'
                    if auto_close_enabled:
                        # Automatically close the ticket
                        update_data['status'] = 'cerrado'
                        update_data['closed_at'] = datetime.utcnow()
                        changes.append("Ticket cerrado automáticamente tras resolución")
                        self.logger.info(f"Ticket {ticket_id} auto-closed after resolution")
                elif ticket_data['status'] == 'cerrado':
                    update_data['closed_at'] = datetime.utcnow()
                elif ticket_data['status'] == 'reabierto':
                    # Clear resolution data when reopening
                    update_data['resolved_at'] = None
                    update_data['closed_at'] = None
                    # Keep resolution_notes for reference but add reopening note
                    if existing_ticket.get('resolution_notes'):
                        update_data['resolution_notes'] = existing_ticket['resolution_notes'] + '\n\n[TICKET REABIERTO]'

            # Handle assignment changes
            if 'assigned_to' in ticket_data:
                if ticket_data['assigned_to'] != existing_ticket['assigned_to']:
                    if ticket_data['assigned_to']:
                        # Validate assignee exists
                        assignee = self.db.execute_query(
                            "SELECT user_id, name FROM users WHERE user_id = %s AND is_active = true",
                            (ticket_data['assigned_to'],),
                            fetch='one'
                        )
                        if not assignee:
                            return {'success': False, 'errors': {'assigned_to': 'Invalid assignee'}}

                        update_data['assigned_to'] = ticket_data['assigned_to']
                        update_data['assigned_at'] = datetime.utcnow()
                        if existing_ticket['status'] == 'nuevo':
                            update_data['status'] = 'en_proceso'
                        changes.append(f"Asignado a {assignee['name']}")
                    else:
                        update_data['assigned_to'] = None
                        update_data['assigned_at'] = None
                        changes.append("Asignación removida")

            # Handle other updatable fields
            updatable_fields = ['subject', 'description', 'priority', 'category_id', 'affected_person', 'affected_person_contact', 'additional_emails']
            for field in updatable_fields:
                if field in ticket_data and ticket_data[field] != existing_ticket.get(field):
                    if field in ['subject', 'description', 'affected_person', 'affected_person_contact']:
                        update_data[field] = ticket_data[field].strip() if ticket_data[field] else None
                    elif field == 'priority':
                        valid_priorities = ['baja', 'media', 'alta', 'critica']
                        if ticket_data[field] not in valid_priorities:
                            return {'success': False, 'errors': {'priority': 'Invalid priority'}}
                        update_data[field] = ticket_data[field]
                    else:
                        update_data[field] = ticket_data[field]

                    changes.append(f"{field} actualizado")

            # Update ticket
            if len(update_data) > 0:  # Has actual changes to make
                rows_updated = self.db.execute_update(
                    'tickets',
                    update_data,
                    'ticket_id = %s',
                    (ticket_id,)
                )

                if rows_updated > 0:
                    # Create activity log for changes
                    if changes:
                        self._create_activity_log(
                            ticket_id,
                            updated_by,
                            'updated',
                            '; '.join(changes)
                        )

                    # Get updated ticket
                    updated_ticket = self.get_ticket_by_id(ticket_id)
                    self.logger.info(f"Ticket updated successfully: {updated_ticket['ticket_number']}")

                    # Send notification for ticket update
                    try:
                        from modules.notifications.service import notifications_service

                        # Check if this is a resolution
                        if 'resolution_notes' in ticket_data and ticket_data['resolution_notes']:
                            notifications_service.send_ticket_notification('ticket_resolved', ticket_id)
                        elif 'status' in ticket_data and ticket_data['status'] == 'reabierto':
                            # Send specific notification for ticket reopening
                            notifications_service.send_ticket_notification('ticket_reopened', ticket_id)
                        elif 'status' in ticket_data:
                            notifications_service.send_ticket_notification('ticket_status_changed', ticket_id)
                        else:
                            notifications_service.send_ticket_notification('ticket_status_changed', ticket_id)
                    except Exception as e:
                        self.logger.warning(f"Failed to send ticket update notification: {e}")

                    return {'success': True, 'ticket': updated_ticket}
                else:
                    return {'success': False, 'errors': {'general': 'Failed to update ticket'}}
            else:
                return {'success': True, 'ticket': existing_ticket, 'message': 'No changes detected'}

        except Exception as e:
            self.logger.error(f"Error updating ticket {ticket_id}: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}

    def assign_ticket(self, ticket_id: str, assigned_to: str, assigned_by: str) -> Dict[str, Any]:
        """Assign ticket to a technician"""
        try:
            # Validate ticket exists
            ticket = self.get_ticket_by_id(ticket_id)
            if not ticket:
                return {'success': False, 'errors': {'ticket_id': 'Ticket not found'}}

            # Validate assignee
            assignee = self.db.execute_query(
                "SELECT user_id, name, role FROM users WHERE user_id = %s AND is_active = true",
                (assigned_to,),
                fetch='one'
            )
            if not assignee:
                return {'success': False, 'errors': {'assigned_to': 'Invalid assignee'}}

            # Check if assignee can handle tickets
            if assignee['role'] not in ['superadmin', 'admin', 'technician']:
                return {'success': False, 'errors': {'assigned_to': 'User cannot be assigned tickets'}}

            # Update ticket assignment
            update_data = {
                'assigned_to': assigned_to,
                'assigned_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }

            # Update status if currently open
            if ticket['status'] == 'nuevo':
                update_data['status'] = 'en_proceso'

            rows_updated = self.db.execute_update(
                'tickets',
                update_data,
                'ticket_id = %s',
                (ticket_id,)
            )

            if rows_updated > 0:
                # Create activity log
                self._create_activity_log(
                    ticket_id,
                    assigned_by,
                    'assigned',
                    f"Ticket asignado a {assignee['name']}"
                )

                # Send notification for ticket assignment
                try:
                    from modules.notifications.service import notifications_service
                    notifications_service.send_ticket_notification('ticket_assigned', ticket_id)
                except Exception as e:
                    self.logger.warning(f"Failed to send ticket assignment notification: {e}")

                self.logger.info(f"Ticket {ticket['ticket_number']} assigned to {assignee['name']}")
                return {'success': True, 'message': f"Ticket assigned to {assignee['name']}"}
            else:
                return {'success': False, 'errors': {'general': 'Failed to assign ticket'}}

        except Exception as e:
            self.logger.error(f"Error assigning ticket {ticket_id}: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}

    def add_comment(self, ticket_id: str, comment_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Add comment to ticket"""
        try:
            # Validate ticket exists
            ticket = self.get_ticket_by_id(ticket_id)
            if not ticket:
                return {'success': False, 'errors': {'ticket_id': 'Ticket not found'}}

            # Validate comment data
            if not comment_data.get('content') or not comment_data['content'].strip():
                return {'success': False, 'errors': {'content': 'Comment content is required'}}

            # Prepare comment data
            new_comment_data = {
                'comment_id': str(uuid.uuid4()),
                'ticket_id': ticket_id,
                'user_id': created_by,
                'comment_text': comment_data['content'].strip(),
                'is_internal': comment_data.get('is_internal', False),
                'is_email_reply': comment_data.get('is_email_reply', False)
                # Note: created_at and updated_at will use DEFAULT CURRENT_TIMESTAMP from PostgreSQL
                # which respects the database timezone (America/Mexico_City)
            }

            # Insert comment
            result = self.db.execute_insert(
                'ticket_comments',
                new_comment_data,
                returning='comment_id, comment_text, is_internal, created_at'
            )

            if result:
                # LÓGICA AUTOMÁTICA: Si ticket está en "espera_cliente" y cliente comenta → reabrir
                # Obtener info del usuario que comenta
                user_info = self.db.execute_query(
                    'SELECT role FROM users WHERE user_id = %s',
                    (created_by,),
                    fetch='one'
                )
                is_client_user = user_info and user_info.get('role') in ['client_admin', 'solicitante']

                update_data = {'updated_at': datetime.utcnow()}

                if (ticket['status'] == 'espera_cliente' and
                    is_client_user and
                    not new_comment_data['is_internal']):

                    # Reabrir automáticamente el ticket
                    update_data['status'] = 'reabierto'

                    # Log de actividad para la reapertura automática
                    self._create_activity_log(
                        ticket_id,
                        created_by,
                        'auto_reopened',
                        f"Ticket reabierto automáticamente por respuesta del cliente"
                    )

                    self.logger.info(f"Ticket {ticket['ticket_number']} automatically reopened by client response")

                # Update ticket
                self.db.execute_update(
                    'tickets',
                    update_data,
                    'ticket_id = %s',
                    (ticket_id,)
                )

                # Create activity log for comment
                comment_type = "nota interna" if new_comment_data['is_internal'] else "comentario"
                self._create_activity_log(
                    ticket_id,
                    created_by,
                    'commented',
                    f"Agregó {comment_type}"
                )

                # Send notifications for ticket comment and potential reopening
                try:
                    from modules.notifications.service import notifications_service

                    # Check if ticket was automatically reopened
                    was_reopened = (ticket['status'] == 'espera_cliente' and
                                  is_client_user and
                                  not new_comment_data['is_internal'])

                    if was_reopened:
                        # Send ticket reopened notification instead of comment notification
                        # This provides better context about what happened
                        notifications_service.send_ticket_notification('ticket_reopened', ticket_id)
                        self.logger.info(f"Sent ticket reopened notification for {ticket['ticket_number']}")
                    else:
                        # Send regular comment notification
                        notifications_service.send_ticket_notification('ticket_commented', ticket_id, comment_id=result['comment_id'])

                except Exception as e:
                    self.logger.warning(f"Failed to send ticket notification: {e}")

                self.logger.info(f"Comment added to ticket {ticket['ticket_number']}")
                return {'success': True, 'comment': result}
            else:
                return {'success': False, 'errors': {'general': 'Failed to add comment'}}

        except Exception as e:
            self.logger.error(f"Error adding comment to ticket {ticket_id}: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}

    def bulk_actions(self, ticket_ids: list, action: str, action_data: dict, current_user_id: str, user_role: str) -> Dict[str, Any]:
        """Perform bulk actions on multiple tickets"""
        try:
            self.logger.info(f"🔧 SERVICE BULK_ACTIONS: Starting with {len(ticket_ids)} tickets, action: {action}")

            # Validate all ticket IDs exist and user has access
            accessible_tickets = []
            inaccessible_tickets = []

            for ticket_id in ticket_ids:
                # Validate UUID format
                if not self.db.validate_uuid(ticket_id):
                    inaccessible_tickets.append({'ticket_id': ticket_id, 'reason': 'Invalid UUID format'})
                    continue

                # Check if ticket exists and user has access (using RLS)
                ticket = self.db.execute_query(
                    "SELECT ticket_id, ticket_number, status, client_id FROM tickets WHERE ticket_id = %s",
                    (ticket_id,),
                    fetch='one'
                )

                if ticket:
                    accessible_tickets.append(ticket)
                else:
                    inaccessible_tickets.append({'ticket_id': ticket_id, 'reason': 'Ticket not found or access denied'})

            if not accessible_tickets:
                return {'success': False, 'errors': {'general': 'No accessible tickets found'}}

            # Perform the bulk action
            successful_updates = []
            failed_updates = []

            for ticket in accessible_tickets:
                try:
                    if action == 'update_status':
                        result = self._bulk_update_status(ticket, action_data, current_user_id, user_role)
                    elif action == 'assign':
                        result = self._bulk_assign(ticket, action_data, current_user_id)
                    elif action == 'update_priority':
                        result = self._bulk_update_priority(ticket, action_data, current_user_id)
                    elif action == 'delete':
                        result = self._bulk_delete(ticket, current_user_id, user_role)
                    else:
                        result = {'success': False, 'error': 'Invalid action'}

                    if result['success']:
                        successful_updates.append({
                            'ticket_id': ticket['ticket_id'],
                            'ticket_number': ticket['ticket_number'],
                            'action': action
                        })
                    else:
                        failed_updates.append({
                            'ticket_id': ticket['ticket_id'],
                            'ticket_number': ticket['ticket_number'],
                            'error': result.get('error', 'Unknown error')
                        })

                except Exception as e:
                    failed_updates.append({
                        'ticket_id': ticket['ticket_id'],
                        'ticket_number': ticket['ticket_number'],
                        'error': str(e)
                    })

            # Prepare response
            response = {
                'success': len(successful_updates) > 0,
                'total_requested': len(ticket_ids),
                'successful_updates': len(successful_updates),
                'failed_updates': len(failed_updates),
                'inaccessible_tickets': len(inaccessible_tickets),
                'details': {
                    'successful': successful_updates,
                    'failed': failed_updates,
                    'inaccessible': inaccessible_tickets
                }
            }

            self.logger.info(f"Bulk action {action} completed: {len(successful_updates)} successful, {len(failed_updates)} failed")
            return response

        except Exception as e:
            self.logger.error(f"🔧 SERVICE BULK_ACTIONS: Exception occurred: {e}")
            self.logger.error(f"🔧 SERVICE BULK_ACTIONS: Exception type: {type(e)}")
            import traceback
            self.logger.error(f"🔧 SERVICE BULK_ACTIONS: Traceback: {traceback.format_exc()}")
            return {'success': False, 'errors': {'general': f'Internal server error: {str(e)}'}}

    def _bulk_update_status(self, ticket: dict, action_data: dict, current_user_id: str, user_role: str) -> Dict[str, Any]:
        """Update ticket status in bulk operation"""
        try:
            new_status = action_data.get('status')
            if not new_status:
                return {'success': False, 'error': 'Status is required'}

            # Validate status
            valid_statuses = ['nuevo', 'asignado', 'en_proceso', 'espera_cliente', 'resuelto', 'cerrado', 'cancelado', 'pendiente_aprobacion', 'reabierto']
            if new_status not in valid_statuses:
                return {'success': False, 'error': 'Invalid status'}

            # Check permissions for client users
            if user_role in ['client_admin', 'solicitante']:
                if new_status not in ['cerrado', 'reabierto']:
                    return {'success': False, 'error': 'Clients can only close or reopen tickets'}

            # For resolution, require resolution notes
            if new_status == 'resuelto':
                resolution_notes = action_data.get('resolution_notes')
                if not resolution_notes or not resolution_notes.strip():
                    return {'success': False, 'error': 'Resolution notes are required when resolving tickets'}

            # For closing, check if ticket is resolved first
            if new_status == 'cerrado':
                if ticket['status'] not in ['resuelto']:
                    return {'success': False, 'error': 'Tickets must be resolved before closing'}

            # Update ticket
            update_data = {
                'status': new_status,
                'updated_at': datetime.utcnow()
            }

            # Set resolution data if resolving
            if new_status == 'resuelto':
                update_data['resolved_at'] = datetime.utcnow()
                update_data['resolution'] = action_data.get('resolution_notes', '').strip()
            elif new_status == 'cerrado':
                update_data['closed_at'] = datetime.utcnow()

            # Build dynamic query based on what fields we're updating
            set_clauses = ['status = %s', 'updated_at = %s']
            params = [update_data['status'], update_data['updated_at']]

            if 'resolved_at' in update_data:
                set_clauses.append('resolved_at = %s')
                params.append(update_data['resolved_at'])

            if 'resolution' in update_data:
                set_clauses.append('resolution_notes = %s')
                params.append(update_data['resolution'])

            if 'closed_at' in update_data:
                set_clauses.append('closed_at = %s')
                params.append(update_data['closed_at'])

            params.append(ticket['ticket_id'])

            query = f"UPDATE tickets SET {', '.join(set_clauses)} WHERE ticket_id = %s"
            result = self.db.execute_query(query, params, fetch='none')

            # Log activity
            activity_desc = f"Estado cambiado a '{new_status}' (acción masiva)"
            if new_status == 'resuelto' and 'resolution' in update_data:
                activity_desc += f" - Resolución: {update_data['resolution'][:100]}..."

            self._create_activity_log(
                ticket['ticket_id'],
                current_user_id,
                'status_changed',
                activity_desc
            )

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _bulk_assign(self, ticket: dict, action_data: dict, current_user_id: str) -> Dict[str, Any]:
        """Assign ticket in bulk operation"""
        try:
            assigned_to = action_data.get('assigned_to')
            if not assigned_to:
                return {'success': False, 'error': 'assigned_to is required'}

            # Validate assignee exists and can handle tickets
            assignee = self.db.execute_query(
                "SELECT user_id, name, role FROM users WHERE user_id = %s AND is_active = true",
                (assigned_to,),
                fetch='one'
            )

            if not assignee:
                return {'success': False, 'error': 'Invalid assignee'}

            if assignee['role'] not in ['superadmin', 'admin', 'technician']:
                return {'success': False, 'error': 'User cannot be assigned tickets'}

            # Update ticket
            update_data = {
                'assigned_to': assigned_to,
                'status': 'en_proceso',  # Change to valid status
                'updated_at': datetime.utcnow()
            }

            result = self.db.execute_query(
                "UPDATE tickets SET assigned_to = %s, status = %s, updated_at = %s WHERE ticket_id = %s",
                (update_data['assigned_to'], update_data['status'],
                 update_data['updated_at'], ticket['ticket_id']),
                fetch='none'
            )

            # Log activity
            self._create_activity_log(
                ticket['ticket_id'],
                current_user_id,
                'assigned',
                f"Asignado a {assignee['name']} (acción masiva)"
            )

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _bulk_update_priority(self, ticket: dict, action_data: dict, current_user_id: str) -> Dict[str, Any]:
        """Update ticket priority in bulk operation"""
        try:
            new_priority = action_data.get('priority')
            if not new_priority:
                return {'success': False, 'error': 'Priority is required'}

            # Validate priority
            valid_priorities = ['baja', 'media', 'alta', 'critica']
            if new_priority not in valid_priorities:
                return {'success': False, 'error': 'Invalid priority'}

            # Update ticket
            result = self.db.execute_query(
                "UPDATE tickets SET priority = %s, updated_at = %s WHERE ticket_id = %s",
                (new_priority, datetime.utcnow(), ticket['ticket_id']),
                fetch='none'
            )

            # Log activity
            self._create_activity_log(
                ticket['ticket_id'],
                current_user_id,
                'priority_changed',
                f"Prioridad cambiada a '{new_priority}' (acción masiva)"
            )

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _bulk_delete(self, ticket: dict, current_user_id: str, user_role: str) -> Dict[str, Any]:
        """Delete ticket in bulk operation (only superadmin/admin)"""
        try:
            # Double-check permissions
            if user_role not in ['superadmin', 'admin']:
                return {'success': False, 'error': 'Insufficient permissions to delete tickets'}

            # Cannot delete closed tickets (following Zendesk pattern)
            if ticket['status'] == 'cerrado':
                return {'success': False, 'error': 'Cannot delete closed tickets'}

            # Log activity before deletion
            self._create_activity_log(
                ticket['ticket_id'],
                current_user_id,
                'deleted',
                f"Ticket eliminado (acción masiva)"
            )

            # Delete related records first to avoid foreign key constraint violations
            # Delete in order to respect dependencies

            # Delete from notification_tracking
            self.db.execute_query(
                "DELETE FROM notification_tracking WHERE ticket_id = %s",
                (ticket['ticket_id'],),
                fetch='none'
            )

            # Delete from notification_queue
            self.db.execute_query(
                "DELETE FROM notification_queue WHERE ticket_id = %s",
                (ticket['ticket_id'],),
                fetch='none'
            )

            # Delete from email_routing_log
            self.db.execute_query(
                "DELETE FROM email_routing_log WHERE created_ticket_id = %s",
                (ticket['ticket_id'],),
                fetch='none'
            )

            # Delete from email_processing_log
            self.db.execute_query(
                "DELETE FROM email_processing_log WHERE ticket_id = %s",
                (ticket['ticket_id'],),
                fetch='none'
            )

            # Delete from email_queue
            self.db.execute_query(
                "DELETE FROM email_queue WHERE ticket_id = %s",
                (ticket['ticket_id'],),
                fetch='none'
            )

            # Delete from sla_tracking
            self.db.execute_query(
                "DELETE FROM sla_tracking WHERE ticket_id = %s",
                (ticket['ticket_id'],),
                fetch='none'
            )

            # Delete from sla_compliance
            self.db.execute_query(
                "DELETE FROM sla_compliance WHERE ticket_id = %s",
                (ticket['ticket_id'],),
                fetch='none'
            )

            # Delete from ticket_resolutions
            self.db.execute_query(
                "DELETE FROM ticket_resolutions WHERE ticket_id = %s",
                (ticket['ticket_id'],),
                fetch='none'
            )

            # Delete from ticket_attachments
            self.db.execute_query(
                "DELETE FROM ticket_attachments WHERE ticket_id = %s",
                (ticket['ticket_id'],),
                fetch='none'
            )

            # Delete from file_attachments
            self.db.execute_query(
                "DELETE FROM file_attachments WHERE ticket_id = %s",
                (ticket['ticket_id'],),
                fetch='none'
            )

            # Delete from ticket_activities
            self.db.execute_query(
                "DELETE FROM ticket_activities WHERE ticket_id = %s",
                (ticket['ticket_id'],),
                fetch='none'
            )

            # Delete from ticket_comments
            self.db.execute_query(
                "DELETE FROM ticket_comments WHERE ticket_id = %s",
                (ticket['ticket_id'],),
                fetch='none'
            )

            # Finally, delete the ticket itself
            result = self.db.execute_query(
                "DELETE FROM tickets WHERE ticket_id = %s",
                (ticket['ticket_id'],),
                fetch='none'
            )

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}
