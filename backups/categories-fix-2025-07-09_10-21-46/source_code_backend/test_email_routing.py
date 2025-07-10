#!/usr/bin/env python3
"""
Test script for email routing system
Tests both domain-based and email-based authorization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from modules.email.routing_service import EmailRoutingService

def test_email_routing():
    """Test email routing for screege@gmail.com"""
    
    app = create_app()
    
    with app.app_context():
        print("🔧 Testing Email Routing for screege@gmail.com")
        print("=" * 60)
        
        routing_service = EmailRoutingService()
        
        # Test the routing
        test_email = "screege@gmail.com"
        print(f"Testing email: {test_email}")
        
        try:
            result = routing_service.route_email_to_client_site(test_email)
            
            print(f"\n📧 Routing Result:")
            print(f"   Email: {test_email}")
            print(f"   Decision: {result.get('routing_decision')}")
            print(f"   Confidence: {result.get('routing_confidence')}")
            print(f"   Client ID: {result.get('client_id')}")
            print(f"   Client Name: {result.get('client_name')}")
            print(f"   Site ID: {result.get('site_id')}")
            print(f"   Site Name: {result.get('site_name')}")
            print(f"   Priority: {result.get('priority')}")
            print(f"   Reason: {result.get('reason', 'N/A')}")
            
            if result.get('routing_decision') == 'unauthorized':
                print(f"\n❌ ROUTING FAILED!")
                print(f"   Reason: {result.get('reason')}")
                return False
            else:
                print(f"\n✅ ROUTING SUCCESSFUL!")
                print(f"   Routed to: {result.get('client_name')} - {result.get('site_name')}")
                return True
                
        except Exception as e:
            print(f"\n❌ ERROR during routing: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_email_routing()
    sys.exit(0 if success else 1)
