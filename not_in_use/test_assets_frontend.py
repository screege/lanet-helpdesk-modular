#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Assets API and Frontend Data
"""

import requests
import psycopg2
import json

def test_database_assets():
    """Test assets directly from database"""
    print("🔍 Testing database assets...")
    
    try:
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()
        
        # Get all assets for API Test Site
        cur.execute("""
            SELECT a.asset_id, a.name, a.status, a.last_seen, s.name as site_name, c.name as client_name
            FROM assets a
            JOIN sites s ON a.site_id = s.site_id
            JOIN clients c ON a.client_id = c.client_id
            WHERE s.site_id = %s
            ORDER BY a.last_seen DESC
        """, ('ec2368ae-cd4b-417d-86be-504088e5678c',))
        
        results = cur.fetchall()
        print(f"📊 Assets found in database: {len(results)}")
        
        for r in results:
            print(f"  Asset ID: {r[0]}")
            print(f"  Name: {r[1]}")
            print(f"  Status: {r[2]}")
            print(f"  Last Seen: {r[3]}")
            print(f"  Site: {r[4]}")
            print(f"  Client: {r[5]}")
            print("  ---")
        
        conn.close()
        return len(results)
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return 0

def test_assets_api():
    """Test assets API endpoint"""
    print("\n🌐 Testing assets API...")
    
    try:
        # Test without authentication first
        response = requests.get('http://localhost:5001/api/assets', timeout=10)
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Assets from API: {len(data.get('assets', []))}")
            
            # Look for our specific assets
            for asset in data.get('assets', []):
                if 'benny' in asset.get('name', '').lower():
                    print(f"  Found benny asset: {asset.get('name')} - {asset.get('status')}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API error: {e}")

def test_with_auth():
    """Test with authentication"""
    print("\n🔐 Testing with authentication...")
    
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
            
            # Get assets with auth
            headers = {'Authorization': f'Bearer {token}'}
            assets_response = requests.get('http://localhost:5001/api/assets', 
                                         headers=headers, timeout=10)
            
            if assets_response.status_code == 200:
                data = assets_response.json()
                print(f"📊 Authenticated assets: {len(data.get('assets', []))}")
                
                # Show all assets
                for asset in data.get('assets', []):
                    print(f"  Asset: {asset.get('name')} - {asset.get('status')} - Site: {asset.get('site_name', 'N/A')}")
            else:
                print(f"❌ Assets API error: {assets_response.status_code}")
                print(f"Response: {assets_response.text}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Auth error: {e}")

def main():
    """Main test function"""
    print("🧪 LANET Assets Frontend Test")
    print("=" * 40)
    
    # Test database
    db_count = test_database_assets()
    
    # Test API
    test_assets_api()
    
    # Test with auth
    test_with_auth()
    
    print(f"\n📋 Summary:")
    print(f"   Database assets: {db_count}")
    print(f"   Check frontend at: http://localhost:5173")
    print(f"   Login: ba@lanet.mx / TestAdmin123!")

if __name__ == "__main__":
    main()
