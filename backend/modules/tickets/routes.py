#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Tickets Module Routes
Ticket management endpoints
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils.security import require_role
from datetime import datetime
import uuid
import logging

# Configure detailed logging for debugging
logging.basicConfig(
    filename='C:/temp/backend_tickets.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='w'  # Overwrite on each restart
)

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/', methods=['GET'])
@jwt_required()
def get_tickets():
    """Get all tickets"""
    try:
        tickets = current_app.db_manager.execute_query(
            "SELECT * FROM tickets ORDER BY created_at DESC LIMIT 50"
        )
        
        # Format tickets data
        formatted_tickets = [current_app.response_manager.format_ticket_data(ticket) for ticket in tickets]
        
        return current_app.response_manager.success(formatted_tickets)
        
    except Exception as e:
        current_app.logger.error(f"Get tickets error: {e}")
        return current_app.response_manager.server_error('Failed to get tickets')

@tickets_bp.route('/<ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    """Get specific ticket"""
    try:
        ticket = current_app.db_manager.execute_query(
            "SELECT * FROM tickets WHERE ticket_id = %s",
            (ticket_id,),
            fetch='one'
        )
        
        if not ticket:
            return current_app.response_manager.not_found('Ticket')
        
        formatted_ticket = current_app.response_manager.format_ticket_data(ticket)
        return current_app.response_manager.success(formatted_ticket)
        
    except Exception as e:
        current_app.logger.error(f"Get ticket error: {e}")
        return current_app.response_manager.server_error('Failed to get ticket')

@tickets_bp.route('/', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician', 'client_admin', 'solicitante'])
def create_ticket():
    """Create a new ticket"""
    logging.info("--- Petición recibida en el endpoint /api/tickets ---")

    try:
        # Get JSON data from request
        data = request.get_json()

        # CRITICAL LOGGING: Log exactly what we receive
        if data:
            logging.debug(f"Payload (cuerpo de la petición) recibido: {data}")
        else:
            logging.warning("La petición llegó sin un cuerpo JSON.")
            return current_app.response_manager.bad_request('No data provided')

        # Log user info
        current_user_id = get_jwt_identity()
        current_user = get_jwt()
        user_role = current_user.get('role')
        user_client_id = current_user.get('client_id')
        logging.info(f"Usuario autenticado: {current_user_id}, Role: {user_role}")

        # ✅ FIX: Set RLS context for database queries
        current_app.db_manager.set_rls_context(
            user_id=current_user_id,
            user_role=user_role,
            client_id=user_client_id
        )

        if not data:
            logging.error("Error: No se proporcionaron datos")
            return current_app.response_manager.bad_request('No data provided')

        # Validate required fields
        required_fields = ['client_id', 'site_id', 'subject', 'description', 'affected_person', 'affected_person_contact', 'priority']
        for field in required_fields:
            if field not in data or not data[field]:
                return current_app.response_manager.bad_request(f'{field} is required')

        # Validate client exists and is active
        client = current_app.db_manager.execute_query(
            "SELECT client_id, name FROM clients WHERE client_id = %s AND is_active = true",
            (data['client_id'],),
            fetch='one'
        )
        if not client:
            return current_app.response_manager.bad_request('Invalid or inactive client')

        # Validate site exists and belongs to client
        site = current_app.db_manager.execute_query(
            "SELECT site_id, name FROM sites WHERE site_id = %s AND client_id = %s AND is_active = true",
            (data['site_id'], data['client_id']),
            fetch='one'
        )
        if not site:
            return current_app.response_manager.bad_request('Invalid site or site does not belong to client')

        # Validate priority
        valid_priorities = ['baja', 'media', 'alta', 'critica']
        if data['priority'] not in valid_priorities:
            return current_app.response_manager.bad_request('Invalid priority level')

        # Check access permissions for client users
        claims = get_jwt()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')
        current_user_id = get_jwt_identity()

        if current_user_role in ['client_admin', 'solicitante']:
            if data['client_id'] != current_user_client_id:
                return current_app.response_manager.forbidden('Access denied')

        # Generate simple consecutive ticket number (TKT-0001, TKT-0002, etc.)
        sequence_query = """
        SELECT COALESCE(MAX(
            CASE
                WHEN ticket_number ~ '^TKT-[0-9]{4}$'
                THEN CAST(SUBSTRING(ticket_number FROM 5) AS INTEGER)
                ELSE 0
            END
        ), 0) + 1 as next_seq
        FROM tickets
        """

        result = current_app.db_manager.execute_query(
            sequence_query,
            fetch='one'
        )

        next_seq = result['next_seq'] if result else 1
        ticket_number = f"TKT-{next_seq:04d}"

        # DEBUG: Log ticket number generation
        logging.info(f"Generated ticket number: {ticket_number}")

        # Helper function to convert empty strings to None
        def clean_field(value):
            if value is None:
                return None
            if isinstance(value, str):
                cleaned = value.strip()
                return None if cleaned == '' else cleaned
            return value

        # Validate category_id exists if provided (now using categories table)
        category_id = clean_field(data.get('category_id'))
        if category_id:
            category_check = current_app.db_manager.execute_query(
                'SELECT category_id FROM categories WHERE category_id = %s AND is_active = true',
                (category_id,),
                fetch='one'
            )
            if not category_check:
                logging.warning(f"Category ID {category_id} not found, setting to NULL")
                category_id = None

        # Prepare ticket data - handle empty strings properly for optional fields
        ticket_data = {
            'ticket_id': str(uuid.uuid4()),
            'ticket_number': ticket_number,
            'client_id': data['client_id'],
            'site_id': data['site_id'],
            'asset_id': clean_field(data.get('asset_id')),
            'created_by': current_user_id,
            'assigned_to': clean_field(data.get('assigned_to')),
            'subject': data['subject'].strip(),
            'description': data['description'].strip(),
            'affected_person': data['affected_person'].strip(),
            'affected_person_contact': data['affected_person_contact'].strip(),
            'additional_emails': data.get('additional_emails', []) if data.get('additional_emails') else [],
            'priority': data['priority'],
            'category_id': category_id,  # Use validated category_id
            'status': 'nuevo',
            'channel': data.get('channel', 'portal'),
            'is_email_originated': data.get('is_email_originated', False),
            'from_email': clean_field(data.get('from_email')),
            'email_message_id': clean_field(data.get('email_message_id')),
            'email_thread_id': clean_field(data.get('email_thread_id')),
            'approval_status': 'pendiente',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Auto-assign if assigned_to is provided and not None
        if ticket_data['assigned_to'] is not None:
            ticket_data['status'] = 'asignado'
            ticket_data['assigned_at'] = datetime.utcnow()

        # DEBUG: Log ticket data before insert
        logging.info(f"About to insert ticket data: {ticket_data}")

        # Insert ticket
        try:
            logging.info("Attempting database insert...")
            result = current_app.db_manager.execute_insert(
                'tickets',
                ticket_data,
                returning='ticket_id, ticket_number, subject, status, created_at'
            )
            logging.info(f"Insert successful: {result}")
        except Exception as insert_error:
            logging.error(f"Insert failed: {insert_error}")
            raise insert_error

        if result:
            current_app.logger.info(f"Ticket created successfully: {result['ticket_number']}")
            formatted_ticket = current_app.response_manager.format_ticket_data(result)
            return current_app.response_manager.success(formatted_ticket, "Ticket created successfully", 201)
        else:
            return current_app.response_manager.server_error('Failed to create ticket')

    except Exception as e:
        # CRUCIAL! Esto capturará CUALQUIER error que ocurra en el bloque try
        # y lo escribirá en tu archivo de log, incluyendo la traza completa.
        logging.error("Ha ocurrido una excepción no controlada al crear el ticket.", exc_info=True)

        # También log el error específico
        logging.error(f"Error específico: {str(e)}")

        # Responde al cliente con un error 500 genérico
        return current_app.response_manager.server_error('Failed to create ticket')

@tickets_bp.route('/<ticket_id>', methods=['PUT'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician'])
def update_ticket(ticket_id):
    """Update an existing ticket"""
    try:
        from .service import TicketService

        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        current_user_id = get_jwt_identity()
        ticket_service = TicketService(current_app.db_manager, current_app.auth_manager)

        result = ticket_service.update_ticket(ticket_id, data, current_user_id)

        if result['success']:
            return current_app.response_manager.success(result['ticket'], 'Ticket updated successfully')
        else:
            return current_app.response_manager.error('Failed to update ticket', 400, details=result.get('errors'))

    except Exception as e:
        current_app.logger.error(f"Update ticket error: {e}")
        return current_app.response_manager.server_error('Failed to update ticket')

@tickets_bp.route('/<ticket_id>/assign', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician'])
def assign_ticket(ticket_id):
    """Assign ticket to a technician"""
    try:
        from .service import TicketService

        data = request.get_json()
        if not data or 'assigned_to' not in data:
            return current_app.response_manager.bad_request('assigned_to is required')

        current_user_id = get_jwt_identity()
        ticket_service = TicketService(current_app.db_manager, current_app.auth_manager)

        result = ticket_service.assign_ticket(ticket_id, data['assigned_to'], current_user_id)

        if result['success']:
            return current_app.response_manager.success({'message': result['message']}, 'Ticket assigned successfully')
        else:
            return current_app.response_manager.error('Failed to assign ticket', 400, details=result.get('errors'))

    except Exception as e:
        current_app.logger.error(f"Assign ticket error: {e}")
        return current_app.response_manager.server_error('Failed to assign ticket')

@tickets_bp.route('/<ticket_id>/comments', methods=['GET'])
@jwt_required()
def get_ticket_comments(ticket_id):
    """Get all comments for a ticket"""
    try:
        # Validate ticket ID
        if not current_app.db_manager.validate_uuid(ticket_id):
            return current_app.response_manager.bad_request('Invalid ticket ID format')

        # Check if ticket exists and user has access
        ticket = current_app.db_manager.execute_query(
            "SELECT ticket_id, client_id FROM tickets WHERE ticket_id = %s",
            (ticket_id,),
            fetch='one'
        )

        if not ticket:
            return current_app.response_manager.not_found('Ticket')

        # Check access permissions
        claims = get_jwt()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')

        if current_user_role in ['client_admin', 'solicitante']:
            if ticket['client_id'] != current_user_client_id:
                return current_app.response_manager.forbidden('Access denied')

        # Get comments
        query = """
        SELECT tc.comment_id, tc.ticket_id, tc.user_id, tc.comment_text as content,
               tc.is_internal, tc.is_email_reply, tc.email_message_id,
               tc.created_at, tc.updated_at,
               u.name as user_name, u.role as user_role
        FROM ticket_comments tc
        LEFT JOIN users u ON tc.user_id = u.user_id
        WHERE tc.ticket_id = %s
        ORDER BY tc.created_at ASC
        """

        comments = current_app.db_manager.execute_query(query, (ticket_id,))

        # Filter internal comments for non-technician users
        if current_user_role in ['client_admin', 'solicitante']:
            comments = [c for c in comments if not c['is_internal']]

        formatted_comments = [current_app.response_manager.format_comment_data(comment) for comment in (comments or [])]

        return current_app.response_manager.success(formatted_comments)

    except Exception as e:
        current_app.logger.error(f"Get ticket comments error: {e}")
        return current_app.response_manager.server_error('Failed to get ticket comments')

@tickets_bp.route('/<ticket_id>/comments', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician', 'client_admin', 'solicitante'])
def add_ticket_comment(ticket_id):
    """Add a comment to a ticket"""
    try:
        from .service import TicketService

        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        current_user_id = get_jwt_identity()
        ticket_service = TicketService(current_app.db_manager, current_app.auth_manager)

        result = ticket_service.add_comment(ticket_id, data, current_user_id)

        if result['success']:
            return current_app.response_manager.success(result['comment'], 'Comment added successfully', 201)
        else:
            return current_app.response_manager.error('Failed to add comment', 400, details=result.get('errors'))

    except Exception as e:
        current_app.logger.error(f"Add comment error: {e}")
        return current_app.response_manager.server_error('Failed to add comment')

@tickets_bp.route('/<ticket_id>/activities', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician'])
def get_ticket_activities(ticket_id):
    """Get activity log for a ticket"""
    try:
        # Validate ticket ID
        if not current_app.db_manager.validate_uuid(ticket_id):
            return current_app.response_manager.bad_request('Invalid ticket ID format')

        # Check if ticket exists
        ticket = current_app.db_manager.execute_query(
            "SELECT ticket_id FROM tickets WHERE ticket_id = %s",
            (ticket_id,),
            fetch='one'
        )

        if not ticket:
            return current_app.response_manager.not_found('Ticket')

        # Get activities
        query = """
        SELECT ta.activity_id, ta.ticket_id, ta.user_id, ta.action,
               ta.description, ta.created_at,
               u.name as user_name, u.role as user_role
        FROM ticket_activities ta
        LEFT JOIN users u ON ta.user_id = u.user_id
        WHERE ta.ticket_id = %s
        ORDER BY ta.created_at DESC
        """

        activities = current_app.db_manager.execute_query(query, (ticket_id,))
        formatted_activities = [current_app.response_manager.format_activity_data(activity) for activity in (activities or [])]

        return current_app.response_manager.success(formatted_activities)

    except Exception as e:
        current_app.logger.error(f"Get ticket activities error: {e}")
        return current_app.response_manager.server_error('Failed to get ticket activities')

@tickets_bp.route('/stats', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician'])
def get_ticket_stats():
    """Get ticket statistics"""
    try:
        claims = get_jwt()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')

        # Build base query with RLS considerations
        where_conditions = ["t.ticket_id IS NOT NULL"]
        params = []

        if current_user_role in ['client_admin', 'solicitante']:
            where_conditions.append("t.client_id = %s")
            params.append(current_user_client_id)

        where_clause = " AND ".join(where_conditions)

        # Get ticket statistics
        stats_query = f"""
        SELECT
            COUNT(*) as total_tickets,
            COUNT(CASE WHEN status = 'nuevo' THEN 1 END) as new_tickets,
            COUNT(CASE WHEN status = 'asignado' THEN 1 END) as assigned_tickets,
            COUNT(CASE WHEN status = 'en_proceso' THEN 1 END) as in_progress_tickets,
            COUNT(CASE WHEN status = 'espera_cliente' THEN 1 END) as waiting_customer_tickets,
            COUNT(CASE WHEN status = 'resuelto' THEN 1 END) as resolved_tickets,
            COUNT(CASE WHEN status = 'cerrado' THEN 1 END) as closed_tickets,
            COUNT(CASE WHEN priority = 'critica' THEN 1 END) as critical_tickets,
            COUNT(CASE WHEN priority = 'alta' THEN 1 END) as high_tickets,
            COUNT(CASE WHEN priority = 'media' THEN 1 END) as medium_tickets,
            COUNT(CASE WHEN priority = 'baja' THEN 1 END) as low_tickets,
            COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as tickets_last_24h,
            COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as tickets_last_week
        FROM tickets t
        WHERE {where_clause}
        """

        stats = current_app.db_manager.execute_query(stats_query, tuple(params), fetch='one')

        return current_app.response_manager.success(stats)

    except Exception as e:
        current_app.logger.error(f"Get ticket stats error: {e}")
        return current_app.response_manager.server_error('Failed to get ticket statistics')

@tickets_bp.route('/search', methods=['GET'])
@jwt_required()
def search_tickets():
    """Search tickets with filters"""
    try:
        from .service import TicketService

        # Get query parameters
        search = request.args.get('search', '')
        status = request.args.get('status')
        priority = request.args.get('priority')
        client_id = request.args.get('client_id')
        assigned_to = request.args.get('assigned_to')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)

        # Build filters
        filters = {}
        if search:
            filters['search'] = search
        if status:
            filters['status'] = status
        if priority:
            filters['priority'] = priority
        if client_id:
            filters['client_id'] = client_id
        if assigned_to:
            filters['assigned_to'] = assigned_to

        # Apply RLS for client users
        claims = get_jwt()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')

        if current_user_role in ['client_admin', 'solicitante']:
            filters['client_id'] = current_user_client_id

        ticket_service = TicketService(current_app.db_manager, current_app.auth_manager)
        result = ticket_service.get_all_tickets(page, per_page, filters)

        # Format tickets
        formatted_tickets = [current_app.response_manager.format_ticket_data(ticket) for ticket in result['tickets']]

        response_data = {
            'tickets': formatted_tickets,
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'total_pages': result['total_pages']
            }
        }

        return current_app.response_manager.success(response_data)

    except Exception as e:
        current_app.logger.error(f"Search tickets error: {e}")
        return current_app.response_manager.server_error('Failed to search tickets')

@tickets_bp.route('/<ticket_id>/status', methods=['PATCH'])
@jwt_required()
def update_ticket_status(ticket_id):
    """Update ticket status"""
    try:
        from .service import TicketService

        data = request.get_json()
        if not data or 'status' not in data:
            return current_app.response_manager.bad_request('status is required')

        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        new_status = data['status']

        # Validar permisos por estado
        if user_role in ['client_admin', 'solicitante']:
            # Clientes solo pueden cerrar y reabrir
            if new_status not in ['cerrado', 'reabierto']:
                return current_app.response_manager.forbidden('Clients can only close or reopen tickets')
        elif user_role in ['superadmin', 'technician']:
            # Técnicos pueden cambiar a cualquier estado
            pass
        else:
            return current_app.response_manager.forbidden('Insufficient permissions')

        ticket_service = TicketService(current_app.db_manager, current_app.auth_manager)

        # Update status and resolution notes if provided
        update_data = {'status': new_status}
        if 'resolution_notes' in data:
            update_data['resolution_notes'] = data['resolution_notes']

        result = ticket_service.update_ticket(ticket_id, update_data, current_user_id)

        if result['success']:
            return current_app.response_manager.success(result['ticket'], 'Ticket status updated successfully')
        else:
            return current_app.response_manager.error('Failed to update ticket status', 400, details=result.get('errors'))

    except Exception as e:
        current_app.logger.error(f"Update ticket status error: {e}")
        return current_app.response_manager.server_error('Failed to update ticket status')

@tickets_bp.route('/<ticket_id>/resolutions', methods=['GET'])
@jwt_required()
def get_ticket_resolutions(ticket_id):
    """Get ticket resolution history"""
    try:
        # Validate ticket ID
        if not current_app.db_manager.validate_uuid(ticket_id):
            return current_app.response_manager.bad_request('Invalid ticket ID format')

        # Check if ticket exists and user has access
        ticket = current_app.db_manager.execute_query(
            "SELECT ticket_id, client_id FROM tickets WHERE ticket_id = %s",
            (ticket_id,),
            fetch='one'
        )

        if not ticket:
            return current_app.response_manager.not_found('Ticket')

        # Check access permissions
        claims = get_jwt()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')

        if current_user_role in ['client_admin', 'solicitante']:
            if ticket['client_id'] != current_user_client_id:
                return current_app.response_manager.forbidden('Access denied')

        # Get resolution history
        query = """
        SELECT tr.resolution_id, tr.ticket_id, tr.resolution_notes,
               tr.resolved_by, tr.resolved_at, tr.created_at,
               u.name as resolved_by_name, u.role as resolved_by_role
        FROM ticket_resolutions tr
        LEFT JOIN users u ON tr.resolved_by = u.user_id
        WHERE tr.ticket_id = %s
        ORDER BY tr.resolved_at DESC
        """

        resolutions = current_app.db_manager.execute_query(query, (ticket_id,))

        # Format resolutions manually since format_resolution_data doesn't exist
        formatted_resolutions = []
        for resolution in (resolutions or []):
            formatted_resolutions.append({
                'resolution_id': str(resolution['resolution_id']),
                'ticket_id': str(resolution['ticket_id']),
                'resolution_notes': resolution['resolution_notes'],
                'resolved_by': str(resolution['resolved_by']),
                'resolved_by_name': resolution['resolved_by_name'],
                'resolved_by_role': resolution['resolved_by_role'],
                'resolved_at': resolution['resolved_at'].isoformat() if resolution['resolved_at'] else None,
                'created_at': resolution['created_at'].isoformat() if resolution['created_at'] else None
            })

        return current_app.response_manager.success(formatted_resolutions)

    except Exception as e:
        current_app.logger.error(f"Get ticket resolutions error: {e}")
        return current_app.response_manager.server_error('Failed to get ticket resolutions')
