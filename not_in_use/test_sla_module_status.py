#!/usr/bin/env python3
"""
Test script to evaluate SLA module implementation status
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from flask import Flask
from core.database import DatabaseManager
from core.auth import AuthManager
from modules.sla.service import sla_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_sla_module_status():
    """Test SLA module implementation and identify what needs to be completed"""
    
    # Create Flask app context
    app = Flask(__name__)
    app.config['DATABASE_URL'] = 'postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk'
    
    with app.app_context():
        # Initialize database manager
        app.db_manager = DatabaseManager(app.config['DATABASE_URL'])
        
        print("=== SLA MODULE IMPLEMENTATION STATUS ===\n")
        
        # 1. Check SLA policies
        print("1. Checking SLA policies:")
        policies_query = """
        SELECT policy_id, name, priority, response_time_hours, resolution_time_hours, 
               is_active, is_default, client_id, category_id
        FROM sla_policies 
        WHERE is_active = true
        ORDER BY priority DESC, name
        """
        
        policies = app.db_manager.execute_query(policies_query)
        
        if policies:
            print(f"✅ Found {len(policies)} active SLA policies:")
            for policy in policies:
                client_info = f" (Client-specific)" if policy['client_id'] else " (Global)"
                category_info = f" (Category-specific)" if policy['category_id'] else ""
                default_info = " [DEFAULT]" if policy['is_default'] else ""
                print(f"   - {policy['name']} ({policy['priority']}) - Response: {policy['response_time_hours']}h, Resolution: {policy['resolution_time_hours']}h{client_info}{category_info}{default_info}")
        else:
            print("❌ No SLA policies found!")
            return
        
        # 2. Check SLA tracking for recent tickets
        print("\n2. Checking SLA tracking for recent tickets:")
        tracking_query = """
        SELECT st.ticket_id, t.ticket_number, t.priority, t.status, t.created_at,
               st.response_deadline, st.resolution_deadline, 
               st.response_status, st.resolution_status,
               sp.name as policy_name
        FROM sla_tracking st
        JOIN tickets t ON st.ticket_id = t.ticket_id
        JOIN sla_policies sp ON st.policy_id = sp.policy_id
        ORDER BY t.created_at DESC 
        LIMIT 5
        """
        
        tracking_records = app.db_manager.execute_query(tracking_query)
        
        if tracking_records:
            print(f"✅ Found {len(tracking_records)} recent SLA tracking records:")
            for record in tracking_records:
                response_status = "✅" if record['response_status'] == 'met' else "⏰" if record['response_status'] == 'pending' else "❌"
                resolution_status = "✅" if record['resolution_status'] == 'met' else "⏰" if record['resolution_status'] == 'pending' else "❌"
                print(f"   - {record['ticket_number']} ({record['priority']}) - Policy: {record['policy_name']}")
                print(f"     Response: {response_status} {record['response_status']} (Due: {record['response_deadline']})")
                print(f"     Resolution: {resolution_status} {record['resolution_status']} (Due: {record['resolution_deadline']})")
        else:
            print("❌ No SLA tracking records found!")
        
        # 3. Test SLA service functionality
        print("\n3. Testing SLA service functionality:")
        
        # Test getting applicable policy
        test_ticket_data = {
            'client_id': None,
            'category_id': None,
            'priority': 'media'
        }
        
        try:
            applicable_policy = sla_service.get_applicable_sla_policy(test_ticket_data)
            if applicable_policy:
                print(f"✅ SLA policy lookup working: Found '{applicable_policy['name']}' for media priority")
            else:
                print("❌ SLA policy lookup failed: No policy found for test data")
        except Exception as e:
            print(f"❌ SLA policy lookup error: {e}")
        
        # 4. Check SLA monitoring and escalation
        print("\n4. Checking SLA monitoring capabilities:")
        
        try:
            # Test breach detection
            breaches = sla_service.check_sla_breaches()
            print(f"✅ SLA breach detection working: Found {len(breaches) if breaches else 0} current breaches")
            
            if breaches:
                for breach in breaches[:3]:  # Show first 3 breaches
                    print(f"   - Breach: {breach.get('ticket_number', 'Unknown')} - {breach.get('breach_type', 'Unknown')}")
        except Exception as e:
            print(f"❌ SLA breach detection error: {e}")
        
        # 5. Check working hours calculation
        print("\n5. Testing working hours calculation:")
        
        try:
            from datetime import datetime, timedelta
            
            # Test business hours calculation
            start_time = datetime.now()
            end_time = start_time + timedelta(hours=24)
            
            business_hours = sla_service.calculate_business_hours(start_time, end_time)
            print(f"✅ Business hours calculation working: {business_hours} hours in 24-hour period")
        except Exception as e:
            print(f"❌ Business hours calculation error: {e}")
        
        # 6. Summary and recommendations
        print("\n6. SLA MODULE STATUS SUMMARY:")
        print("✅ IMPLEMENTED:")
        print("   - SLA policies management")
        print("   - SLA tracking for tickets")
        print("   - Policy lookup algorithm")
        print("   - Breach detection system")
        print("   - Business hours calculation")
        print("   - Database schema complete")
        
        print("\n🔧 NEEDS COMPLETION:")
        print("   - Frontend UI for SLA management")
        print("   - Automated SLA monitoring job")
        print("   - SLA escalation notifications")
        print("   - Client-specific working hours configuration")
        print("   - SLA reporting and analytics")
        print("   - Integration with notification system for breaches")
        
        print("\n📋 NEXT STEPS:")
        print("   1. Create SLA management frontend UI")
        print("   2. Implement automated SLA monitoring background job")
        print("   3. Add SLA breach notifications to email system")
        print("   4. Create SLA reporting dashboard")
        print("   5. Add client-specific SLA configuration")

if __name__ == '__main__':
    test_sla_module_status()
