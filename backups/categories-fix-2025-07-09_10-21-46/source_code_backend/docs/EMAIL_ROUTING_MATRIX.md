# LANET Helpdesk V3 - Email Routing Matrix

## Overview
This document defines the complete email notification routing logic for all user roles and ticket lifecycle events in LANET Helpdesk V3.

## User Roles
- **superadmin**: System administrators with full access
- **technician**: Technical staff who handle tickets
- **client_admin**: Client organization administrators
- **solicitante**: End users who create tickets

## Email Routing Rules

### 1. Ticket Creation Notifications

#### When ANY user creates a ticket:
**Recipients:**
- ✅ **All superadmin users** (ba@lanet.mx, etc.)
- ✅ **All active technician users** (excluding deactivated ones like carlos.tech@lanet.mx)
- ✅ **Client admin of the ticket's organization** (client_admin role for that client)
- ✅ **Affected person email** (if provided in optional "Notificar" field)

**NOT included:**
- ❌ **Ticket creator** (unless they are also in one of the above categories)
- ❌ **Other solicitante users** from the same organization

#### Special Cases:
1. **If solicitante creates ticket**: They do NOT automatically receive notification unless:
   - They are also a client_admin for that organization, OR
   - Their email is specified in the "Notificar" field

2. **If client_admin creates ticket**: They receive notification as client_admin (not as creator)

3. **If superadmin/technician creates ticket**: They receive notification as superadmin/technician (not as creator)

### 2. Ticket Assignment Notifications

**Recipients:**
- ✅ **Assigned technician** (the user being assigned)
- ✅ **Client admin of the ticket's organization**
- ✅ **Affected person email** (if provided)

### 3. Ticket Status Change Notifications

**Recipients:**
- ✅ **Assigned technician** (if assigned)
- ✅ **Client admin of the ticket's organization**
- ✅ **Affected person email** (if provided)

### 4. Ticket Comment Notifications

**Recipients:**
- ✅ **Assigned technician** (if assigned)
- ✅ **Client admin of the ticket's organization**
- ✅ **Affected person email** (if provided)

**Special Rule:**
- If ticket is in "espera_cliente" status and client adds comment → automatically reopen ticket and notify technicians

### 5. Ticket Resolution Notifications

**Recipients:**
- ✅ **Client admin of the ticket's organization**
- ✅ **Affected person email** (if provided)

**NOT included:**
- ❌ **Technicians** (they already know they resolved it)

### 6. SLA Breach/Warning Notifications

**Recipients:**
- ✅ **All superadmin users**
- ✅ **All active technician users**

## Field Definitions

### Current Ticket Form Fields:
- **affected_person**: Text field for person's name (required)
- **affected_person_contact**: Currently email field → **NEEDS TO BE CHANGED TO PHONE**

### Proposed Ticket Form Fields:
- **affected_person**: Text field for person's name (required)
- **affected_person_contact**: Phone number field (optional)
- **notificar**: Email field for additional notification recipient (optional)

## Implementation Notes

### Database Changes Needed:
1. **Rename field**: `affected_person_contact` → `affected_person_phone`
2. **Add new field**: `notification_email` (for the "Notificar" field)
3. **Update validation**: Phone number validation for affected_person_phone

### Frontend Changes Needed:
1. **Change input type**: affected_person_contact from email to tel
2. **Add new field**: "Notificar" email input (optional)
3. **Update validation**: Phone number format validation

### Backend Changes Needed:
1. **Update notification logic**: Use `notification_email` instead of `affected_person_contact` for email routing
2. **Update database schema**: Add `notification_email` field to tickets table
3. **Update API validation**: Phone number validation for affected_person_phone

## Email Template Variables

### Available Variables:
- `{{ticket_number}}`: TKT-XXXX
- `{{subject}}`: Ticket subject
- `{{client_name}}`: Organization name
- `{{site_name}}`: Site name
- `{{priority}}`: Ticket priority
- `{{status}}`: Current status
- `{{affected_person}}`: Person affected
- `{{created_by}}`: User who created ticket
- `{{assigned_to}}`: Assigned technician name

## Testing Matrix

### Test Scenarios:
1. **Superadmin creates ticket** → Check all recipients receive notification
2. **Technician creates ticket** → Check all recipients receive notification
3. **Client_admin creates ticket** → Check all recipients receive notification
4. **Solicitante creates ticket** → Check solicitante does NOT receive notification (unless in Notificar field)
5. **Ticket with Notificar email** → Check additional recipient receives notification
6. **Ticket without Notificar email** → Check only standard recipients receive notification
7. **Invalid email in Notificar** → Check system handles gracefully
8. **Deactivated users** → Check they do NOT receive notifications

## Security Considerations

### Email Validation:
- Validate email format for "Notificar" field
- Prevent email injection attacks
- Log failed email deliveries separately from system errors

### Privacy:
- Only send ticket details to authorized recipients
- Client admins only see tickets from their organization
- Solicitante users only see tickets they're authorized for

## Error Handling

### Invalid Email Addresses:
- Log as "delivery failure to invalid address"
- Continue processing other recipients
- Do not mark entire notification as failed

### SMTP Failures:
- Retry with exponential backoff
- Log as "system error"
- Alert administrators if persistent failures
