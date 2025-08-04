#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run LANET Agent Locally
Copies agent to local directory and runs it with proper permissions
"""

import os
import sys
import shutil
import json
from pathlib import Path

def copy_agent_to_local():
    """Copy agent from Program Files to local directory"""
    print("📁 Copying agent to local directory...")
    
    source_dir = Path("C:/Program Files/LANET Agent")
    local_dir = Path("lanet_agent_local")
    
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return None
    
    # Remove existing local directory
    if local_dir.exists():
        shutil.rmtree(local_dir)
        print("  🗑️ Removed existing local directory")
    
    # Copy agent files
    shutil.copytree(source_dir, local_dir)
    print(f"  ✅ Agent copied to: {local_dir}")
    
    # Create logs directory with proper permissions
    logs_dir = local_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Create data directory
    data_dir = local_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    return local_dir

def update_config_for_local(agent_dir):
    """Update configuration for local execution"""
    print("🔧 Updating configuration for local execution...")
    
    config_file = agent_dir / "config" / "agent_config.json"
    
    if not config_file.exists():
        print("❌ Configuration file not found")
        return False
    
    try:
        # Read current config
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Update paths to be relative
        config['database']['local_db_path'] = "data/agent.db"
        
        # Ensure server URL is correct
        config['server']['url'] = "http://localhost:5001/api"
        config['server']['base_url'] = "http://localhost:5001/api"
        
        # Write updated config
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("  ✅ Configuration updated")
        return True
        
    except Exception as e:
        print(f"  ❌ Error updating config: {e}")
        return False

def run_agent_local(agent_dir):
    """Run the agent from local directory"""
    print("🚀 Starting LANET Agent locally...")
    
    # Change to agent directory
    os.chdir(str(agent_dir))
    
    # Set environment variables
    os.environ['LANET_SERVICE_MODE'] = '1'
    os.environ['LANET_NO_UI'] = '1'
    
    print(f"📂 Working directory: {os.getcwd()}")
    print("🔧 Environment configured")
    print("📋 Press Ctrl+C to stop the agent")
    print("-" * 50)
    
    try:
        # Import and run agent directly
        sys.path.insert(0, str(agent_dir))
        
        # Import main agent
        from main import main as agent_main
        
        # Run agent
        agent_main()
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️ Agent stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error running agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_backend():
    """Check if backend is running"""
    print("🔍 Checking backend connection...")
    
    try:
        import requests
        response = requests.get("http://localhost:5001/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"⚠️ Backend responded with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        print("💡 Make sure the backend is running: python backend/app.py")
    
    return False

def show_agent_status():
    """Show current agent status"""
    print("📊 Checking agent status in database...")
    
    try:
        import psycopg2
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()
        
        # Check for recent assets
        cur.execute('''
            SELECT asset_id, name, last_seen, client_id, site_id
            FROM assets 
            WHERE last_seen > NOW() - INTERVAL '10 minutes'
            ORDER BY last_seen DESC
            LIMIT 5
        ''')
        
        assets = cur.fetchall()
        if assets:
            print(f"✅ Found {len(assets)} recent assets:")
            for asset in assets:
                print(f"  📱 {asset[1]} - Last seen: {asset[2]}")
        else:
            print("⚠️ No recent assets found")
        
        # Check BitLocker keys
        cur.execute('SELECT COUNT(*) FROM bitlocker_keys')
        bitlocker_count = cur.fetchone()[0]
        print(f"🔐 BitLocker keys in database: {bitlocker_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")

def main():
    """Main function"""
    print("🤖 LANET Agent Local Runner")
    print("=" * 50)
    
    # Check backend first
    if not check_backend():
        print("\n⚠️ Warning: Backend is not running")
        response = input("Do you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    print()
    
    # Copy agent to local directory
    agent_dir = copy_agent_to_local()
    if not agent_dir:
        print("❌ Failed to copy agent")
        return
    
    # Update configuration
    if not update_config_for_local(agent_dir):
        print("❌ Failed to update configuration")
        return
    
    print()
    
    # Show current status
    show_agent_status()
    
    print()
    
    # Run agent
    print("🚀 Starting agent...")
    success = run_agent_local(agent_dir)
    
    if success:
        print("\n✅ Agent finished successfully")
        
        # Show final status
        print("\n📊 Final status:")
        show_agent_status()
    else:
        print("\n❌ Agent finished with errors")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
