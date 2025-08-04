#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify software inventory works and shows in database
"""

import sys
import os
import logging
import json

# Add the agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lanet_agent'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_software_inventory_simple():
    """Test software inventory and verify it appears in database"""
    print("🧪 Testing software inventory simple...")
    
    try:
        # Import the monitoring module
        from modules.monitoring import MonitoringModule
        
        # Create mock objects
        class MockConfig:
            def get(self, key, default=None):
                return default
        
        class MockDatabase:
            def store_metrics(self, metrics):
                pass
            def set_config(self, key, value):
                pass
        
        config = MockConfig()
        database = MockDatabase()
        
        # Create monitoring module
        monitoring = MonitoringModule(config, database)
        
        print("\n🔍 Testing software inventory...")
        software_info = monitoring.get_software_inventory()
        
        if software_info:
            print("✅ Software inventory collected successfully!")
            print(f"📋 Software keys: {list(software_info.keys())}")
            
            # Show installed programs
            if 'installed_programs' in software_info:
                programs = software_info['installed_programs']
                print(f"  📦 Installed programs: {len(programs)} found")
                for i, program in enumerate(programs[:10]):  # Show first 10
                    name = program.get('name', 'Unknown')
                    version = program.get('version', 'N/A')
                    publisher = program.get('publisher', 'N/A')
                    print(f"    {i+1}. {name} ({version}) - {publisher}")
                
                if len(programs) > 10:
                    print(f"    ... and {len(programs) - 10} more")
            else:
                print("❌ No installed_programs found")
            
            # Show system info
            if 'system_info' in software_info:
                sys_info = software_info['system_info']
                print(f"  💻 System info: {len(sys_info)} fields")
                for key, value in sys_info.items():
                    print(f"    {key}: {value}")
            
            # Test JSON serialization
            try:
                json_str = json.dumps(software_info)
                print(f"  ✅ JSON serialization successful ({len(json_str)} characters)")
            except Exception as e:
                print(f"  ❌ JSON serialization failed: {e}")
        else:
            print("❌ Software inventory failed")
        
        print("\n✅ Software inventory test completed!")
        
    except Exception as e:
        print(f"❌ Error testing software inventory: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_software_inventory_simple()
