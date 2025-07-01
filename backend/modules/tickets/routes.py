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
    try:
        data = request.get_json()

        if not data:
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

        # Generate ticket number
        now = datetime.utcnow()
        year_month = now.strftime("%Y%m")

        # Get next sequence number for this month
        sequence_query = """
        SELECT COALESCE(MAX(CAST(SUBSTRING(ticket_number FROM 8) AS INTEGER)), 0) + 1 as next_seq
        FROM tickets
        WHERE ticket_number LIKE %s
        """

        result = current_app.db_manager.execute_query(
            sequence_query,
            (f"TKT-{year_month}%",),
            fetch='one'
        )

        next_seq = result['next_seq'] if result else 1
        ticket_number = f"TKT-{year_month}{next_seq:04d}"

        # Prepare ticket data
        ticket_data = {
            'ticket_id': str(uuid.uuid4()),
            'ticket_number': ticket_number,
            'client_id': data['client_id'],
            'site_id': data['site_id'],
            'asset_id': data.get('asset_id'),
            'created_by': current_user_id,
            'assigned_to': data.get('assigned_to'),
            'subject': data['subject'].strip(),
            'description': data['description'].strip(),
            'affected_person': data['affected_person'].strip(),
            'affected_person_contact': data['affected_person_contact'].strip(),
            'additional_emails': data.get('additional_emails', []),
            'priority': data['priority'],
            'category_id': data.get('category_id'),
            'status': 'nuevo',
            'channel': data.get('channel', 'portal'),
            'is_email_originated': data.get('is_email_originated', False),
            'from_email': data.get('from_email'),
            'email_message_id': data.get('email_message_id'),
            'email_thread_id': data.get('email_thread_id'),
            'approval_status': 'pendiente',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Auto-assign if assigned_to is provided
        if ticket_data['assigned_to']:
            ticket_data['status'] = 'asignado'
            ticket_data['assigned_at'] = datetime.utcnow()

        # Insert ticket
        result = current_app.db_manager.execute_insert(
            'tickets',
            ticket_data,
            returning='ticket_id, ticket_number, subject, status, created_at'
        )

        if result:
            current_app.logger.info(f"Ticket created successfully: {result['ticket_number']}")
            formatted_ticket = current_app.response_manager.format_ticket_data(result)
            return current_app.response_manager.success(formatted_ticket, "Ticket created successfully", 201)
        else:
            return current_app.response_manager.server_error('Failed to create ticket')

    except Exception as e:
        current_app.logger.error(f"Create ticket error: {e}")
        return current_app.response_manager.server_error('Failed to create ticket')
