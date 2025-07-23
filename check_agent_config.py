import sqlite3
import json
import os

def check_agent_config():
    """Check agent local configuration"""
    
    # Path to agent database
    db_path = "lanet_agent/data/agent.db"
    
    if not os.path.exists(db_path):
        print("❌ Agent database not found")
        return
    
    print("🔍 Checking agent local configuration...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all configuration
        cursor.execute('SELECT key, value FROM agent_config ORDER BY key')
        configs = cursor.fetchall()
        
        print(f"\n📊 Found {len(configs)} configuration entries:")
        
        for key, value in configs:
            try:
                # Try to parse as JSON
                parsed_value = json.loads(value)
                if isinstance(parsed_value, dict):
                    print(f"\n  {key}:")
                    for k, v in parsed_value.items():
                        print(f"    {k}: {v}")
                else:
                    print(f"  {key}: {parsed_value}")
            except json.JSONDecodeError:
                print(f"  {key}: {value}")
        
        # Check specific client/site info
        print("\n🏢 Client/Site Information:")
        important_keys = ['client_id', 'client_name', 'site_id', 'site_name', 'asset_id', 'agent_token']
        
        for key in important_keys:
            cursor.execute('SELECT value FROM agent_config WHERE key = ?', (key,))
            result = cursor.fetchone()
            if result:
                try:
                    value = json.loads(result[0])
                except json.JSONDecodeError:
                    value = result[0]
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: NOT SET")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking agent config: {e}")

if __name__ == "__main__":
    check_agent_config()
