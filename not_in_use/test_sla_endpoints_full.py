#!/usr/bin/env python3
"""
Test SLA endpoints with authentication
"""

import requests
import json

BASE_URL = "http://localhost:5001/api"

def test_sla_endpoints_full():
    print("🧪 Testing SLA endpoints with authentication...")
    
    # Step 1: Login to get token
    print("\n1. Testing login...")
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "test@test.com",
            "password": "test"
        })
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data['data']['access_token']
            print(f"✅ Got access token: {token[:20]}...")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        else:
            print(f"❌ Login failed: {login_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Test GET policies
    print("\n2. Testing GET /sla/policies")
    try:
        response = requests.get(f"{BASE_URL}/sla/policies", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            policies = data.get('data', [])
            print(f"✅ Found {len(policies)} policies")
            for policy in policies[:3]:  # Show first 3
                print(f"   - {policy.get('name')} ({policy.get('priority')})")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 3: Test GET clients
    print("\n3. Testing GET /clients")
    try:
        response = requests.get(f"{BASE_URL}/clients", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            clients = data.get('data', [])
            print(f"✅ Found {len(clients)} clients")
            for client in clients[:3]:  # Show first 3
                print(f"   - {client.get('name')} (ID: {client.get('client_id')})")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 4: Test POST policy (create)
    print("\n4. Testing POST /sla/policies (create)")
    test_policy = {
        "name": "Test Policy API",
        "description": "Test policy created via API",
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
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            policy_id = data.get('data', {}).get('policy_id')
            print(f"✅ Created policy ID: {policy_id}")
            
            # Step 5: Test PUT policy (update)
            if policy_id:
                print(f"\n5. Testing PUT /sla/policies/{policy_id} (update)")
                update_data = {
                    "name": "Test Policy API - Updated",
                    "response_time_hours": 2
                }
                
                try:
                    update_response = requests.put(
                        f"{BASE_URL}/sla/policies/{policy_id}",
                        json=update_data,
                        headers=headers
                    )
                    print(f"Update Status: {update_response.status_code}")
                    if update_response.status_code == 200:
                        print("✅ Policy updated successfully")
                    else:
                        print(f"❌ Update failed: {update_response.text}")
                except Exception as e:
                    print(f"❌ Update error: {e}")
                
                # Step 6: Test DELETE policy
                print(f"\n6. Testing DELETE /sla/policies/{policy_id}")
                try:
                    delete_response = requests.delete(
                        f"{BASE_URL}/sla/policies/{policy_id}",
                        headers=headers
                    )
                    print(f"Delete Status: {delete_response.status_code}")
                    if delete_response.status_code == 200:
                        print("✅ Policy deleted successfully")
                    else:
                        print(f"❌ Delete failed: {delete_response.text}")
                except Exception as e:
                    print(f"❌ Delete error: {e}")
                    
        else:
            print(f"❌ Create failed: {response.text}")
    except Exception as e:
        print(f"❌ Create error: {e}")
    
    # Step 7: Verify final state
    print("\n7. Final verification - GET policies again")
    try:
        response = requests.get(f"{BASE_URL}/sla/policies", headers=headers)
        if response.status_code == 200:
            data = response.json()
            policies = data.get('data', [])
            print(f"✅ Final count: {len(policies)} policies")
        else:
            print(f"❌ Final check failed: {response.text}")
    except Exception as e:
        print(f"❌ Final check error: {e}")

if __name__ == "__main__":
    test_sla_endpoints_full()
