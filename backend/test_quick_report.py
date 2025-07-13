#!/usr/bin/env python3
"""
Test the quick report functionality
"""

import requests
import json

def test_quick_report():
    """Test the quick report endpoint"""
    print("🔍 TESTING QUICK REPORT FUNCTIONALITY")
    print("=" * 50)
    
    try:
        # Login first
        login_response = requests.post('http://localhost:5001/api/auth/login', json={
            'email': 'ba@lanet.mx',
            'password': 'TestAdmin123!'
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        login_data = login_response.json()
        token = login_data['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        print("✅ Login successful")
        
        # Test quick report PDF
        print("\n📄 Testing Quick Report PDF...")
        pdf_response = requests.post('http://localhost:5001/api/reports/generate-quick', 
                                   headers=headers,
                                   json={'output_format': 'pdf'})
        
        print(f"PDF Response status: {pdf_response.status_code}")
        if pdf_response.status_code == 200:
            pdf_data = pdf_response.json()
            print(f"✅ PDF Success: {pdf_data.get('message', 'Generated')}")
        else:
            print(f"❌ PDF Error: {pdf_response.text}")
        
        # Test quick report Excel
        print("\n📊 Testing Quick Report Excel...")
        excel_response = requests.post('http://localhost:5001/api/reports/generate-quick', 
                                     headers=headers,
                                     json={'output_format': 'excel'})
        
        print(f"Excel Response status: {excel_response.status_code}")
        if excel_response.status_code == 200:
            excel_data = excel_response.json()
            print(f"✅ Excel Success: {excel_data.get('message', 'Generated')}")
        else:
            print(f"❌ Excel Error: {excel_response.text}")
        
        # Test statistics report
        print("\n📈 Testing Statistics Report...")
        stats_response = requests.post('http://localhost:5001/api/reports/generate-statistics', 
                                     headers=headers,
                                     json={'output_format': 'excel'})
        
        print(f"Statistics Response status: {stats_response.status_code}")
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print(f"✅ Statistics Success: {stats_data.get('message', 'Generated')}")
        else:
            print(f"❌ Statistics Error: {stats_response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_quick_report()
