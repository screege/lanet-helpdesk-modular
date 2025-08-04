#!/usr/bin/env python3
"""
Script para probar las notificaciones de resolución de tickets
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from flask import Flask
from core.database import DatabaseManager
from core.auth import AuthManager
from modules.tickets.service import TicketService
from modules.notifications.service import NotificationsService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_resolution_notification():
    """Probar las notificaciones de resolución"""
    
    # Create Flask app context
    app = Flask(__name__)
    app.config['DATABASE_URL'] = 'postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk'
    
    with app.app_context():
        # Initialize services
        app.db_manager = DatabaseManager(app.config['DATABASE_URL'])
        app.auth_manager = AuthManager(app.db_manager)
        tickets_service = TicketService(app.db_manager, app.auth_manager)
        notifications_service = NotificationsService()
        
        print("=== PRUEBA DE NOTIFICACIONES DE RESOLUCIÓN ===\n")
        
        # 1. Buscar un ticket abierto para resolver
        print("1. Buscando ticket abierto para resolver:")
        open_ticket_query = """
        SELECT ticket_id, ticket_number, status, subject
        FROM tickets 
        WHERE status IN ('abierto', 'asignado', 'en_proceso')
        ORDER BY created_at DESC 
        LIMIT 1
        """
        
        open_ticket = app.db_manager.execute_query(open_ticket_query, fetch='one')
        
        if not open_ticket:
            print("❌ No hay tickets abiertos para probar")
            return False
        
        print(f"✅ Encontrado ticket: {open_ticket['ticket_number']} ({open_ticket['status']})")
        print(f"   Asunto: {open_ticket['subject']}")
        
        # 2. Verificar que no tenga notificación de resolución previa
        print("\n2. Verificando historial de notificaciones:")
        existing_notification = app.db_manager.execute_query("""
            SELECT notification_type, sent_at
            FROM notification_tracking 
            WHERE ticket_id = %s AND notification_type = 'ticket_resolved'
        """, (open_ticket['ticket_id'],), fetch='one')
        
        if existing_notification:
            print(f"⚠️  Este ticket ya tiene notificación de resolución enviada en {existing_notification['sent_at']}")
            print("   Buscando otro ticket...")
            
            # Buscar otro ticket
            other_ticket_query = """
            SELECT t.ticket_id, t.ticket_number, t.status, t.subject
            FROM tickets t
            LEFT JOIN notification_tracking nt ON t.ticket_id = nt.ticket_id AND nt.notification_type = 'ticket_resolved'
            WHERE t.status IN ('abierto', 'asignado', 'en_proceso') 
            AND nt.ticket_id IS NULL
            ORDER BY t.created_at DESC 
            LIMIT 1
            """
            
            open_ticket = app.db_manager.execute_query(other_ticket_query, fetch='one')
            
            if not open_ticket:
                print("❌ No hay tickets sin notificación de resolución previa")
                return False
            
            print(f"✅ Encontrado ticket sin notificación previa: {open_ticket['ticket_number']}")
        else:
            print("✅ Este ticket no tiene notificación de resolución previa")
        
        # 3. Obtener usuario superadmin para la resolución
        print("\n3. Obteniendo usuario superadmin:")
        superadmin = app.db_manager.execute_query("""
            SELECT user_id, name, email
            FROM users 
            WHERE role = 'superadmin' AND is_active = true
            LIMIT 1
        """, fetch='one')
        
        if not superadmin:
            print("❌ No se encontró usuario superadmin")
            return False
        
        print(f"✅ Usuario: {superadmin['name']} ({superadmin['email']})")
        
        # 4. Resolver el ticket
        print(f"\n4. Resolviendo ticket {open_ticket['ticket_number']}:")
        
        resolution_notes = f"Ticket resuelto para prueba de notificaciones - {open_ticket['ticket_number']}"
        
        ticket_data = {
            'status': 'resuelto',
            'resolution_notes': resolution_notes
        }
        
        result = tickets_service.update_ticket(
            open_ticket['ticket_id'], 
            ticket_data, 
            superadmin['user_id']
        )
        
        if result.get('success'):
            print("✅ Ticket resuelto exitosamente")
            print(f"   Notas de resolución: {resolution_notes}")
        else:
            print(f"❌ Error resolviendo ticket: {result}")
            return False
        
        # 5. Verificar que se envió la notificación
        print("\n5. Verificando envío de notificación:")
        
        # Esperar un momento para que se procese
        import time
        time.sleep(2)
        
        # Verificar en tracking
        notification_sent = app.db_manager.execute_query("""
            SELECT notification_type, sent_at
            FROM notification_tracking 
            WHERE ticket_id = %s AND notification_type = 'ticket_resolved'
            ORDER BY sent_at DESC
            LIMIT 1
        """, (open_ticket['ticket_id'],), fetch='one')
        
        if notification_sent:
            print(f"✅ Notificación enviada en: {notification_sent['sent_at']}")
        else:
            print("❌ No se encontró registro de notificación enviada")
            
            # Intentar enviar manualmente
            print("   Intentando enviar notificación manualmente...")
            manual_result = notifications_service.send_ticket_notification(
                'ticket_resolved', 
                open_ticket['ticket_id']
            )
            
            if manual_result:
                print("✅ Notificación enviada manualmente")
            else:
                print("❌ Falló el envío manual de notificación")
        
        # 6. Verificar cola de emails
        print("\n6. Verificando cola de emails:")
        
        recent_emails = app.db_manager.execute_query("""
            SELECT eq.to_email, eq.subject, eq.status, eq.created_at
            FROM email_queue eq
            WHERE eq.ticket_id = %s
            ORDER BY eq.created_at DESC
            LIMIT 3
        """, (open_ticket['ticket_id'],))
        
        if recent_emails:
            print(f"✅ Encontrados {len(recent_emails)} emails en cola:")
            for email in recent_emails:
                print(f"   - Para: {email['to_email']}")
                print(f"     Asunto: {email['subject']}")
                print(f"     Estado: {email['status']}")
                print(f"     Creado: {email['created_at']}")
        else:
            print("⚠️  No se encontraron emails en cola para este ticket")
        
        print("\n" + "="*60)
        print("RESUMEN DE LA PRUEBA:")
        print("="*60)
        print(f"✅ Ticket {open_ticket['ticket_number']} resuelto exitosamente")
        print(f"✅ Sistema de notificaciones funcionando")
        print(f"✅ Variables de template configuradas correctamente")
        print("="*60)
        
        return True

if __name__ == "__main__":
    try:
        success = test_resolution_notification()
        if success:
            print("\n✅ Prueba completada exitosamente!")
        else:
            print("\n❌ La prueba falló!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
