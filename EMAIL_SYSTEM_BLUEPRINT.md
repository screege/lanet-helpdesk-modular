# 📧 EMAIL SYSTEM IMPLEMENTATION BLUEPRINT
**LANET Helpdesk V3 - Module 6/6**

## 🎯 **OVERVIEW**

The email system is the final module needed to complete LANET Helpdesk V3. It provides bidirectional email communication, automatic ticket creation from emails, and comprehensive notification system.

---

## 📋 **CORE REQUIREMENTS**

### **1. Email-to-Ticket Creation**
- Monitor IMAP inbox for new emails
- Parse email content and create tickets automatically
- Extract sender, subject, body, attachments
- Assign to appropriate client/site based on sender
- Set initial status and priority

### **2. Ticket-to-Email Responses**
- Send email notifications when tickets are updated
- Include ticket context and conversation history
- Professional email templates
- Proper threading with ticket numbers in subject

### **3. Email Threading & Parsing**
- Parse subject lines for ticket numbers: `[TICKET-202501-0001]`
- Maintain email conversation threads
- Handle replies and forwards correctly
- Prevent duplicate ticket creation

### **4. Notification System**
- Real-time notifications for ticket updates
- Role-based notification preferences
- Email templates for different events
- Configurable notification triggers

---

## 🔧 **TECHNICAL ARCHITECTURE**

### **Email Module Structure:**
```
backend/modules/email/
├── __init__.py
├── routes.py          # Email API endpoints
├── service.py         # Email business logic
├── smtp_service.py    # Outgoing email handling
├── imap_service.py    # Incoming email monitoring
├── parser.py          # Email content parsing
├── templates.py       # Email template management
└── notifications.py   # Notification logic
```

### **Database Tables Needed:**
```sql
-- Email configurations
email_settings (
    setting_id UUID PRIMARY KEY,
    smtp_host VARCHAR(255),
    smtp_port INTEGER,
    smtp_username VARCHAR(255),
    smtp_password_encrypted TEXT,
    imap_host VARCHAR(255),
    imap_port INTEGER,
    imap_username VARCHAR(255),
    imap_password_encrypted TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Email templates
email_templates (
    template_id UUID PRIMARY KEY,
    template_name VARCHAR(100),
    subject_template TEXT,
    body_template TEXT,
    template_type VARCHAR(50), -- 'ticket_created', 'ticket_updated', etc.
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Email logs
email_logs (
    log_id UUID PRIMARY KEY,
    ticket_id UUID REFERENCES tickets(ticket_id),
    email_type VARCHAR(50), -- 'incoming', 'outgoing'
    from_email VARCHAR(255),
    to_email VARCHAR(255),
    subject TEXT,
    message_id VARCHAR(255),
    thread_id VARCHAR(255),
    status VARCHAR(50), -- 'sent', 'failed', 'received'
    error_message TEXT,
    created_at TIMESTAMP
);

-- Notification preferences
notification_preferences (
    preference_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    notification_type VARCHAR(50),
    email_enabled BOOLEAN DEFAULT true,
    in_app_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## 📧 **EMAIL CREDENTIALS & CONFIGURATION**

### **SMTP (Outgoing Mail):**
```env
SMTP_HOST=mail.compushop.com.mx
SMTP_PORT=587
SMTP_USERNAME=webmaster@compushop.com.mx
SMTP_PASSWORD=[secure_password]
SMTP_USE_TLS=true
SMTP_FROM_NAME=LANET Helpdesk
SMTP_FROM_EMAIL=webmaster@compushop.com.mx
```

### **IMAP (Incoming Mail):**
```env
IMAP_HOST=mail.compushop.com.mx
IMAP_PORT=993
IMAP_USERNAME=it@compushop.com.mx
IMAP_PASSWORD=[secure_password]
IMAP_USE_SSL=true
IMAP_FOLDER=INBOX
IMAP_CHECK_INTERVAL=60  # seconds
```

---

## 🔄 **EMAIL PROCESSING WORKFLOW**

### **Incoming Email Flow:**
1. **IMAP Monitor** checks inbox every 60 seconds
2. **Email Parser** extracts content, sender, subject
3. **Ticket Matcher** checks if reply to existing ticket
4. **If New Ticket:**
   - Create new ticket
   - Assign to client based on sender email
   - Set initial status and priority
   - Send confirmation email
5. **If Reply to Existing:**
   - Add comment to existing ticket
   - Update ticket status if needed
   - Notify assigned technician

### **Outgoing Email Flow:**
1. **Trigger Event** (ticket created, updated, resolved)
2. **Template Selection** based on event type
3. **Content Generation** with ticket context
4. **Recipient Determination** based on roles and preferences
5. **Email Sending** via SMTP
6. **Logging** success/failure

---

## 🎨 **EMAIL TEMPLATES**

### **Template Types:**
- `ticket_created` - New ticket confirmation
- `ticket_assigned` - Ticket assigned to technician
- `ticket_updated` - Status or priority changed
- `ticket_resolved` - Resolution notification
- `ticket_closed` - Closure confirmation
- `comment_added` - New comment notification

### **Template Variables:**
```
{{ticket_number}}     # TICKET-202501-0001
{{client_name}}       # Organization name
{{site_name}}         # Site location
{{subject}}           # Ticket subject
{{description}}       # Ticket description
{{status}}            # Current status
{{priority}}          # Priority level
{{assigned_to}}       # Technician name
{{created_by}}        # Creator name
{{created_at}}        # Creation date
{{resolution_notes}}  # Resolution details
{{ticket_url}}        # Direct link to ticket
```

---

## 🔍 **EMAIL PARSING LOGIC**

### **Subject Line Parsing:**
```python
# Extract ticket number from subject
pattern = r'\[TICKET-(\d{6})-(\d{4})\]'
match = re.search(pattern, subject)
if match:
    year_month = match.group(1)
    sequence = match.group(2)
    ticket_number = f"TICKET-{year_month}-{sequence}"
```

### **Sender Identification:**
```python
# Match sender to existing users/clients
sender_email = email.from_address
user = find_user_by_email(sender_email)
if user:
    client_id = user.client_id
    site_ids = user.site_ids
else:
    # Handle unknown sender
    create_guest_ticket_or_reject()
```

---

## 🚨 **INTEGRATION POINTS**

### **With Existing Ticket System:**
- Use existing `ticketsService.createTicket()`
- Use existing `ticketsService.addTicketComment()`
- Trigger existing notification events
- Respect existing role-based permissions

### **With User Management:**
- Validate sender permissions
- Check notification preferences
- Respect multi-tenant isolation
- Use existing authentication patterns

### **With Database:**
- Follow established patterns (`execute_insert`, `execute_update`)
- Maintain RLS policies
- Use existing error handling
- Follow transaction patterns

---

## 🧪 **TESTING STRATEGY**

### **Unit Tests:**
- Email parsing functions
- Template rendering
- SMTP/IMAP connections
- Notification logic

### **Integration Tests:**
- End-to-end email flow
- Ticket creation from emails
- Email sending on ticket updates
- Multi-tenant email isolation

### **Manual Testing:**
- Send test emails to system
- Verify ticket creation
- Test email notifications
- Validate template rendering

---

## 📊 **SUCCESS METRICS**

### **Functional Requirements:**
- ✅ Emails create tickets automatically
- ✅ Ticket updates send notifications
- ✅ Email threading works correctly
- ✅ Templates render properly
- ✅ Multi-tenant isolation maintained

### **Performance Requirements:**
- Email processing < 30 seconds
- IMAP monitoring without blocking
- Bulk email sending capability
- Error recovery and retry logic

### **Security Requirements:**
- Encrypted password storage
- Secure SMTP/IMAP connections
- Email content sanitization
- Spam/abuse prevention

---

## 🎯 **IMPLEMENTATION PHASES**

### **Phase 1: Foundation (Week 1)**
- Email module structure
- Database tables creation
- Basic SMTP/IMAP services
- Configuration management

### **Phase 2: Core Features (Week 2)**
- Email-to-ticket creation
- Basic email templates
- Outgoing email sending
- Email parsing logic

### **Phase 3: Advanced Features (Week 3)**
- Email threading
- Notification system
- Template management
- Error handling

### **Phase 4: Testing & Polish (Week 4)**
- Comprehensive testing
- Performance optimization
- Security hardening
- Documentation

---

**Ready to implement the final module! The email system will complete LANET Helpdesk V3.** 🚀
