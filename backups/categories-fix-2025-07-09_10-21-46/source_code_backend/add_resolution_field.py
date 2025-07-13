#!/usr/bin/env python3
"""
Add resolution_notes field to tickets table
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def add_resolution_field():
    try:
        # Parse DATABASE_URL
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            # Extract connection details from URL
            import re
            match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', database_url)
            if match:
                user, password, host, port, database = match.groups()
                conn = psycopg2.connect(
                    host=host,
                    database=database,
                    user=user,
                    password=password,
                    port=port
                )
            else:
                raise ValueError("Invalid DATABASE_URL format")
        else:
            # Fallback to individual env vars
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'lanet_helpdesk'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'admin123'),
                port=os.getenv('DB_PORT', '5432')
            )
        
        cursor = conn.cursor()
        
        # Add resolution_notes column
        print('Adding resolution_notes column...')
        cursor.execute('ALTER TABLE tickets ADD COLUMN IF NOT EXISTS resolution_notes TEXT')
        
        # Verify column exists
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'tickets' AND column_name = 'resolution_notes'
        """)
        
        result = cursor.fetchone()
        
        if result:
            print(f'✅ Verified: {result[0]} ({result[1]}) - Nullable: {result[2]}')
        else:
            print('❌ Column verification failed')
            return False
            
        # Test query
        cursor.execute('SELECT ticket_id, resolution_notes FROM tickets LIMIT 1')
        test_result = cursor.fetchone()
        
        print('✅ Database queries working correctly')
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == '__main__':
    success = add_resolution_field()
    if success:
        print('\n🎉 Resolution field added successfully!')
    else:
        print('\n💥 Failed to add resolution field')
