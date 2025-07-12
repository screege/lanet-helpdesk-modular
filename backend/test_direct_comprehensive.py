#!/usr/bin/env python3
"""
Test directo de la función comprehensive report
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from modules.reports.monthly_reports import MonthlyReportsService
from datetime import datetime

def test_direct_comprehensive():
    """Test direct comprehensive report function"""
    print("🔍 TESTING DIRECT COMPREHENSIVE REPORT")
    print("=" * 50)
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        try:
            # Initialize service
            service = MonthlyReportsService()
            print("✅ Service initialized")
            
            # Test with specific dates
            start_date = datetime(2025, 7, 1)
            end_date = datetime(2025, 7, 31, 23, 59, 59)
            
            print(f"📅 Testing with dates: {start_date} to {end_date}")
            
            # Test comprehensive report
            result = service.generate_comprehensive_report(
                start_date=start_date,
                end_date=end_date,
                client_id=None
            )
            
            if result:
                print(f"✅ Comprehensive report generated: {result}")
                
                # Check file size
                if os.path.exists(result):
                    file_size = os.path.getsize(result)
                    print(f"📁 File size: {file_size} bytes")
                    print(f"📁 File exists: ✅")
                else:
                    print(f"❌ File does not exist: {result}")
            else:
                print("❌ Comprehensive report generation failed")
            
            # Test with specific client
            print(f"\n🎯 Testing with specific client...")
            result2 = service.generate_comprehensive_report(
                start_date=start_date,
                end_date=end_date,
                client_id="550e8400-e29b-41d4-a716-446655440001"  # Cafe Mexico
            )
            
            if result2:
                print(f"✅ Client-specific report generated: {result2}")
                if os.path.exists(result2):
                    file_size = os.path.getsize(result2)
                    print(f"📁 File size: {file_size} bytes")
                else:
                    print(f"❌ File does not exist: {result2}")
            else:
                print("❌ Client-specific report generation failed")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_direct_comprehensive()
