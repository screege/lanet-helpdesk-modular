#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BitLocker module for LANET Agent
Collects BitLocker status and recovery keys from Windows systems
"""

import platform
import subprocess
import json
import logging
from typing import Dict, List, Optional

class BitLockerCollector:
    """Collects BitLocker information from Windows systems"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_windows = platform.system() == 'Windows'
    
    def get_bitlocker_info(self) -> Dict:
        """Get comprehensive BitLocker information"""
        try:
            if not self.is_windows:
                self.logger.info("BitLocker collection skipped - not a Windows system")
                return {
                    'supported': False,
                    'reason': 'Not a Windows system',
                    'volumes': []
                }

            self.logger.info("Starting BitLocker information collection...")

            # Get BitLocker volumes
            volumes = self._get_bitlocker_volumes()

            # If no volumes found, it might be a permission issue
            if not volumes:
                # Check if BitLocker is available but we lack permissions
                if self.is_bitlocker_available():
                    self.logger.warning("BitLocker is available but no volumes found - likely permission issue")
                    return {
                        'supported': True,
                        'permission_required': True,
                        'reason': 'Administrator privileges required to access BitLocker information',
                        'total_volumes': 0,
                        'protected_volumes': 0,
                        'unprotected_volumes': 0,
                        'volumes': [],
                        'collection_timestamp': self._get_timestamp()
                    }
                else:
                    self.logger.info("BitLocker not available on this system")
                    return {
                        'supported': False,
                        'reason': 'BitLocker not available on this system',
                        'volumes': []
                    }

            # Calculate summary
            total_volumes = len(volumes)
            protected_volumes = len([v for v in volumes if v.get('protection_status') == 'Protected'])

            result = {
                'supported': True,
                'permission_required': False,
                'total_volumes': total_volumes,
                'protected_volumes': protected_volumes,
                'unprotected_volumes': total_volumes - protected_volumes,
                'volumes': volumes,
                'collection_timestamp': self._get_timestamp()
            }

            self.logger.info(f"BitLocker collection completed: {protected_volumes}/{total_volumes} volumes protected")
            return result

        except Exception as e:
            self.logger.error(f"BitLocker collection failed: {e}")
            return {
                'supported': False,
                'reason': f'Collection failed: {str(e)}',
                'volumes': []
            }
    
    def _get_bitlocker_volumes(self) -> List[Dict]:
        """Get BitLocker information for all volumes"""
        try:
            volumes = []

            # First try PowerShell method
            volumes = self._get_volumes_powershell()
            if volumes:
                return volumes

            # If PowerShell failed, try manage-bde method
            self.logger.info("PowerShell method failed, trying manage-bde...")
            volumes = self._get_volumes_manage_bde()
            if volumes:
                return volumes

            # If both methods failed, check if it's a permission issue
            self._check_permissions()
            return []

        except Exception as e:
            self.logger.error(f"Failed to get BitLocker volumes: {e}")
            return []

    def _get_volumes_powershell(self) -> List[Dict]:
        """Get BitLocker volumes using PowerShell"""
        try:
            # Get all BitLocker volumes using PowerShell
            powershell_cmd = """
            try {
                Get-BitLockerVolume | ForEach-Object {
                    $volume = $_
                    $keyProtectors = $volume.KeyProtector

                    # Get recovery password key protector
                    $recoveryKey = $keyProtectors | Where-Object { $_.KeyProtectorType -eq 'RecoveryPassword' } | Select-Object -First 1

                    [PSCustomObject]@{
                        MountPoint = $volume.MountPoint
                        VolumeLabel = if ($volume.VolumeLabel) { $volume.VolumeLabel } else { "Local Disk" }
                        ProtectionStatus = $volume.ProtectionStatus.ToString()
                        EncryptionMethod = $volume.EncryptionMethod.ToString()
                        VolumeStatus = $volume.VolumeStatus.ToString()
                        EncryptionPercentage = $volume.EncryptionPercentage
                        KeyProtectorCount = $keyProtectors.Count
                        RecoveryKeyId = if ($recoveryKey) { $recoveryKey.KeyProtectorId } else { $null }
                        RecoveryPassword = if ($recoveryKey) { $recoveryKey.RecoveryPassword } else { $null }
                        KeyProtectorTypes = ($keyProtectors | ForEach-Object { $_.KeyProtectorType.ToString() }) -join ","
                    }
                } | ConvertTo-Json -Depth 3
            } catch {
                Write-Error "PERMISSION_DENIED: $($_.Exception.Message)"
            }
            """

            result = subprocess.run(
                ['powershell', '-Command', powershell_cmd],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                if "PERMISSION_DENIED" in error_msg or "Acceso denegado" in error_msg:
                    self.logger.warning("BitLocker access denied - administrator privileges required")
                    return []
                else:
                    self.logger.error(f"PowerShell command failed: {error_msg}")
                    return []

            if not result.stdout.strip():
                self.logger.info("No BitLocker volumes found via PowerShell")
                return []

            # Parse JSON output
            try:
                bitlocker_data = json.loads(result.stdout)

                # Handle single volume (not in array)
                if isinstance(bitlocker_data, dict):
                    bitlocker_data = [bitlocker_data]

                # Process each volume
                volumes = []
                for volume_data in bitlocker_data:
                    volume_info = self._process_volume_data(volume_data)
                    if volume_info:
                        volumes.append(volume_info)

                self.logger.info(f"Found {len(volumes)} BitLocker volumes via PowerShell")
                return volumes

            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse BitLocker JSON output: {e}")
                self.logger.debug(f"Raw output: {result.stdout}")
                return []

        except subprocess.TimeoutExpired:
            self.logger.error("BitLocker PowerShell command timed out")
            return []
        except Exception as e:
            self.logger.error(f"PowerShell BitLocker collection failed: {e}")
            return []

    def _get_volumes_manage_bde(self) -> List[Dict]:
        """Get BitLocker volumes using manage-bde command"""
        try:
            result = subprocess.run(
                ['manage-bde', '-status'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stdout + result.stderr
                if "se denegó un intento" in error_msg or "access" in error_msg.lower():
                    self.logger.warning("manage-bde access denied - administrator privileges required")
                    return []
                else:
                    self.logger.error(f"manage-bde command failed: {error_msg}")
                    return []

            # Parse manage-bde output
            volumes = self._parse_manage_bde_output(result.stdout)
            self.logger.info(f"Found {len(volumes)} BitLocker volumes via manage-bde")
            return volumes

        except subprocess.TimeoutExpired:
            self.logger.error("manage-bde command timed out")
            return []
        except Exception as e:
            self.logger.error(f"manage-bde BitLocker collection failed: {e}")
            return []
    
    def _parse_manage_bde_output(self, output: str) -> List[Dict]:
        """Parse manage-bde -status output"""
        volumes = []
        try:
            lines = output.split('\n')
            current_volume = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Look for volume identifier (e.g., "Volumen C:")
                if line.startswith('Volumen ') and ':' in line:
                    if current_volume:
                        volumes.append(current_volume)

                    volume_letter = line.split()[1].rstrip(':')
                    current_volume = {
                        'volume_letter': volume_letter,
                        'volume_label': 'Local Disk',
                        'protection_status': 'Unknown',
                        'encryption_method': 'Unknown',
                        'volume_status': 'Unknown',
                        'encryption_percentage': 0,
                        'key_protector_type': 'Unknown',
                        'key_protector_count': 0,
                        'recovery_key_id': None,
                        'recovery_key': None
                    }

                elif current_volume:
                    # Parse volume properties
                    if 'Estado de cifrado:' in line:
                        status = line.split(':', 1)[1].strip()
                        if 'Cifrado' in status:
                            current_volume['protection_status'] = 'Protected'
                        else:
                            current_volume['protection_status'] = 'Unprotected'

                    elif 'Método de cifrado:' in line:
                        method = line.split(':', 1)[1].strip()
                        current_volume['encryption_method'] = method

                    elif 'Porcentaje cifrado:' in line:
                        try:
                            percentage_str = line.split(':', 1)[1].strip().replace('%', '')
                            current_volume['encryption_percentage'] = float(percentage_str)
                        except:
                            pass

            # Add the last volume
            if current_volume:
                volumes.append(current_volume)

            return volumes

        except Exception as e:
            self.logger.error(f"Failed to parse manage-bde output: {e}")
            return []

    def _check_permissions(self) -> None:
        """Check if the agent has the necessary permissions for BitLocker access"""
        try:
            # Try a simple test to see if we have admin privileges
            result = subprocess.run(
                ['powershell', '-Command', 'Test-Path "HKLM:\\SOFTWARE"'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip() == 'True':
                self.logger.warning("BitLocker access requires administrator privileges")
                self.logger.warning("Please run the agent as administrator to collect BitLocker information")
            else:
                self.logger.error("Unable to determine permission level")

        except Exception as e:
            self.logger.debug(f"Permission check failed: {e}")

    def _process_volume_data(self, volume_data: Dict) -> Optional[Dict]:
        """Process raw volume data into standardized format"""
        try:
            mount_point = volume_data.get('MountPoint', '').strip()
            if not mount_point:
                return None

            # Map protection status
            protection_status = volume_data.get('ProtectionStatus', 'Unknown')
            if protection_status == 'On':
                protection_status = 'Protected'
            elif protection_status == 'Off':
                protection_status = 'Unprotected'

            # Get key protector types
            key_protector_types = volume_data.get('KeyProtectorTypes', '')
            if key_protector_types:
                key_protector_type = key_protector_types.replace(',', ' + ')
            else:
                key_protector_type = 'None'

            volume_info = {
                'volume_letter': mount_point,
                'volume_label': volume_data.get('VolumeLabel', 'Local Disk'),
                'protection_status': protection_status,
                'encryption_method': volume_data.get('EncryptionMethod', 'Unknown'),
                'volume_status': volume_data.get('VolumeStatus', 'Unknown'),
                'encryption_percentage': volume_data.get('EncryptionPercentage', 0),
                'key_protector_type': key_protector_type,
                'key_protector_count': volume_data.get('KeyProtectorCount', 0),
                'recovery_key_id': volume_data.get('RecoveryKeyId'),
                'recovery_key': volume_data.get('RecoveryPassword')
            }

            self.logger.info(f"Processed BitLocker volume {mount_point}: {protection_status}")
            if volume_info['recovery_key']:
                self.logger.info(f"  Recovery key available for {mount_point}")

            return volume_info

        except Exception as e:
            self.logger.error(f"Failed to process volume data: {e}")
            return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def is_bitlocker_available(self) -> bool:
        """Check if BitLocker is available on this system"""
        if not self.is_windows:
            return False
        
        try:
            # Try to run Get-BitLockerVolume to see if BitLocker is available
            result = subprocess.run(
                ['powershell', '-Command', 'Get-Command Get-BitLockerVolume -ErrorAction SilentlyContinue'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0 and result.stdout.strip()
            
        except Exception as e:
            self.logger.debug(f"BitLocker availability check failed: {e}")
            return False
