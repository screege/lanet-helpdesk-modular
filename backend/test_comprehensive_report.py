#!/usr/bin/env python3
"""
Test script para verificar el reporte consolidado
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from modules.reports.monthly_reports import MonthlyReportsService
from datetime import datetime

def test_comprehensive_report():
    """Test comprehensive report with ALL tickets"""
    print("🔍 TESTING COMPREHENSIVE REPORT")
    print("=" * 50)
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        try:
            # Initialize service
            service = MonthlyReportsService()
            print("✅ Service initialized")
            
            # Test comprehensive report
            print("🚀 Generating comprehensive report...")
            result = service.generate_comprehensive_report()
            
            if result:
                print(f"✅ Comprehensive report generated: {result}")
                
                # Check file size
                if os.path.exists(result):
                    file_size = os.path.getsize(result)
                    print(f"📁 File size: {file_size} bytes")
                else:
                    print(f"❌ File does not exist: {result}")
            else:
                print("❌ Comprehensive report generation failed")
            
            # Also test current month tickets count
            now = datetime.now()
            start_date = datetime(now.year, now.month, 1)
            if now.month == 12:
                end_date = datetime(now.year + 1, 1, 1)
            else:
                end_date = datetime(now.year, now.month + 1, 1)
            
            tickets_query = """
                SELECT COUNT(*) as count
                FROM tickets t
                WHERE t.created_at >= %s AND t.created_at < %s
            """
            
            count_result = app.db_manager.execute_query(tickets_query, (start_date, end_date), fetch='one')
            print(f"📊 Total tickets in current month: {count_result['count']}")
            
            # Count by client
            by_client_query = """
                SELECT c.name, COUNT(*) as count
                FROM tickets t
                JOIN clients c ON t.client_id = c.client_id
                WHERE t.created_at >= %s AND t.created_at < %s
                GROUP BY c.name
                ORDER BY count DESC
            """
            
            by_client = app.db_manager.execute_query(by_client_query, (start_date, end_date), fetch='all')
            print(f"\n📋 Tickets by client this month:")
            for client in by_client:
                print(f"   - {client['name']}: {client['count']} tickets")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_comprehensive_report()
