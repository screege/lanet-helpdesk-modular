#!/usr/bin/env python3
"""
Simple test para reportes mensuales con prints
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from datetime import datetime

def simple_test():
    """Simple test with prints"""
    print("🔍 SIMPLE MONTHLY REPORTS TEST")
    print("=" * 50)
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        try:
            # Test basic database connection
            client_query = "SELECT client_id, name FROM clients WHERE is_active = true LIMIT 1"
            client = app.db_manager.execute_query(client_query, fetch='one')
            
            if not client:
                print("❌ No active clients found!")
                return
                
            print(f"✅ Found client: {client['name']} ({client['client_id']})")
            
            # Test tickets query
            client_id = client['client_id']
            now = datetime.now()
            start_date = datetime(now.year, now.month, 1)
            if now.month == 12:
                end_date = datetime(now.year + 1, 1, 1)
            else:
                end_date = datetime(now.year, now.month + 1, 1)
            
            tickets_query = """
                SELECT
                    t.ticket_number,
                    t.subject,
                    t.status,
                    t.priority,
                    t.created_at,
                    t.resolved_at,
                    u.name as technician_name,
                    s.name as site_name
                FROM tickets t
                LEFT JOIN users u ON t.assigned_to = u.user_id
                LEFT JOIN sites s ON t.site_id = s.site_id
                WHERE t.client_id = %s
                AND t.created_at >= %s
                AND t.created_at < %s
                ORDER BY t.created_at DESC
            """
            
            print(f"🔍 Searching tickets from {start_date} to {end_date}")
            tickets = app.db_manager.execute_query(
                tickets_query, 
                (client_id, start_date, end_date), 
                fetch='all'
            )
            
            print(f"📊 Found {len(tickets)} tickets")
            
            # Test file creation
            reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports_files')
            reports_dir = os.path.abspath(reports_dir)
            print(f"📁 Reports directory: {reports_dir}")
            print(f"📁 Directory exists: {os.path.exists(reports_dir)}")
            
            # Create test file
            client_name = client['name']
            filename = f"test_report_{client_name.lower().replace(' ', '_')}_{now.year}_{now.month:02d}.txt"
            file_path = os.path.join(reports_dir, filename)
            
            print(f"📄 Creating test file: {file_path}")
            
            # Ensure directory exists
            os.makedirs(reports_dir, exist_ok=True)
            
            # Create simple text file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"REPORTE DE PRUEBA - {client_name.upper()}\n")
                f.write(f"Período: {now.month}/{now.year}\n")
                f.write(f"Generado: {now.strftime('%d/%m/%Y %H:%M')}\n")
                f.write("="*50 + "\n\n")
                
                if tickets:
                    f.write(f"TOTAL DE TICKETS: {len(tickets)}\n\n")
                    for ticket in tickets:
                        f.write(f"Ticket #{ticket.get('ticket_number', 'N/A')}\n")
                        f.write(f"Asunto: {ticket.get('subject', 'Sin asunto')}\n")
                        f.write(f"Estado: {ticket.get('status', 'N/A')}\n")
                        f.write("-"*30 + "\n")
                else:
                    f.write("No se encontraron tickets para este período.\n")
            
            # Verify file was created
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"✅ File created successfully!")
                print(f"📁 File path: {file_path}")
                print(f"📁 File size: {file_size} bytes")
                
                # Show content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(300)
                    print(f"📄 First 300 characters:\n{content}")
                    
                return file_path
            else:
                print("❌ File was not created!")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

if __name__ == "__main__":
    result = simple_test()
    print(f"\n🎯 Final result: {result}")
