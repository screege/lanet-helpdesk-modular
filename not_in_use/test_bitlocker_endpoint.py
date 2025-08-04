#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test BitLocker endpoint directly
"""

import requests

def test_bitlocker_endpoint():
    """Test BitLocker endpoint"""
    try:
        print("🔐 Testing BitLocker endpoint...")
        
        # Test without authentication first
        response = requests.get('http://localhost:5001/api/bitlocker/b0efd80c-15ac-493b-b4eb-ad325ddacdcd')
        print(f"Without auth - Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Test with authentication
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MzEyNzcwMiwianRpIjoiZGMwMTZhYTctODY4Ni00ZTI0LTk0ZWEtNWU4ZmVmNzI0MDZmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Ijc3MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMyIsIm5iZiI6MTc1MzEyNzcwMiwicm9sZSI6InRlY2huaWNpYW4iLCJjbGllbnRfaWQiOm51bGwsInNpdGVfaWRzIjpbXSwibmFtZSI6Ik1hclx1MDBlZGEgR29uelx1MDBlMWxleiIsImVtYWlsIjoidGVjaEB0ZXN0LmNvbSJ9.8Hb2HhqIiuVOsGfin4puIVj1Ua5Ed1WOfhXZ6F5oAVU"
        
        response = requests.get(
            'http://localhost:5001/api/bitlocker/b0efd80c-15ac-493b-b4eb-ad325ddacdcd',
            headers={'Authorization': f'Bearer {token}'}
        )
        print(f"\nWith auth - Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_bitlocker_endpoint()
