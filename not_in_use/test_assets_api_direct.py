#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Assets API Directly
"""

import requests
import json

def test_assets_endpoint():
    """Test the assets endpoint directly"""
    print("🧪 Testing Assets API Endpoint")
    print("=" * 40)
    
    try:
        # Test the main assets endpoint
        print("📡 Testing /api/assets...")
        response = requests.get('http://localhost:5001/api/assets', timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            print(f"Assets Count: {len(data.get('assets', []))}")
            print(f"Total: {data.get('total', 'N/A')}")
            
            # Show first few assets
            assets = data.get('assets', [])
            for i, asset in enumerate(assets[:3]):
                print(f"  Asset {i+1}: {asset.get('name')} - {asset.get('site_name')} - {asset.get('client_name')}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_assets_with_auth():
    """Test assets with authentication"""
    print("\n🔐 Testing with Authentication...")
    
    try:
        # Login first
        login_data = {
            "email": "ba@lanet.mx",
            "password": "TestAdmin123!"
        }
        
        login_response = requests.post('http://localhost:5001/api/auth/login', 
                                     json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            print("✅ Login successful")
            
            # Test assets with auth
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test main endpoint
            response = requests.get('http://localhost:5001/api/assets', 
                                  headers=headers, timeout=10)
            
            print(f"Authenticated Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Authenticated Assets: {len(data.get('assets', []))}")
                
                # Show assets
                for asset in data.get('assets', [])[:5]:
                    print(f"  {asset.get('name')} - {asset.get('site_name')} - {asset.get('agent_status', 'N/A')}")
            else:
                print(f"Auth Error: {response.text}")
                
            # Test technician filtered endpoint
            print("\n📊 Testing technician filtered endpoint...")
            tech_response = requests.get('http://localhost:5001/api/assets/technician/filtered', 
                                       headers=headers, timeout=10)
            
            print(f"Technician Filtered Status: {tech_response.status_code}")
            
            if tech_response.status_code == 200:
                tech_data = tech_response.json()
                print(f"Technician Assets: {len(tech_data.get('assets', []))}")
                
                for asset in tech_data.get('assets', [])[:5]:
                    print(f"  {asset.get('name')} - {asset.get('site_name')} - {asset.get('connection_status', 'N/A')}")
            else:
                print(f"Technician Error: {tech_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Login Error: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Auth Error: {e}")

def test_simple_endpoints():
    """Test simple test endpoints"""
    print("\n🔧 Testing Simple Endpoints...")
    
    endpoints = [
        '/api/assets/test',
        '/api/assets/simple-test',
        '/api/health'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'http://localhost:5001{endpoint}', timeout=5)
            print(f"{endpoint}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")

def main():
    """Main test function"""
    test_simple_endpoints()
    test_assets_endpoint()
    test_assets_with_auth()
    
    print("\n📋 Summary:")
    print("   If assets show 0 but database has data, there's a backend issue")
    print("   Check backend logs for SQL errors or JOIN issues")

if __name__ == "__main__":
    main()
