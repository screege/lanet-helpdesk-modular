#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Excel report generation and download functionality
"""

import requests
import json
import os

def test_login():
    """Test login to get JWT token"""
    try:
        login_data = {
            "email": "ba@lanet.mx",
            "password": "TestAdmin123!"
        }
        response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['access_token']
                print("✅ Login successful")
                return token
        print(f"❌ Login failed: {response.text}")
        return None
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def test_excel_generation_and_download(token):
    """Test Excel generation and download"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n🔍 Testing Excel report generation...")
    
    # Generate Excel report
    response = requests.post(
        'http://localhost:5001/api/reports/generate-quick',
        headers=headers,
        json={'output_format': 'excel'}
    )
    
    print(f"Generation status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            execution_id = data['data']['execution_id']
            file_path = data['data'].get('file_path', 'unknown')
            print(f"✅ Excel report generated successfully!")
            print(f"   Execution ID: {execution_id}")
            print(f"   File path: {file_path}")
            
            # Test download
            print(f"\n🔽 Testing download for execution_id: {execution_id}")
            
            download_response = requests.get(
                f'http://localhost:5001/api/reports/executions/{execution_id}/download',
                headers=headers
            )
            
            print(f"Download status: {download_response.status_code}")
            
            if download_response.status_code == 200:
                # Check if it's actually an Excel file
                content_type = download_response.headers.get('Content-Type', '')
                content_disposition = download_response.headers.get('Content-Disposition', '')
                
                print(f"✅ Download successful!")
                print(f"   Content-Type: {content_type}")
                print(f"   Content-Disposition: {content_disposition}")
                print(f"   File size: {len(download_response.content)} bytes")
                
                # Save the file to verify it's a valid Excel file
                download_filename = f"test_download_{execution_id}.xlsx"
                with open(download_filename, 'wb') as f:
                    f.write(download_response.content)
                
                print(f"   File saved as: {download_filename}")
                
                # Verify it's a valid Excel file by checking the file signature
                if download_response.content.startswith(b'PK'):
                    print("✅ File appears to be a valid Excel file (ZIP-based format)")
                    return True
                else:
                    print("❌ File does not appear to be a valid Excel file")
                    return False
            else:
                print(f"❌ Download failed: {download_response.text}")
                return False
        else:
            print(f"❌ Generation failed: {data}")
            return False
    else:
        print(f"❌ Generation failed: {response.text}")
        return False

def test_monthly_report_excel(token):
    """Test monthly report Excel generation"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n📊 Testing monthly Excel report generation...")
    
    # Generate monthly Excel report
    response = requests.post(
        'http://localhost:5001/api/reports/monthly/generate-test',
        headers=headers,
        json={}
    )
    
    print(f"Monthly generation status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            execution_id = data['data']['execution_id']
            file_path = data['data'].get('file_path', 'unknown')
            print(f"✅ Monthly Excel report generated successfully!")
            print(f"   Execution ID: {execution_id}")
            print(f"   File path: {file_path}")
            return True
        else:
            print(f"❌ Monthly generation failed: {data}")
            return False
    else:
        print(f"❌ Monthly generation failed: {response.text}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing LANET Helpdesk V3 Excel Report Generation & Download")
    print("=" * 60)
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test Excel generation and download
    excel_success = test_excel_generation_and_download(token)
    
    # Test monthly report
    monthly_success = test_monthly_report_excel(token)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 EXCEL FUNCTIONALITY TEST RESULTS")
    print("=" * 60)
    
    if excel_success:
        print("✅ Excel generation and download: WORKING")
    else:
        print("❌ Excel generation and download: FAILED")
    
    if monthly_success:
        print("✅ Monthly Excel reports: WORKING")
    else:
        print("❌ Monthly Excel reports: FAILED")
    
    if excel_success and monthly_success:
        print("\n🎉 ALL EXCEL FUNCTIONALITY IS WORKING CORRECTLY!")
        print("   - Excel files are being generated")
        print("   - Downloads are working")
        print("   - Files are valid Excel format")
    else:
        print("\n⚠️ Some Excel functionality issues detected")

if __name__ == "__main__":
    main()
