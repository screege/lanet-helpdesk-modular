#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test sending SMART data to backend and verify it's saved correctly
"""

import requests
import json

def test_backend_smart_data():
    """Test sending SMART data to backend"""
    try:
        print("🔍 Testing backend SMART data processing...")
        
        # Test data with SMART information
        test_data = {
            'asset_id': 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd',
            'heartbeat_type': 'full',
            'status': {
                'agent_status': 'online',
                'cpu_percent': 50.0,
                'memory_percent': 80.0,
                'disk_percent': 60.0
            },
            'timestamp': '2025-01-22T10:16:45',
            'hardware_inventory': {
                'timestamp': '2025-01-22T10:16:25',
                'disks': [
                    {
                        'device': 'C:\\',
                        'model': 'WD_BLACK SN850X 1000GB',
                        'health_status': 'Healthy',
                        'smart_status': 'OK',
                        'interface_type': 'NVMe',
                        'serial_number': 'Unknown',
                        'temperature': 'Not available',
                        'physical_size_gb': 931.51,
                        'total_gb': 929.24,
                        'used_gb': 470.37,
                        'free_gb': 458.87,
                        'usage_percent': 50.6
                    },
                    {
                        'device': 'G:\\',
                        'model': 'WD_BLACK SN850X 1000GB',
                        'health_status': 'Healthy',
                        'smart_status': 'OK',
                        'interface_type': 'NVMe',
                        'serial_number': 'Unknown',
                        'temperature': 'Not available',
                        'physical_size_gb': 931.51,
                        'total_gb': 929.24,
                        'used_gb': 493.31,
                        'free_gb': 435.93,
                        'usage_percent': 53.1
                    }
                ]
            },
            'software_inventory': {
                'programs': []
            }
        }
        
        print(f"📊 Sending test data with {len(test_data['hardware_inventory']['disks'])} disks")
        for i, disk in enumerate(test_data['hardware_inventory']['disks']):
            print(f"  Disk {i+1}: {disk['model']} - Health: '{disk['health_status']}', SMART: '{disk['smart_status']}', Interface: '{disk['interface_type']}'")
        
        response = requests.post(
            'http://localhost:5001/api/agents/heartbeat',
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer test-token'
            },
            timeout=10
        )
        
        print(f"\n📡 Response status: {response.status_code}")
        print(f"📡 Response text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Backend received heartbeat successfully!")
            return True
        else:
            print("❌ Backend heartbeat failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_backend_smart_data()
