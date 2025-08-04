#!/usr/bin/env python3
"""
Check agent tokens in database
"""
import psycopg2

def check_tokens():
    """Check agent tokens"""
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
        
        # Check if agent_tokens table exists
        try:
            cursor.execute("SELECT token, client_id, site_id, is_active FROM agent_tokens WHERE token LIKE %s", ('LANET-550E-660E%',))
            results = cursor.fetchall()
            
            if results:
                for row in results:
                    print(f'Token: {row[0]}')
                    print(f'Client: {row[1]}')
                    print(f'Site: {row[2]}')
                    print(f'Active: {row[3]}')
            else:
                print('No matching tokens found')
                
                # Check what tokens exist
                cursor.execute('SELECT token, is_active FROM agent_tokens LIMIT 5')
                all_tokens = cursor.fetchall()
                print(f'Available tokens: {len(all_tokens)}')
                for token, active in all_tokens:
                    print(f'  {token} - Active: {active}')
                    
        except Exception as e:
            print(f'Error accessing agent_tokens: {e}')
            
            # Check what tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name LIKE '%token%'
            """)
            tables = cursor.fetchall()
            print(f'Token-related tables: {[t[0] for t in tables]}')
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'Database error: {e}')

if __name__ == '__main__':
    check_tokens()
