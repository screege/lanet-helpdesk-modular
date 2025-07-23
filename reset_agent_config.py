import sqlite3
import os

def reset_agent_config():
    """Reset agent local configuration to force re-registration"""
    
    # Path to agent database
    db_path = "lanet_agent/data/agent.db"
    
    if not os.path.exists(db_path):
        print("❌ Agent database not found")
        return
    
    print("🔄 Resetting agent local configuration...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear all configuration except the token
        print("  Clearing old configuration...")
        
        # Keep only the agent_token, clear everything else
        cursor.execute("DELETE FROM agent_config WHERE key != 'agent_token'")
        deleted_count = cursor.rowcount
        
        print(f"  Deleted {deleted_count} configuration entries")
        
        # Show remaining config
        cursor.execute('SELECT key, value FROM agent_config ORDER BY key')
        configs = cursor.fetchall()
        
        print(f"  Remaining configuration entries: {len(configs)}")
        for key, value in configs:
            print(f"    {key}: {value}")
        
        conn.commit()
        conn.close()
        
        print("✅ Agent configuration reset successfully!")
        print("🔄 The agent will re-register with correct information on next startup")
        
    except Exception as e:
        print(f"❌ Error resetting agent config: {e}")

if __name__ == "__main__":
    reset_agent_config()
