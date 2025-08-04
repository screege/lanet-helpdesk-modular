# 🏗️ LANET HELPDESK V3 - COMPREHENSIVE SYSTEM ARCHITECTURE

**Version:** 3.0  
**Date:** July 5, 2025  
**Status:** Production Ready (66% Complete - 4/6 Core Modules)  
**Architecture:** 100% Modular MSP Helpdesk System  

---

## 📋 **TABLE OF CONTENTS**

1. [System Overview](#system-overview)
2. [Module Architecture](#module-architecture)
3. [Database Architecture](#database-architecture)
4. [Security Layer](#security-layer)
5. [API Endpoints](#api-endpoints)
6. [Data Flow](#data-flow)
7. [Function Dependencies](#function-dependencies)
8. [Agent System Architecture](#agent-system-architecture)
9. [Deployment Architecture](#deployment-architecture)

---

## 🎯 **SYSTEM OVERVIEW**

### **System Overview Diagram**

```mermaid
graph TB
    subgraph "Frontend Layer (React 18 + TypeScript)"
        UI[Web Portal UI]
        AUTH[Auth Context]
        SERVICES[API Services]
    end

    subgraph "Backend Layer (Flask + Python)"
        API[API Gateway]
        AUTH_MOD[Auth Module]
        USERS_MOD[Users Module]
        CLIENTS_MOD[Clients Module]
        SITES_MOD[Sites Module]
        TICKETS_MOD[Tickets Module]
        EMAIL_MOD[Email Module]
        NOTIF_MOD[Notifications Module]
        AGENT_MOD[Agent Management Module]
        BITLOCKER_MOD[BitLocker Module]
    end

    subgraph "Core Services"
        DB_MGR[Database Manager]
        AUTH_MGR[Auth Manager]
        RESP_MGR[Response Manager]
        REDIS[Redis Cache]
        SCRIPT_MGR[Script Manager]
        ALERT_MGR[Alert Manager]
    end

    subgraph "Database Layer (PostgreSQL)"
        MAIN_DB[(Main Database)]
        RLS[Row Level Security]
        POLICIES[RLS Policies]
    end

    subgraph "External Services"
        SMTP[SMTP Server]
        IMAP[IMAP Server]
        EMAIL_QUEUE[Email Queue]
    end

    subgraph "Client Sites (Agent Network)"
        AGENT1[LANET Agent - Site A]
        AGENT2[LANET Agent - Site B]
        AGENT3[LANET Agent - Site C]
        AGENT4[LANET Agent - Site N...]
    end

    UI --> SERVICES
    SERVICES --> API
    API --> AUTH_MOD
    API --> USERS_MOD
    API --> CLIENTS_MOD
    API --> SITES_MOD
    API --> TICKETS_MOD
    API --> EMAIL_MOD
    API --> NOTIF_MOD
    API --> AGENT_MOD
    API --> BITLOCKER_MOD

    AUTH_MOD --> AUTH_MGR
    USERS_MOD --> DB_MGR
    CLIENTS_MOD --> DB_MGR
    SITES_MOD --> DB_MGR
    TICKETS_MOD --> DB_MGR
    EMAIL_MOD --> DB_MGR
    NOTIF_MOD --> DB_MGR
    AGENT_MOD --> DB_MGR
    AGENT_MOD --> SCRIPT_MGR
    AGENT_MOD --> ALERT_MGR
    BITLOCKER_MOD --> DB_MGR

    DB_MGR --> MAIN_DB
    AUTH_MGR --> MAIN_DB
    RESP_MGR --> REDIS
    SCRIPT_MGR --> MAIN_DB
    ALERT_MGR --> MAIN_DB

    MAIN_DB --> RLS
    RLS --> POLICIES

    EMAIL_MOD --> SMTP
    EMAIL_MOD --> IMAP
    NOTIF_MOD --> EMAIL_QUEUE

    AGENT1 -.->|HTTPS/SSL| API
    AGENT2 -.->|HTTPS/SSL| API
    AGENT3 -.->|HTTPS/SSL| API
    AGENT4 -.->|HTTPS/SSL| API

    AGENT_MOD --> AGENT1
    AGENT_MOD --> AGENT2
    AGENT_MOD --> AGENT3
    AGENT_MOD --> AGENT4
```

### **Core Principles**

- **100% Modular Architecture**: Each module is self-contained with its own routes, services, and business logic
- **MSP Multi-Tenant**: Complete data isolation between clients using PostgreSQL RLS
- **Role-Based Access Control**: 5 distinct roles with granular permissions
- **Unified Ticket Numbering**: TKT-XXXXXX format shared between web and email creation
- **Enterprise Email Integration**: Bidirectional SMTP/IMAP with template system
- **Production Security**: JWT authentication, RLS policies, input validation

---

## 🧩 **MODULE ARCHITECTURE**

### **Module Dependencies Diagram**

```mermaid
graph LR
    subgraph "Core Modules (Completed)"
        AUTH[Auth Module]
        USERS[Users Module]
        CLIENTS[Clients Module]
        SITES[Sites Module]
    end

    subgraph "Business Modules (In Progress)"
        TICKETS[Tickets Module]
        EMAIL[Email Module]
        NOTIF[Notifications Module]
        AGENTS[Agent Management Module]
        SLA[SLA Module]
    end

    subgraph "Core Services"
        DB[Database Manager]
        AUTH_SVC[Auth Manager]
        RESP[Response Manager]
        SCRIPT_SVC[Script Manager]
        ALERT_SVC[Alert Manager]
    end

    AUTH --> AUTH_SVC
    AUTH --> DB

    USERS --> AUTH
    USERS --> DB
    USERS --> RESP

    CLIENTS --> AUTH
    CLIENTS --> USERS
    CLIENTS --> DB

    SITES --> AUTH
    SITES --> CLIENTS
    SITES --> DB

    TICKETS --> AUTH
    TICKETS --> USERS
    TICKETS --> CLIENTS
    TICKETS --> SITES
    TICKETS --> NOTIF
    TICKETS --> DB

    EMAIL --> AUTH
    EMAIL --> TICKETS
    EMAIL --> NOTIF
    EMAIL --> DB

    NOTIF --> AUTH
    NOTIF --> EMAIL
    NOTIF --> DB

    AGENTS --> AUTH
    AGENTS --> CLIENTS
    AGENTS --> SITES
    AGENTS --> TICKETS
    AGENTS --> NOTIF
    AGENTS --> DB
    AGENTS --> SCRIPT_SVC
    AGENTS --> ALERT_SVC

    SLA --> AUTH
    SLA --> CLIENTS
    SLA --> TICKETS
    SLA --> AGENTS
    SLA --> DB
```

### **Module Status & Implementation**

| Module | Status | Completion | Key Features |
|--------|--------|------------|--------------|
| **Auth** | ✅ Complete | 100% | JWT tokens, role validation, session management |
| **Users** | ✅ Complete | 100% | CRUD operations, role assignment, site assignments |
| **Clients** | ✅ Complete | 100% | MSP client management, wizard creation, RLS isolation |
| **Sites** | ✅ Complete | 100% | Site management, client association, user assignments |
| **Tickets** | 🔄 In Progress | 85% | Unified numbering, web/email creation, lifecycle management |
| **Email** | 🔄 In Progress | 75% | SMTP/IMAP integration, email-to-ticket, templates |
| **Notifications** | 🔄 In Progress | 70% | Email notifications, template system, queue management |
| **Agents** | ⏳ Planned | 0% | Asset monitoring, inventory collection, script execution, auto-ticketing |
| **SLA** | ⏳ Planned | 0% | SLA policies, compliance tracking, escalation |

---

## 🗄️ **DATABASE ARCHITECTURE**

### **Database Schema Diagram**

```mermaid
erDiagram
    users ||--o{ clients : "belongs_to"
    users ||--o{ user_site_assignments : "has_many"
    users ||--o{ tickets : "creates"
    users ||--o{ tickets : "assigned_to"
    
    clients ||--o{ sites : "has_many"
    clients ||--o{ tickets : "has_many"
    clients ||--o{ assets : "has_many"
    clients ||--o{ slas : "has_many"
    
    sites ||--o{ user_site_assignments : "has_many"
    sites ||--o{ tickets : "has_many"
    sites ||--o{ assets : "has_many"
    
    tickets ||--o{ ticket_comments : "has_many"
    tickets ||--o{ file_attachments : "has_many"
    tickets ||--o{ sla_compliance : "has_one"
    tickets ||--o{ email_queue : "triggers"
    
    categories ||--o{ tickets : "categorizes"
    assets ||--o{ tickets : "related_to"
    
    email_config ||--o{ email_queue : "uses"
    email_templates ||--o{ email_queue : "uses"
    
    users {
        uuid user_id PK
        uuid client_id FK
        string name
        string email
        string password_hash
        enum role
        string phone
        boolean is_active
        timestamp created_at
    }
    
    clients {
        uuid client_id PK
        string name
        string rfc
        string email
        string phone
        text_array allowed_emails
        boolean is_active
        timestamp created_at
    }
    
    sites {
        uuid site_id PK
        uuid client_id FK
        string name
        text address
        string city
        string state
        boolean is_active
        timestamp created_at
    }
    
    tickets {
        uuid ticket_id PK
        string ticket_number UK
        uuid client_id FK
        uuid site_id FK
        uuid created_by FK
        uuid assigned_to FK
        text subject
        text description
        string affected_person
        string affected_person_contact
        enum priority
        enum status
        boolean is_email_originated
        timestamp created_at
    }
```

### **Core Tables Schema**

#### **Users Table**
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(client_id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL, -- 'superadmin', 'admin', 'technician', 'client_admin', 'solicitante'
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### **Clients Table**
```sql
CREATE TABLE clients (
    client_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    rfc VARCHAR(13),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    allowed_emails TEXT[], -- Domain and individual email authorization
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### **Tickets Table**
```sql
CREATE TABLE tickets (
    ticket_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_number VARCHAR(20) UNIQUE NOT NULL, -- TKT-XXXXXX format
    client_id UUID NOT NULL REFERENCES clients(client_id),
    site_id UUID NOT NULL REFERENCES sites(site_id),
    created_by UUID NOT NULL REFERENCES users(user_id),
    assigned_to UUID REFERENCES users(user_id),
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    affected_person VARCHAR(255) NOT NULL,
    affected_person_contact VARCHAR(255) NOT NULL,
    priority ticket_priority DEFAULT 'media',
    status ticket_status DEFAULT 'nuevo',
    is_email_originated BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### **Unified Ticket Numbering System**

```sql
-- PostgreSQL sequence for unified numbering
CREATE SEQUENCE ticket_number_seq START 1;

-- Function to generate ticket numbers
CREATE OR REPLACE FUNCTION generate_ticket_number()
RETURNS TEXT AS $$
BEGIN
    RETURN 'TKT-' || LPAD(nextval('ticket_number_seq')::TEXT, 6, '0');
END;
$$ LANGUAGE plpgsql;

-- Usage: Both web and email tickets use same sequence
-- Result: TKT-000001, TKT-000002, TKT-000003...
```

---

## 🔐 **SECURITY LAYER**

### **Authentication Flow**

```mermaid
sequenceDiagram
    participant Client as Frontend
    participant API as Backend API
    participant Auth as Auth Manager
    participant DB as Database
    participant RLS as RLS Engine
    
    Client->>API: POST /api/auth/login
    API->>Auth: authenticate_user(email, password)
    Auth->>DB: SELECT user WHERE email = ?
    DB-->>Auth: User data + role + client_id
    Auth->>Auth: verify_password(hash)
    Auth->>Auth: create_tokens(user)
    Auth-->>API: JWT tokens + user data
    API-->>Client: {access_token, refresh_token, user}
    
    Note over Client,RLS: Subsequent API Calls
    
    Client->>API: GET /api/tickets/ (with JWT)
    API->>API: verify_jwt_in_request()
    API->>RLS: set_rls_context(user_id, role, client_id)
    RLS->>DB: Apply RLS policies
    DB-->>API: Filtered results
    API-->>Client: Authorized data only
```

### **JWT Token Structure**

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "fresh": false,
    "iat": 1751593649,
    "jti": "c9552c1b-b18c-4dca-96db-c1877b94d2d3",
    "type": "access",
    "sub": "00d40348-91ce-45f0-ac64-75979cb8657c",
    "nbf": 1751593649,
    "role": "solicitante",
    "client_id": "75f6b906-db3a-404d-b032-3a52eac324c4",
    "site_ids": ["d01df78a-c48b-40c2-b943-ef0830e26bf1"],
    "name": "Mauricio",
    "email": "screege@hotmail.com"
  }
}
```

### **Role-Based Access Control (RBAC)**

| Role | Permissions | Access Level |
|------|-------------|--------------|
| **superadmin** | All operations | Global access, can delete users, manage system config |
| **admin** | Most operations | Global read/write, cannot delete superadmins |
| **technician** | Ticket management | All tickets, limited user management |
| **client_admin** | Client management | Own client data only, manage client users |
| **solicitante** | Basic operations | Assigned sites only, create tickets, view own data |

### **Row Level Security (RLS) Policies**

#### **Core RLS Functions**
```sql
-- Get current user context from JWT
CREATE OR REPLACE FUNCTION current_user_id() RETURNS UUID AS $$
BEGIN
    RETURN COALESCE(current_setting('app.current_user_id', true)::UUID, NULL);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION current_user_role() RETURNS TEXT AS $$
BEGIN
    RETURN COALESCE(current_setting('app.current_user_role', true), 'anonymous');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION current_user_client_id() RETURNS UUID AS $$
BEGIN
    RETURN COALESCE(current_setting('app.current_user_client_id', true)::UUID, NULL);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

#### **Example RLS Policies**

**Clients Table:**
```sql
-- Superadmin/Admin see all, clients see only their own
CREATE POLICY clients_select_policy ON clients
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        client_id = current_user_client_id()
    );
```

**Tickets Table:**
```sql
-- Multi-level access based on role and relationships
CREATE POLICY tickets_select_policy ON tickets
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        client_id = current_user_client_id() OR
        site_id = ANY(current_user_site_ids()) OR
        created_by = current_user_id() OR
        assigned_to = current_user_id()
    );
```

### **Multi-Tenant Data Isolation**

- **Admin/Technician**: See ALL data across all clients
- **Client Admin**: See ONLY their organization's data (filtered by `client_id`)
- **Solicitante**: See ONLY assigned sites (filtered by `site_id` array)
- **Superadmin Protection**: Cannot delete own account, special escalation privileges

---

## 🔌 **API ENDPOINTS**

### **Complete API Route Mapping**

| Module | Endpoint | Method | Auth | Role Required | Description |
|--------|----------|--------|------|---------------|-------------|
| **Auth** | `/api/auth/login` | POST | No | None | User authentication |
| **Auth** | `/api/auth/refresh` | POST | JWT(R) | Any | Token refresh |
| **Auth** | `/api/auth/me` | GET | JWT | Any | Current user info |
| **Auth** | `/api/auth/logout` | POST | JWT | Any | User logout |
| **Users** | `/api/users` | GET | JWT | Admin+ | List users |
| **Users** | `/api/users` | POST | JWT | Admin+ | Create user |
| **Users** | `/api/users/<id>` | GET | JWT | Admin+ | Get user details |
| **Users** | `/api/users/<id>` | PUT | JWT | Admin+ | Update user |
| **Users** | `/api/users/<id>` | DELETE | JWT | Superadmin | Delete user |
| **Clients** | `/api/clients` | GET | JWT | Any | List clients (RLS filtered) |
| **Clients** | `/api/clients` | POST | JWT | Admin+ | Create client |
| **Clients** | `/api/clients/wizard` | POST | JWT | Admin+ | MSP client creation wizard |
| **Sites** | `/api/sites` | GET | JWT | Any | List sites (RLS filtered) |
| **Sites** | `/api/sites` | POST | JWT | Admin+ | Create site |
| **Tickets** | `/api/tickets` | GET | JWT | Any | List tickets (RLS filtered) |
| **Tickets** | `/api/tickets` | POST | JWT | Any | Create ticket |
| **Tickets** | `/api/tickets/<id>` | GET | JWT | Any | Get ticket details |
| **Email** | `/api/email/config` | GET | JWT | Admin+ | Email configuration |
| **Email** | `/api/email/templates` | GET | JWT | Admin+ | Email templates |

### **Authentication Headers**
```http
Authorization: Bearer <JWT_ACCESS_TOKEN>
Content-Type: application/json
```

### **Standard Response Format**
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... },
  "errors": null,
  "timestamp": "2025-07-05T15:30:00Z"
}
```

---

## 🔄 **DATA FLOW**

### **Ticket Creation Flow (Web Portal)**

```mermaid
sequenceDiagram
    participant UI as Frontend UI
    participant API as Tickets API
    participant Service as TicketsService
    participant DB as Database
    participant Notif as NotificationService
    participant Email as Email Queue
    
    UI->>API: POST /api/tickets/ {ticket_data}
    API->>API: Validate JWT & extract user context
    API->>API: Validate required fields
    API->>API: Map frontend fields to service format
    API->>Service: create_ticket(ticket_data, user_id)
    Service->>Service: Validate business rules
    Service->>DB: Generate ticket number (TKT-XXXXXX)
    Service->>DB: INSERT INTO tickets
    DB-->>Service: ticket_id + ticket_number
    Service->>Notif: send_ticket_notification('ticket_created', ticket_id)
    Notif->>Email: Queue notification emails
    Service-->>API: {success: true, ticket: ticket_data}
    API-->>UI: 201 Created {ticket_number: "TKT-000089"}
```

### **Email-to-Ticket Flow**

```mermaid
sequenceDiagram
    participant IMAP as IMAP Server
    participant Email as EmailService
    participant Auth as Email Authorization
    participant Service as TicketsService
    participant DB as Database
    participant Notif as NotificationService
    
    IMAP->>Email: New email received
    Email->>Email: Parse email headers & body
    Email->>Auth: Validate sender authorization
    Auth->>DB: Check allowed_emails for client
    Auth-->>Email: Authorization result
    Email->>Email: Extract ticket data from email
    Email->>Service: create_ticket(email_data, system_user)
    Service->>DB: Generate ticket number (same sequence)
    Service->>DB: INSERT INTO tickets (is_email_originated=true)
    Service->>Notif: send_ticket_notification('ticket_created', ticket_id)
    Email->>IMAP: Delete processed email
    Service-->>Email: {success: true, ticket_number: "TKT-000090"}
```

### **User Authentication & RLS Context Flow**

```mermaid
sequenceDiagram
    participant Client as Frontend
    participant API as Flask API
    participant Auth as AuthManager
    participant DB as DatabaseManager
    participant RLS as PostgreSQL RLS
    
    Client->>API: Request with JWT token
    API->>API: before_request() middleware
    API->>Auth: verify_jwt_in_request()
    Auth->>Auth: Extract user_id, role, client_id, site_ids
    API->>DB: set_rls_context(user_id, role, client_id, site_ids)
    DB->>RLS: SET app.current_user_id = user_id
    DB->>RLS: SET app.current_user_role = role
    DB->>RLS: SET app.current_user_client_id = client_id
    RLS->>RLS: Apply policies to all subsequent queries
    API->>API: Process request with RLS active
    API-->>Client: Filtered response based on user permissions
```

---

## ⚙️ **FUNCTION DEPENDENCIES**

### **Core Service Classes**

#### **DatabaseManager** (`backend/core/database.py`)
- **Purpose**: Centralized database operations with RLS support
- **Key Methods**:
  - `execute_query(query, params, fetch)`: Execute SQL with RLS context
  - `set_rls_context(user_id, role, client_id, site_ids)`: Set PostgreSQL session variables
  - `get_connection()`: Get pooled database connection
  - `validate_uuid(uuid_string)`: UUID format validation

#### **AuthManager** (`backend/core/auth.py`)
- **Purpose**: JWT token management and user authentication
- **Key Methods**:
  - `authenticate_user(email, password)`: Verify credentials
  - `create_tokens(user)`: Generate JWT access/refresh tokens
  - `verify_password(password, hash)`: bcrypt password verification
  - `hash_password(password)`: bcrypt password hashing

#### **ResponseManager** (`backend/core/response.py`)
- **Purpose**: Standardized API response formatting
- **Key Methods**:
  - `success(data, message)`: Success response format
  - `error(message, status_code)`: Error response format
  - `format_user_data(user)`: User data sanitization
  - `format_ticket_data(ticket)`: Ticket data formatting

### **Module Service Dependencies**

#### **TicketsService** (`backend/modules/tickets/service.py`)
- **Dependencies**: DatabaseManager, NotificationService
- **Key Methods**:
  - `create_ticket(ticket_data, created_by)`: Business logic for ticket creation
  - `get_ticket(ticket_id)`: Retrieve ticket with RLS filtering
  - `update_ticket(ticket_id, data)`: Update ticket with validation
  - `assign_ticket(ticket_id, user_id)`: Ticket assignment logic

#### **EmailService** (`backend/modules/email/service.py`)
- **Dependencies**: DatabaseManager, TicketsService, NotificationService
- **Key Methods**:
  - `process_incoming_emails()`: IMAP email processing
  - `create_ticket_from_email(email_data)`: Email-to-ticket conversion
  - `validate_email_authorization(sender, client)`: Authorization check
  - `parse_email_content(email)`: Extract ticket data from email

#### **NotificationService** (`backend/modules/notifications/service.py`)
- **Dependencies**: DatabaseManager, EmailService
- **Key Methods**:
  - `send_ticket_notification(type, ticket_id)`: Trigger notifications
  - `get_notification_recipients(ticket, type)`: Determine recipients
  - `render_email_template(template, variables)`: Template rendering
  - `queue_email(recipient, subject, body)`: Email queue management

---

## 🤖 **AGENT SYSTEM ARCHITECTURE**

### **Agent System Overview Diagram**

```mermaid
graph TB
    subgraph "LANET Helpdesk Central Server"
        API[API Gateway]
        AGENT_MGR[Agent Manager]
        ASSET_DB[(Assets Database)]
        TICKET_SYS[Ticket System]
        SCRIPT_REPO[Script Repository]
        ALERT_SYS[Alert System]
    end

    subgraph "Client Site A"
        AGENT_A1[LANET Agent - PC001]
        AGENT_A2[LANET Agent - PC002]
        AGENT_A3[LANET Agent - Server01]
        ROUTER_A[Network Router]
    end

    subgraph "Client Site B"
        AGENT_B1[LANET Agent - PC010]
        AGENT_B2[LANET Agent - PC011]
        AGENT_B3[LANET Agent - Server02]
        ROUTER_B[Network Router]
    end

    subgraph "Client Site C"
        AGENT_C1[LANET Agent - PC020]
        AGENT_C2[LANET Agent - PC021]
        ROUTER_C[Network Router]
    end

    AGENT_A1 -->|HTTPS/SSL| API
    AGENT_A2 -->|HTTPS/SSL| API
    AGENT_A3 -->|HTTPS/SSL| API

    AGENT_B1 -->|HTTPS/SSL| API
    AGENT_B2 -->|HTTPS/SSL| API
    AGENT_B3 -->|HTTPS/SSL| API

    AGENT_C1 -->|HTTPS/SSL| API
    AGENT_C2 -->|HTTPS/SSL| API

    API --> AGENT_MGR
    AGENT_MGR --> ASSET_DB
    AGENT_MGR --> TICKET_SYS
    AGENT_MGR --> SCRIPT_REPO
    AGENT_MGR --> ALERT_SYS

    ROUTER_A -.->|Firewall Rules| AGENT_A1
    ROUTER_B -.->|Firewall Rules| AGENT_B1
    ROUTER_C -.->|Firewall Rules| AGENT_C1
```

### **Agent Architecture Components**

#### **LANET Agent (Client-Side)**
```mermaid
graph LR
    subgraph "LANET Agent Process"
        CORE[Agent Core]
        INVENTORY[Inventory Collector]
        MONITOR[System Monitor]
        EXECUTOR[Script Executor]
        COMM[Communication Module]
        SECURITY[Security Module]
    end

    subgraph "System Integration"
        WMI[WMI/PowerShell]
        REGISTRY[Windows Registry]
        SERVICES[Windows Services]
        EVENTLOG[Event Logs]
        FILESYSTEM[File System]
    end

    subgraph "Network Communication"
        HTTPS[HTTPS Client]
        WEBSOCKET[WebSocket Client]
        ENCRYPTION[AES Encryption]
    end

    CORE --> INVENTORY
    CORE --> MONITOR
    CORE --> EXECUTOR
    CORE --> COMM
    CORE --> SECURITY

    INVENTORY --> WMI
    INVENTORY --> REGISTRY
    MONITOR --> SERVICES
    MONITOR --> EVENTLOG
    EXECUTOR --> FILESYSTEM

    COMM --> HTTPS
    COMM --> WEBSOCKET
    SECURITY --> ENCRYPTION
```

### **Agent Functionality Matrix**

| Function | Description | Frequency | Data Sent | Triggers |
|----------|-------------|-----------|-----------|----------|
| **Hardware Inventory** | CPU, RAM, Storage, Network cards | Daily | JSON payload | Scheduled + On demand |
| **Software Inventory** | Installed programs, versions, licenses | Daily | JSON payload | Scheduled + On demand |
| **System Status** | CPU usage, RAM usage, disk space | Every 5 min | Metrics JSON | Real-time monitoring |
| **Service Monitoring** | Windows services status | Every 10 min | Service states | Service changes |
| **Event Log Monitoring** | Critical system events | Real-time | Event details | Error/Warning events |
| **Security Status** | Antivirus, firewall, updates | Hourly | Security state | Status changes |
| **Network Status** | Connectivity, bandwidth usage | Every 5 min | Network metrics | Connection issues |
| **Automatic Ticketing** | Create tickets for critical issues | Real-time | Issue details | Threshold breaches |
| **Script Execution** | Run PowerShell/batch scripts | On demand | Execution results | Technician request |
| **Remote Assistance** | Enable remote desktop access | On demand | Session details | Support request |

### **Agent Database Schema**

#### **Assets Table (Extended for Agents)**
```sql
CREATE TABLE assets (
    asset_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(client_id),
    site_id UUID NOT NULL REFERENCES sites(site_id),

    -- Basic asset info
    asset_type asset_type NOT NULL, -- 'workstation', 'server', 'laptop', 'printer', etc.
    name VARCHAR(255) NOT NULL,
    serial_number VARCHAR(255),

    -- Agent-specific fields
    agent_status agent_status DEFAULT 'offline', -- 'online', 'offline', 'error', 'installing'
    agent_version VARCHAR(50),
    last_seen TIMESTAMP WITH TIME ZONE,
    last_inventory_update TIMESTAMP WITH TIME ZONE,

    -- Hardware specifications (JSON)
    hardware_specs JSONB,
    software_inventory JSONB,
    system_metrics JSONB,

    -- Network and security
    ip_address INET,
    mac_address VARCHAR(17),
    domain_joined BOOLEAN DEFAULT false,
    antivirus_status VARCHAR(100),
    firewall_enabled BOOLEAN,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### **Agent Metrics Table**
```sql
CREATE TABLE agent_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID NOT NULL REFERENCES assets(asset_id),

    -- System performance metrics
    cpu_usage_percent DECIMAL(5,2),
    memory_usage_percent DECIMAL(5,2),
    disk_usage_percent DECIMAL(5,2),
    network_usage_mbps DECIMAL(10,2),

    -- System health indicators
    uptime_hours INTEGER,
    temperature_celsius INTEGER,
    error_count INTEGER,
    warning_count INTEGER,

    -- Timestamp
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Indexes for performance
    INDEX idx_agent_metrics_asset_time (asset_id, recorded_at),
    INDEX idx_agent_metrics_recorded_at (recorded_at)
);
```

#### **Agent Scripts Table**
```sql
CREATE TABLE agent_scripts (
    script_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    script_type VARCHAR(50) NOT NULL, -- 'powershell', 'batch', 'python'
    script_content TEXT NOT NULL,

    -- Execution parameters
    timeout_seconds INTEGER DEFAULT 300,
    requires_admin BOOLEAN DEFAULT false,
    client_id UUID REFERENCES clients(client_id), -- NULL for global scripts

    -- Security and approval
    is_approved BOOLEAN DEFAULT false,
    approved_by UUID REFERENCES users(user_id),
    approved_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id)
);
```

#### **Script Execution Log**
```sql
CREATE TABLE script_executions (
    execution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    script_id UUID NOT NULL REFERENCES agent_scripts(script_id),
    asset_id UUID NOT NULL REFERENCES assets(asset_id),
    executed_by UUID NOT NULL REFERENCES users(user_id),

    -- Execution details
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'running', -- 'running', 'completed', 'failed', 'timeout'
    exit_code INTEGER,

    -- Results
    stdout_output TEXT,
    stderr_output TEXT,
    execution_time_seconds INTEGER,

    -- Context
    ticket_id UUID REFERENCES tickets(ticket_id), -- If executed as part of ticket resolution

    INDEX idx_script_executions_asset (asset_id),
    INDEX idx_script_executions_script (script_id),
    INDEX idx_script_executions_time (started_at)
);
```

### **Agent Communication Protocol**

#### **Agent Registration Flow**
```mermaid
sequenceDiagram
    participant Agent as LANET Agent
    participant API as Helpdesk API
    participant DB as Database
    participant Auth as Auth System

    Agent->>API: POST /api/agents/register
    Note over Agent,API: {client_key, site_key, hardware_info}

    API->>Auth: Validate client/site keys
    Auth-->>API: Validation result

    API->>DB: INSERT INTO assets (agent registration)
    DB-->>API: asset_id + agent_token

    API-->>Agent: {agent_id, auth_token, config}

    Note over Agent: Store credentials securely

    Agent->>API: POST /api/agents/heartbeat
    Note over Agent,API: Regular heartbeat every 60 seconds
```

#### **Inventory Update Flow**
```mermaid
sequenceDiagram
    participant Agent as LANET Agent
    participant API as Helpdesk API
    participant DB as Database
    participant Alert as Alert System

    Note over Agent: Collect system inventory

    Agent->>API: POST /api/agents/inventory
    Note over Agent,API: {hardware_specs, software_list, system_metrics}

    API->>DB: UPDATE assets SET hardware_specs = ?, software_inventory = ?
    DB-->>API: Update confirmation

    API->>Alert: Check for threshold breaches
    Alert->>Alert: Evaluate disk space, CPU, memory

    alt Critical threshold exceeded
        Alert->>DB: CREATE ticket (auto-generated)
        Alert->>API: Send notification
    end

    API-->>Agent: {status: 'success', next_update: 3600}
```

#### **Script Execution Flow**
```mermaid
sequenceDiagram
    participant Tech as Technician
    participant Web as Web Portal
    participant API as Helpdesk API
    participant Agent as LANET Agent
    participant DB as Database

    Tech->>Web: Select asset + script to execute
    Web->>API: POST /api/agents/execute-script
    Note over Web,API: {asset_id, script_id, parameters}

    API->>DB: INSERT INTO script_executions
    API->>Agent: WebSocket: execute_script command

    Agent->>Agent: Validate script permissions
    Agent->>Agent: Execute PowerShell/batch script

    Agent->>API: WebSocket: execution_progress
    Agent->>API: WebSocket: execution_completed
    Note over Agent,API: {exit_code, stdout, stderr, execution_time}

    API->>DB: UPDATE script_executions SET status = 'completed'
    API-->>Web: Real-time execution results
    Web-->>Tech: Display script output
```

### **Agent Security Model**

#### **Authentication & Authorization**
- **Agent Registration**: Client-specific keys for initial registration
- **Token-Based Auth**: JWT tokens for ongoing communication
- **Certificate Pinning**: SSL certificate validation
- **Encrypted Communication**: AES-256 encryption for sensitive data

#### **Script Execution Security**
- **Approval Workflow**: Scripts must be approved by superadmin/admin
- **Permission Levels**: Scripts marked as requiring admin privileges
- **Execution Sandboxing**: Limited execution environment
- **Audit Trail**: Complete logging of all script executions

#### **Network Security**
- **Firewall Rules**: Outbound HTTPS only (port 443)
- **IP Whitelisting**: Optional IP restriction for agent communication
- **VPN Support**: Agents can work through VPN connections
- **Proxy Support**: Corporate proxy server compatibility

### **Agent Deployment & Management**

#### **Agent Installation Methods**
1. **MSI Installer**: Windows installer package with client/site pre-configuration
2. **Group Policy**: Domain-wide deployment via Active Directory
3. **Manual Installation**: Individual workstation setup
4. **Remote Installation**: Deploy via existing RMM tools

#### **Agent Configuration**
```json
{
  "server_url": "https://helpdesk.lanet.mx/api",
  "client_id": "75f6b906-db3a-404d-b032-3a52eac324c4",
  "site_id": "d01df78a-c48b-40c2-b943-ef0830e26bf1",
  "update_intervals": {
    "heartbeat": 60,
    "inventory": 3600,
    "metrics": 300
  },
  "monitoring": {
    "cpu_threshold": 90,
    "memory_threshold": 85,
    "disk_threshold": 90,
    "auto_ticket_creation": true
  },
  "security": {
    "require_approval_for_scripts": true,
    "allow_remote_assistance": true,
    "encrypt_communications": true
  }
}
```

#### **Agent Update Mechanism**
- **Automatic Updates**: Agents check for updates daily
- **Staged Rollouts**: Updates deployed to test sites first
- **Rollback Capability**: Ability to revert to previous version
- **Update Notifications**: Alerts when agents need updates

### **Integration with Helpdesk System**

#### **Automatic Ticket Creation**
```python
# Example: Agent detects critical disk space
def check_disk_space_threshold():
    if disk_usage > 90:
        ticket_data = {
            "subject": f"Critical Disk Space Alert - {asset_name}",
            "description": f"Disk usage at {disk_usage}% on {asset_name}",
            "priority": "critica",
            "category": "hardware",
            "auto_generated": True,
            "asset_id": asset_id,
            "affected_person": "System Administrator",
            "affected_person_contact": site_admin_phone
        }
        create_ticket(ticket_data)
```

#### **Asset Lifecycle Management**
- **Discovery**: Automatic asset discovery when agents install
- **Tracking**: Real-time status and location tracking
- **Maintenance**: Scheduled maintenance reminders
- **Retirement**: Asset decommissioning workflow

---

## 🚀 **DEPLOYMENT ARCHITECTURE**

### **Production Environment**

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx Load Balancer]
    end
    
    subgraph "Application Servers"
        APP1[Flask App Server 1]
        APP2[Flask App Server 2]
        APP3[Flask App Server 3]
    end
    
    subgraph "Database Cluster"
        PG_PRIMARY[(PostgreSQL Primary)]
        PG_REPLICA[(PostgreSQL Replica)]
    end
    
    subgraph "Cache & Queue"
        REDIS[(Redis Cache)]
        EMAIL_QUEUE[(Email Queue)]
    end
    
    subgraph "External Services"
        SMTP[SMTP Server]
        IMAP[IMAP Server]
    end
    
    LB --> APP1
    LB --> APP2
    LB --> APP3
    
    APP1 --> PG_PRIMARY
    APP2 --> PG_PRIMARY
    APP3 --> PG_PRIMARY
    
    APP1 --> PG_REPLICA
    APP2 --> PG_REPLICA
    APP3 --> PG_REPLICA
    
    APP1 --> REDIS
    APP2 --> REDIS
    APP3 --> REDIS
    
    APP1 --> EMAIL_QUEUE
    APP2 --> EMAIL_QUEUE
    APP3 --> EMAIL_QUEUE
    
    EMAIL_QUEUE --> SMTP
    EMAIL_QUEUE --> IMAP
```

### **Environment Configuration**

#### **Production Settings**
```python
# backend/config.py
DATABASE_URL = "postgresql://user:pass@db-cluster:5432/lanet_helpdesk"
REDIS_URL = "redis://redis-cluster:6379/0"
JWT_SECRET_KEY = "production-secret-key-256-bit"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
SMTP_HOST = "mail.compushop.com.mx"
SMTP_PORT = 587
SMTP_USERNAME = "webmaster@compushop.com.mx"
```

#### **Security Hardening**
- HTTPS only (TLS 1.3)
- JWT secret rotation
- Database connection encryption
- Rate limiting on authentication endpoints
- Input sanitization and validation
- CORS restricted to production domains
- File upload restrictions (10MB, specific types)

---

## 📊 **SYSTEM METRICS & MONITORING**

### **Key Performance Indicators**

- **Ticket Creation**: Web (TKT-000089) + Email (unified sequence)
- **Response Time**: < 200ms for API endpoints
- **Database Queries**: RLS-filtered, optimized with indexes
- **Email Processing**: Bidirectional SMTP/IMAP integration
- **User Sessions**: JWT-based, 8-hour expiration
- **Data Isolation**: 100% multi-tenant via RLS policies

### **Current System Status**

| Component | Status | Version | Notes |
|-----------|--------|---------|-------|
| **Backend API** | ✅ Operational | v3.0 | Flask + Python 3.10 |
| **Database** | ✅ Operational | PostgreSQL 14+ | RLS enabled |
| **Authentication** | ✅ Operational | JWT | Role-based access |
| **Ticket System** | ✅ Operational | v3.0 | Unified numbering |
| **Email Integration** | 🔄 Partial | v3.0 | SMTP working, IMAP in progress |
| **Notifications** | 🔄 Partial | v3.0 | Templates working, queue optimization needed |

---

## 🔧 **TECHNICAL IMPLEMENTATION DETAILS**

### **Frontend Architecture (React 18 + TypeScript)**

#### **Service Layer Structure**
```typescript
// services/apiService.ts - Base API service with authentication
class ApiService {
  private baseURL = 'http://localhost:5001/api';

  private getHeaders(): Record<string, string> {
    const token = localStorage.getItem('access_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    // Centralized error handling and token refresh
  }
}

// services/ticketsService.ts - Tickets-specific operations
class TicketsService extends ApiService {
  async createTicket(ticketData: CreateTicketRequest): Promise<TicketResponse> {
    return this.post<TicketResponse>('/tickets/', ticketData);
  }

  async getTickets(filters?: TicketFilters): Promise<TicketListResponse> {
    return this.get<TicketListResponse>('/tickets/', filters);
  }
}
```

#### **Authentication Context**
```typescript
// contexts/AuthContext.tsx
interface AuthContextType {
  user: User | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  hasRole: (roles: UserRole[]) => boolean;
}

// Automatic token refresh and role-based UI rendering
const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // JWT token management, automatic refresh, role validation
};
```

### **Backend Module Structure**

#### **Module Template Pattern**
```python
# modules/{module_name}/routes.py
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils.security import require_role
from .service import {ModuleName}Service

{module_name}_bp = Blueprint('{module_name}', __name__)

@{module_name}_bp.route('/', methods=['GET'])
@jwt_required()
def get_{module_name}():
    """Standard GET endpoint with RLS filtering"""
    try:
        service = {ModuleName}Service(current_app.db_manager)
        result = service.get_all()
        return current_app.response_manager.success(result)
    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return current_app.response_manager.server_error()
```

#### **Service Layer Pattern**
```python
# modules/{module_name}/service.py
class {ModuleName}Service:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)

    def create_{entity}(self, data: Dict, created_by: str) -> Dict:
        """Business logic with validation and RLS compliance"""
        # 1. Validate input data
        # 2. Apply business rules
        # 3. Execute database operations
        # 4. Return standardized response
```

### **Database Implementation Details**

#### **RLS Context Management**
```python
# core/database.py
class DatabaseManager:
    def set_rls_context(self, user_id: str, user_role: str,
                       client_id: str = None, site_ids: List[str] = None):
        """Set PostgreSQL session variables for RLS"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT set_config('app.current_user_id', %s, false)", (str(user_id),))
                cur.execute("SELECT set_config('app.current_user_role', %s, false)", (user_role,))
                if client_id:
                    cur.execute("SELECT set_config('app.current_user_client_id', %s, false)", (str(client_id),))
                if site_ids:
                    site_ids_str = ','.join(str(sid) for sid in site_ids)
                    cur.execute("SELECT set_config('app.current_user_site_ids', %s, false)", (site_ids_str,))
                conn.commit()
```

#### **Unified Ticket Numbering Implementation**
```sql
-- Database sequence and trigger
CREATE SEQUENCE ticket_number_seq START 1;

CREATE OR REPLACE FUNCTION generate_ticket_number()
RETURNS TEXT AS $$
BEGIN
    RETURN 'TKT-' || LPAD(nextval('ticket_number_seq')::TEXT, 6, '0');
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-generate ticket numbers
CREATE OR REPLACE FUNCTION set_ticket_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ticket_number IS NULL OR NEW.ticket_number = '' THEN
        NEW.ticket_number := generate_ticket_number();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ticket_number_trigger
    BEFORE INSERT ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION set_ticket_number();
```

### **Email System Architecture**

#### **Email Configuration Structure**
```sql
CREATE TABLE email_config (
    config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- SMTP Configuration
    smtp_host VARCHAR(255) NOT NULL,
    smtp_port INTEGER DEFAULT 587,
    smtp_username VARCHAR(255) NOT NULL,
    smtp_password_encrypted TEXT NOT NULL,
    smtp_use_tls BOOLEAN DEFAULT true,
    smtp_use_ssl BOOLEAN DEFAULT false,

    -- IMAP Configuration
    imap_host VARCHAR(255) NOT NULL,
    imap_port INTEGER DEFAULT 993,
    imap_username VARCHAR(255) NOT NULL,
    imap_password_encrypted TEXT NOT NULL,
    imap_use_ssl BOOLEAN DEFAULT true,

    -- Email-to-ticket settings
    enable_email_to_ticket BOOLEAN DEFAULT false,
    default_client_id UUID REFERENCES clients(client_id),
    default_priority VARCHAR(20) DEFAULT 'media',

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### **Email Template System**
```sql
CREATE TABLE email_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    template_type VARCHAR(50) NOT NULL, -- 'ticket_created', 'ticket_updated', etc.
    subject_template TEXT NOT NULL,
    body_template TEXT NOT NULL,
    is_html BOOLEAN DEFAULT true,
    variables JSONB, -- Available template variables
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false
);

-- Example template variables
{
  "variables": [
    "{{ticket_number}}",
    "{{client_name}}",
    "{{subject}}",
    "{{description}}",
    "{{priority}}",
    "{{status}}",
    "{{created_by}}",
    "{{assigned_to}}",
    "{{created_date}}",
    "{{site_name}}"
  ]
}
```

### **Notification System Implementation**

#### **Email Queue Management**
```python
# modules/notifications/service.py
class NotificationService:
    def send_ticket_notification(self, notification_type: str, ticket_id: str):
        """Send notifications based on ticket lifecycle events"""

        # 1. Get ticket details with RLS filtering
        ticket = self.get_ticket_details(ticket_id)

        # 2. Determine recipients based on notification type and roles
        recipients = self.get_notification_recipients(ticket, notification_type)

        # 3. Get appropriate email template
        template = self.get_email_template(notification_type)

        # 4. Render template with ticket variables
        rendered_email = self.render_template(template, ticket)

        # 5. Queue emails for delivery
        for recipient in recipients:
            self.queue_email(recipient, rendered_email['subject'], rendered_email['body'])

    def get_notification_recipients(self, ticket: Dict, notification_type: str) -> List[str]:
        """Determine who should receive notifications based on type and roles"""
        recipients = []

        if notification_type == 'ticket_created':
            # Superadmins and technicians get all ticket notifications
            recipients.extend(self.get_users_by_role(['superadmin', 'technician']))
            # Client admin and solicitante for their tickets
            recipients.extend(self.get_client_users(ticket['client_id']))

        elif notification_type == 'ticket_assigned':
            # Assigned technician + client contacts
            recipients.append(ticket['assigned_to_email'])
            recipients.extend(self.get_client_contacts(ticket['client_id']))

        return list(set(recipients))  # Remove duplicates
```

### **Security Implementation Details**

#### **Input Validation and Sanitization**
```python
# utils/security.py
class SecurityUtils:
    @staticmethod
    def sanitize_dict(data: Dict) -> Dict:
        """Sanitize all string values in a dictionary"""
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = SecurityUtils.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = SecurityUtils.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [SecurityUtils.sanitize_string(item) if isinstance(item, str) else item for item in value]
            else:
                sanitized[key] = value
        return sanitized

    @staticmethod
    def sanitize_string(text: str) -> str:
        """Remove potentially dangerous characters"""
        if not text:
            return text
        # Remove HTML tags, SQL injection patterns, XSS attempts
        return html.escape(text.strip())
```

#### **Role-Based Decorator Implementation**
```python
# utils/security.py
def require_role(allowed_roles: List[str]):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                claims = get_jwt()
                user_role = claims.get('role')

                if not user_role or user_role not in allowed_roles:
                    return current_app.response_manager.forbidden(
                        f"Access denied. Required roles: {', '.join(allowed_roles)}"
                    )

                return f(*args, **kwargs)
            except Exception as e:
                current_app.logger.error(f"Role check failed: {e}")
                return current_app.response_manager.unauthorized()

        return decorated_function
    return decorator

# Usage in routes
@tickets_bp.route('/<ticket_id>', methods=['DELETE'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def delete_ticket(ticket_id):
    """Only superadmin and admin can delete tickets"""
```

---

## 📋 **DEVELOPMENT GUIDELINES**

### **Code Standards**

#### **Python Backend Standards**
- **Type Hints**: All functions must include type hints
- **Docstrings**: Google-style docstrings for all public methods
- **Error Handling**: Try-catch blocks with proper logging
- **RLS Compliance**: All database queries must respect RLS policies
- **Input Validation**: Validate and sanitize all user inputs

#### **TypeScript Frontend Standards**
- **Strict Mode**: TypeScript strict mode enabled
- **Interface Definitions**: All API responses must have TypeScript interfaces
- **Error Boundaries**: React error boundaries for component error handling
- **Accessibility**: ARIA labels and semantic HTML
- **Responsive Design**: Mobile-first responsive design

### **Testing Requirements**

#### **Backend Testing**
```python
# tests/test_tickets.py
class TestTicketsAPI:
    def test_create_ticket_with_valid_data(self):
        """Test ticket creation with valid data"""
        # Test unified numbering
        # Test RLS filtering
        # Test notification triggering

    def test_create_ticket_unauthorized_access(self):
        """Test RLS prevents unauthorized access"""
        # Test client isolation
        # Test role-based restrictions
```

#### **Frontend Testing**
```typescript
// tests/TicketCreate.test.tsx
describe('TicketCreate Component', () => {
  test('creates ticket with valid data', async () => {
    // Test form validation
    // Test API integration
    // Test success/error handling
  });

  test('shows validation errors for invalid data', () => {
    // Test client-side validation
    // Test error message display
  });
});
```

### **Deployment Checklist**

#### **Pre-Production Validation**
- [ ] All RLS policies tested and verified
- [ ] JWT token expiration configured for production
- [ ] Database migrations applied and tested
- [ ] Email configuration tested with production SMTP
- [ ] SSL certificates installed and configured
- [ ] Environment variables secured
- [ ] Backup and recovery procedures tested
- [ ] Performance testing completed
- [ ] Security audit completed

---

**📝 Document Version:** 1.0
**📅 Last Updated:** July 5, 2025
**👤 Maintained By:** LANET Development Team
**🔄 Next Review:** August 1, 2025

---

*This documentation serves as the definitive reference for LANET Helpdesk V3 architecture. All new AI agents should review this document before making system modifications.*
