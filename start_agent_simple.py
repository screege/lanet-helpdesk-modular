#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple LANET Agent Starter
Runs the agent without Windows service complications
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def start_agent_simple():
    """Start the agent in a simple way"""
    print("🚀 Starting LANET Agent (Simple Mode)")
    print("=" * 50)
    
    # Change to agent directory
    agent_dir = Path("C:/Program Files/LANET Agent")
    
    if not agent_dir.exists():
        print(f"❌ Agent directory not found: {agent_dir}")
        return False
    
    print(f"📁 Agent directory: {agent_dir}")
    
    # Check if main.py exists
    main_file = agent_dir / "main.py"
    if not main_file.exists():
        print(f"❌ Main agent file not found: {main_file}")
        return False
    
    print(f"✅ Agent main file found: {main_file}")
    
    # Change working directory
    os.chdir(str(agent_dir))
    print(f"📂 Changed to directory: {os.getcwd()}")
    
    # Set environment variable to disable UI
    os.environ['LANET_SERVICE_MODE'] = '1'
    os.environ['LANET_NO_UI'] = '1'
    
    print("🔧 Environment configured for service mode")
    print("🚀 Starting agent...")
    print("📋 Press Ctrl+C to stop the agent")
    print("-" * 50)
    
    try:
        # Run the agent
        result = subprocess.run([
            sys.executable, 
            str(main_file)
        ], cwd=str(agent_dir))
        
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Agent stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error running agent: {e}")
        return False

def check_backend_connection():
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
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        print("💡 Make sure the backend is running: python backend/app.py")
        return False

def show_agent_info():
    """Show agent configuration info"""
    print("📋 Agent Information:")
    
    config_file = Path("C:/Program Files/LANET Agent/config/agent_config.json")
    if config_file.exists():
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"  🔗 Server URL: {config.get('server', {}).get('url', 'Not configured')}")
            print(f"  🎫 Token: {config.get('registration', {}).get('installation_token', 'Not configured')}")
            print(f"  🏢 Client ID: {config.get('registration', {}).get('client_id', 'Not configured')}")
            print(f"  🏪 Site ID: {config.get('registration', {}).get('site_id', 'Not configured')}")
            print(f"  🔒 BitLocker: {'Enabled' if config.get('bitlocker', {}).get('enabled') else 'Disabled'}")
            
        except Exception as e:
            print(f"  ❌ Error reading config: {e}")
    else:
        print("  ❌ Configuration file not found")

def main():
    """Main function"""
    print("🤖 LANET Agent Simple Starter")
    print("=" * 50)
    
    # Show agent info
    show_agent_info()
    print()
    
    # Check backend
    if not check_backend_connection():
        print("\n⚠️ Warning: Backend is not running")
        print("The agent will try to connect but may fail")
        
        response = input("\nDo you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    print()
    
    # Start agent
    success = start_agent_simple()
    
    if success:
        print("\n✅ Agent finished successfully")
    else:
        print("\n❌ Agent finished with errors")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
