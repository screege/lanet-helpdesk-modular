#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Agents Routes
API endpoints for agent installation tokens and agent registration
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .service import AgentsService

agents_bp = Blueprint('agents', __name__)

# =====================================================
# TOKEN MANAGEMENT ENDPOINTS
# =====================================================

@agents_bp.route('/clients/<client_id>/sites/<site_id>/tokens', methods=['GET'])
@jwt_required()
def get_tokens_for_site(client_id, site_id):
    """Get all installation tokens for a specific client and site"""
    try:
        service = AgentsService(current_app.db_manager)
        tokens = service.get_tokens_for_client_site(client_id, site_id)
        
        return current_app.response_manager.success({
            'tokens': tokens,
            'total': len(tokens)
        })
        
    except ValueError as e:
        return current_app.response_manager.bad_request(str(e))
    except Exception as e:
        current_app.logger.error(f"Error getting tokens for site: {e}")
        return current_app.response_manager.server_error('Failed to get tokens')

@agents_bp.route('/clients/<client_id>/sites/<site_id>/tokens', methods=['POST'])
@jwt_required()
def create_token_for_site(client_id, site_id):
    """Create a new installation token for a specific client and site"""
    try:
        current_app.logger.info(f"🔥 STARTING TOKEN CREATION for client {client_id}, site {site_id}")

        # Get request data
        data = request.get_json()
        expires_days = data.get('expires_days')
        notes = data.get('notes', '')

        # Get user info
        current_user = get_jwt_identity()

        # Create token using service
        service = AgentsService(current_app.db_manager)
        token = service.create_installation_token(
            client_id=client_id,
            site_id=site_id,
            created_by=current_user,
            expires_days=expires_days,
            notes=notes
        )

        return current_app.response_manager.success(token)
        
    except ValueError as e:
        return current_app.response_manager.bad_request(str(e))
    except Exception as e:
        current_app.logger.error(f"Error creating token: {e}")
        return current_app.response_manager.server_error('Failed to create token')

@agents_bp.route('/clients/<client_id>/tokens', methods=['GET'])
@jwt_required()
def get_tokens_for_client(client_id):
    """Get all installation tokens for a specific client (all sites)"""
    try:
        service = AgentsService(current_app.db_manager)
        tokens = service.get_all_tokens_for_client(client_id)
        
        return current_app.response_manager.success({
            'tokens': tokens,
            'total': len(tokens)
        })
        
    except ValueError as e:
        return current_app.response_manager.bad_request(str(e))
    except Exception as e:
        current_app.logger.error(f"Error getting tokens for client: {e}")
        return current_app.response_manager.server_error('Failed to get tokens')

@agents_bp.route('/tokens', methods=['GET'])
@jwt_required()
def get_all_tokens():
    """Get all installation tokens (superadmin/technician only)"""
    try:
        service = AgentsService(current_app.db_manager)
        tokens = service.get_all_tokens()
        
        return current_app.response_manager.success({
            'tokens': tokens,
            'total': len(tokens)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting all tokens: {e}")
        return current_app.response_manager.server_error('Failed to get tokens')

@agents_bp.route('/tokens/<token_id>', methods=['GET'])
@jwt_required()
def get_token_by_id(token_id):
    """Get specific token by ID"""
    try:
        service = AgentsService(current_app.db_manager)
        token = service.get_token_by_id(token_id)
        
        return current_app.response_manager.success(token)
        
    except ValueError as e:
        return current_app.response_manager.not_found('Token')
    except Exception as e:
        current_app.logger.error(f"Error getting token by ID: {e}")
        return current_app.response_manager.server_error('Failed to get token')

@agents_bp.route('/tokens/<token_id>', methods=['PUT'])
@jwt_required()
def update_token(token_id):
    """Update token status (activate/deactivate)"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('Request body required')
        
        if 'is_active' not in data:
            return current_app.response_manager.bad_request('is_active field required')
        
        is_active = data['is_active']
        if not isinstance(is_active, bool):
            return current_app.response_manager.bad_request('is_active must be boolean')
        
        service = AgentsService(current_app.db_manager)
        token = service.update_token_status(token_id, is_active)
        
        action = 'activated' if is_active else 'deactivated'
        return current_app.response_manager.success(token, f'Token {action} successfully')
        
    except ValueError as e:
        return current_app.response_manager.bad_request(str(e))
    except Exception as e:
        current_app.logger.error(f"Error updating token: {e}")
        return current_app.response_manager.server_error('Failed to update token')

@agents_bp.route('/tokens/<token_id>', methods=['DELETE'])
@jwt_required()
def delete_token(token_id):
    """Delete token (superadmin only)"""
    try:
        # For now, we'll just deactivate instead of delete to preserve history
        service = AgentsService(current_app.db_manager)
        token = service.update_token_status(token_id, False)
        
        return current_app.response_manager.success(token, 'Token deactivated successfully')
        
    except ValueError as e:
        return current_app.response_manager.not_found('Token')
    except Exception as e:
        current_app.logger.error(f"Error deleting token: {e}")
        return current_app.response_manager.server_error('Failed to delete token')

# =====================================================
# TOKEN VALIDATION ENDPOINTS
# =====================================================

@agents_bp.route('/validate-token', methods=['POST'])
def validate_installation_token():
    """Validate an installation token and return client/site information (no authentication required)"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('Request body required')

        token_value = data.get('token')
        if not token_value:
            return current_app.response_manager.bad_request('token field required')

        service = AgentsService(current_app.db_manager)
        validation_result = service.validate_token_for_installation(token_value)

        return current_app.response_manager.success(validation_result)

    except ValueError as e:
        return current_app.response_manager.bad_request(str(e))
    except Exception as e:
        current_app.logger.error(f"Error validating token: {e}")
        return current_app.response_manager.server_error('Failed to validate token')

# =====================================================
# AGENT REGISTRATION ENDPOINTS
# =====================================================

@agents_bp.route('/register-with-token', methods=['POST'])
def register_agent_with_token():
    """Register a new agent using an installation token (no authentication required)"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('Request body required')
        
        # Validate required fields
        token_value = data.get('token')
        hardware_info = data.get('hardware_info', {})
        
        if not token_value:
            return current_app.response_manager.bad_request('token field required')
        
        if not hardware_info:
            return current_app.response_manager.bad_request('hardware_info field required')
        
        # Get client IP and user agent
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
        user_agent = request.headers.get('User-Agent', '')
        
        service = AgentsService(current_app.db_manager)
        result = service.register_agent_with_token(
            token_value=token_value,
            hardware_info=hardware_info,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return current_app.response_manager.success(result, 'Agent registered successfully')
        
    except ValueError as e:
        return current_app.response_manager.bad_request(str(e))
    except Exception as e:
        current_app.logger.error(f"Error registering agent: {e}")
        return current_app.response_manager.server_error('Failed to register agent')

# =====================================================
# AGENT COMMUNICATION ENDPOINTS
# =====================================================

@agents_bp.route('/heartbeat', methods=['POST'])
def agent_heartbeat():
    """Agent heartbeat endpoint with tiered data support (agent authentication required)"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('Request body required')

        asset_id = data.get('asset_id')
        status = data.get('status', {})
        heartbeat_type = data.get('heartbeat_type', 'full')  # 'status' or 'full'
        hardware_inventory = data.get('hardware_inventory')
        software_inventory = data.get('software_inventory')

        if not asset_id:
            return current_app.response_manager.bad_request('asset_id field required')

        current_app.logger.info(f"Received {heartbeat_type} heartbeat from asset {asset_id}")

        # Handle tiered heartbeat processing
        import json
        import hashlib

        if heartbeat_type == 'status':
            # TIER 1: Lightweight status update (optimized for performance)
            current_app.logger.info(f"Processing TIER 1 status heartbeat for {asset_id}")

            # Update optimized status table
            status_update_query = """
            INSERT INTO assets_status_optimized (
                asset_id, agent_status, cpu_percent, memory_percent,
                disk_percent, last_seen, last_heartbeat, updated_at
            ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), NOW())
            ON CONFLICT (asset_id) DO UPDATE SET
                agent_status = EXCLUDED.agent_status,
                cpu_percent = EXCLUDED.cpu_percent,
                memory_percent = EXCLUDED.memory_percent,
                disk_percent = EXCLUDED.disk_percent,
                last_seen = EXCLUDED.last_seen,
                last_heartbeat = EXCLUDED.last_heartbeat,
                updated_at = EXCLUDED.updated_at
            """

            current_app.db_manager.execute_query(
                status_update_query,
                (
                    asset_id,
                    status.get('agent_status', 'online'),
                    status.get('cpu_percent', 0),
                    status.get('memory_percent', 0),
                    status.get('disk_percent', 0)
                ),
                fetch='none'
            )

            # NUEVO: Registrar heartbeat en tabla asset_heartbeats
            heartbeat_insert_query = """
            INSERT INTO asset_heartbeats (
                asset_id, cpu_usage, memory_usage, disk_usage,
                status, agent_version, network_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            current_app.db_manager.execute_query(
                heartbeat_insert_query,
                (
                    asset_id,
                    status.get('cpu_percent', 0),
                    status.get('memory_percent', 0),
                    status.get('disk_percent', 0),
                    status.get('agent_status', 'online'),
                    status.get('agent_version', '1.0.0'),
                    'connected'
                ),
                fetch='none'
            )

            # Return shorter interval for status heartbeats
            return current_app.response_manager.success({
                'status': 'ok',
                'next_heartbeat': 300  # 5 minutes for status heartbeats
            })

        else:
            # TIER 2: Full heartbeat with inventory (less frequent)
            current_app.logger.info(f"TIER 2: Processing full heartbeat for {asset_id}")
            current_app.logger.info(f"Hardware inventory present: {bool(hardware_inventory)}")
            current_app.logger.info(f"Software inventory present: {bool(software_inventory)}")

            # Log SMART data if present
            if hardware_inventory and 'disks' in hardware_inventory:
                disks = hardware_inventory['disks']
                current_app.logger.info(f"Found {len(disks)} disks in hardware inventory")
                for i, disk in enumerate(disks):
                    health = disk.get('health_status', 'Unknown')
                    smart = disk.get('smart_status', 'Unknown')
                    model = disk.get('model', 'Unknown')
                    interface = disk.get('interface_type', 'Unknown')
                    current_app.logger.info(f"  Disk {i+1}: {model} - Health: '{health}', SMART: '{smart}', Interface: '{interface}'")
                    current_app.logger.info(f"    All disk keys: {list(disk.keys())}")
            else:
                current_app.logger.warning("No disk data found in hardware_inventory")

            # Update status table
            status_update_query = """
            INSERT INTO assets_status_optimized (
                asset_id, agent_status, cpu_percent, memory_percent,
                disk_percent, last_seen, last_heartbeat, updated_at
            ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), NOW())
            ON CONFLICT (asset_id) DO UPDATE SET
                agent_status = EXCLUDED.agent_status,
                cpu_percent = EXCLUDED.cpu_percent,
                memory_percent = EXCLUDED.memory_percent,
                disk_percent = EXCLUDED.disk_percent,
                last_seen = EXCLUDED.last_seen,
                last_heartbeat = EXCLUDED.last_heartbeat,
                updated_at = EXCLUDED.updated_at
            """

            current_app.db_manager.execute_query(
                status_update_query,
                (
                    asset_id,
                    status.get('agent_status', 'online'),
                    status.get('cpu_usage', 0),
                    status.get('memory_usage', 0),
                    status.get('disk_usage', 0)
                ),
                fetch='none'
            )

            # NUEVO: Registrar heartbeat completo en tabla asset_heartbeats
            heartbeat_insert_query = """
            INSERT INTO asset_heartbeats (
                asset_id, cpu_usage, memory_usage, disk_usage,
                status, agent_version, network_status, system_uptime
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            current_app.db_manager.execute_query(
                heartbeat_insert_query,
                (
                    asset_id,
                    status.get('cpu_usage', 0),
                    status.get('memory_usage', 0),
                    status.get('disk_usage', 0),
                    status.get('agent_status', 'online'),
                    status.get('agent_version', '1.0.0'),
                    'connected',
                    status.get('uptime', 0)
                ),
                fetch='none'
            )

            # Update inventory if provided
            if hardware_inventory or software_inventory:
                current_app.logger.info(f"Updating inventory snapshot for {asset_id}")

                # Create inventory snapshot
                inventory_data = {
                    'hardware_info': hardware_inventory or {},
                    'software_info': software_inventory or {}
                }

                inventory_hash = hashlib.md5(json.dumps(inventory_data, sort_keys=True).encode()).hexdigest()

                # Insert or update inventory snapshot
                inventory_query = """
                INSERT INTO assets_inventory_snapshots (
                    asset_id, hardware_summary, software_summary,
                    full_inventory_compressed, inventory_hash
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (asset_id, version) DO UPDATE SET
                    hardware_summary = EXCLUDED.hardware_summary,
                    software_summary = EXCLUDED.software_summary,
                    full_inventory_compressed = EXCLUDED.full_inventory_compressed,
                    inventory_hash = EXCLUDED.inventory_hash,
                    created_at = NOW()
                """

                import gzip
                compressed_inventory = gzip.compress(json.dumps(inventory_data).encode())

                # Log what we're about to save
                current_app.logger.info(f"SAVING TO DB: About to save hardware inventory for {asset_id}")
                if hardware_inventory and 'disks' in hardware_inventory:
                    for i, disk in enumerate(hardware_inventory['disks']):
                        current_app.logger.info(f"SAVING DISK {i+1}: health='{disk.get('health_status')}', smart='{disk.get('smart_status')}', interface='{disk.get('interface_type')}'")

                current_app.db_manager.execute_query(
                    inventory_query,
                    (
                        asset_id,
                        json.dumps(hardware_inventory or {}),
                        json.dumps(software_inventory or {}),
                        compressed_inventory,
                        inventory_hash
                    ),
                    fetch='none'
                )

                current_app.logger.info(f"SAVED TO DB: Hardware inventory saved successfully for {asset_id}")

                # Process BitLocker data if present
                if hardware_inventory and 'bitlocker' in hardware_inventory:
                    try:
                        current_app.logger.info(f"Processing BitLocker data for asset {asset_id}")
                        bitlocker_data = hardware_inventory['bitlocker']
                        
                        if bitlocker_data.get('supported') and bitlocker_data.get('volumes'):
                            from utils.encryption import encrypt_data
                            
                            for volume in bitlocker_data['volumes']:
                                volume_letter = volume.get('volume_letter')
                                recovery_key = volume.get('recovery_key')
                                
                                if volume_letter and recovery_key:
                                    # Encrypt the recovery key
                                    encrypted_key = encrypt_data(recovery_key)
                                    
                                    # Upsert BitLocker data
                                    bitlocker_upsert_query = """
                                        INSERT INTO bitlocker_keys (
                                            asset_id, volume_letter, volume_label, protection_status,
                                            encryption_method, key_protector_type, recovery_key_id,
                                            recovery_key_encrypted, last_verified_at
                                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
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
                                        bitlocker_upsert_query,
                                        (
                                            asset_id,
                                            volume_letter,
                                            volume.get('volume_label', 'Local Disk'),
                                            volume.get('protection_status', 'Unknown'),
                                            volume.get('encryption_method'),
                                            volume.get('key_protector_type'),
                                            volume.get('recovery_key_id'),
                                            encrypted_key
                                        ),
                                        fetch='none'
                                    )
                                    
                                    current_app.logger.info(f"✅ BitLocker data saved for volume {volume_letter}")
                            
                            current_app.logger.info(f"✅ BitLocker processing completed for asset {asset_id}")
                        else:
                            current_app.logger.info(f"BitLocker not supported or no volumes for asset {asset_id}")
                    
                    except Exception as e:
                        current_app.logger.error(f"Error processing BitLocker data for asset {asset_id}: {e}")

                # Process BitLocker data if present
                if hardware_inventory and 'bitlocker' in hardware_inventory:
                    try:
                        current_app.logger.info(f"Processing BitLocker data for asset {asset_id}")
                        bitlocker_data = hardware_inventory['bitlocker']
                        
                        if bitlocker_data.get('supported') and bitlocker_data.get('volumes'):
                            from utils.encryption import encrypt_data
                            
                            for volume in bitlocker_data['volumes']:
                                volume_letter = volume.get('volume_letter')
                                recovery_key = volume.get('recovery_key')
                                
                                if volume_letter and recovery_key:
                                    # Encrypt the recovery key
                                    encrypted_key = encrypt_data(recovery_key)
                                    
                                    # Upsert BitLocker data
                                    bitlocker_upsert_query = """
                                        INSERT INTO bitlocker_keys (
                                            asset_id, volume_letter, volume_label, protection_status,
                                            encryption_method, key_protector_type, recovery_key_id,
                                            recovery_key_encrypted, last_verified_at
                                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
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
                                        bitlocker_upsert_query,
                                        (
                                            asset_id,
                                            volume_letter,
                                            volume.get('volume_label', 'Local Disk'),
                                            volume.get('protection_status', 'Unknown'),
                                            volume.get('encryption_method'),
                                            volume.get('key_protector_type'),
                                            volume.get('recovery_key_id'),
                                            encrypted_key
                                        ),
                                        fetch='none'
                                    )
                                    
                                    current_app.logger.info(f"✅ BitLocker data saved for volume {volume_letter}")
                            
                            current_app.logger.info(f"✅ BitLocker processing completed for asset {asset_id}")
                        else:
                            current_app.logger.info(f"BitLocker not supported or no volumes for asset {asset_id}")
                    
                    except Exception as e:
                        current_app.logger.error(f"Error processing BitLocker data for asset {asset_id}: {e}")

                # Process BitLocker data if present
                if hardware_inventory and 'bitlocker' in hardware_inventory:
                    try:
                        current_app.logger.info(f"Processing BitLocker data for asset {asset_id}")
                        bitlocker_data = hardware_inventory['bitlocker']
                        
                        if bitlocker_data.get('supported') and bitlocker_data.get('volumes'):
                            from utils.encryption import encrypt_data
                            
                            for volume in bitlocker_data['volumes']:
                                volume_letter = volume.get('volume_letter')
                                recovery_key = volume.get('recovery_key')
                                
                                if volume_letter and recovery_key:
                                    # Encrypt the recovery key
                                    encrypted_key = encrypt_data(recovery_key)
                                    
                                    # Upsert BitLocker data
                                    bitlocker_upsert_query = """
                                        INSERT INTO bitlocker_keys (
                                            asset_id, volume_letter, volume_label, protection_status,
                                            encryption_method, key_protector_type, recovery_key_id,
                                            recovery_key_encrypted, last_verified_at
                                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
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
                                        bitlocker_upsert_query,
                                        (
                                            asset_id,
                                            volume_letter,
                                            volume.get('volume_label', 'Local Disk'),
                                            volume.get('protection_status', 'Unknown'),
                                            volume.get('encryption_method'),
                                            volume.get('key_protector_type'),
                                            volume.get('recovery_key_id'),
                                            encrypted_key
                                        ),
                                        fetch='none'
                                    )
                                    
                                    current_app.logger.info(f"✅ BitLocker data saved for volume {volume_letter}")
                            
                            current_app.logger.info(f"✅ BitLocker processing completed for asset {asset_id}")
                        else:
                            current_app.logger.info(f"BitLocker not supported or no volumes for asset {asset_id}")
                    
                    except Exception as e:
                        current_app.logger.error(f"Error processing BitLocker data for asset {asset_id}: {e}")

                # Also update main assets table for backward compatibility
                update_data = {'system_metrics': status}
                if hardware_inventory:
                    update_data['hardware_info'] = hardware_inventory
                if software_inventory:
                    update_data['software_info'] = software_inventory

                legacy_update_query = """
                UPDATE assets
                SET last_seen = NOW(),
                    agent_status = 'online',
                    specifications = COALESCE(specifications, '{}')::jsonb || %s::jsonb
                WHERE asset_id = %s
                """

                current_app.db_manager.execute_query(
                    legacy_update_query,
                    (json.dumps(update_data), asset_id),
                    fetch='none'
                )

            # Return normal interval for all heartbeats (15 minutes)
            return current_app.response_manager.success({
                'status': 'ok',
                'next_heartbeat': 900  # 15 minutes for all heartbeats
            })

    except Exception as e:
        current_app.logger.error(f"Error processing heartbeat: {e}")
        return current_app.response_manager.server_error('Failed to process heartbeat')

@agents_bp.route('/inventory', methods=['POST'])
def agent_inventory_update():
    """Agent inventory update endpoint"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('Request body required')
        
        asset_id = data.get('asset_id')
        hardware_specs = data.get('hardware_specs', {})
        software_inventory = data.get('software_inventory', [])
        
        if not asset_id:
            return current_app.response_manager.bad_request('asset_id field required')
        
        # Update asset inventory
        update_query = """
        UPDATE assets 
        SET last_inventory_update = NOW(),
            hardware_specs = %s,
            software_inventory = %s,
            last_seen = NOW(),
            agent_status = 'online'
        WHERE asset_id = %s
        """
        
        current_app.db_manager.execute_query(
            update_query, 
            (hardware_specs, software_inventory, asset_id)
        )
        
        return current_app.response_manager.success({
            'status': 'ok',
            'next_update': 3600  # seconds
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating inventory: {e}")
        return current_app.response_manager.server_error('Failed to update inventory')

@agents_bp.route('/create-ticket', methods=['POST'])
@jwt_required()
def create_ticket_from_agent():
    """Create a ticket automatically from an agent"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('Request body required')

        # Get current agent info
        current_user_id = get_jwt_identity()

        # Get agent information
        agent_query = """
        SELECT a.asset_id, a.name as asset_name, a.client_id, a.site_id,
               c.name as client_name, s.name as site_name
        FROM assets a
        JOIN clients c ON a.client_id = c.client_id
        JOIN sites s ON a.site_id = s.site_id
        WHERE a.agent_user_id = %s AND a.is_active = true
        """

        agent_info = current_app.db_manager.execute_query(
            agent_query, (current_user_id,), fetch='one'
        )

        if not agent_info:
            return current_app.response_manager.bad_request('Agent not found or not associated with an asset')

        # Validate required fields
        required_fields = ['subject', 'description', 'priority']
        for field in required_fields:
            if not data.get(field):
                return current_app.response_manager.bad_request(f'{field} is required')

        # Get assigned technician for this client/site
        technician_query = """
        SELECT ta.technician_id
        FROM technician_assignments ta
        WHERE ta.client_id = %s AND ta.is_active = true
        ORDER BY ta.is_primary DESC, ta.priority ASC
        LIMIT 1
        """

        assigned_technician = current_app.db_manager.execute_query(
            technician_query, (agent_info['client_id'],), fetch='one'
        )

        # Prepare ticket data
        ticket_data = {
            'client_id': str(agent_info['client_id']),
            'site_id': str(agent_info['site_id']),
            'asset_id': str(agent_info['asset_id']),
            'created_by': current_user_id,
            'assigned_to': assigned_technician['technician_id'] if assigned_technician else None,
            'subject': data['subject'],
            'description': f"[TICKET AUTOMÁTICO DESDE AGENTE]\n\n{data['description']}\n\n--- Información del Sistema ---\nEquipo: {agent_info['asset_name']}\nCliente: {agent_info['client_name']}\nSitio: {agent_info['site_name']}",
            'affected_person': data.get('affected_person', 'Sistema Automático'),
            'affected_person_contact': data.get('affected_person_contact', 'agente@sistema.local'),
            'priority': data['priority'],
            'channel': 'agente',
            'category_id': data.get('category_id'),
            'agent_auto_info': {
                'asset_name': agent_info['asset_name'],
                'client_name': agent_info['client_name'],
                'site_name': agent_info['site_name'],
                'created_automatically': True,
                'agent_data': data.get('agent_data', {})
            }
        }

        # Create ticket using tickets service
        from modules.tickets.service import TicketsService
        tickets_service = TicketsService(current_app.db_manager)

        result = tickets_service.create_ticket(ticket_data)

        if result:
            current_app.logger.info(f"Automatic ticket created by agent {current_user_id}: {result.get('ticket_number')}")
            return current_app.response_manager.success(result, 'Ticket created successfully from agent')
        else:
            return current_app.response_manager.server_error('Failed to create ticket from agent')

    except Exception as e:
        current_app.logger.error(f"Error creating ticket from agent: {e}")
        return current_app.response_manager.server_error('Failed to create ticket from agent')
