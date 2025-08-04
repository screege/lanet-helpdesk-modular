#!/usr/bin/env python3
"""
Test script for SLA endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5001/api"

def test_sla_endpoints():
    print("🧪 Testing SLA endpoints...")
    
    # Test GET policies
    print("\n1. Testing GET /sla/policies")
    try:
        response = requests.get(f"{BASE_URL}/sla/policies")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Policies found: {len(data.get('data', []))}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test GET clients (to verify client service)
    print("\n2. Testing GET /clients")
    try:
        response = requests.get(f"{BASE_URL}/clients")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Clients found: {len(data.get('data', []))}")
            if data.get('data'):
                print(f"First client: {data['data'][0].get('name', 'Unknown')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test POST policy (create)
    print("\n3. Testing POST /sla/policies")
    test_policy = {
        "name": "Test SLA Policy",
        "description": "Test policy for debugging",
        "priority": "media",
        "response_time_hours": 4,
        "resolution_time_hours": 24,
        "business_hours_only": True,
        "escalation_enabled": False,
        "is_active": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/sla/policies",
            json=test_policy,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Created policy ID: {data.get('data', {}).get('policy_id')}")
            return data.get('data', {}).get('policy_id')
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    return None

if __name__ == "__main__":
    test_sla_endpoints()
