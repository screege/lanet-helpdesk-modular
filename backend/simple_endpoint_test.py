#!/usr/bin/env python3
"""
Test simple del endpoint sin autenticación
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from datetime import datetime

def test_endpoint_directly():
    """Test endpoint directly without HTTP"""
    print("🔍 TESTING ENDPOINT DIRECTLY")
    print("=" * 50)
    
    # Create app
    app = create_app()
    
    with app.app_context():
        try:
            # Import the service directly
            from modules.reports.monthly_reports import MonthlyReportsService
            
            print("✅ Service imported successfully")
            
            # Create service instance
            service = MonthlyReportsService()
            print("✅ Service instance created")
            
            # Test the function that's failing
            start_date = datetime(2025, 7, 1)
            end_date = datetime(2025, 7, 31, 23, 59, 59)
            client_id = ""  # Empty string like frontend sends
            
            print(f"📅 Testing with: start={start_date}, end={end_date}, client_id='{client_id}'")
            
            # Handle empty string client_id
            if client_id == "":
                client_id = None
                
            print(f"📅 Converted client_id to: {client_id}")
            
            # Call the function
            result = service.generate_comprehensive_report(
                start_date=start_date,
                end_date=end_date,
                client_id=client_id
            )
            
            if result:
                print(f"✅ SUCCESS: {result}")
                if os.path.exists(result):
                    file_size = os.path.getsize(result)
                    print(f"📁 File size: {file_size} bytes")
                else:
                    print(f"❌ File doesn't exist: {result}")
            else:
                print("❌ Function returned None")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_endpoint_directly()
