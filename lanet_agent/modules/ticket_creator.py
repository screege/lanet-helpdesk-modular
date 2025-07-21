#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent - Ticket Creator Module
Handles ticket creation from the agent
"""

import logging
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
import platform
import getpass

class TicketCreatorModule:
    """Handles ticket creation through the agent"""
    
    def __init__(self, config_manager, database_manager):
        self.logger = logging.getLogger('lanet_agent.ticket_creator')
        self.config = config_manager
        self.database = database_manager
        
        # HTTP session for requests
        self.session = requests.Session()
        self.session.timeout = self.config.get('server.timeout', 30)
        
        # Configure SSL verification
        verify_ssl = self.config.get('server.verify_ssl', True)
        if not verify_ssl:
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.logger.info("Ticket creator module initialized")
    
    def create_ticket(self, subject: str, description: str, priority: str = 'media', 
                     include_system_info: bool = True) -> bool:
        """Create a ticket through the agent"""
        try:
            self.logger.info(f"Creating ticket: {subject}")
            
            # Get registration info
            asset_id = self.database.get_config('asset_id')
            agent_token = self.database.get_config('agent_token')
            
            if not asset_id or not agent_token:
                self.logger.error("No registration info found - cannot create ticket")
                return False
            
            # Prepare ticket data
            ticket_data = {
                'subject': subject,
                'description': description,
                'priority': priority,
                'channel': 'agente',
                'created_by_agent': True
            }
            
            # Add system information if requested
            if include_system_info:
                agent_auto_info = self._collect_agent_auto_info()
                ticket_data['agent_auto_info'] = agent_auto_info
                
                # Append system info to description
                system_info_text = self._format_system_info_for_description(agent_auto_info)
                ticket_data['description'] += f"\n\n--- Información del Sistema ---\n{system_info_text}"
            
            # Get server URL
            server_url = self.config.get_server_url()
            
            # Try the agent-specific endpoint first
            ticket_url = f"{server_url}/agents/create-ticket"
            
            # Send ticket creation request
            response = self.session.post(
                ticket_url,
                json=ticket_data,
                headers={
                    'Authorization': f'Bearer {agent_token}',
                    'Content-Type': 'application/json',
                    'User-Agent': f"LANET-Agent/{self.config.get('agent.version', '1.0.0')}"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Ticket created successfully: {result.get('message', 'OK')}")
                
                # Store ticket info locally
                if 'data' in result:
                    ticket_info = result['data']
                    self._store_ticket_locally(ticket_info)
                    
                    # Log success
                    self.logger.info(f"Ticket #{ticket_info.get('ticket_number')} created successfully")
                    return True
                else:
                    self.logger.warning("Ticket created but no data returned")
                    return True
                    
            elif response.status_code == 404:
                # Fallback to regular ticket endpoint
                self.logger.info("Agent endpoint not found, trying regular ticket endpoint")
                return self._create_ticket_fallback(ticket_data, agent_token)
            else:
                error_msg = f"Ticket creation failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('message', 'Unknown error')}"
                except:
                    error_msg += f": {response.text}"
                
                self.logger.error(error_msg)
                return False
                
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error during ticket creation: {e}")
            return False
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout during ticket creation: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during ticket creation: {e}", exc_info=True)
            return False
    
    def _create_ticket_fallback(self, ticket_data: Dict[str, Any], agent_token: str) -> bool:
        """Fallback to regular ticket creation endpoint"""
        try:
            server_url = self.config.get_server_url()
            ticket_url = f"{server_url}/tickets/"
            
            response = self.session.post(
                ticket_url,
                json=ticket_data,
                headers={
                    'Authorization': f'Bearer {agent_token}',
                    'Content-Type': 'application/json',
                    'User-Agent': f"LANET-Agent/{self.config.get('agent.version', '1.0.0')}"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Ticket created via fallback: {result.get('message', 'OK')}")
                
                if 'data' in result:
                    ticket_info = result['data']
                    self._store_ticket_locally(ticket_info)
                
                return True
            else:
                self.logger.error(f"Fallback ticket creation failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in fallback ticket creation: {e}")
            return False
    
    def _collect_agent_auto_info(self) -> Dict[str, Any]:
        """Collect automatic system information for tickets"""
        try:
            # Get basic system info
            auto_info = {
                'computer_name': platform.node(),
                'current_user': getpass.getuser(),
                'os': platform.system(),
                'os_version': platform.version(),
                'agent_version': self.config.get('agent.version', '1.0.0'),
                'collection_timestamp': datetime.now().isoformat()
            }
            
            # Get current system metrics
            recent_metrics = self.database.get_recent_metrics(1)
            if recent_metrics:
                metrics = recent_metrics[0]
                auto_info['system_metrics'] = {
                    'cpu_usage': metrics.get('cpu_usage', 0),
                    'memory_usage': metrics.get('memory_usage', 0),
                    'disk_usage': metrics.get('disk_usage', 0),
                    'uptime_hours': round(metrics.get('uptime', 0) / 3600, 1),
                    'network_status': metrics.get('network_status', 'unknown')
                }
            
            # Get recent system events/logs if available
            auto_info['recent_events'] = self._get_recent_system_events()
            
            # Get running processes count
            try:
                import psutil
                auto_info['processes_count'] = len(psutil.pids())
                
                # Get top CPU processes
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                    try:
                        proc_info = proc.info
                        if proc_info['cpu_percent'] > 5:  # Only processes using >5% CPU
                            processes.append({
                                'name': proc_info['name'],
                                'cpu_percent': proc_info['cpu_percent']
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Sort by CPU usage and take top 5
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
                auto_info['high_cpu_processes'] = processes[:5]
                
            except Exception as e:
                self.logger.debug(f"Could not get process info: {e}")
            
            return auto_info
            
        except Exception as e:
            self.logger.error(f"Error collecting agent auto info: {e}")
            return {
                'computer_name': platform.node(),
                'current_user': getpass.getuser(),
                'error': str(e),
                'collection_timestamp': datetime.now().isoformat()
            }
    
    def _get_recent_system_events(self) -> list:
        """Get recent system events (simplified for now)"""
        try:
            # This is a placeholder - in a full implementation you might:
            # - Check Windows Event Log
            # - Check system logs
            # - Check application logs
            # For now, return basic info
            
            events = []
            
            # Check if any alerts were logged recently
            # This would integrate with the monitoring module
            
            return events
            
        except Exception as e:
            self.logger.debug(f"Could not get recent events: {e}")
            return []
    
    def _format_system_info_for_description(self, auto_info: Dict[str, Any]) -> str:
        """Format system information for ticket description"""
        try:
            lines = []
            
            # Basic system info
            lines.append(f"Equipo: {auto_info.get('computer_name', 'N/A')}")
            lines.append(f"Usuario: {auto_info.get('current_user', 'N/A')}")
            lines.append(f"Sistema: {auto_info.get('os', 'N/A')} {auto_info.get('os_version', '')}")
            
            # System metrics
            if 'system_metrics' in auto_info:
                metrics = auto_info['system_metrics']
                lines.append(f"CPU: {metrics.get('cpu_usage', 0):.1f}%")
                lines.append(f"Memoria: {metrics.get('memory_usage', 0):.1f}%")
                lines.append(f"Disco: {metrics.get('disk_usage', 0):.1f}%")
                lines.append(f"Tiempo encendido: {metrics.get('uptime_hours', 0)} horas")
                lines.append(f"Red: {metrics.get('network_status', 'N/A')}")
            
            # High CPU processes
            if 'high_cpu_processes' in auto_info and auto_info['high_cpu_processes']:
                lines.append("\nProcesos con alto uso de CPU:")
                for proc in auto_info['high_cpu_processes']:
                    lines.append(f"- {proc['name']}: {proc['cpu_percent']:.1f}%")
            
            # Recent events
            if 'recent_events' in auto_info and auto_info['recent_events']:
                lines.append("\nEventos recientes del sistema:")
                for event in auto_info['recent_events']:
                    lines.append(f"- {event}")
            
            lines.append(f"\nAgente versión: {auto_info.get('agent_version', 'N/A')}")
            lines.append(f"Información recopilada: {auto_info.get('collection_timestamp', 'N/A')}")
            
            return "\n".join(lines)
            
        except Exception as e:
            self.logger.error(f"Error formatting system info: {e}")
            return f"Error al formatear información del sistema: {e}"
    
    def _store_ticket_locally(self, ticket_info: Dict[str, Any]):
        """Store ticket information locally for reference"""
        try:
            ticket_id = ticket_info.get('ticket_id')
            if ticket_id:
                # Store in database
                self.database.set_config(f'ticket_{ticket_id}', {
                    'ticket_id': ticket_id,
                    'ticket_number': ticket_info.get('ticket_number'),
                    'subject': ticket_info.get('subject'),
                    'status': ticket_info.get('status'),
                    'priority': ticket_info.get('priority'),
                    'created_at': ticket_info.get('created_at'),
                    'created_via_agent': True,
                    'stored_at': datetime.now().isoformat()
                })
                
                self.logger.info(f"Ticket {ticket_id} stored locally")
                
        except Exception as e:
            self.logger.error(f"Error storing ticket locally: {e}")
    
    def get_my_tickets(self) -> list:
        """Get tickets created by this agent (placeholder)"""
        try:
            # This would query the backend for tickets from this asset
            # For now, return locally stored tickets
            
            tickets = []
            # Implementation would go here
            
            return tickets
            
        except Exception as e:
            self.logger.error(f"Error getting my tickets: {e}")
            return []
