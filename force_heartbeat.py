#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Force send heartbeat with inventory data
"""

import sys
import os
import logging
import json
import requests
from datetime import datetime

# Add the agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lanet_agent'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def force_heartbeat():
    """Force send heartbeat with inventory data"""
    print("🚀 Forcing heartbeat with inventory data...")
    
    try:
        # Import modules
        from modules.monitoring import MonitoringModule
        from core.database import DatabaseManager
        
        # Create database manager
        database = DatabaseManager("data/agent.db")
        
        # Get registration info
        asset_id = database.get_config('asset_id')
        agent_token = database.get_config('agent_token')
        
        if not asset_id or not agent_token:
            print("❌ No registration info found")
            return False
        
        print(f"✅ Asset ID: {asset_id}")
        print(f"✅ Token: {agent_token[:20]}...")
        
        # Create mock config
        class MockConfig:
            def get(self, key, default=None):
                if key == 'server.base_url':
                    return 'http://localhost:5001/api'
                return default
            
            def get_server_url(self):
                return 'http://localhost:5001/api'
        
        config = MockConfig()
        
        # Create monitoring module
        monitoring = MonitoringModule(config, database)
        
        # Get system status
        print("📊 Getting system status...")
        import psutil
        status = {
            'cpu_percent': round(psutil.cpu_percent(interval=1), 1),
            'memory_percent': round(psutil.virtual_memory().percent, 1),
            'disk_percent': round(psutil.disk_usage('/').percent, 1) if os.name != 'nt' else round(psutil.disk_usage('C:').percent, 1),
            'agent_status': 'online'
        }
        print(f"✅ Status: CPU {status['cpu_percent']}%, RAM {status['memory_percent']}%, Disk {status['disk_percent']}%")
        
        # Get inventories
        print("🔧 Getting hardware inventory...")
        hardware_inventory = monitoring.get_hardware_inventory()
        print(f"✅ Hardware inventory: {len(str(hardware_inventory))} characters")
        
        print("📦 Getting software inventory...")
        software_inventory = monitoring.get_software_inventory()
        print(f"✅ Software inventory: {len(str(software_inventory))} characters")
        
        if 'installed_programs' in software_inventory:
            print(f"📋 Found {len(software_inventory['installed_programs'])} installed programs")
        
        # Prepare heartbeat data
        heartbeat_data = {
            'asset_id': asset_id,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'hardware_inventory': hardware_inventory,
            'software_inventory': software_inventory
        }
        
        print(f"📊 Total heartbeat data: {len(str(heartbeat_data))} characters")
        
        # Send heartbeat
        server_url = 'http://localhost:5001/api'
        heartbeat_url = f"{server_url}/agents/heartbeat"
        
        print(f"🚀 Sending heartbeat to {heartbeat_url}")
        
        headers = {
            'Authorization': f'Bearer {agent_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'LANET-Agent/1.0.0'
        }
        
        response = requests.post(
            heartbeat_url,
            json=heartbeat_data,
            headers=headers,
            timeout=60
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Heartbeat sent successfully!")
            print(f"Response: {response.text}")
            
            # Update database
            database.set_config('last_heartbeat', datetime.now().isoformat())
            database.set_config('last_inventory_sent', datetime.now().isoformat())
            
            return True
        else:
            print(f"❌ Heartbeat failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error forcing heartbeat: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    force_heartbeat()
