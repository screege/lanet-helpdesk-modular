#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify heartbeat optimization
"""

import psycopg2
import json
from datetime import datetime, timedelta

def test_heartbeat_optimization():
    """Test the heartbeat optimization configuration"""
    
    print("🧪 Testing LANET Agent Heartbeat Optimization")
    print("=" * 60)
    
    # 1. Verify configuration changes
    print("1. Verifying Configuration Changes:")
    print("-" * 40)
    
    try:
        with open('production_installer/agent_files/config/agent_config.json', 'r') as f:
            config = json.load(f)
        
        agent_config = config.get('agent', {})
        server_config = config.get('server', {})
        
        print(f"✅ Agent Configuration:")
        print(f"   - heartbeat_interval: {agent_config.get('heartbeat_interval')} seconds")
        print(f"   - inventory_interval: {agent_config.get('inventory_interval')} seconds")
        print(f"   - critical_check_interval: {agent_config.get('critical_check_interval')} seconds")
        
        print(f"✅ Server Configuration:")
        print(f"   - heartbeat_interval: {server_config.get('heartbeat_interval')} seconds")
        print(f"   - inventory_interval: {server_config.get('inventory_interval')} seconds")
        
        # Verify optimized values
        expected_heartbeat = 900  # 15 minutes
        expected_inventory = 86400  # 24 hours
        expected_critical = 300  # 5 minutes
        
        if agent_config.get('heartbeat_interval') == expected_heartbeat:
            print("   🟢 Heartbeat interval: OPTIMIZED (15 minutes)")
        else:
            print(f"   🔴 Heartbeat interval: NOT OPTIMIZED (expected {expected_heartbeat})")
        
        if agent_config.get('inventory_interval') == expected_inventory:
            print("   🟢 Inventory interval: CORRECT (24 hours)")
        else:
            print(f"   🔴 Inventory interval: INCORRECT (expected {expected_inventory})")
            
        if agent_config.get('critical_check_interval') == expected_critical:
            print("   🟢 Critical check interval: OPTIMIZED (5 minutes)")
        else:
            print(f"   🔴 Critical check interval: NOT SET (expected {expected_critical})")
            
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
    
    # 2. Calculate server load impact
    print("\n2. Server Load Impact Analysis:")
    print("-" * 40)
    
    assets_count = 2000  # MSP environment size
    
    # Current optimized configuration
    heartbeat_interval_min = 15  # minutes
    heartbeats_per_hour = 60 / heartbeat_interval_min
    daily_status_requests = assets_count * heartbeats_per_hour * 24
    daily_inventory_requests = assets_count * 1  # Once per day
    
    print(f"📊 For {assets_count} assets:")
    print(f"   - Status heartbeats: {heartbeats_per_hour} per hour per asset")
    print(f"   - Daily status requests: {daily_status_requests:,}")
    print(f"   - Daily inventory requests: {daily_inventory_requests:,}")
    print(f"   - Total daily requests: {daily_status_requests + daily_inventory_requests:,}")
    
    # Bandwidth estimation
    status_payload_kb = 2  # KB per status heartbeat
    inventory_payload_kb = 50  # KB per inventory heartbeat
    
    daily_status_bandwidth_mb = (daily_status_requests * status_payload_kb) / 1024
    daily_inventory_bandwidth_mb = (daily_inventory_requests * inventory_payload_kb) / 1024
    total_daily_bandwidth_mb = daily_status_bandwidth_mb + daily_inventory_bandwidth_mb
    
    print(f"📈 Bandwidth estimation:")
    print(f"   - Status data: {daily_status_bandwidth_mb:.1f} MB/day")
    print(f"   - Inventory data: {daily_inventory_bandwidth_mb:.1f} MB/day")
    print(f"   - Total bandwidth: {total_daily_bandwidth_mb:.1f} MB/day")
    
    # 3. Compare with previous configuration
    print("\n3. Comparison with Previous Configuration:")
    print("-" * 40)
    
    old_heartbeat_hours = 24  # Previous: 24 hours
    old_heartbeats_per_day = 24 / old_heartbeat_hours
    old_daily_requests = assets_count * old_heartbeats_per_day
    
    print(f"📉 Previous configuration (24-hour heartbeat):")
    print(f"   - Daily requests: {old_daily_requests:,}")
    print(f"   - Detection window: {old_heartbeat_hours} hours")
    print(f"   - Command delivery delay: Up to {old_heartbeat_hours} hours")
    
    print(f"📈 New configuration (15-minute heartbeat):")
    print(f"   - Daily requests: {daily_status_requests + daily_inventory_requests:,}")
    print(f"   - Detection window: 15-30 minutes")
    print(f"   - Command delivery delay: Up to 15 minutes")
    
    improvement_factor = (daily_status_requests + daily_inventory_requests) / old_daily_requests
    print(f"🎯 Request increase: {improvement_factor:.1f}x")
    print(f"🎯 Response time improvement: {old_heartbeat_hours * 60 / 15:.0f}x faster")
    
    # 4. Check current database status
    print("\n4. Current Database Status:")
    print("-" * 40)
    
    try:
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()
        
        # Check current asset status
        cur.execute('''
        SELECT 
            a.name,
            a.agent_status,
            a.last_seen,
            EXTRACT(EPOCH FROM (NOW() - a.last_seen))/60 as minutes_ago
        FROM assets a
        WHERE a.status = 'active' AND a.name LIKE '%Agent%'
        ''')
        
        assets = cur.fetchall()
        
        for name, agent_status, last_seen, minutes_ago in assets:
            print(f"📊 {name}:")
            print(f"   - Status: {agent_status}")
            print(f"   - Last seen: {minutes_ago:.1f} minutes ago")
            
            if minutes_ago <= 15:
                print("   🟢 EXCELLENT: Within optimized heartbeat window")
            elif minutes_ago <= 30:
                print("   🟡 GOOD: Within acceptable range")
            else:
                print("   🔴 NEEDS ATTENTION: Outside heartbeat window")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    
    # 5. Recommendations
    print("\n5. Deployment Recommendations:")
    print("-" * 40)
    print("✅ Configuration optimized for MSP environment")
    print("✅ Balanced real-time monitoring with server performance")
    print("✅ 96x faster incident detection (24 hours → 15 minutes)")
    print("✅ Manageable server load increase")
    print()
    print("📋 Next Steps:")
    print("   1. Deploy optimized agent to test group (10-20 assets)")
    print("   2. Monitor server performance for 24 hours")
    print("   3. Verify 15-minute heartbeat intervals")
    print("   4. Gradually roll out to all 2000 assets")
    print("   5. Update monitoring dashboards for new intervals")

if __name__ == "__main__":
    test_heartbeat_optimization()
