#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Force a TIER 2 heartbeat to test the new SMART functionality
"""

import sqlite3
import os

def force_tier2_heartbeat():
    """Force the next heartbeat to be TIER 2 (full inventory)"""
    try:
        print("🔄 Forcing TIER 2 heartbeat...")
        
        # Connect to the agent's database
        db_path = os.path.join('lanet_agent', 'data', 'agent.db')
        if not os.path.exists(db_path):
            db_path = os.path.join('data', 'agent.db')
            
        if not os.path.exists(db_path):
            print("❌ Agent database not found")
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Set the last inventory sent to a very old date to force a new one
        cursor.execute("""
            UPDATE agent_config
            SET value = '2020-01-01T00:00:00'
            WHERE key = 'last_inventory_sent'
        """)

        # If the key doesn't exist, insert it
        cursor.execute("""
            INSERT OR IGNORE INTO agent_config (key, value, updated_at)
            VALUES ('last_inventory_sent', '2020-01-01T00:00:00', datetime('now'))
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Forced TIER 2 heartbeat - agent will send full inventory on next heartbeat")
        print("⏳ Wait for the next heartbeat cycle (up to 5 minutes) or restart the agent")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    force_tier2_heartbeat()
