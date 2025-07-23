#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify detailed inventory methods
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

def test_detailed_inventory():
    """Test the detailed inventory methods"""
    print("🧪 Testing detailed inventory methods...")
    
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
        
        print("\n🔍 Testing hardware inventory...")
        hardware_info = monitoring.get_hardware_inventory()
        
        if hardware_info:
            print("✅ Hardware inventory collected successfully!")
            print(f"📋 Hardware keys: {list(hardware_info.keys())}")
            
            # Show system info
            if 'system' in hardware_info:
                system = hardware_info['system']
                print(f"  System: {system.get('hostname', 'N/A')} - {system.get('platform', 'N/A')}")
                print(f"  Processor: {system.get('processor', 'N/A')}")
                print(f"  Architecture: {system.get('architecture', 'N/A')}")
            
            # Show CPU info
            if 'cpu' in hardware_info:
                cpu = hardware_info['cpu']
                print(f"  CPU: {cpu.get('name', 'N/A')}")
                print(f"  Cores: {cpu.get('cores_logical', 'N/A')} logical, {cpu.get('cores_physical', 'N/A')} physical")
                print(f"  Frequency: {cpu.get('frequency_current', 'N/A')} MHz")
            
            # Show memory info
            if 'memory' in hardware_info:
                memory = hardware_info['memory']
                print(f"  Memory: {memory.get('total_gb', 'N/A')} GB total")
                print(f"  Usage: {memory.get('usage_percent', 'N/A')}%")
            
            # Show disk info
            if 'disks' in hardware_info:
                disks = hardware_info['disks']
                print(f"  Disks: {len(disks)} found")
                for i, disk in enumerate(disks[:3]):  # Show first 3
                    print(f"    Disk {i+1}: {disk.get('device', 'N/A')} - {disk.get('total_gb', 'N/A')} GB")
                    print(f"      Usage: {disk.get('usage_percent', 'N/A')}%")
                    print(f"      Health: {disk.get('smart_status', 'N/A')}")
            
            # Show network info
            if 'network_interfaces' in hardware_info:
                interfaces = hardware_info['network_interfaces']
                print(f"  Network: {len(interfaces)} interfaces found")
                for i, interface in enumerate(interfaces[:3]):  # Show first 3
                    print(f"    Interface {i+1}: {interface.get('name', 'N/A')}")
                    print(f"      MAC: {interface.get('mac_address', 'N/A')}")
                    print(f"      Status: {'UP' if interface.get('is_up') else 'DOWN'}")
            
            # Show motherboard info
            if 'motherboard' in hardware_info:
                mb = hardware_info['motherboard']
                print(f"  Motherboard: {mb.get('manufacturer', 'N/A')} {mb.get('product', 'N/A')}")
            
            # Show BIOS info
            if 'bios' in hardware_info:
                bios = hardware_info['bios']
                print(f"  BIOS: {bios.get('manufacturer', 'N/A')} {bios.get('version', 'N/A')}")
        else:
            print("❌ Hardware inventory failed")
        
        print("\n🔍 Testing software inventory...")
        software_info = monitoring.get_software_inventory()
        
        if software_info:
            print("✅ Software inventory collected successfully!")
            print(f"📋 Software keys: {list(software_info.keys())}")
            
            # Show installed programs
            if 'installed_programs' in software_info:
                programs = software_info['installed_programs']
                print(f"  Installed programs: {len(programs)} found")
                for i, program in enumerate(programs[:5]):  # Show first 5
                    name = program.get('name', 'Unknown')
                    version = program.get('version', 'N/A')
                    publisher = program.get('publisher', 'N/A')
                    print(f"    {i+1}. {name} ({version}) - {publisher}")
            else:
                print("❌ No installed_programs found")
        else:
            print("❌ Software inventory failed")
        
        print("\n✅ Detailed inventory test completed!")
        
    except Exception as e:
        print(f"❌ Error testing detailed inventory: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_detailed_inventory()
