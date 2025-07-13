#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Enterprise Reporting Columns
Simple, working implementation of enterprise reporting columns
"""

# 34 Enterprise Columns for MSP Reporting
ENTERPRISE_COLUMNS = {
    # Basic Information (12 columns)
    'ticket_id': {
        'display_name': 'ID de la solicitud (TKT-XXXXXX)',
        'description': 'Número único de identificación del ticket',
        'sql_expression': "CONCAT('TKT-', LPAD(tickets.ticket_number::text, 6, '0'))",
        'data_type': 'text',
        'category': 'basic',
        'is_filterable': True,
        'is_sortable': True
    },
    'created_at': {
        'display_name': 'Fecha y hora de creación',
        'description': 'Fecha y hora cuando se creó el ticket',
        'sql_expression': "tickets.created_at AT TIME ZONE 'America/Mexico_City'",
        'data_type': 'datetime',
        'category': 'basic',
        'is_filterable': True,
        'is_sortable': True
    },
    'requester_name': {
        'display_name': '¿Qué persona tiene el problema?',
        'description': 'Nombre del usuario que reportó el problema',
        'sql_expression': 'requester.name',
        'data_type': 'text',
        'category': 'basic',
        'is_filterable': True,
        'is_sortable': True,
        'requires_join': True,
        'join_tables': ['users AS requester ON tickets.created_by = requester.user_id']
    },
    'requester_full': {
        'display_name': 'Solicitante completo',
        'description': 'Nombre completo y email del solicitante',
        'sql_expression': "CONCAT(requester.name, ' (', requester.email, ')')",
        'data_type': 'text',
        'category': 'basic',
        'is_filterable': True,
        'is_sortable': True,
        'requires_join': True,
        'join_tables': ['users AS requester ON tickets.created_by = requester.user_id']
    },
    'subject': {
        'display_name': 'Asunto',
        'description': 'Título o asunto del ticket',
        'sql_expression': 'tickets.subject',
        'data_type': 'text',
        'category': 'basic',
        'is_filterable': True,
        'is_sortable': True
    },
    'status': {
        'display_name': 'Estado',
        'description': 'Estado actual del ticket',
        'sql_expression': 'tickets.status',
        'data_type': 'text',
        'category': 'basic',
        'is_filterable': True,
        'is_sortable': True
    },
    'priority': {
        'display_name': 'Prioridad',
        'description': 'Nivel de prioridad del ticket',
        'sql_expression': 'tickets.priority',
        'data_type': 'text',
        'category': 'basic',
        'is_filterable': True,
        'is_sortable': True
    },
    'assigned_technician': {
        'display_name': 'Técnico asignado',
        'description': 'Técnico responsable del ticket',
        'sql_expression': 'COALESCE(technician.name, \'Sin asignar\')',
        'data_type': 'text',
        'category': 'basic',
        'is_filterable': True,
        'is_sortable': True,
        'requires_join': True,
        'join_tables': ['users AS technician ON tickets.assigned_to = technician.user_id']
    },
    'client_name': {
        'display_name': 'Cliente/Organización',
        'description': 'Nombre del cliente u organización',
        'sql_expression': 'clients.name',
        'data_type': 'text',
        'category': 'basic',
        'is_filterable': True,
        'is_sortable': True,
        'requires_join': True,
        'join_tables': ['clients ON tickets.client_id = clients.client_id']
    },
    'site_name': {
        'display_name': 'Sitio',
        'description': 'Sitio donde ocurrió el problema',
        'sql_expression': 'COALESCE(sites.name, \'Sin sitio\')',
        'data_type': 'text',
        'category': 'basic',
        'is_filterable': True,
        'is_sortable': True,
        'requires_join': True,
        'join_tables': ['sites ON tickets.site_id = sites.site_id']
    },
    'category': {
        'display_name': 'Categoría',
        'description': 'Categoría del problema',
        'sql_expression': 'COALESCE(categories.name, \'Sin categoría\')',
        'data_type': 'text',
        'category': 'basic',
        'is_filterable': True,
        'is_sortable': True,
        'requires_join': True,
        'join_tables': ['categories ON tickets.category_id = categories.category_id']
    },
    'description': {
        'display_name': 'Descripción',
        'description': 'Descripción detallada del problema',
        'sql_expression': 'LEFT(tickets.description, 200)',
        'data_type': 'text',
        'category': 'basic',
        'is_filterable': False,
        'is_sortable': False
    },

    # SLA Metrics (5 columns)
    'sla_response_time': {
        'display_name': 'Tiempo de respuesta SLA',
        'description': 'Tiempo límite de respuesta según SLA',
        'sql_expression': 'COALESCE(sla_policies.response_time_hours, 24)',
        'data_type': 'number',
        'category': 'sla',
        'is_filterable': True,
        'is_sortable': True,
        'requires_join': True,
        'join_tables': ['sla_policies ON tickets.priority = sla_policies.priority AND tickets.client_id = sla_policies.client_id']
    },
    'sla_resolution_time': {
        'display_name': 'Tiempo de resolución SLA',
        'description': 'Tiempo límite de resolución según SLA',
        'sql_expression': 'COALESCE(sla_policies.resolution_time_hours, 72)',
        'data_type': 'number',
        'category': 'sla',
        'is_filterable': True,
        'is_sortable': True,
        'requires_join': True,
        'join_tables': ['sla_policies ON tickets.priority = sla_policies.priority AND tickets.client_id = sla_policies.client_id']
    },
    'sla_response_met': {
        'display_name': 'SLA Respuesta cumplido',
        'description': 'Si se cumplió el SLA de respuesta',
        'sql_expression': """
            CASE 
                WHEN tickets.first_response_at IS NULL THEN 'Pendiente'
                WHEN EXTRACT(EPOCH FROM (tickets.first_response_at - tickets.created_at))/3600 <= COALESCE(sla_policies.response_time_hours, 24) THEN 'Cumplido'
                ELSE 'Incumplido'
            END
        """,
        'data_type': 'text',
        'category': 'sla',
        'is_filterable': True,
        'is_sortable': True,
        'requires_join': True,
        'join_tables': ['sla_policies ON tickets.priority = sla_policies.priority AND tickets.client_id = sla_policies.client_id']
    },
    'sla_resolution_met': {
        'display_name': 'SLA Resolución cumplido',
        'description': 'Si se cumplió el SLA de resolución',
        'sql_expression': """
            CASE 
                WHEN tickets.resolved_at IS NULL THEN 'Pendiente'
                WHEN EXTRACT(EPOCH FROM (tickets.resolved_at - tickets.created_at))/3600 <= COALESCE(sla_policies.resolution_time_hours, 72) THEN 'Cumplido'
                ELSE 'Incumplido'
            END
        """,
        'data_type': 'text',
        'category': 'sla',
        'is_filterable': True,
        'is_sortable': True,
        'requires_join': True,
        'join_tables': ['sla_policies ON tickets.priority = sla_policies.priority AND tickets.client_id = sla_policies.client_id']
    },
    'escalated': {
        'display_name': 'Estado de aprobación',
        'description': 'Estado de aprobación del ticket',
        'sql_expression': 'COALESCE(tickets.approval_status, \'No requerido\')',
        'data_type': 'text',
        'category': 'sla',
        'is_filterable': True,
        'is_sortable': True
    },

    # Technical Details (8 columns)
    'channel': {
        'display_name': 'Canal de origen',
        'description': 'Canal por el que se creó el ticket',
        'sql_expression': 'tickets.channel',
        'data_type': 'text',
        'category': 'technical',
        'is_filterable': True,
        'is_sortable': True
    },
    'affected_person': {
        'display_name': 'Persona afectada',
        'description': 'Nombre de la persona afectada',
        'sql_expression': 'tickets.affected_person',
        'data_type': 'text',
        'category': 'technical',
        'is_filterable': True,
        'is_sortable': True
    },
    'affected_person_phone': {
        'display_name': 'Teléfono persona afectada',
        'description': 'Teléfono de la persona afectada',
        'sql_expression': 'COALESCE(tickets.affected_person_phone, \'Sin teléfono\')',
        'data_type': 'text',
        'category': 'technical',
        'is_filterable': True,
        'is_sortable': True
    },
    'assigned_at': {
        'display_name': 'Fecha de asignación',
        'description': 'Fecha y hora cuando se asignó el ticket',
        'sql_expression': "tickets.assigned_at AT TIME ZONE 'America/Mexico_City'",
        'data_type': 'datetime',
        'category': 'technical',
        'is_filterable': True,
        'is_sortable': True
    },
    'resolved_at': {
        'display_name': 'Resolución',
        'description': 'Fecha y hora de resolución',
        'sql_expression': "tickets.resolved_at AT TIME ZONE 'America/Mexico_City'",
        'data_type': 'datetime',
        'category': 'technical',
        'is_filterable': True,
        'is_sortable': True
    },
    'closed_at': {
        'display_name': 'Cierre',
        'description': 'Fecha y hora de cierre',
        'sql_expression': "tickets.closed_at AT TIME ZONE 'America/Mexico_City'",
        'data_type': 'datetime',
        'category': 'technical',
        'is_filterable': True,
        'is_sortable': True
    },
    'is_email_originated': {
        'display_name': 'Originado por email',
        'description': 'Si el ticket fue creado por email',
        'sql_expression': 'CASE WHEN tickets.is_email_originated THEN \'Sí\' ELSE \'No\' END',
        'data_type': 'text',
        'category': 'technical',
        'is_filterable': True,
        'is_sortable': True
    },
    'resolution_notes': {
        'display_name': 'Notas de resolución',
        'description': 'Notas sobre cómo se resolvió el ticket',
        'sql_expression': 'CASE WHEN tickets.resolution_notes IS NOT NULL THEN \'Sí\' ELSE \'No\' END',
        'data_type': 'text',
        'category': 'technical',
        'is_filterable': True,
        'is_sortable': True
    },

    # Business Metrics (9 columns)
    'total_resolution_time': {
        'display_name': 'Tiempo total resolución',
        'description': 'Tiempo total desde creación hasta resolución',
        'sql_expression': """
            CASE 
                WHEN tickets.resolved_at IS NOT NULL THEN 
                    ROUND(EXTRACT(EPOCH FROM (tickets.resolved_at - tickets.created_at))/3600, 2)
                ELSE NULL
            END
        """,
        'data_type': 'number',
        'category': 'business',
        'is_filterable': True,
        'is_sortable': True
    },
    'days_since_creation': {
        'display_name': 'Días desde creación',
        'description': 'Días transcurridos desde la creación',
        'sql_expression': 'ROUND(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - tickets.created_at))/86400, 1)',
        'data_type': 'number',
        'category': 'business',
        'is_filterable': True,
        'is_sortable': True
    },
    'resolution_status': {
        'display_name': 'Estado de resolución',
        'description': 'Estado detallado de resolución',
        'sql_expression': """
            CASE 
                WHEN tickets.status = 'Cerrado' THEN 'Completado'
                WHEN tickets.status = 'Resuelto' THEN 'Resuelto - Pendiente cierre'
                WHEN tickets.resolved_at IS NOT NULL THEN 'Resuelto'
                WHEN tickets.first_response_at IS NOT NULL THEN 'En progreso'
                ELSE 'Sin respuesta'
            END
        """,
        'data_type': 'text',
        'category': 'business',
        'is_filterable': True,
        'is_sortable': True
    }
}

# Category definitions
COLUMN_CATEGORIES = {
    'basic': {
        'name': 'Información Básica',
        'description': 'Campos fundamentales del ticket como ID, fecha, estado, solicitante',
        'icon': 'info'
    },
    'sla': {
        'name': 'Métricas SLA',
        'description': 'Métricas de cumplimiento de SLA, tiempos de respuesta y resolución',
        'icon': 'clock'
    },
    'technical': {
        'name': 'Detalles Técnicos',
        'description': 'Información técnica como categorías, horas estimadas, notas internas',
        'icon': 'settings'
    },
    'business': {
        'name': 'Métricas de Negocio',
        'description': 'Métricas de negocio como satisfacción, rendimiento, análisis',
        'icon': 'trending-up'
    }
}

def get_columns_by_category():
    """Get columns organized by category"""
    categorized = {}
    for column_key, column_data in ENTERPRISE_COLUMNS.items():
        category = column_data['category']
        if category not in categorized:
            categorized[category] = []
        categorized[category].append({
            'column_key': column_key,
            **column_data
        })
    return categorized

def get_column_sql(column_keys, include_joins=True):
    """Generate SQL for selected columns"""
    selected_columns = []
    join_tables = set()
    
    for key in column_keys:
        if key in ENTERPRISE_COLUMNS:
            column = ENTERPRISE_COLUMNS[key]
            selected_columns.append(f"{column['sql_expression']} AS {key}")
            
            if include_joins and column.get('requires_join') and 'join_tables' in column:
                for join_table in column['join_tables']:
                    join_tables.add(join_table)
    
    return selected_columns, list(join_tables)

def build_enterprise_query(column_keys, filters=None, limit=None):
    """Build complete SQL query for enterprise reporting"""
    selected_columns, join_tables = get_column_sql(column_keys)
    
    if not selected_columns:
        return None
    
    # Base query
    query = f"""
    SELECT 
        {', '.join(selected_columns)}
    FROM tickets
    """
    
    # Add joins
    for join_table in join_tables:
        query += f"\n    LEFT JOIN {join_table}"
    
    # Add filters
    where_conditions = []
    if filters:
        if filters.get('date_from'):
            where_conditions.append(f"tickets.created_at >= '{filters['date_from']}'")
        if filters.get('date_to'):
            where_conditions.append(f"tickets.created_at <= '{filters['date_to']}'")
        if filters.get('status'):
            status_list = "', '".join(filters['status'])
            where_conditions.append(f"tickets.status IN ('{status_list}')")
        if filters.get('priority'):
            priority_list = "', '".join(filters['priority'])
            where_conditions.append(f"tickets.priority IN ('{priority_list}')")
        if filters.get('client_id'):
            where_conditions.append(f"tickets.client_id = '{filters['client_id']}'")
        if filters.get('assigned_technician'):
            where_conditions.append(f"tickets.assigned_to = '{filters['assigned_technician']}'")
    
    if where_conditions:
        query += f"\n    WHERE {' AND '.join(where_conditions)}"
    
    # Add ordering
    query += "\n    ORDER BY tickets.created_at DESC"
    
    # Add limit
    if limit:
        query += f"\n    LIMIT {limit}"
    
    return query
