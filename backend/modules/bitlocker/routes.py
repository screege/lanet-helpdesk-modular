#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BitLocker routes for LANET Helpdesk V3
Handles BitLocker recovery keys and volume information
"""

from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.security import require_role
from utils.encryption import encrypt_data, decrypt_data
import json
from datetime import datetime

bitlocker_bp = Blueprint('bitlocker', __name__)

@bitlocker_bp.route('/<asset_id>', methods=['GET'])
@jwt_required()
def get_bitlocker_info(asset_id):
    """Get BitLocker information for an asset"""
    try:
        # Get user info from JWT claims
        claims = get_jwt()
        current_user = {
            'sub': get_jwt_identity(),
            'role': claims.get('role'),
            'client_id': claims.get('client_id'),
            'site_ids': claims.get('site_ids', []),
            'email': claims.get('email', 'unknown')
        }

        current_app.logger.info(f"Getting BitLocker info for asset {asset_id} by user {current_user.get('email')}")

        # Check if user has access to this asset
        if not _user_has_asset_access(current_user, asset_id):
            return jsonify({'error': 'Access denied to this asset'}), 403
        
        # Get BitLocker information
        query = """
            SELECT 
                bk.id,
                bk.volume_letter,
                bk.volume_label,
                bk.protection_status,
                bk.encryption_method,
                bk.key_protector_type,
                bk.recovery_key_id,
                bk.recovery_key_encrypted,
                bk.created_at,
                bk.updated_at,
                bk.last_verified_at
            FROM bitlocker_keys bk
            WHERE bk.asset_id = %s
            ORDER BY bk.volume_letter
        """
        
        result = current_app.db_manager.execute_query(query, (asset_id,), fetch='all')
        
        bitlocker_volumes = []
        for row in result:
            volume_data = {
                'id': str(row['id']),
                'volume_letter': row['volume_letter'],
                'volume_label': row['volume_label'],
                'protection_status': row['protection_status'],
                'encryption_method': row['encryption_method'],
                'key_protector_type': row['key_protector_type'],
                'recovery_key_id': row['recovery_key_id'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None,
                'last_verified_at': row['last_verified_at'].isoformat() if row['last_verified_at'] else None
            }

            # Only include recovery key for superadmin and technician
            if current_user.get('role') in ['superadmin', 'technician']:
                if row['recovery_key_encrypted']:  # recovery_key_encrypted
                    try:
                        volume_data['recovery_key'] = decrypt_data(row['recovery_key_encrypted'])
                    except Exception as e:
                        current_app.logger.error(f"Failed to decrypt recovery key: {e}")
                        volume_data['recovery_key'] = None
                else:
                    volume_data['recovery_key'] = None

            bitlocker_volumes.append(volume_data)
        
        # Calculate summary
        total_volumes = len(bitlocker_volumes)
        protected_volumes = len([v for v in bitlocker_volumes if v['protection_status'] == 'Protected'])
        
        summary = {
            'total_volumes': total_volumes,
            'protected_volumes': protected_volumes,
            'unprotected_volumes': total_volumes - protected_volumes,
            'protection_percentage': round((protected_volumes / total_volumes * 100) if total_volumes > 0 else 0, 1)
        }
        
        return jsonify({
            'success': True,
            'data': {
                'summary': summary,
                'volumes': bitlocker_volumes
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting BitLocker info: {e}")
        import traceback
        current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to get BitLocker information: {str(e)}'}), 500

@bitlocker_bp.route('/<asset_id>/update', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'technician'])
def update_bitlocker_info(asset_id):
    """Update BitLocker information for an asset (from agent)"""
    try:
        # Get user info from JWT claims
        claims = get_jwt()
        current_user = {
            'sub': get_jwt_identity(),
            'role': claims.get('role'),
            'client_id': claims.get('client_id'),
            'site_ids': claims.get('site_ids', []),
            'email': claims.get('email', 'unknown')
        }

        data = request.get_json()
        current_app.logger.info(f"Updating BitLocker info for asset {asset_id}")
        
        if not data or 'volumes' not in data:
            return jsonify({'error': 'Invalid data format'}), 400
        
        volumes = data['volumes']
        updated_count = 0
        
        for volume_data in volumes:
            volume_letter = volume_data.get('volume_letter')
            if not volume_letter:
                continue
            
            # Encrypt recovery key if present
            recovery_key_encrypted = None
            if volume_data.get('recovery_key'):
                recovery_key_encrypted = encrypt_data(volume_data['recovery_key'])
            
            # Upsert volume information
            upsert_query = """
                INSERT INTO bitlocker_keys (
                    asset_id, volume_letter, volume_label, protection_status,
                    encryption_method, key_protector_type, recovery_key_id,
                    recovery_key_encrypted, last_verified_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (asset_id, volume_letter) DO UPDATE SET
                    volume_label = EXCLUDED.volume_label,
                    protection_status = EXCLUDED.protection_status,
                    encryption_method = EXCLUDED.encryption_method,
                    key_protector_type = EXCLUDED.key_protector_type,
                    recovery_key_id = EXCLUDED.recovery_key_id,
                    recovery_key_encrypted = EXCLUDED.recovery_key_encrypted,
                    last_verified_at = EXCLUDED.last_verified_at,
                    updated_at = NOW()
            """
            
            current_app.db_manager.execute_query(
                upsert_query,
                (
                    asset_id,
                    volume_letter,
                    volume_data.get('volume_label'),
                    volume_data.get('protection_status', 'Unknown'),
                    volume_data.get('encryption_method'),
                    volume_data.get('key_protector_type'),
                    volume_data.get('recovery_key_id'),
                    recovery_key_encrypted,
                    datetime.now()
                ),
                fetch='none'
            )
            
            updated_count += 1
        
        current_app.logger.info(f"Updated {updated_count} BitLocker volumes for asset {asset_id}")
        
        return jsonify({
            'success': True,
            'message': f'Updated {updated_count} BitLocker volumes'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating BitLocker info: {e}")
        return jsonify({'error': 'Failed to update BitLocker information'}), 500

def _user_has_asset_access(current_user, asset_id):
    """Check if user has access to the specified asset"""
    try:
        role = current_user.get('role')
        
        # Superadmin and technician have access to all assets
        if role in ['superadmin', 'technician']:
            return True
        
        # Client admin can only access assets from their organization
        if role == 'client_admin':
            query = """
                SELECT 1 FROM assets 
                WHERE asset_id = %s AND client_id = %s
            """
            result = current_app.db_manager.execute_query(
                query, (asset_id, current_user.get('client_id')), fetch='one'
            )
            return result is not None
        
        # Solicitante can only access assets from their assigned sites
        if role == 'solicitante':
            user_id = current_user.get('sub')  # JWT subject
            query = """
                SELECT 1 FROM assets a
                JOIN user_sites us ON us.site_id = a.site_id
                WHERE a.asset_id = %s AND us.user_id = %s
            """
            result = current_app.db_manager.execute_query(
                query, (asset_id, user_id), fetch='one'
            )
            return result is not None
        
        return False
        
    except Exception as e:
        current_app.logger.error(f"Error checking asset access: {e}")
        return False
