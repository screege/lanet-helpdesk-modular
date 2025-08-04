-- Script para corregir caracteres UTF-8 en plantillas de email
-- Ejecutar después de restaurar base de datos para corregir caracteres españoles

-- Corregir plantilla de comentarios
UPDATE email_templates 
SET 
    subject = 'Actualización de Ticket: {{ticket_number}}',
    body = '<h2>Actualización de Ticket</h2>
<p>Estimado/a {{contact_name}},</p>
<p>Su ticket {{ticket_number}} ha sido actualizado:</p>
<p><strong>Comentario del técnico:</strong></p>
<div style="background-color: #f5f5f5; padding: 10px; margin: 10px 0;">{{comment_text}}</div>
<p>Estado actual: {{status}}</p>
<p>Puede responder a este correo o acceder al portal: <a href="{{portal_url}}">Portal de Clientes LANET</a></p>
<p>Saludos cordiales,<br>{{technician_name}}<br>Equipo de Soporte LANET</p>'
WHERE name = 'comment_default';

-- Corregir plantilla de restablecimiento de contraseña
UPDATE email_templates 
SET 
    subject = 'Restablecimiento de Contraseña - LANET Helpdesk',
    body = '<h2>Restablecimiento de Contraseña</h2>
<p>Estimado/a {{user_name}},</p>
<p>Ha solicitado restablecer su contraseña para el sistema LANET Helpdesk.</p>
<p>Haga clic en el siguiente enlace para crear una nueva contraseña:</p>
<p><a href="{{reset_url}}" style="background-color: #1e40af; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Restablecer Contraseña</a></p>
<p>Este enlace expirará en 15 minutos por seguridad.</p>
<p>Si no solicitó este cambio, ignore este correo.</p>
<p>Saludos cordiales,<br>Equipo de Soporte LANET</p>'
WHERE name = 'password_reset_default';

-- Corregir plantilla de nuevo ticket
UPDATE email_templates 
SET 
    subject = 'Nuevo Ticket Creado: {{ticket_number}}',
    body = '<h2>Nuevo Ticket Creado</h2>
<p>Estimado/a {{contact_name}},</p>
<p>Su ticket ha sido creado exitosamente:</p>
<p><strong>Número de Ticket:</strong> {{ticket_number}}</p>
<p><strong>Título:</strong> {{title}}</p>
<p><strong>Descripción:</strong> {{description}}</p>
<p><strong>Prioridad:</strong> {{priority}}</p>
<p><strong>Sitio:</strong> {{site}}</p>
<p><strong>Persona Afectada:</strong> {{affected_person}}</p>
<p><strong>Fecha de Creación:</strong> {{created_at}}</p>
<p>Nuestro equipo técnico revisará su solicitud y se pondrá en contacto con usted a la brevedad.</p>
<p><strong>Importante:</strong> Para mantener la continuidad de la comunicación, responda directamente a este correo manteniendo el número de ticket en el asunto.</p>
<p>Gracias por confiar en LANET Helpdesk.</p>
<p>Saludos cordiales,<br>Equipo de Soporte LANET</p>'
WHERE name = 'ticket_creation_default';

-- Corregir plantilla de asignación de ticket
UPDATE email_templates 
SET 
    subject = 'Ticket Asignado: {{ticket_number}}',
    body = '<h2>Ticket Asignado</h2>
<p>Estimado/a {{technician_name}},</p>
<p>Se le ha asignado un nuevo ticket:</p>
<p><strong>Número de Ticket:</strong> {{ticket_number}}</p>
<p><strong>Título:</strong> {{title}}</p>
<p><strong>Descripción:</strong> {{description}}</p>
<p><strong>Prioridad:</strong> {{priority}}</p>
<p><strong>Cliente:</strong> {{client_name}}</p>
<p><strong>Sitio:</strong> {{site}}</p>
<p><strong>Contacto:</strong> {{contact_name}} ({{contact_email}})</p>
<p><strong>Fecha de Creación:</strong> {{created_at}}</p>
<p>Por favor, revise el ticket y tome las acciones necesarias.</p>
<p>Acceder al sistema: <a href="{{portal_url}}">LANET Helpdesk</a></p>
<p>Saludos cordiales,<br>Sistema LANET Helpdesk</p>'
WHERE name = 'Ticket Assigned Default';

-- Corregir plantilla de nuevo comentario
UPDATE email_templates 
SET 
    subject = 'Nuevo Comentario - Notificación',
    body = '<h2>Nuevo Comentario en Ticket</h2>
<p>Estimado/a {{recipient_name}},</p>
<p>Se ha agregado un nuevo comentario al ticket {{ticket_number}}:</p>
<p><strong>Comentario:</strong></p>
<div style="background-color: #f5f5f5; padding: 10px; margin: 10px 0;">{{comment_text}}</div>
<p><strong>Autor:</strong> {{author_name}}</p>
<p><strong>Fecha:</strong> {{comment_date}}</p>
<p>Puede responder a este correo o acceder al portal para más detalles.</p>
<p>Saludos cordiales,<br>Equipo de Soporte LANET</p>'
WHERE name = 'Nuevo Comentario - Notificación';

-- Verificar correcciones
SELECT name, subject FROM email_templates WHERE name IN (
    'comment_default', 
    'password_reset_default', 
    'ticket_creation_default', 
    'Ticket Assigned Default',
    'Nuevo Comentario - Notificación'
);
