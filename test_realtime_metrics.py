#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test real-time metrics API
"""

import requests
import json

def test_realtime_metrics():
    """Test if real-time metrics are working"""
    try:
        print("🔍 Testing real-time metrics API...")
        
        # Test the assets API
        response = requests.get('http://localhost:5001/api/assets/')
        
        if response.status_code == 200:
            data = response.json()
            
            if data['success'] and data['data']['assets']:
                asset = data['data']['assets'][0]
                
                print(f"\n📊 Asset: {asset['name']}")
                print(f"Status: {asset['agent_status']}")
                print(f"CPU: {asset.get('cpu_percent', 'N/A')}%")
                print(f"Memory: {asset.get('memory_percent', 'N/A')}%")
                print(f"Disk: {asset.get('disk_percent', 'N/A')}%")
                print(f"Last seen: {asset['last_seen']}")
                print(f"Connection: {asset.get('connection_status', 'N/A')}")
                
                # Check if real-time metrics are present
                has_cpu = asset.get('cpu_percent') is not None
                has_memory = asset.get('memory_percent') is not None
                has_disk = asset.get('disk_percent') is not None
                
                if has_cpu and has_memory and has_disk:
                    print("\n✅ Real-time metrics are working!")
                    return True
                else:
                    print(f"\n❌ Missing metrics - CPU: {has_cpu}, Memory: {has_memory}, Disk: {has_disk}")
                    return False
            else:
                print("❌ No assets found in response")
                return False
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing metrics: {e}")
        return False

if __name__ == "__main__":
    test_realtime_metrics()
