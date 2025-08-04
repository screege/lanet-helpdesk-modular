#!/usr/bin/env python3
"""
Debug Registration - Test the exact registration process
"""

import requests
import json
import socket
import sys
import os

def debug_registration():
    print("=== DEBUGGING REGISTRATION ===")
    
    token = "LANET-75F6-EC23-85DC9D"
    server_url = "http://localhost:5001"
    
    print(f"Token: {token}")
    print(f"Server: {server_url}")
    print("")
    
    # Prepare test data
    hardware_info = {
        'agent_version': '2.0.0',
        'computer_name': socket.gethostname(),
        'hardware': {'cpu': 'Test CPU', 'ram': '8GB'},
        'software': [],
        'status': {'cpu_usage': 25, 'memory_usage': 60}
    }
    
    print("Hardware info prepared:")
    print(json.dumps(hardware_info, indent=2))
    print("")
    
    try:
        print("Sending registration request...")
        response = requests.post(
            f"{server_url}/api/agents/register-with-token",
            json={
                'token': token,
                'hardware_info': hardware_info
            },
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print("")
        
        if response.status_code == 200:
            print("✅ SUCCESS - Status 200")
            response_data = response.json()
            print("Raw response:")
            print(json.dumps(response_data, indent=2))
            print("")
            
            # Test the fix logic
            if 'data' in response_data:
                registration_data = response_data['data']
                print("✅ Using data from 'data' field")
            else:
                registration_data = response_data
                print("✅ Using data from root level")
            
            print("Registration data:")
            print(json.dumps(registration_data, indent=2))
            print("")
            
            # Check required fields
            required_fields = ['asset_id', 'agent_token', 'client_id', 'site_id', 'client_name', 'site_name']
            missing_fields = []
            
            for field in required_fields:
                if field in registration_data:
                    print(f"✅ {field}: {registration_data[field]}")
                else:
                    print(f"❌ {field}: MISSING")
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"\n❌ Missing fields: {missing_fields}")
                return False
            else:
                print(f"\n🎉 ALL REQUIRED FIELDS PRESENT!")
                return True
                
        else:
            print(f"❌ FAILED - Status {response.status_code}")
            try:
                error_data = response.json()
                print("Error response:")
                print(json.dumps(error_data, indent=2))
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_registration()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
