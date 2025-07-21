#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Assets Routes
Endpoints for managing and viewing assets/equipment
"""

from flask import Blueprint, request, current_app, g
from flask_jwt_extended import jwt_required
from utils.security import require_role

assets_bp = Blueprint('assets', __name__)

@assets_bp.route('/test', methods=['GET'])
def test_assets():
    """Test endpoint to verify assets blueprint is working"""
    return {'message': 'Assets blueprint is working!', 'status': 'success'}

@assets_bp.route('/simple-test', methods=['GET'])
def simple_test():
    """Simple test endpoint"""
    print("SIMPLE TEST ENDPOINT CALLED", flush=True)
    return {'message': 'Simple test working!', 'success': True}

@assets_bp.route('/debug-routes', methods=['GET'])
def debug_routes():
    """Debug endpoint to show all registered routes"""
    from flask import current_app
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return {'routes': routes, 'total': len(routes), 'success': True}



@assets_bp.route('/dashboard/my-organization', methods=['GET'])
@jwt_required()
@require_role(['client_admin'])
def get_organization_dashboard():
    """Get assets dashboard for client admin's organization"""
    try:
        current_user = g.current_user
        client_id = current_user.get('client_id')
        if not client_id:
            return current_app.response_manager.bad_request('Client ID not found')

        # Get assets summary
        summary_query = """
        SELECT 
            COUNT(*) as total_assets,
            COUNT(CASE WHEN agent_status = 'online' THEN 1 END) as online_assets,
            COUNT(CASE WHEN agent_status = 'error' THEN 1 END) as warning_assets,
            COUNT(CASE WHEN agent_status = 'offline' THEN 1 END) as offline_assets,
            MAX(last_seen) as last_update
        FROM assets 
        WHERE client_id = %s AND status = 'active'
        """
        
        summary = current_app.db_manager.execute_query(
            summary_query, (client_id,), fetch='one'
        )

        return current_app.response_manager.success({
            'summary': summary or {
                'total_assets': 0,
                'online_assets': 0, 
                'warning_assets': 0,
                'offline_assets': 0,
                'last_update': None
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error getting organization dashboard: {e}")
        return current_app.response_manager.server_error('Failed to get dashboard data')

@assets_bp.route('/inventory/my-organization', methods=['GET'])
@jwt_required()
@require_role(['client_admin'])
def get_organization_inventory():
    """Get complete inventory for client admin's organization"""
    try:
        current_user = g.current_user
        client_id = current_user.get('client_id')
        if not client_id:
            return current_app.response_manager.bad_request('Client ID not found')

        # Get assets for the organization
        assets_query = """
        SELECT 
            a.asset_id,
            a.name,
            a.agent_status,
            a.last_seen,
            a.specifications,
            s.name as site_name,
            s.site_id
        FROM assets a
        JOIN sites s ON a.site_id = s.site_id
        WHERE a.client_id = %s AND a.status = 'active'
        ORDER BY a.last_seen DESC
        LIMIT 50
        """
        
        assets = current_app.db_manager.execute_query(
            assets_query, (client_id,), fetch='all'
        )

        return current_app.response_manager.success({
            'assets': assets or [],
            'total': len(assets) if assets else 0
        })

    except Exception as e:
        current_app.logger.error(f"Error getting organization inventory: {e}")
        return current_app.response_manager.server_error('Failed to get inventory')

@assets_bp.route('/dashboard/technician', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'technician'])
def get_technician_dashboard():
    """Get organized assets dashboard for technicians - grouped by client"""
    try:
        # Get assets summary grouped by client
        client_summary_query = """
        SELECT
            c.client_id,
            c.name as client_name,
            COUNT(a.asset_id) as total_assets,
            COUNT(CASE WHEN a.agent_status = 'online' THEN 1 END) as online_assets,
            COUNT(CASE WHEN a.agent_status = 'error' THEN 1 END) as warning_assets,
            COUNT(CASE WHEN a.agent_status = 'offline' THEN 1 END) as offline_assets,
            MAX(a.last_seen) as last_update
        FROM clients c
        LEFT JOIN assets a ON c.client_id = a.client_id AND a.status = 'active'
        WHERE c.is_active = true
        GROUP BY c.client_id, c.name
        HAVING COUNT(a.asset_id) > 0
        ORDER BY c.name
        """

        client_summaries = current_app.db_manager.execute_query(
            client_summary_query, fetch='all'
        )

        # Get overall summary
        overall_summary_query = """
        SELECT
            COUNT(*) as total_assets,
            COUNT(CASE WHEN agent_status = 'online' THEN 1 END) as online_assets,
            COUNT(CASE WHEN agent_status = 'error' THEN 1 END) as warning_assets,
            COUNT(CASE WHEN agent_status = 'offline' THEN 1 END) as offline_assets,
            MAX(last_seen) as last_update
        FROM assets
        WHERE status = 'active'
        """

        overall_summary = current_app.db_manager.execute_query(
            overall_summary_query, fetch='one'
        )

        # Get recent alerts (assets with issues)
        alerts_query = """
        SELECT
            a.name as asset_name,
            a.agent_status,
            a.last_seen,
            s.name as site_name,
            c.name as client_name
        FROM assets a
        JOIN sites s ON a.site_id = s.site_id
        JOIN clients c ON a.client_id = c.client_id
        WHERE a.status = 'active'
        AND (a.agent_status IN ('error', 'offline') OR a.last_seen < NOW() - INTERVAL '1 hour')
        ORDER BY a.last_seen DESC
        LIMIT 10
        """

        alerts = current_app.db_manager.execute_query(
            alerts_query, fetch='all'
        )

        return current_app.response_manager.success({
            'overall_summary': overall_summary or {
                'total_assets': 0,
                'online_assets': 0,
                'warning_assets': 0,
                'offline_assets': 0,
                'last_update': None
            },
            'client_summaries': client_summaries or [],
            'alerts': alerts or []
        })

    except Exception as e:
        current_app.logger.error(f"Error getting technician dashboard: {e}")
        return current_app.response_manager.server_error('Failed to get technician dashboard')

@assets_bp.route('/technician/filtered', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'technician'])
def get_filtered_assets_for_technician():
    """Get filtered assets for technicians with advanced filtering"""
    try:
        # Get query parameters
        client_id = request.args.get('client_id')
        site_id = request.args.get('site_id')
        status = request.args.get('status')  # online, offline, warning
        search = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)  # Max 100 per page

        # Build WHERE conditions
        where_conditions = ["a.status = 'active'"]
        params = []

        if client_id:
            where_conditions.append("a.client_id = %s")
            params.append(client_id)

        if site_id:
            where_conditions.append("a.site_id = %s")
            params.append(site_id)

        if status:
            where_conditions.append("a.agent_status = %s")
            params.append(status)

        if search:
            where_conditions.append("(a.name ILIKE %s OR c.name ILIKE %s OR s.name ILIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])

        where_clause = " AND ".join(where_conditions)

        # Get total count
        count_query = f"""
        SELECT COUNT(*)
        FROM assets a
        JOIN sites s ON a.site_id = s.site_id
        JOIN clients c ON a.client_id = c.client_id
        WHERE {where_clause}
        """

        total_count = current_app.db_manager.execute_query(
            count_query, params, fetch='one'
        )['count']

        # Get paginated assets
        offset = (page - 1) * per_page
        assets_query = f"""
        SELECT
            a.asset_id,
            a.name,
            a.agent_status,
            a.last_seen,
            a.specifications,
            s.name as site_name,
            s.site_id,
            s.address as site_address,
            c.name as client_name,
            c.client_id
        FROM assets a
        JOIN sites s ON a.site_id = s.site_id
        JOIN clients c ON a.client_id = c.client_id
        WHERE {where_clause}
        ORDER BY c.name, s.name, a.name
        LIMIT %s OFFSET %s
        """

        params.extend([per_page, offset])
        assets = current_app.db_manager.execute_query(
            assets_query, params, fetch='all'
        )

        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page

        return current_app.response_manager.success({
            'assets': assets or [],
            'pagination': {
                'total': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error getting filtered assets: {e}")
        return current_app.response_manager.server_error('Failed to get filtered assets')

@assets_bp.route('/clients', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'technician'])
def get_clients_with_assets():
    """Get list of clients that have assets (for filter dropdown)"""
    try:
        clients_query = """
        SELECT DISTINCT
            c.client_id,
            c.name as client_name,
            COUNT(a.asset_id) as asset_count
        FROM clients c
        JOIN assets a ON c.client_id = a.client_id
        WHERE c.is_active = true AND a.status = 'active'
        GROUP BY c.client_id, c.name
        ORDER BY c.name
        """

        clients = current_app.db_manager.execute_query(
            clients_query, fetch='all'
        )

        return current_app.response_manager.success({
            'clients': clients or []
        })

    except Exception as e:
        current_app.logger.error(f"Error getting clients with assets: {e}")
        return current_app.response_manager.server_error('Failed to get clients')

@assets_bp.route('/sites', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'technician'])
def get_sites_with_assets():
    """Get list of sites that have assets (for filter dropdown)"""
    try:
        client_id = request.args.get('client_id')

        where_conditions = ["s.is_active = true", "a.status = 'active'"]
        params = []

        if client_id:
            where_conditions.append("s.client_id = %s")
            params.append(client_id)

        where_clause = " AND ".join(where_conditions)

        sites_query = f"""
        SELECT DISTINCT
            s.site_id,
            s.name as site_name,
            s.client_id,
            c.name as client_name,
            COUNT(a.asset_id) as asset_count
        FROM sites s
        JOIN clients c ON s.client_id = c.client_id
        JOIN assets a ON s.site_id = a.site_id
        WHERE {where_clause}
        GROUP BY s.site_id, s.name, s.client_id, c.name
        ORDER BY c.name, s.name
        """

        sites = current_app.db_manager.execute_query(
            sites_query, params, fetch='all'
        )

        return current_app.response_manager.success({
            'sites': sites or []
        })

    except Exception as e:
        current_app.logger.error(f"Error getting sites with assets: {e}")
        return current_app.response_manager.server_error('Failed to get sites')

@assets_bp.route('/', methods=['GET'])
def get_all_assets():
    """Get all assets with real data from database"""
    try:
        current_app.logger.info("🔧 Assets endpoint called - fetching real data")

        # Get all assets with available information
        assets_query = """
        SELECT
            a.asset_id,
            a.name,
            a.agent_status,
            a.last_seen,
            a.specifications,
            s.name as site_name,
            s.site_id,
            c.name as client_name,
            c.client_id
        FROM assets a
        JOIN sites s ON a.site_id = s.site_id
        JOIN clients c ON a.client_id = c.client_id
        WHERE a.status = 'active'
        ORDER BY a.last_seen DESC NULLS LAST
        LIMIT 100
        """

        current_app.logger.info("🔧 Executing assets query...")
        assets = current_app.db_manager.execute_query(assets_query, fetch='all')
        current_app.logger.info(f"🔧 Found {len(assets) if assets else 0} assets")

        return current_app.response_manager.success({
            'assets': assets or [],
            'total': len(assets) if assets else 0
        })
    except Exception as e:
        current_app.logger.error(f"Error getting all assets: {e}")
        return current_app.response_manager.server_error('Failed to get assets')

@assets_bp.route('/detail-test', methods=['GET'])
def get_asset_detail_test():
    """Test endpoint for asset detail"""
    print("ASSET DETAIL TEST ENDPOINT CALLED", flush=True)
    return {'message': 'Asset detail test working!', 'success': True}

@assets_bp.route('/detail/<asset_id>', methods=['GET'])
def get_asset_detail(asset_id):
    """Get detailed information for a specific asset"""
    print(f"ASSET DETAIL ENDPOINT CALLED WITH ID: {asset_id}", flush=True)
    try:
        # Simple test first
        return {
            'data': {
                'asset': {
                    'asset_id': asset_id,
                    'name': 'Test Asset',
                    'status': 'test'
                }
            },
            'success': True
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR IN ASSET DETAIL: {e}", flush=True)
        print(f"TRACEBACK: {error_details}", flush=True)
        return {'error': 'Failed to get asset detail', 'success': False}
