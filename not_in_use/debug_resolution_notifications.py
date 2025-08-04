#!/usr/bin/env python3
"""
Script de diagnóstico para identificar por qué no se envían las notificaciones de tickets resueltos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from flask import Flask
from core.database import DatabaseManager
from core.auth import AuthManager
from modules.notifications.service import NotificationsService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def debug_resolution_notifications():
    """Diagnosticar el sistema de notificaciones de resolución"""
    
    # Create Flask app context
    app = Flask(__name__)
    app.config['DATABASE_URL'] = 'postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk'
    
    with app.app_context():
        # Initialize database manager and auth manager
        app.db_manager = DatabaseManager(app.config['DATABASE_URL'])
        app.auth_manager = AuthManager(app.db_manager)

        # Initialize notifications service
        notifications_service = NotificationsService()
        
        print("=== DIAGNÓSTICO DE NOTIFICACIONES DE RESOLUCIÓN ===\n")
        
        # 1. Verificar que existe la tabla notification_tracking
        print("1. Verificando tabla notification_tracking:")
        try:
            tracking_check = app.db_manager.execute_query("""
                SELECT COUNT(*) as count FROM notification_tracking
            """, fetch='one')
            print(f"✅ Tabla notification_tracking existe con {tracking_check['count']} registros")
        except Exception as e:
            print(f"❌ Error con tabla notification_tracking: {e}")
            print("   Esto puede estar bloqueando las notificaciones")
            return False
        
        # 2. Verificar templates de email para ticket_resolved
        print("\n2. Verificando templates de email:")
        template_query = """
        SELECT template_id, name, template_type, is_active, subject_template, body_template
        FROM email_templates 
        WHERE template_type = 'ticket_resolved'
        """
        
        templates = app.db_manager.execute_query(template_query)
        
        if templates:
            print(f"✅ Encontrados {len(templates)} templates para ticket_resolved:")
            for template in templates:
                status = "ACTIVO" if template['is_active'] else "INACTIVO"
                print(f"   - {template['name']} ({status})")
                if '{{resolution}}' in template['body_template']:
                    print(f"     ✅ Contiene variable {{{{resolution}}}}")
                else:
                    print(f"     ⚠️  NO contiene variable {{{{resolution}}}}")
        else:
            print("❌ No se encontraron templates para ticket_resolved")
            return False
        
        # 3. Buscar un ticket resuelto reciente para probar
        print("\n3. Buscando tickets resueltos recientes:")
        recent_resolved_query = """
        SELECT ticket_id, ticket_number, status, resolution_notes, resolved_at, client_id
        FROM tickets 
        WHERE status = 'resuelto' 
        ORDER BY resolved_at DESC 
        LIMIT 3
        """
        
        resolved_tickets = app.db_manager.execute_query(recent_resolved_query)
        
        if not resolved_tickets:
            print("❌ No hay tickets resueltos para probar")
            return False
        
        print(f"✅ Encontrados {len(resolved_tickets)} tickets resueltos:")
        for ticket in resolved_tickets:
            print(f"   - {ticket['ticket_number']} resuelto en {ticket['resolved_at']}")
        
        # Usar el primer ticket para las pruebas
        test_ticket = resolved_tickets[0]
        print(f"\n🔧 Usando ticket {test_ticket['ticket_number']} para diagnóstico")
        
        # 4. Verificar si ya se envió notificación para este ticket
        print("\n4. Verificando historial de notificaciones:")
        notification_history_query = """
        SELECT notification_type, sent_at, comment_id
        FROM notification_tracking 
        WHERE ticket_id = %s
        ORDER BY sent_at DESC
        """
        
        history = app.db_manager.execute_query(notification_history_query, (test_ticket['ticket_id'],))
        
        if history:
            print(f"   Encontradas {len(history)} notificaciones previas:")
            for notif in history:
                print(f"   - {notif['notification_type']} enviada en {notif['sent_at']}")
        else:
            print("   No hay notificaciones previas para este ticket")
        
        # 5. Probar obtener detalles del ticket
        print("\n5. Probando _get_ticket_details:")
        ticket_details = notifications_service._get_ticket_details(test_ticket['ticket_id'])
        
        if ticket_details:
            print("✅ Detalles del ticket obtenidos correctamente")
            print(f"   Ticket: {ticket_details['ticket_number']}")
            print(f"   Estado: {ticket_details['status']}")
            print(f"   Cliente: {ticket_details.get('client_name', 'N/A')}")
            
            # Verificar campos de resolución
            resolution = ticket_details.get('resolution')
            resolution_notes = ticket_details.get('resolution_notes')
            print(f"   Campo 'resolution': {resolution[:50] if resolution else 'None'}...")
            print(f"   Campo 'resolution_notes': {resolution_notes[:50] if resolution_notes else 'None'}...")
        else:
            print("❌ No se pudieron obtener detalles del ticket")
            return False
        
        # 6. Probar preparación de variables de template
        print("\n6. Probando _prepare_template_variables:")
        template_vars = notifications_service._prepare_template_variables(ticket_details)
        
        resolution_var = template_vars.get('resolution')
        resolution_notes_var = template_vars.get('resolution_notes')
        
        print(f"   Variable 'resolution': {resolution_var[:50] if resolution_var else 'None'}...")
        print(f"   Variable 'resolution_notes': {resolution_notes_var[:50] if resolution_notes_var else 'None'}...")
        
        if not resolution_var and not resolution_notes_var:
            print("❌ Las variables de resolución están vacías")
        else:
            print("✅ Variables de resolución configuradas correctamente")
        
        # 7. Verificar destinatarios
        print("\n7. Verificando destinatarios de notificaciones:")
        notification_config = notifications_service.notification_types['ticket_resolved']
        
        try:
            recipients = notifications_service._get_notification_recipients(
                ticket_details,
                notification_config['recipients'],
                None
            )
            
            if recipients:
                print(f"✅ Encontrados {len(recipients)} destinatarios:")
                for recipient in recipients:
                    print(f"   - {recipient['email']} ({recipient.get('type', 'unknown')})")
            else:
                print("❌ No se encontraron destinatarios")
                print("   Esto puede ser la causa de que no se envíen notificaciones")
        except Exception as e:
            print(f"❌ Error obteniendo destinatarios: {e}")
        
        # 8. Verificar configuración de email
        print("\n8. Verificando configuración de email:")
        email_config_query = """
        SELECT config_id, smtp_server, smtp_port, smtp_username, is_active
        FROM email_configurations 
        WHERE is_active = true AND is_default = true
        """
        
        email_config = app.db_manager.execute_query(email_config_query, fetch='one')
        
        if email_config:
            print(f"✅ Configuración de email activa:")
            print(f"   Servidor: {email_config['smtp_server']}:{email_config['smtp_port']}")
            print(f"   Usuario: {email_config['smtp_username']}")
        else:
            print("❌ No hay configuración de email activa")
            print("   Las notificaciones no se pueden enviar sin configuración SMTP")
        
        # 9. Verificar cola de emails
        print("\n9. Verificando cola de emails:")
        queue_query = """
        SELECT COUNT(*) as pending_count
        FROM email_queue 
        WHERE status = 'pending'
        """
        
        queue_status = app.db_manager.execute_query(queue_query, fetch='one')
        print(f"   Emails pendientes en cola: {queue_status['pending_count']}")
        
        # 10. Simular envío de notificación (sin enviar realmente)
        print("\n10. Simulando envío de notificación:")
        
        # Verificar si ya se envió
        already_sent = notifications_service._is_notification_already_sent(
            test_ticket['ticket_id'], 
            'ticket_resolved'
        )
        
        if already_sent:
            print("⚠️  La notificación ya fue enviada para este ticket")
            print("   El sistema de deduplicación está funcionando")
        else:
            print("✅ El ticket está listo para recibir notificación de resolución")
        
        print("\n" + "="*60)
        print("RESUMEN DEL DIAGNÓSTICO:")
        print("="*60)
        
        return True

if __name__ == "__main__":
    try:
        success = debug_resolution_notifications()
        if success:
            print("\n✅ Diagnóstico completado!")
        else:
            print("\n❌ Se encontraron problemas en el diagnóstico!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error en diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
