#!/usr/bin/env python3
"""
Register agent manually in database for real data collection
"""
import psycopg2
import uuid
from datetime import datetime

def register_agent_manually():
    """Register agent manually in database"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='lanet_helpdesk',
            user='postgres',
            password='Poikl55+*'
        )
        
        cursor = conn.cursor()
        
        # Check if asset already exists
        hostname = 'benny-lenovo'
        cursor.execute("SELECT asset_id FROM assets WHERE name = %s", (hostname,))
        existing = cursor.fetchone()
        
        if existing:
            asset_id = existing[0]
            print(f'✅ Asset ya existe: {asset_id}')
        else:
            # Create new asset for real agent
            asset_id = str(uuid.uuid4())
            
            # Get client and site IDs
            cursor.execute("SELECT id FROM clients WHERE name = 'Industrias Tebi'")
            client_result = cursor.fetchone()
            
            if not client_result:
                print('❌ Cliente "Industrias Tebi" no encontrado')
                return False
            
            client_id = client_result[0]
            
            cursor.execute("SELECT id FROM sites WHERE client_id = %s LIMIT 1", (client_id,))
            site_result = cursor.fetchone()
            
            if not site_result:
                print('❌ Sitio no encontrado para Industrias Tebi')
                return False
            
            site_id = site_result[0]
            
            # Insert asset
            insert_asset_query = """
                INSERT INTO assets (
                    asset_id, name, hostname, client_id, site_id, 
                    status, created_at, updated_at, last_seen
                ) VALUES (
                    %s, %s, %s, %s, %s, 
                    'online', %s, %s, %s
                )
            """
            
            now = datetime.now()
            cursor.execute(insert_asset_query, (
                asset_id, hostname, hostname, client_id, site_id,
                now, now, now
            ))
            
            print(f'✅ Asset creado: {asset_id}')
        
        # Update agent config with asset_id
        config_update = f"""
        {{
            "asset_id": "{asset_id}",
            "client_id": "{client_id}",
            "site_id": "{site_id}",
            "registered": true,
            "registration_date": "{datetime.now().isoformat()}"
        }}
        """
        
        # Save to agent config file
        import json
        
        # Read current config
        with open('lanet_agent/config/agent_config.json', 'r') as f:
            config = json.load(f)
        
        # Add registration info
        config['registration'] = {
            "asset_id": asset_id,
            "client_id": client_id,
            "site_id": site_id,
            "registered": True,
            "registration_date": datetime.now().isoformat()
        }
        
        # Save updated config
        with open('lanet_agent/config/agent_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Commit database changes
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f'✅ Agente registrado manualmente')
        print(f'   Asset ID: {asset_id}')
        print(f'   Cliente: {client_id}')
        print(f'   Sitio: {site_id}')
        print('✅ Configuración actualizada')
        
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    register_agent_manually()
