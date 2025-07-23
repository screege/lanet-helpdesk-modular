#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Force a full heartbeat to see what data is being sent
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'lanet_agent'))

from lanet_agent.modules.config_manager import ConfigManager
from lanet_agent.modules.database_manager import DatabaseManager
from lanet_agent.modules.monitoring import MonitoringModule
from lanet_agent.modules.heartbeat import HeartbeatModule

def force_full_heartbeat():
    """Force a full heartbeat to see the data"""
    try:
        print("🔧 Initializing agent modules...")
        
        # Initialize modules
        config = ConfigManager()
        database = DatabaseManager(config)
        monitoring = MonitoringModule(config, database)
        heartbeat = HeartbeatModule(config, database, monitoring)
        
        print("📦 Forcing full heartbeat with inventory...")
        
        # Force a full heartbeat
        success = heartbeat.send_heartbeat(include_inventory=True)
        
        if success:
            print("✅ Full heartbeat sent successfully!")
        else:
            print("❌ Full heartbeat failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    force_full_heartbeat()
