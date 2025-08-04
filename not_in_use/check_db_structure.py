#!/usr/bin/env python3
"""
Check database structure for agent registration
"""
import psycopg2

def check_db_structure():
    """Check database structure"""
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
        
        # Check clients table structure
        print('🔍 Clients table structure:')
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'clients' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        for column_name, data_type in columns:
            print(f'  {column_name}: {data_type}')
        
        # Check assets table structure
        print('\n🔍 Assets table structure:')
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'assets' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        for column_name, data_type in columns:
            print(f'  {column_name}: {data_type}')
        
        # Check what clients exist
        print('\n🔍 Available clients:')
        cursor.execute("SELECT * FROM clients LIMIT 3")
        clients = cursor.fetchall()
        
        # Get column names
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'clients' 
            ORDER BY ordinal_position
        """)
        client_columns = [row[0] for row in cursor.fetchall()]
        
        for client in clients:
            print(f'  Client: {dict(zip(client_columns, client))}')
        
        # Check what assets exist
        print('\n🔍 Available assets:')
        cursor.execute("SELECT * FROM assets LIMIT 3")
        assets = cursor.fetchall()
        
        # Get column names
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'assets' 
            ORDER BY ordinal_position
        """)
        asset_columns = [row[0] for row in cursor.fetchall()]
        
        for asset in assets:
            print(f'  Asset: {dict(zip(asset_columns, asset))}')
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == '__main__':
    check_db_structure()
