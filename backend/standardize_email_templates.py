#!/usr/bin/env python3
"""
Email Template Standardization Script
CRITICAL: Preserves bidirectional email communication subject line patterns
"""

import psycopg2
import json
import sys
from datetime import datetime

def standardize_email_templates():
    """Standardize email templates while preserving critical subject line patterns"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='localhost',
            database='lanet_helpdesk',
            user='postgres',
            password='Poikl55+*'
        )
        
        cur = conn.cursor()
        
        print("🔧 STANDARDIZING EMAIL TEMPLATES")
        print("⚠️  PRESERVING BIDIRECTIONAL EMAIL COMMUNICATION PATTERNS")
        print("=" * 60)
        
        # Standard LANET email template structure
        def get_standard_html_template(title, content):
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title} - LANET Helpdesk</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white;">
        <!-- Header -->
        <div style="background-color: #1e40af; color: white; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 24px; font-weight: bold;">LANET Helpdesk</h1>
            <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">Soluciones Tecnológicas</p>
        </div>
        
        <!-- Content -->
        <div style="padding: 30px;">
            {content}
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e0e0e0;">
            <p style="margin: 0; font-size: 14px; color: #666;">
                <strong>LANET - Soluciones Tecnológicas</strong><br>
                www.lanet.mx | soporte@lanet.mx<br>
                <em>Esta es una respuesta automática del sistema de tickets.</em>
            </p>
        </div>
    </div>
</body>
</html>"""

        # Template updates with preserved subject patterns
        template_updates = [
            {
                'template_type': 'ticket_created',
                'name': 'Ticket Creado - Notificación Cliente',
                'subject_template': '[LANET-{{ticket_number}}] Nuevo ticket creado: {{subject}}',
                'variables': ['{{ticket_number}}', '{{client_name}}', '{{site_name}}', '{{subject}}', '{{description}}', '{{priority}}', '{{affected_person}}', '{{created_date}}'],
                'content': """
            <h2 style="color: #1e40af; margin-bottom: 20px;">Ticket Creado Exitosamente</h2>
            <p>Estimado/a cliente de <strong>{{client_name}}</strong>,</p>
            <p>Su ticket ha sido creado exitosamente con los siguientes detalles:</p>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>Número de Ticket:</strong> {{ticket_number}}</li>
                    <li><strong>Título:</strong> {{subject}}</li>
                    <li><strong>Descripción:</strong> {{description}}</li>
                    <li><strong>Prioridad:</strong> {{priority}}</li>
                    <li><strong>Sitio:</strong> {{site_name}}</li>
                    <li><strong>Persona Afectada:</strong> {{affected_person}}</li>
                    <li><strong>Fecha de Creación:</strong> {{created_date}}</li>
                </ul>
            </div>
            <p>Nuestro equipo técnico revisará su solicitud y se pondrá en contacto con usted a la brevedad.</p>
            <p><strong>Importante:</strong> Para mantener la continuidad de la comunicación, responda directamente a este correo manteniendo el número de ticket en el asunto.</p>
            <p>Gracias por confiar en LANET Helpdesk.</p>
                """
            },
            {
                'template_type': 'ticket_reopened',
                'name': 'Ticket Reabierto - Notificación',
                'subject_template': '[LANET-{{ticket_number}}] Ticket reabierto: {{subject}}',
                'variables': ['{{ticket_number}}', '{{client_name}}', '{{site_name}}', '{{subject}}', '{{priority}}', '{{reopened_by}}', '{{reopened_date}}', '{{reopen_reason}}'],
                'content': """
            <h2 style="color: #dc2626; margin-bottom: 20px;">Ticket Reabierto</h2>
            <p>Estimado/a cliente de <strong>{{client_name}}</strong>,</p>
            <p>El ticket <strong>{{ticket_number}}</strong> ha sido reabierto:</p>
            <div style="background-color: #fef2f2; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc2626;">
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>Título:</strong> {{subject}}</li>
                    <li><strong>Sitio:</strong> {{site_name}}</li>
                    <li><strong>Prioridad:</strong> {{priority}}</li>
                    <li><strong>Reabierto por:</strong> {{reopened_by}}</li>
                    <li><strong>Fecha de Reapertura:</strong> {{reopened_date}}</li>
                    <li><strong>Motivo:</strong> {{reopen_reason}}</li>
                </ul>
            </div>
            <p>Nuestro equipo técnico atenderá nuevamente su solicitud.</p>
            <p><strong>Importante:</strong> Para mantener la continuidad de la comunicación, responda directamente a este correo manteniendo el número de ticket en el asunto.</p>
                """
            },
            {
                'template_type': 'ticket_commented',
                'name': 'Nuevo Comentario - Notificación',
                'subject_template': '[LANET-{{ticket_number}}] Nuevo comentario: {{subject}}',
                'variables': ['{{ticket_number}}', '{{client_name}}', '{{subject}}', '{{comment_author}}', '{{comment_date}}', '{{comment_text}}'],
                'content': """
            <h2 style="color: #059669; margin-bottom: 20px;">Nuevo Comentario Agregado</h2>
            <p>Estimado/a cliente de <strong>{{client_name}}</strong>,</p>
            <p>Se ha agregado un nuevo comentario al ticket <strong>{{ticket_number}}</strong>:</p>
            <div style="background-color: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #059669;">
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>Título:</strong> {{subject}}</li>
                    <li><strong>Comentario por:</strong> {{comment_author}}</li>
                    <li><strong>Fecha:</strong> {{comment_date}}</li>
                </ul>
                <div style="margin-top: 15px; padding: 15px; background-color: white; border-radius: 4px;">
                    <strong>Comentario:</strong><br>
                    {{comment_text}}
                </div>
            </div>
            <p><strong>Importante:</strong> Para mantener la continuidad de la comunicación, responda directamente a este correo manteniendo el número de ticket en el asunto.</p>
                """
            },
            {
                'template_type': 'ticket_resolved',
                'name': 'Ticket Resuelto - Notificación',
                'subject_template': '[LANET-{{ticket_number}}] Ticket resuelto: {{subject}}',
                'variables': ['{{ticket_number}}', '{{client_name}}', '{{subject}}', '{{resolution_notes}}', '{{resolved_by}}', '{{resolved_date}}'],
                'content': """
            <h2 style="color: #059669; margin-bottom: 20px;">Ticket Resuelto</h2>
            <p>Estimado/a cliente de <strong>{{client_name}}</strong>,</p>
            <p>El ticket <strong>{{ticket_number}}</strong> ha sido marcado como resuelto:</p>
            <div style="background-color: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #059669;">
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>Título:</strong> {{subject}}</li>
                    <li><strong>Resuelto por:</strong> {{resolved_by}}</li>
                    <li><strong>Fecha de Resolución:</strong> {{resolved_date}}</li>
                </ul>
                <div style="margin-top: 15px; padding: 15px; background-color: white; border-radius: 4px;">
                    <strong>Notas de Resolución:</strong><br>
                    {{resolution_notes}}
                </div>
            </div>
            <p>Si considera que el problema no está completamente resuelto, puede responder a este correo para reabrir el ticket.</p>
            <p>Gracias por confiar en LANET Helpdesk.</p>
                """
            }
        ]
        
        # Update templates
        for template_data in template_updates:
            content = get_standard_html_template(
                template_data['name'], 
                template_data['content']
            )
            
            # Update the template
            update_query = """
            UPDATE email_templates 
            SET name = %s,
                subject_template = %s,
                body_template = %s,
                variables = %s,
                updated_at = NOW()
            WHERE template_type = %s AND is_default = true
            """
            
            cur.execute(update_query, (
                template_data['name'],
                template_data['subject_template'],
                content,
                json.dumps(template_data['variables']),
                template_data['template_type']
            ))
            
            print(f"✅ Updated {template_data['template_type']} template")
            print(f"   Subject: {template_data['subject_template']}")
            print(f"   Variables: {len(template_data['variables'])} defined")
            print()
        
        # Commit changes
        conn.commit()
        print("🎉 EMAIL TEMPLATE STANDARDIZATION COMPLETED")
        print("✅ Bidirectional email communication patterns preserved")
        print("✅ Consistent LANET branding applied")
        print("✅ Template variables standardized")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error standardizing templates: {e}")
        return False

if __name__ == '__main__':
    standardize_email_templates()
