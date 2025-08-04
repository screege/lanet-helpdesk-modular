#!/usr/bin/env python3
"""
Setup agent registration in local database
"""
import sqlite3
import os

def setup_agent_registration():
    """Setup agent registration in local database"""
    try:
        # Path to agent database
        db_path = 'lanet_agent/data/agent.db'
        
        if not os.path.exists(db_path):
            print(f'❌ Agent database not found: {db_path}')
            return False
        
        # Connect to agent database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if agent_config table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='agent_config'
        """)

        if not cursor.fetchone():
            print('❌ agent_config table not found in agent database')
            return False
        
        # Insert registration data
        registration_data = [
            ('asset_id', 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'),
            ('agent_token', 'LANET-REAL-TOKEN-12345'),  # Dummy token for now
            ('client_id', '75f6b906-db3a-404d-b032-3a52eac324c4'),
            ('site_id', 'd01df78a-c48b-40c2-b943-ef0830e26bf1'),
            ('client_name', 'Industrias Tebi'),
            ('site_name', 'Naucalpan'),
            ('registered', 'true'),
            ('registration_date', '2025-07-26T08:30:00.000000')
        ]
        
        # Delete existing registration data
        for key, _ in registration_data:
            cursor.execute('DELETE FROM agent_config WHERE key = ?', (key,))

        # Insert new registration data
        for key, value in registration_data:
            cursor.execute(
                'INSERT INTO agent_config (key, value, updated_at) VALUES (?, ?, datetime("now"))',
                (key, value)
            )
        
        # Commit changes
        conn.commit()
        
        # Verify data was inserted
        cursor.execute('SELECT key, value FROM agent_config WHERE key IN (?, ?)', ('asset_id', 'agent_token'))
        results = cursor.fetchall()
        
        print('✅ Agent registration data inserted:')
        for key, value in results:
            print(f'  {key}: {value}')
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    setup_agent_registration()
