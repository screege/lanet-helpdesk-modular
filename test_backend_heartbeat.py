#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test if the backend is receiving heartbeats
"""

import requests
import json

def test_backend_heartbeat():
    """Test if the backend is receiving heartbeats"""
    try:
        print("🔍 Testing backend heartbeat endpoint...")
        
        # Test data
        test_data = {
            'asset_id': 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd',
            'heartbeat_type': 'full',
            'status': {
                'agent_status': 'online',
                'cpu_percent': 50.0,
                'memory_percent': 80.0,
                'disk_percent': 60.0
            },
            'timestamp': '2025-01-21T20:33:43',
            'hardware_inventory': {
                'disks': [
                    {
                        'device': 'C:\\',
                        'model': 'WD_BLACK SN850X 1000GB',
                        'health_status': 'Healthy',
                        'smart_status': 'OK',
                        'interface_type': 'NVMe'
                    }
                ]
            }
        }
        
        response = requests.post(
            'http://localhost:5001/api/agents/heartbeat',
            json=test_data,
            headers={
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Backend is receiving heartbeats!")
        else:
            print("❌ Backend heartbeat failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_backend_heartbeat()
