#!/usr/bin/env python3
"""
Diagnóstico del módulo BitLocker
"""
import sys
import os
import logging

# Add the lanet_agent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lanet_agent'))

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_bitlocker_import():
    """Test BitLocker module import"""
    print("🔍 Testing BitLocker module import...")
    
    try:
        from lanet_agent.modules.bitlocker import BitLockerCollector
        print("✅ BitLocker module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import BitLocker module: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing BitLocker: {e}")
        return False

def test_bitlocker_initialization():
    """Test BitLocker collector initialization"""
    print("\n🔍 Testing BitLocker collector initialization...")
    
    try:
        from lanet_agent.modules.bitlocker import BitLockerCollector
        collector = BitLockerCollector()
        print("✅ BitLocker collector initialized successfully")
        return collector
    except Exception as e:
        print(f"❌ Failed to initialize BitLocker collector: {e}")
        return None

def test_bitlocker_collection(collector):
    """Test BitLocker data collection"""
    print("\n🔍 Testing BitLocker data collection...")
    
    if not collector:
        print("❌ No collector available for testing")
        return None
    
    try:
        bitlocker_info = collector.get_bitlocker_info()
        print("✅ BitLocker data collection completed")
        print(f"📊 Result: {bitlocker_info}")
        return bitlocker_info
    except Exception as e:
        print(f"❌ Failed to collect BitLocker data: {e}")
        return None

def test_monitoring_module():
    """Test monitoring module BitLocker integration"""
    print("\n🔍 Testing monitoring module BitLocker integration...")
    
    try:
        from lanet_agent.core.config_manager import ConfigManager
        from lanet_agent.core.database import DatabaseManager
        from lanet_agent.modules.monitoring import MonitoringModule
        
        # Initialize components
        config = ConfigManager()
        db = DatabaseManager('data/agent.db')
        monitoring = MonitoringModule(config, db)
        
        print(f"✅ Monitoring module initialized")
        print(f"📊 BitLocker collector available: {monitoring.bitlocker_collector is not None}")
        
        if monitoring.bitlocker_collector:
            print("🔍 Testing get_bitlocker_info method...")
            bitlocker_info = monitoring.get_bitlocker_info()
            print(f"📊 BitLocker info: {bitlocker_info}")
        
        return monitoring
        
    except Exception as e:
        print(f"❌ Failed to test monitoring module: {e}")
        return None

def main():
    print("🚀 LANET Agent BitLocker Diagnosis")
    print("=" * 50)
    
    # Test 1: Import
    import_success = test_bitlocker_import()
    
    # Test 2: Initialization
    collector = test_bitlocker_initialization() if import_success else None
    
    # Test 3: Data collection
    bitlocker_data = test_bitlocker_collection(collector) if collector else None
    
    # Test 4: Monitoring module integration
    monitoring = test_monitoring_module()
    
    print("\n" + "=" * 50)
    print("📋 DIAGNOSIS SUMMARY:")
    print(f"✅ Import: {'SUCCESS' if import_success else 'FAILED'}")
    print(f"✅ Initialization: {'SUCCESS' if collector else 'FAILED'}")
    print(f"✅ Data Collection: {'SUCCESS' if bitlocker_data else 'FAILED'}")
    print(f"✅ Monitoring Integration: {'SUCCESS' if monitoring and monitoring.bitlocker_collector else 'FAILED'}")
    
    if bitlocker_data:
        print(f"\n📊 BitLocker Status:")
        print(f"   Supported: {bitlocker_data.get('supported', 'Unknown')}")
        print(f"   Total Volumes: {bitlocker_data.get('total_volumes', 0)}")
        print(f"   Protected Volumes: {bitlocker_data.get('protected_volumes', 0)}")
        if bitlocker_data.get('reason'):
            print(f"   Reason: {bitlocker_data.get('reason')}")

if __name__ == '__main__':
    main()
