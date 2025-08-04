#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Configuration URL Issue
Update the config to use the correct key that the agent expects
"""

import json
from pathlib import Path

def fix_config():
    """Fix the configuration file to use the correct server URL key"""
    config_path = Path("C:/Program Files/LANET Agent/config/agent_config.json")
    
    print("Fixing configuration URL issue...")
    
    try:
        # Read current config
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("Current config server section:")
        print(json.dumps(config.get('server', {}), indent=2))
        
        # Fix the server URL key
        if 'server' in config:
            # Add base_url key that the agent expects
            if 'url' in config['server']:
                config['server']['base_url'] = config['server']['url']
                print(f"Added base_url: {config['server']['url']}")
            
            # Also ensure production_url exists
            if 'base_url' in config['server'] and 'production_url' not in config['server']:
                # If it's localhost, set production URL
                if 'localhost' in config['server']['base_url']:
                    config['server']['production_url'] = "https://helpdesk.lanet.mx/api"
                else:
                    config['server']['production_url'] = config['server']['base_url']
                print(f"Added production_url: {config['server']['production_url']}")
            
            # Set environment
            if 'environment' not in config['server']:
                config['server']['environment'] = 'development'
                print("Added environment: development")
        
        # Write updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("Configuration updated successfully!")
        
        print("\nUpdated config server section:")
        print(json.dumps(config.get('server', {}), indent=2))
        
        return True
        
    except Exception as e:
        print(f"Error fixing config: {e}")
        return False

def test_config():
    """Test that the config now works"""
    print("\nTesting configuration...")
    
    try:
        import sys
        sys.path.insert(0, "C:/Program Files/LANET Agent")
        
        from core.config_manager import ConfigManager
        
        config_manager = ConfigManager("C:/Program Files/LANET Agent/config/agent_config.json")
        
        # Test the methods the agent uses
        server_url = config_manager.get_server_url()
        base_url = config_manager.get('server.base_url')
        url = config_manager.get('server.url')
        token = config_manager.get('registration.installation_token')
        
        print(f"get_server_url(): {server_url}")
        print(f"server.base_url: {base_url}")
        print(f"server.url: {url}")
        print(f"token: {token}")
        
        if server_url and server_url != 'None' and token:
            print("✅ Configuration is now working correctly!")
            return True
        else:
            print("❌ Configuration still has issues")
            return False
            
    except Exception as e:
        print(f"Error testing config: {e}")
        return False

def main():
    """Main fix function"""
    print("LANET Agent Configuration URL Fix")
    print("=" * 40)
    
    if fix_config():
        if test_config():
            print("\n🎉 SUCCESS: Configuration fixed!")
            print("\nNow try running the agent again:")
            print('python "C:\\Program Files\\LANET Agent\\run_direct.py"')
        else:
            print("\n❌ Configuration fix failed verification")
    else:
        print("\n❌ Failed to fix configuration")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
