#!/usr/bin/env python3
"""
Crear tabla para historial de resoluciones
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_resolution_history_table():
    try:
        # Parse DATABASE_URL
        database_url = os.getenv('DATABASE_URL')
        if database_url:
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
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'lanet_helpdesk'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'admin123'),
                port=os.getenv('DB_PORT', '5432')
            )
        
        cursor = conn.cursor()
        
        # Crear tabla de historial de resoluciones
        print('Creando tabla ticket_resolutions...')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket_resolutions (
                resolution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                ticket_id UUID NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
                resolution_notes TEXT NOT NULL,
                resolved_by UUID NOT NULL REFERENCES users(user_id),
                resolved_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticket_resolutions_ticket_id ON ticket_resolutions(ticket_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticket_resolutions_resolved_at ON ticket_resolutions(resolved_at)')
        
        print('✅ Tabla ticket_resolutions creada')
        
        # Migrar resoluciones existentes
        cursor.execute('''
            INSERT INTO ticket_resolutions (ticket_id, resolution_notes, resolved_by, resolved_at)
            SELECT
                ticket_id,
                resolution_notes,
                COALESCE(assigned_to, created_by) as resolved_by,
                resolved_at
            FROM tickets
            WHERE resolution_notes IS NOT NULL
            AND resolved_at IS NOT NULL
            AND COALESCE(assigned_to, created_by) IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM ticket_resolutions tr
                WHERE tr.ticket_id = tickets.ticket_id
            )
        ''')
        
        migrated = cursor.rowcount
        print(f'✅ Migradas {migrated} resoluciones existentes')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == '__main__':
    success = create_resolution_history_table()
    if success:
        print('\n🎉 Tabla de historial de resoluciones creada!')
    else:
        print('\n💥 Error al crear tabla')
