#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Tickets Module Routes
Ticket management endpoints
"""

from flask import Blueprint, request, current_app, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils.security import require_role
from datetime import datetime
import uuid
import logging
import os
from .service import TicketService

# Configure detailed logging for debugging
import os
log_dir = os.environ.get('LOG_FOLDER', '/app/logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'backend_tickets.log')

logging.basicConfig(
    filename=log_file,
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
        # Import TicketService here to avoid circular imports
        from .service import TicketService

        # Use the service to get complete ticket data with joins
        ticket_service = TicketService(current_app.db_manager, current_app.auth_manager)
        ticket = ticket_service.get_ticket_by_id(ticket_id)

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
    print("🚨🚨🚨 CREATE_TICKET FUNCTION CALLED! 🚨🚨🚨", flush=True)
    logging.info("--- Petición recibida en el endpoint /api/tickets ---")

    current_user_id = None
    try:
        current_user_id = get_jwt_identity()
        print(f"🚨 Current user ID: {current_user_id}", flush=True)
    except Exception as e:
        print(f"🚨 ERROR getting current user: {e}", flush=True)

    try:
        # Handle both JSON and FormData (for file uploads)
        logging.info(f"🔍 Request content_type: {request.content_type}")
        logging.info(f"🔍 Request headers: {dict(request.headers)}")

        if request.content_type and 'multipart/form-data' in request.content_type:
            # FormData with files
            data = request.form.to_dict()
            files = request.files.getlist('attachments')
            logging.info(f"📋 FormData recibido: {data}")
            logging.info(f"📎 Archivos recibidos: {len(files)} archivos")
            for i, file in enumerate(files):
                logging.info(f"  Archivo {i}: {file.filename} ({file.content_type})")
        else:
            # Regular JSON
            data = request.get_json()
            files = []
            logging.info(f"📋 JSON recibido: {data}")
            logging.info(f"📎 No hay archivos (JSON request)")

        if not data:
            logging.warning("La petición llegó sin datos.")
            return current_app.response_manager.error('No data provided', 400)

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
            return current_app.response_manager.error('No data provided', 400)

        # Validate required fields - add affected_person_contact for TicketsService compatibility
        required_fields = ['client_id', 'site_id', 'subject', 'description', 'affected_person', 'priority']
        for field in required_fields:
            if field not in data or not data[field]:
                return current_app.response_manager.error(f'{field} is required', 400)

        # Map frontend fields to TicketsService expected fields
        # Frontend sends affected_person_phone, but TicketsService expects affected_person_contact
        # According to user requirements, affected_person_contact should be phone-only
        affected_person_phone = data.get('affected_person_phone', '').strip()
        affected_person_contact = data.get('affected_person_contact', '').strip()

        # Use phone if provided, otherwise use contact, otherwise use a default value
        if affected_person_phone:
            data['affected_person_contact'] = affected_person_phone
        elif affected_person_contact:
            data['affected_person_contact'] = affected_person_contact
        else:
            # TicketsService requires this field, so provide a default
            data['affected_person_contact'] = 'No especificado'

        # Validate client exists and is active
        client = current_app.db_manager.execute_query(
            "SELECT client_id, name FROM clients WHERE client_id = %s AND is_active = true",
            (data['client_id'],),
            fetch='one'
        )
        if not client:
            return current_app.response_manager.error('Invalid or inactive client', 400)

        # Validate site exists and belongs to client
        site = current_app.db_manager.execute_query(
            "SELECT site_id, name FROM sites WHERE site_id = %s AND client_id = %s AND is_active = true",
            (data['site_id'], data['client_id']),
            fetch='one'
        )
        if not site:
            return current_app.response_manager.error('Invalid site or site does not belong to client', 400)

        # Validate priority
        valid_priorities = ['baja', 'media', 'alta', 'critica']
        if data['priority'] not in valid_priorities:
            return current_app.response_manager.error('Invalid priority level', 400)

        # Check access permissions for client users
        claims = get_jwt()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')
        current_user_id = get_jwt_identity()

        if current_user_role in ['client_admin', 'solicitante']:
            if data['client_id'] != current_user_client_id:
                return current_app.response_manager.forbidden('Access denied')

        # Use TicketsService for proper ticket creation
        from modules.tickets.service import TicketService
        tickets_service = TicketService(current_app.db_manager, current_app.auth_manager)

        # Extract file attachments from request
        files = []
        current_app.logger.info(f"🔍 DEBUG: request.files keys: {list(request.files.keys())}")
        current_app.logger.info(f"🔍 DEBUG: request.form keys: {list(request.form.keys())}")

        if 'attachments' in request.files:
            files = request.files.getlist('attachments')
            current_app.logger.info(f"✅ Found {len(files)} attachments in request")
        else:
            current_app.logger.info("❌ No 'attachments' key found in request.files")

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

        # Prepare ticket data for TicketsService
        ticket_data = {
            'client_id': data['client_id'],
            'site_id': data['site_id'],
            'asset_id': clean_field(data.get('asset_id')),
            'assigned_to': clean_field(data.get('assigned_to')),
            'subject': data['subject'].strip(),
            'description': data['description'].strip(),
            'affected_person': data['affected_person'].strip(),
            'affected_person_contact': clean_field(data.get('affected_person_phone') or data.get('affected_person_contact') or ''),
            'additional_emails': data.get('additional_emails', []) if data.get('additional_emails') else [],
            'priority': data['priority'],
            'category_id': category_id,
            'channel': data.get('channel', 'portal'),
            'is_email_originated': data.get('is_email_originated', False),
            'from_email': clean_field(data.get('from_email')),
            'email_message_id': clean_field(data.get('email_message_id')),
            'email_thread_id': clean_field(data.get('email_thread_id'))
        }

        # DEBUG: Log ticket data before creation
        logging.info(f"About to create ticket with TicketsService: {ticket_data}")

        # Create ticket using TicketsService
        try:
            logging.info("Attempting ticket creation with TicketsService...")
            service_result = tickets_service.create_ticket(ticket_data, current_user_id)
            logging.info(f"TicketsService result: {service_result}")

            if not service_result.get('success'):
                logging.error(f"TicketsService failed: {service_result.get('errors')}")
                return current_app.response_manager.error(f"Ticket creation failed: {service_result.get('errors')}", 400)

            # Check if service_result has the expected structure
            if 'ticket' in service_result:
                result = service_result['ticket']
            else:
                # If no 'ticket' key, use the service_result directly
                result = service_result
            logging.info(f"Ticket created successfully: {result}")

        except Exception as create_error:
            logging.error(f"Ticket creation failed: {create_error}")
            raise create_error

        if result:
            # result is already the ticket data (extracted above)
            ticket_data = result
            current_app.logger.info(f"Ticket created successfully: {ticket_data['ticket_number']}")
            # Notifications are already handled by TicketsService

            # Handle file attachments if any
            if files:
                ticket_id = ticket_data['ticket_id']
                saved_files = []

                import os
                from werkzeug.utils import secure_filename

                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join(current_app.root_path, 'uploads', 'tickets', str(ticket_id))
                os.makedirs(upload_dir, exist_ok=True)

                for file in files:
                    if file and file.filename:
                        # Secure the filename
                        filename = secure_filename(file.filename)

                        # Add timestamp to avoid conflicts
                        import time
                        timestamp = str(int(time.time()))
                        name, ext = os.path.splitext(filename)
                        unique_filename = f"{name}_{timestamp}{ext}"

                        # Save file
                        file_path = os.path.join(upload_dir, unique_filename)
                        file.save(file_path)

                        # Save file info to database (using correct table and column names)
                        file_data = {
                            'ticket_id': ticket_id,
                            'filename': unique_filename,  # stored filename
                            'original_filename': filename,  # original filename
                            'file_path': file_path,
                            'file_size': os.path.getsize(file_path),
                            'mime_type': file.content_type,  # correct column name
                            'uploaded_by': current_user_id,
                            'created_at': datetime.utcnow()
                        }

                        file_result = current_app.db_manager.execute_insert('file_attachments', file_data)
                        if file_result:
                            saved_files.append({
                                'filename': filename,
                                'size': file_data['file_size'],
                                'type': file_data['content_type']
                            })

                current_app.logger.info(f"Saved {len(saved_files)} attachments for ticket {ticket_id}")

            formatted_ticket = current_app.response_manager.format_ticket_data(ticket_data)
            return current_app.response_manager.success(formatted_ticket, "Ticket created successfully", 201)
        else:
            return current_app.response_manager.server_error('Failed to create ticket')

    except Exception as e:
        # CRUCIAL! Esto capturará CUALQUIER error que ocurra en el bloque try
        # y lo escribirá en tu archivo de log, incluyendo la traza completa.
        print(f"🚨🚨🚨 EXCEPTION IN CREATE_TICKET: {e}", flush=True)
        print(f"🚨🚨🚨 EXCEPTION TYPE: {type(e)}", flush=True)
        import traceback
        print(f"🚨🚨🚨 TRACEBACK:", flush=True)
        traceback.print_exc()

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

@tickets_bp.route('/<ticket_id>/attachments', methods=['GET'])
@jwt_required()
def get_ticket_attachments(ticket_id):
    """Get all attachments for a ticket"""
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

        # Get attachments
        query = """
        SELECT fa.attachment_id, fa.ticket_id, fa.filename, fa.original_filename,
               fa.file_size, fa.mime_type, fa.uploaded_by, fa.created_at,
               u.name as uploaded_by_name, u.role as uploaded_by_role
        FROM file_attachments fa
        LEFT JOIN users u ON fa.uploaded_by = u.user_id
        WHERE fa.ticket_id = %s
        ORDER BY fa.created_at ASC
        """

        attachments = current_app.db_manager.execute_query(query, (ticket_id,))
        formatted_attachments = [current_app.response_manager.format_attachment_data(attachment) for attachment in (attachments or [])]

        return current_app.response_manager.success(formatted_attachments)

    except Exception as e:
        current_app.logger.error(f"Get ticket attachments error: {e}")
        return current_app.response_manager.server_error('Failed to get ticket attachments')

@tickets_bp.route('/attachments/<attachment_id>/download', methods=['GET'])
@jwt_required()
def download_attachment(attachment_id):
    """Download a specific attachment by ID"""
    try:
        # Validate attachment ID
        if not current_app.db_manager.validate_uuid(attachment_id):
            return current_app.response_manager.bad_request('Invalid attachment ID format')

        # Get attachment info and check access
        query = """
        SELECT fa.attachment_id, fa.ticket_id, fa.filename, fa.original_filename,
               fa.file_path, fa.file_size, fa.mime_type,
               t.client_id
        FROM file_attachments fa
        JOIN tickets t ON fa.ticket_id = t.ticket_id
        WHERE fa.attachment_id = %s
        """

        attachment = current_app.db_manager.execute_query(query, (attachment_id,), fetch='one')
        if not attachment:
            return current_app.response_manager.not_found('Attachment')

        # Check access permissions
        claims = get_jwt()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')

        if current_user_role in ['client_admin', 'solicitante']:
            if attachment['client_id'] != current_user_client_id:
                return current_app.response_manager.forbidden('Access denied')

        # Check if file exists on disk
        file_path = attachment['file_path']
        if not os.path.exists(file_path):
            current_app.logger.error(f"File not found on disk: {file_path}")
            return current_app.response_manager.not_found('File not found on server')

        # Read file and return as response
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Sanitize filename for Content-Disposition header
            import urllib.parse
            safe_filename = attachment['original_filename'].replace('"', '\\"')
            # URL encode the filename for better browser compatibility
            encoded_filename = urllib.parse.quote(attachment['original_filename'])

            # Create response with proper headers for file download
            response = Response(
                file_data,
                mimetype=attachment['mime_type'] or 'application/octet-stream',
                headers={
                    # Use both filename and filename* for maximum browser compatibility
                    'Content-Disposition': f'attachment; filename="{safe_filename}"; filename*=UTF-8\'\'{encoded_filename}',
                    'Content-Length': str(len(file_data)),
                    'Content-Type': attachment['mime_type'] or 'application/octet-stream',
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0',
                    'Accept-Ranges': 'bytes',
                    'X-Content-Type-Options': 'nosniff'
                }
            )

            current_app.logger.info(f"Download response created successfully for {attachment['original_filename']}")
            return response

        except Exception as file_error:
            current_app.logger.error(f"File read error: {file_error}")
            return current_app.response_manager.server_error('Failed to read file')

    except Exception as e:
        current_app.logger.error(f"Download attachment error: {e}")
        return current_app.response_manager.server_error('Failed to download attachment')

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

@tickets_bp.route('/test-bulk', methods=['POST'])
def test_bulk():
    """Test endpoint for bulk actions"""
    print("🚨🚨🚨 TEST BULK ENDPOINT CALLED! 🚨🚨🚨", flush=True)
    return {'success': True, 'message': 'Test endpoint working'}

@tickets_bp.route('/bulk-actions', methods=['POST'])
@jwt_required()
def bulk_actions():
    """Perform bulk actions on multiple tickets"""
    try:
        data = request.get_json()
        current_app.logger.info(f"🔧 BULK ACTIONS: Received data: {data}")
        print(f"🚨 BULK ACTIONS: Received data: {data}", flush=True)

        print(f"🚨 BULK ACTIONS: Checking if data exists", flush=True)
        if not data:
            print(f"🚨 BULK ACTIONS: No data provided", flush=True)
            return current_app.response_manager.bad_request('No data provided')

        print(f"🚨 BULK ACTIONS: Validating required fields", flush=True)
        # Validate required fields
        if 'ticket_ids' not in data or not data['ticket_ids']:
            print(f"🚨 BULK ACTIONS: Missing ticket_ids", flush=True)
            current_app.logger.error("🔧 BULK ACTIONS: Missing ticket_ids")
            return current_app.response_manager.bad_request('ticket_ids is required')

        if 'action' not in data or not data['action']:
            print(f"🚨 BULK ACTIONS: Missing action", flush=True)
            current_app.logger.error("🔧 BULK ACTIONS: Missing action")
            return current_app.response_manager.bad_request('action is required')

        print(f"🚨 BULK ACTIONS: Extracting data fields", flush=True)
        ticket_ids = data['ticket_ids']
        action = data['action']
        action_data = data.get('action_data', {})
        print(f"🚨 BULK ACTIONS: ticket_ids={ticket_ids}, action={action}", flush=True)

        # Validate ticket_ids is a list
        print(f"🚨 BULK ACTIONS: Validating ticket_ids is list", flush=True)
        if not isinstance(ticket_ids, list):
            print(f"🚨 BULK ACTIONS: ticket_ids is not a list", flush=True)
            return current_app.response_manager.bad_request('ticket_ids must be an array')

        # Limit bulk operations to 100 tickets max (like Zendesk)
        print(f"🚨 BULK ACTIONS: Checking ticket count limit", flush=True)
        if len(ticket_ids) > 100:
            print(f"🚨 BULK ACTIONS: Too many tickets", flush=True)
            return current_app.response_manager.bad_request('Maximum 100 tickets allowed per bulk operation')

        # Validate action
        print(f"🚨 BULK ACTIONS: Validating action", flush=True)
        valid_actions = ['update_status', 'assign', 'update_priority', 'delete']
        if action not in valid_actions:
            print(f"🚨 BULK ACTIONS: Invalid action", flush=True)
            return {'success': False, 'error': f'Invalid action. Valid actions: {", ".join(valid_actions)}'}, 400

        print(f"🚨 BULK ACTIONS: All validations passed, calling real service implementation", flush=True)

        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')

        print(f"🚨 BULK ACTIONS: User {current_user_id}, Role: {user_role}", flush=True)

        # Additional permission checks for delete action
        if action == 'delete' and user_role not in ['superadmin', 'admin']:
            print(f"🚨 BULK ACTIONS: User {user_role} tried to delete tickets", flush=True)
            return current_app.response_manager.forbidden('Only superadmin and admin can delete tickets')

        # Create ticket service and execute bulk action
        ticket_service = TicketService(current_app.db_manager, current_app.auth_manager)
        print(f"🚨 BULK ACTIONS: About to call service.bulk_actions", flush=True)

        result = ticket_service.bulk_actions(ticket_ids, action, action_data, current_user_id, user_role)

        print(f"🚨 BULK ACTIONS: Service returned: {result}", flush=True)

        if result['success']:
            return current_app.response_manager.success(
                data=result,
                message=f'Bulk action {action} completed successfully'
            )
        else:
            print(f"🚨 BULK ACTIONS: Service failed with: {result}", flush=True)
            return current_app.response_manager.error('Bulk action failed', 400, details=result.get('errors'))

    except Exception as e:
        current_app.logger.error(f"Bulk actions error: {e}")
        return current_app.response_manager.server_error('Failed to perform bulk actions')

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
