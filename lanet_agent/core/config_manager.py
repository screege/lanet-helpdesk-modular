#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent - Configuration Manager
Handles all configuration management for the agent
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

class ConfigManager:
    """Manages agent configuration from JSON files and environment variables"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger('lanet_agent.config')
        
        # Default configuration file
        if config_file is None:
            config_file = Path(__file__).parent.parent / "config" / "agent_config.json"
        
        self.config_file = Path(config_file)
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self.logger.warning(f"Configuration file not found: {self.config_file}")
                self.config = self._get_default_config()
                self.save_config()
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.config = self._get_default_config()
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            # Ensure config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'server.base_url')"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        # Check for environment variable override
        env_key = f"LANET_AGENT_{key.upper().replace('.', '_')}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            # Try to convert to appropriate type
            if isinstance(value, bool):
                return env_value.lower() in ('true', '1', 'yes', 'on')
            elif isinstance(value, int):
                try:
                    return int(env_value)
                except ValueError:
                    pass
            elif isinstance(value, float):
                try:
                    return float(env_value)
                except ValueError:
                    pass
            return env_value
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def get_server_url(self) -> str:
        """Get the appropriate server URL based on environment"""
        environment = self.get('server.environment', 'development')
        if environment == 'production':
            return self.get('server.production_url')
        else:
            return self.get('server.base_url')
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "server": {
                "base_url": "http://localhost:5001/api",
                "production_url": "https://helpdesk.lanet.mx/api",
                "timeout": 30,
                "retry_attempts": 3,
                "verify_ssl": True,
                "environment": "development"
            },
            "agent": {
                "heartbeat_interval": 60,
                "inventory_interval": 3600,
                "metrics_interval": 300,
                "log_level": "INFO",
                "auto_start": True,
                "version": "1.0.0"
            },
            "ui": {
                "show_notifications": True,
                "minimize_to_tray": True,
                "auto_hide_after": 5000,
                "language": "es"
            },
            "monitoring": {
                "cpu_threshold": 90,
                "memory_threshold": 85,
                "disk_threshold": 90,
                "collect_logs": True,
                "max_log_entries": 100
            },
            "security": {
                "require_approval_for_scripts": True,
                "allow_remote_assistance": True,
                "encrypt_communications": True
            },
            "database": {
                "local_db_path": "data/agent.db",
                "backup_interval": 86400,
                "max_backup_files": 7
            }
        }
