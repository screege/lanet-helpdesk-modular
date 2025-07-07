#!/usr/bin/env python3
"""
Test SLA service directly without Flask app
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from flask import Flask
from core.database import DatabaseManager
from modules.sla.service import sla_service

def test_sla_service():
    """Test SLA service directly"""
    
    # Create minimal Flask app
    app = Flask(__name__)
    app.config['DATABASE_URL'] = 'postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk'
    
    with app.app_context():
        # Initialize database manager
        app.db_manager = DatabaseManager(app.config['DATABASE_URL'])
        
        print("🧪 Testing SLA service directly...")
        
        # Test 1: Create SLA policy
        print("\n1. Testing create_sla_policy...")
        test_policy_data = {
            'name': 'Test Policy Direct',
            'description': 'Test policy created directly',
            'priority': 'media',
            'response_time_hours': 4,
            'resolution_time_hours': 24,
            'business_hours_only': True,
            'escalation_enabled': False,
            'is_active': True
        }
        
        try:
            policy_id = sla_service.create_sla_policy(test_policy_data)
            if policy_id:
                print(f"✅ Created policy with ID: {policy_id}")
                
                # Test 2: Update the policy
                print("\n2. Testing update_sla_policy...")
                update_data = {
                    'name': 'Test Policy Direct - Updated',
                    'response_time_hours': 2
                }
                
                success = sla_service.update_sla_policy(policy_id, update_data)
                if success:
                    print("✅ Updated policy successfully")
                else:
                    print("❌ Failed to update policy")
                
                # Test 3: Set as default
                print("\n3. Testing set_default_policy...")
                success = sla_service.set_default_policy(policy_id)
                if success:
                    print("✅ Set as default successfully")
                else:
                    print("❌ Failed to set as default")
                
                # Test 4: Delete the policy
                print("\n4. Testing delete_sla_policy...")
                # First unset as default
                sla_service.set_default_policy('some-other-id')  # This will fail but unset current default
                
                success = sla_service.delete_sla_policy(policy_id)
                if success:
                    print("✅ Deleted policy successfully")
                else:
                    print("❌ Failed to delete policy")
                    
            else:
                print("❌ Failed to create policy")
                
        except Exception as e:
            print(f"❌ Error testing SLA service: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 5: Check existing policies
        print("\n5. Testing existing policies...")
        try:
            query = "SELECT policy_id, name, priority FROM sla_policies WHERE is_active = true LIMIT 5"
            policies = app.db_manager.execute_query(query)
            print(f"✅ Found {len(policies)} existing policies:")
            for policy in policies:
                print(f"   - {policy['name']} ({policy['priority']})")
        except Exception as e:
            print(f"❌ Error getting existing policies: {e}")

if __name__ == '__main__':
    test_sla_service()
