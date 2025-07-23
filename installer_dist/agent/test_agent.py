#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent - Test Script
Test the agent functionality against the operational backend
"""

import sys
import os
import logging
import time

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.logger import setup_logging
from core.config_manager import ConfigManager
from core.agent_core import AgentCore

def test_agent_registration():
    """Test agent registration with the verified token"""
    print("🧪 Testing Agent Registration...")
    
    # Setup logging
    setup_logging(logging.INFO)
    logger = logging.getLogger('lanet_agent.test')
    
    try:
        # Initialize configuration
        config = ConfigManager()
        
        # Test token (verified working)
        test_token = "LANET-550E-660E-AEB0F9"
        
        # Initialize agent
        agent = AgentCore(config, ui_enabled=False)
        
        # Test registration
        logger.info(f"Testing registration with token: {test_token}")
        success = agent.register_with_token(test_token)
        
        if success:
            print("✅ Registration test PASSED")
            logger.info("Registration test successful")
            
            # Test if agent is registered
            if agent.is_registered():
                print("✅ Agent registration verification PASSED")
                
                # Get registration details
                asset_id = agent.database.get_config('asset_id')
                client_name = agent.database.get_config('client_name')
                site_name = agent.database.get_config('site_name')
                
                print(f"📋 Registration Details:")
                print(f"   Asset ID: {asset_id}")
                print(f"   Client: {client_name}")
                print(f"   Site: {site_name}")
                
                return True
            else:
                print("❌ Agent registration verification FAILED")
                return False
        else:
            print("❌ Registration test FAILED")
            logger.error("Registration test failed")
            return False
            
    except Exception as e:
        print(f"❌ Registration test ERROR: {e}")
        logger.error(f"Registration test error: {e}", exc_info=True)
        return False

def test_heartbeat():
    """Test heartbeat functionality"""
    print("\n🧪 Testing Heartbeat...")
    
    logger = logging.getLogger('lanet_agent.test')
    
    try:
        # Initialize configuration
        config = ConfigManager()
        
        # Initialize agent
        agent = AgentCore(config, ui_enabled=False)
        
        # Check if agent is registered
        if not agent.is_registered():
            print("❌ Agent not registered - cannot test heartbeat")
            return False
        
        # Test heartbeat
        logger.info("Testing heartbeat...")
        success = agent.heartbeat.send_heartbeat()
        
        if success:
            print("✅ Heartbeat test PASSED")
            logger.info("Heartbeat test successful")
            return True
        else:
            print("❌ Heartbeat test FAILED")
            logger.error("Heartbeat test failed")
            return False
            
    except Exception as e:
        print(f"❌ Heartbeat test ERROR: {e}")
        logger.error(f"Heartbeat test error: {e}", exc_info=True)
        return False

def test_monitoring():
    """Test monitoring functionality"""
    print("\n🧪 Testing Monitoring...")
    
    logger = logging.getLogger('lanet_agent.test')
    
    try:
        # Initialize configuration
        config = ConfigManager()
        
        # Initialize agent
        agent = AgentCore(config, ui_enabled=False)
        
        # Test monitoring
        logger.info("Testing system metrics collection...")
        metrics = agent.monitoring.collect_system_metrics()
        
        if metrics and 'cpu_usage' in metrics:
            print("✅ Monitoring test PASSED")
            print(f"📊 Sample Metrics:")
            print(f"   CPU Usage: {metrics.get('cpu_usage', 0):.1f}%")
            print(f"   Memory Usage: {metrics.get('memory_usage', 0):.1f}%")
            print(f"   Disk Usage: {metrics.get('disk_usage', 0):.1f}%")
            print(f"   Network Status: {metrics.get('network_status', 'unknown')}")
            
            logger.info("Monitoring test successful")
            return True
        else:
            print("❌ Monitoring test FAILED - no metrics collected")
            logger.error("Monitoring test failed")
            return False
            
    except Exception as e:
        print(f"❌ Monitoring test ERROR: {e}")
        logger.error(f"Monitoring test error: {e}", exc_info=True)
        return False

def test_ticket_creation():
    """Test ticket creation functionality"""
    print("\n🧪 Testing Ticket Creation...")
    
    logger = logging.getLogger('lanet_agent.test')
    
    try:
        # Initialize configuration
        config = ConfigManager()
        
        # Initialize agent
        agent = AgentCore(config, ui_enabled=False)
        
        # Check if agent is registered
        if not agent.is_registered():
            print("❌ Agent not registered - cannot test ticket creation")
            return False
        
        # Test ticket creation
        logger.info("Testing ticket creation...")
        
        test_subject = "Test Ticket from Agent"
        test_description = "This is a test ticket created by the LANET Agent during testing."
        
        success = agent.create_ticket(
            subject=test_subject,
            description=test_description,
            priority="baja",
            include_system_info=True
        )
        
        if success:
            print("✅ Ticket creation test PASSED")
            print(f"📝 Test ticket created successfully")
            logger.info("Ticket creation test successful")
            return True
        else:
            print("❌ Ticket creation test FAILED")
            logger.error("Ticket creation test failed")
            return False
            
    except Exception as e:
        print(f"❌ Ticket creation test ERROR: {e}")
        logger.error(f"Ticket creation test error: {e}", exc_info=True)
        return False

def test_configuration():
    """Test configuration management"""
    print("\n🧪 Testing Configuration...")
    
    logger = logging.getLogger('lanet_agent.test')
    
    try:
        # Test configuration loading
        config = ConfigManager()
        
        # Test basic configuration values
        server_url = config.get_server_url()
        heartbeat_interval = config.get('agent.heartbeat_interval')
        agent_version = config.get('agent.version')
        
        print(f"📋 Configuration Test:")
        print(f"   Server URL: {server_url}")
        print(f"   Heartbeat Interval: {heartbeat_interval}s")
        print(f"   Agent Version: {agent_version}")
        
        if server_url and heartbeat_interval and agent_version:
            print("✅ Configuration test PASSED")
            logger.info("Configuration test successful")
            return True
        else:
            print("❌ Configuration test FAILED - missing values")
            logger.error("Configuration test failed")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test ERROR: {e}")
        logger.error(f"Configuration test error: {e}", exc_info=True)
        return False

def main():
    """Run all tests"""
    print("🚀 LANET Agent Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Registration", test_agent_registration),
        ("Monitoring", test_monitoring),
        ("Heartbeat", test_heartbeat),
        ("Ticket Creation", test_ticket_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            print(f"❌ {test_name} test CRASHED: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Agent is ready for use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the logs for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
