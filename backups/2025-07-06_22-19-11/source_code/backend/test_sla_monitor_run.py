#!/usr/bin/env python3
"""
Test the actual SLA monitor run function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sla_monitor_run():
    """Test the actual SLA monitor run function"""
    print("🔧 TESTING ACTUAL SLA MONITOR RUN FUNCTION")
    print("=" * 60)
    
    try:
        from jobs.sla_monitor import run_sla_monitor
        
        print("✅ SLA monitor imported successfully")
        print("🔧 Running single SLA monitor iteration...")
        
        # Run the SLA monitor once
        run_sla_monitor()
        
        print("✅ SLA monitor completed successfully!")
        
    except Exception as e:
        print(f"❌ SLA monitor failed: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()

if __name__ == '__main__':
    test_sla_monitor_run()
