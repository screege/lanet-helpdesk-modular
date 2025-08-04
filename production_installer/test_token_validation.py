#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test token validation for LANET Agent installer
Tests the token validation API endpoint
"""

import requests
import json

def test_token_validation():
    """Test token validation with available tokens"""
    print("LANET Agent Token Validation Test")
    print("=" * 50)
    
    # Available tokens from database cleanup
    test_tokens = [
        "LANET-TEST-PROD-94DA44",
        "LANET-550E-660E-BCC100", 
        "LANET-TEST-PROD-0ADFE6",
        "LANET-75F6-EC23-85DC9D",
        "LANET-TEST-PROD-474FFA"
    ]
    
    server_url = "http://localhost:5001/api"
    
    print(f"Testing token validation against: {server_url}")
    print()
    
    for token in test_tokens:
        print(f"Testing token: {token}")
        
        try:
            response = requests.post(
                f"{server_url}/agents/validate-token",
                json={'token': token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data', {}).get('is_valid'):
                    client_info = data['data']
                    client_name = client_info.get('client_name', 'Unknown')
                    site_name = client_info.get('site_name', 'Unknown')
                    print(f"  ✅ Valid - Client: {client_name} | Site: {site_name}")
                else:
                    error_msg = data.get('data', {}).get('error_message', 'Unknown error')
                    print(f"  ❌ Invalid - {error_msg}")
            else:
                print(f"  ❌ Server error - HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Connection error - {str(e)}")
        except Exception as e:
            print(f"  ❌ Error - {str(e)}")
        
        print()
    
    # Test server health
    print("Testing server health endpoint...")
    try:
        response = requests.get(f"{server_url}/health", timeout=10)
        if response.status_code == 200:
            print("  ✅ Server health check passed")
        else:
            print(f"  ❌ Server health check failed - HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ Server health check failed - {str(e)}")

if __name__ == "__main__":
    test_token_validation()
    input("\nPress Enter to exit...")
