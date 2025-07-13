-- Add ticket reopened email template
-- This template is used when a ticket is reopened (either manually or automatically)

INSERT INTO email_templates (
    name, 
    description, 
    template_type, 
    subject_template, 
    body_template, 
    is_html, 
    is_active, 
    is_default, 
    variables
) VALUES (
    'Ticket Reopened Default',
    'Notificación cuando un ticket es reabierto',
    'ticket_reopened',
    '[LANET-{{ticket_number}}] Ticket reabierto: {{subject}}',
    '<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ticket Reabierto - LANET Helpdesk</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white;">
        <!-- Header -->
        <div style="background-color: #f59e0b; color: white; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 28px;">LANET Helpdesk</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px;">Ticket Reabierto</p>
        </div>
        
        <!-- Content -->
        <div style="padding: 30px;">
            <h2 style="color: #f59e0b; margin-bottom: 20px;">Su ticket ha sido reabierto</h2>
            
            <p>Estimado/a {{client_name}},</p>
            
            <p>Le informamos que el ticket <strong>{{ticket_number}}</strong> ha sido reabierto y requiere atención adicional.</p>
            
            <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
                <h3 style="margin: 0 0 10px 0; color: #92400e;">Detalles del Ticket:</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>Número:</strong> {{ticket_number}}</li>
                    <li><strong>Asunto:</strong> {{subject}}</li>
                    <li><strong>Cliente:</strong> {{client_name}}</li>
                    <li><strong>Sitio:</strong> {{site_name}}</li>
                    <li><strong>Prioridad:</strong> {{priority}}</li>
                    <li><strong>Reabierto por:</strong> {{reopened_by}}</li>
                    <li><strong>Fecha de reapertura:</strong> {{reopened_date}}</li>
                </ul>
            </div>
            
            <div style="background-color: #f3f4f6; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #374151;">Motivo de reapertura:</h4>
                <p style="margin: 0; font-style: italic;">{{reopen_reason}}</p>
            </div>
            
            <p>El ticket ahora está en estado <strong>"Reabierto"</strong> y será atendido por nuestro equipo técnico a la brevedad posible.</p>
            
            <p>Si tiene alguna pregunta adicional o necesita proporcionar más información, no dude en responder a este correo o agregar un comentario al ticket.</p>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f3f4f6; padding: 20px; text-align: center; color: #6b7280;">
            <p style="margin: 0; font-size: 14px;">
                Este es un mensaje automático del sistema LANET Helpdesk.<br>
                Por favor, no responda directamente a este correo.
            </p>
        </div>
    </div>
</body>
</html>',
    true,
    true,
    true,
    '["ticket_number", "client_name", "site_name", "subject", "priority", "reopened_by", "reopened_date", "reopen_reason"]'
);
