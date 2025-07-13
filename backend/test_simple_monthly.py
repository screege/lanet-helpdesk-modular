#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test for monthly reports
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import create_app

def test_monthly_service():
    """Test monthly service directly"""
    
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing Monthly Reports Service Directly")
        print("=" * 50)
        
        try:
            from modules.reports.monthly_reports import monthly_reports_service
            
            # Test 1: Get system status
            print("\n1. Testing get_system_status...")
            status = monthly_reports_service.get_system_status()
            print(f"✅ Status: {status}")
            
            # Test 2: Get first client
            print("\n2. Getting first active client...")
            client_query = "SELECT client_id, name FROM clients WHERE is_active = true LIMIT 1"
            client = app.db_manager.execute_query(client_query, fetch='one')
            
            if client:
                print(f"✅ Found client: {client['name']} ({client['client_id']})")
                
                # Test 3: Check reports directory
                print("\n3. Testing reports directory...")
                reports_dir = monthly_reports_service.reports_dir
                print(f"   Reports directory: {reports_dir}")
                print(f"   Directory exists: {os.path.exists(reports_dir)}")

                if not os.path.exists(reports_dir):
                    print("   Creating reports directory...")
                    os.makedirs(reports_dir, exist_ok=True)
                    print(f"   Directory created: {os.path.exists(reports_dir)}")

                # Test 4: Generate report for this client
                print("\n4. Testing report generation...")
                from datetime import datetime
                now = datetime.now()

                print(f"   Generating for client: {client['client_id']}")
                print(f"   Month: {now.month}, Year: {now.year}")

                try:
                    file_path = monthly_reports_service.generate_monthly_report_for_client(
                        client['client_id'], now.month, now.year
                    )

                    if file_path:
                        print(f"✅ Report generated: {file_path}")

                        # Check if file exists
                        if os.path.exists(file_path):
                            print(f"✅ File exists on disk")
                            print(f"   File size: {os.path.getsize(file_path)} bytes")

                            # Show first few lines
                            with open(file_path, 'r', encoding='utf-8') as f:
                                first_lines = f.read(200)
                                print(f"   First 200 chars: {first_lines}")
                        else:
                            print(f"❌ File does not exist on disk")
                    else:
                        print("❌ Report generation returned None")

                except Exception as e:
                    print(f"❌ Exception during report generation: {e}")
                    import traceback
                    print(f"   Traceback: {traceback.format_exc()}")
            else:
                print("❌ No active clients found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_monthly_service()
