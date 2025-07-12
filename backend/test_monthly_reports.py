#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Monthly Reports System
"""

import requests
import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(__file__))

def test_monthly_reports():
    """Test the monthly reports system"""
    
    base_url = "http://localhost:5001/api"
    
    print("🧪 TESTING MONTHLY REPORTS SYSTEM")
    print("=" * 50)
    
    # Step 1: Login to get token
    print("\n1. 🔐 Logging in as superadmin...")
    
    login_data = {
        "email": "ba@lanet.mx",
        "password": "TestAdmin123!"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['access_token']
                print("✅ Login successful!")
            else:
                print(f"❌ Login failed: {data.get('error')}")
                return
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Headers for authenticated requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Test monthly status endpoint
    print("\n2. 📊 Testing monthly status endpoint...")
    
    try:
        response = requests.get(f"{base_url}/reports/monthly/status", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                status = data['data']
                print("✅ Status endpoint working!")
                print(f"   📅 Next report: {status.get('next_report')}")
                print(f"   👥 Active clients: {status.get('active_clients')}")
                print(f"   📋 Last report: {status.get('last_report')}")
                print(f"   🟢 System active: {status.get('system_active')}")
            else:
                print(f"❌ Status failed: {data.get('error')}")
        else:
            print(f"❌ Status failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Status error: {e}")
    
    # Step 3: Test setup schedules
    print("\n3. ⚙️ Testing setup schedules...")
    
    try:
        response = requests.post(f"{base_url}/reports/monthly/setup-schedules", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Schedules setup successful!")
                print(f"   📝 Message: {data['data'].get('message')}")
            else:
                print(f"❌ Setup failed: {data.get('error')}")
        else:
            print(f"❌ Setup failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Setup error: {e}")
    
    # Step 4: Test generate test report
    print("\n4. 📄 Testing generate test report...")
    
    try:
        response = requests.post(f"{base_url}/reports/monthly/generate-test", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Test report generated successfully!")
                print(f"   📝 Execution ID: {data['data'].get('execution_id')}")
                print(f"   💬 Message: {data['data'].get('message')}")
            else:
                print(f"❌ Test report failed: {data.get('error')}")
        else:
            print(f"❌ Test report failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Test report error: {e}")
    
    # Step 5: Check executions
    print("\n5. 📋 Checking report executions...")
    
    try:
        response = requests.get(f"{base_url}/reports/executions", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                executions = data['data']
                print(f"✅ Found {len(executions)} executions!")
                
                # Show recent executions
                for i, execution in enumerate(executions[:3]):
                    print(f"   📄 {i+1}. {execution.get('config_name', 'Unknown')} - {execution.get('status')} - {execution.get('started_at')}")
            else:
                print(f"❌ Executions failed: {data.get('error')}")
        else:
            print(f"❌ Executions failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Executions error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 MONTHLY REPORTS SYSTEM TEST COMPLETED!")
    print("\nIf all tests passed, the system is ready to use!")
    print("\n📋 Next steps:")
    print("1. Go to frontend: http://localhost:5174/reports")
    print("2. Click on 'Reportes Mensuales' tab")
    print("3. Use the buttons to interact with the system")

if __name__ == "__main__":
    test_monthly_reports()
