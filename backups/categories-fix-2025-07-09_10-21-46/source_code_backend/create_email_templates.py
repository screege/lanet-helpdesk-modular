#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create default email templates for LANET Helpdesk
"""

from app import create_app

def create_email_templates():
    app = create_app()
    with app.app_context():
        # Email templates
        templates = [
            {
                'name': 'Ticket Creado',
                'description': 'Notificación cuando se crea un nuevo ticket',
                'template_type': 'ticket_created',
                'subject_template': '[LANET-{{ticket_number}}] Nuevo ticket creado: {{subject}}',
                'body_template': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ticket Creado - LANET Helpdesk</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white;">
        <!-- Header -->
        <div style="background-color: #1e40af; color: white; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 28px;">LANET Helpdesk</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px;">Su ticket ha sido creado exitosamente</p>
        </div>
        
        <!-- Content -->
        <div style="padding: 30px;">
            <h2 style="color: #1e40af; margin-top: 0;">Detalles del Ticket</h2>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; width: 30%;">Número:</td>
                    <td style="padding: 8px 0;">LANET-{{ticket_number}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Asunto:</td>
                    <td style="padding: 8px 0;">{{subject}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Cliente:</td>
                    <td style="padding: 8px 0;">{{client_name}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Sitio:</td>
                    <td style="padding: 8px 0;">{{site_name}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Prioridad:</td>
                    <td style="padding: 8px 0;">{{priority}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Categoría:</td>
                    <td style="padding: 8px 0;">{{category_name}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Creado por:</td>
                    <td style="padding: 8px 0;">{{created_by_name}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Fecha:</td>
                    <td style="padding: 8px 0;">{{created_at}}</td>
                </tr>
            </table>
            
            <h3 style="color: #1e40af;">Descripción:</h3>
            <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #1e40af; margin: 15px 0;">
                {{description}}
            </div>
            
            <div style="background-color: #e3f2fd; padding: 20px; border-radius: 5px; margin: 30px 0;">
                <h4 style="margin-top: 0; color: #1e40af;">¿Qué sigue?</h4>
                <p style="margin-bottom: 0;">Nuestro equipo técnico revisará su solicitud y se pondrá en contacto con usted pronto. Recibirá actualizaciones por correo electrónico conforme avance la resolución.</p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e0e0e0;">
            <p style="margin: 0; font-size: 14px; color: #666;">
                <strong>LANET - Soluciones Tecnológicas</strong><br>
                www.lanet.mx | soporte@lanet.mx<br>
                <em>Este es un mensaje automático, por favor no responda a este correo.</em>
            </p>
        </div>
    </div>
</body>
</html>''',
                'is_html': True,
                'available_variables': [
                    'ticket_number', 'subject', 'description', 'client_name', 'site_name',
                    'priority', 'category_name', 'created_by_name', 'created_at'
                ],
                'is_active': True,
                'is_default': True
            },
            {
                'name': 'Ticket Asignado',
                'description': 'Notificación cuando se asigna un ticket a un técnico',
                'template_type': 'ticket_assigned',
                'subject_template': '[LANET-{{ticket_number}}] Ticket asignado a {{technician_name}}',
                'body_template': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ticket Asignado - LANET Helpdesk</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white;">
        <!-- Header -->
        <div style="background-color: #1e40af; color: white; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 28px;">LANET Helpdesk</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px;">Su ticket ha sido asignado</p>
        </div>
        
        <!-- Content -->
        <div style="padding: 30px;">
            <h2 style="color: #1e40af; margin-top: 0;">Actualización del Ticket</h2>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; width: 30%;">Número:</td>
                    <td style="padding: 8px 0;">LANET-{{ticket_number}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Asunto:</td>
                    <td style="padding: 8px 0;">{{subject}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Asignado a:</td>
                    <td style="padding: 8px 0;">{{technician_name}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Email del técnico:</td>
                    <td style="padding: 8px 0;">{{technician_email}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Fecha de asignación:</td>
                    <td style="padding: 8px 0;">{{assigned_at}}</td>
                </tr>
            </table>
            
            <div style="background-color: #e8f5e8; padding: 20px; border-radius: 5px; margin: 30px 0;">
                <h4 style="margin-top: 0; color: #2e7d32;">Excelentes noticias</h4>
                <p style="margin-bottom: 0;">Su ticket ha sido asignado a nuestro técnico especializado. Recibirá actualizaciones conforme avance la resolución y podrá contactar directamente al técnico si es necesario.</p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e0e0e0;">
            <p style="margin: 0; font-size: 14px; color: #666;">
                <strong>LANET - Soluciones Tecnológicas</strong><br>
                www.lanet.mx | soporte@lanet.mx
            </p>
        </div>
    </div>
</body>
</html>''',
                'is_html': True,
                'available_variables': [
                    'ticket_number', 'subject', 'technician_name', 'technician_email', 'assigned_at'
                ],
                'is_active': True,
                'is_default': False
            },
            {
                'name': 'Auto-respuesta',
                'description': 'Respuesta automática para emails recibidos',
                'template_type': 'auto_response',
                'subject_template': 'Re: {{original_subject}} - Ticket creado automáticamente',
                'body_template': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Auto-respuesta - LANET Helpdesk</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white;">
        <!-- Header -->
        <div style="background-color: #1e40af; color: white; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 28px;">LANET Helpdesk</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px;">Hemos recibido su mensaje</p>
        </div>
        
        <!-- Content -->
        <div style="padding: 30px;">
            <h2 style="color: #1e40af; margin-top: 0;">Ticket Creado Automáticamente</h2>
            
            <p>Estimado/a {{sender_name}},</p>
            
            <p>Hemos recibido su mensaje y hemos creado automáticamente un ticket de soporte para darle seguimiento.</p>
            
            <div style="background-color: #f0f8ff; padding: 20px; border-left: 4px solid #1e40af; margin: 20px 0;">
                <p style="margin: 0;"><strong>Número de ticket:</strong> LANET-{{ticket_number}}</p>
                <p style="margin: 10px 0 0 0;"><strong>Asunto:</strong> {{subject}}</p>
            </div>
            
            <p><strong>¿Qué sigue?</strong></p>
            <ul>
                <li>Nuestro equipo técnico revisará su solicitud</li>
                <li>Recibirá actualizaciones por correo electrónico</li>
                <li>Puede responder a este correo para agregar información adicional</li>
                <li>Su mensaje será agregado automáticamente al ticket</li>
            </ul>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0; font-size: 14px;"><strong>Importante:</strong> Para garantizar que sus respuestas se asocien correctamente con este ticket, mantenga el número de ticket [LANET-{{ticket_number}}] en el asunto del correo.</p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e0e0e0;">
            <p style="margin: 0; font-size: 14px; color: #666;">
                <strong>LANET - Soluciones Tecnológicas</strong><br>
                www.lanet.mx | soporte@lanet.mx<br>
                <em>Esta es una respuesta automática.</em>
            </p>
        </div>
    </div>
</body>
</html>''',
                'is_html': True,
                'available_variables': [
                    'sender_name', 'ticket_number', 'subject', 'original_subject'
                ],
                'is_active': True,
                'is_default': True
            }
        ]
        
        try:
            for template in templates:
                app.db_manager.execute_insert('email_templates', template)
            print(f'✅ Created {len(templates)} email templates')
        except Exception as e:
            print('❌ Error creating email templates:', str(e))

if __name__ == '__main__':
    create_email_templates()
