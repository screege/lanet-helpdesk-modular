#!/usr/bin/env python3
"""
Debug script para diagnosticar problemas con reportes mensuales
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from modules.reports.monthly_reports import MonthlyReportsService
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_monthly_reports():
    """Debug monthly reports generation"""
    print("🔍 DEBUGGING MONTHLY REPORTS")
    print("=" * 50)
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        try:
            # Initialize service
            service = MonthlyReportsService()
            print("✅ Service initialized")
            
            # Test with superadmin claims
            test_claims = {
                'role': 'superadmin',
                'client_id': None,
                'user_id': 'test-user-id'
            }
            
            print(f"🧪 Testing with claims: {test_claims}")
            
            # Check if there are active clients
            client_query = "SELECT client_id, name FROM clients WHERE is_active = true LIMIT 5"
            clients = app.db_manager.execute_query(client_query, fetch='all')
            
            print(f"📊 Found {len(clients)} active clients:")
            for client in clients:
                print(f"   - {client['name']} (ID: {client['client_id']})")
            
            if not clients:
                print("❌ No active clients found!")
                return
            
            # Try to generate test report
            print("\n🚀 Generating test report...")

            # First test the generate_test_report function
            print("🧪 Testing generate_test_report function...")
            result1 = service.generate_test_report(test_claims)
            print(f"📋 Result from generate_test_report: {result1}")

            # Then test directly with first client
            first_client = clients[0]
            client_id = first_client['client_id']
            client_name = first_client['name']

            print(f"\n🎯 Testing directly with specific client: {client_name} ({client_id})")

            from datetime import datetime
            now = datetime.now()

            # Test the specific function
            result = service.generate_monthly_report_for_client(client_id, now.month, now.year)

            if result:
                print(f"✅ Test report generated successfully: {result}")

                # Check if file exists
                if os.path.exists(result):
                    print(f"✅ File exists and is accessible")
                    file_size = os.path.getsize(result)
                    print(f"📁 File size: {file_size} bytes")

                    # Show first few lines
                    with open(result, 'r', encoding='utf-8') as f:
                        first_lines = f.read(500)
                        print(f"📄 First 500 characters:\n{first_lines}")
                else:
                    print(f"❌ File does not exist: {result}")
            else:
                print("❌ Test report generation failed - returned None")

                # Check reports directory
                reports_dir = service.reports_dir
                print(f"📁 Reports directory: {reports_dir}")
                print(f"📁 Directory exists: {os.path.exists(reports_dir)}")
                if os.path.exists(reports_dir):
                    files = os.listdir(reports_dir)
                    print(f"📁 Files in directory: {files}")
                
        except Exception as e:
            print(f"❌ Error during debugging: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_monthly_reports()
