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
            COUNT(CASE WHEN agent_status = 'warning' THEN 1 END) as warning_assets,
            COUNT(CASE WHEN agent_status = 'offline' THEN 1 END) as offline_assets,
            MAX(last_seen) as last_update
        FROM assets 
        WHERE client_id = %s AND is_active = true
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
        WHERE a.client_id = %s AND a.is_active = true
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

@assets_bp.route('/<asset_id>/detail', methods=['GET'])
@jwt_required()
@require_role(['client_admin', 'solicitante', 'superadmin', 'technician'])
def get_asset_detail(asset_id):
    """Get detailed information for a specific asset"""
    try:
        current_user = g.current_user
        user_role = current_user.get('role')
        client_id = current_user.get('client_id')
        user_id = current_user.get('user_id')

        if user_role in ['superadmin', 'technician']:
            # Superadmin/technician can access any asset
            access_check_query = """
            SELECT a.*, s.name as site_name, c.name as client_name
            FROM assets a
            JOIN sites s ON a.site_id = s.site_id
            JOIN clients c ON a.client_id = c.client_id
            WHERE a.asset_id = %s AND a.is_active = true
            """
            asset = current_app.db_manager.execute_query(
                access_check_query, (asset_id,), fetch='one'
            )
        elif user_role == 'client_admin':
            # Client admin can access assets in their organization
            access_check_query = """
            SELECT a.*, s.name as site_name, c.name as client_name
            FROM assets a
            JOIN sites s ON a.site_id = s.site_id
            JOIN clients c ON a.client_id = c.client_id
            WHERE a.asset_id = %s AND a.client_id = %s AND a.is_active = true
            """
            asset = current_app.db_manager.execute_query(
                access_check_query, (asset_id, client_id), fetch='one'
            )
        else:
            # Solicitante can only access assets in assigned sites
            access_check_query = """
            SELECT a.*, s.name as site_name, c.name as client_name
            FROM assets a
            JOIN sites s ON a.site_id = s.site_id
            JOIN clients c ON a.client_id = c.client_id
            JOIN user_sites us ON s.site_id = us.site_id
            WHERE a.asset_id = %s AND us.user_id = %s AND a.is_active = true
            """
            asset = current_app.db_manager.execute_query(
                access_check_query, (asset_id, user_id), fetch='one'
            )

        if not asset:
            return current_app.response_manager.not_found('Asset not found or access denied')

        return current_app.response_manager.success({
            'asset': asset
        })

    except Exception as e:
        current_app.logger.error(f"Error getting asset detail: {e}")
        return current_app.response_manager.server_error('Failed to get asset detail')
