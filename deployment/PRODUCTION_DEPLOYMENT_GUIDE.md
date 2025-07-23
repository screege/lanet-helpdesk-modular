# LANET Helpdesk V3 - Production Deployment Guide

## Overview
This document provides comprehensive deployment instructions and system configuration details for the LANET Helpdesk V3 production environment on HostWinds VPS.

## Server Information

### Connection Details
- **Server IP:** 104.168.159.24
- **SSH Port:** 57411
- **SSH Key:** `C:\Users\scree\.ssh\lanet_key`
- **Connection Command:** 
  ```bash
  ssh -i "C:\Users\scree\.ssh\lanet_key" -p 57411 -o StrictHostKeyChecking=no root@104.168.159.24
  ```

### Server Configuration
- **OS:** Ubuntu 24.04.2 LTS
- **Timezone:** America/Mexico_City (CST -0600)
- **Domain:** helpdesk.lanet.mx
- **SSL:** Let's Encrypt (auto-renewal configured)

## User Credentials

### Test Accounts
- **Superadmin:** ba@lanet.mx / TestAdmin123!
- **Technician:** tech@test.com / TestTech123!
- **Client Admin:** prueba@prueba.com / Poikl55+*
- **Solicitante:** prueba3@prueba.com / Poikl55+*

⚠️ **NEVER change these test account passwords**

### Database Credentials
- **Host:** localhost:5432
- **Database:** lanet_helpdesk
- **User:** postgres
- **Password:** Poikl55+*

### Email Configuration
- **SMTP Server:** mail.compushop.com.mx
- **User:** ti@compushop.com.mx
- **Password:** Iyhnbsfg55+*

## Docker Infrastructure

### Container Architecture
The system runs 4 main containers:

1. **lanet-helpdesk-frontend** (nginx)
   - Ports: 80:80, 443:443
   - Serves React application
   - SSL termination

2. **lanet-helpdesk-backend** (Python Flask)
   - Port: 5001:5001
   - API server with health checks
   - Includes SLA Monitor

3. **lanet-helpdesk-db** (PostgreSQL 17.4)
   - Port: 5432:5432
   - Primary database

4. **lanet-helpdesk-redis** (Redis 7-alpine)
   - Port: 6379:6379
   - Caching and sessions

### Docker Compose Configuration
Location: `/opt/lanet-helpdesk/deployment/docker/docker-compose.yml`

Key configurations:
- All containers have restart policies
- Health checks on backend
- Volume persistence for database and uploads
- Network isolation

### Volume Mappings
- Database: `postgres_data:/var/lib/postgresql/data`
- Uploads: `./uploads:/app/uploads`
- SSL Certificates: `/etc/letsencrypt:/etc/letsencrypt`

## Auto-Recovery Systems

### Post-Reboot Recovery Script
**Location:** `/opt/lanet-helpdesk/scripts/post-reboot-fix.sh`

**Purpose:** Automatically fixes common issues after server restart

**Features:**
- Stops system nginx (prevents port 80 conflicts)
- Restarts failed frontend containers
- Starts SLA Monitor
- Comprehensive logging to `/var/log/lanet-recovery.log`

**Execution:** Runs 2 minutes after each reboot via crontab

### Systemd Service
**Service:** `lanet-helpdesk.service`
**Location:** `/etc/systemd/system/lanet-helpdesk.service`

**Purpose:** Ensures Docker containers start automatically

**Status:** Enabled and active

### Crontab Configuration
```bash
# Hostwinds Cloud Backups
21 19 * * * /usr/sbin/hwagent backups run

# LANET Helpdesk Auto-Recovery
@reboot sleep 120 && /opt/lanet-helpdesk/scripts/post-reboot-fix.sh
```

### Critical Fix: System Nginx
**Issue:** System nginx conflicts with frontend container on port 80
**Solution:** 
```bash
systemctl stop nginx
systemctl disable nginx
```
**Status:** Permanently disabled

## GitHub Actions Deployment

### Workflow Configuration
**File:** `.github/workflows/deploy-vps.yml`
**Trigger:** Push to main branch
**Target:** HostWinds VPS

### Deployment Process
1. Code checkout
2. SSH connection to VPS
3. Git pull latest changes
4. Docker container rebuild
5. Service restart

### Recent Deployments
- **Last Successful:** Run #22 (Asset Agents Module)
- **Commit:** 69b2633e9242c546930210b2f03e99d4cb7d4323
- **Status:** All modules deployed successfully

### Deployment Verification
```bash
# Check deployment status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Verify site accessibility
curl -I https://helpdesk.lanet.mx
```

## SLA Monitor Configuration

### Integration
- **Type:** Integrated into backend container
- **Script:** `run_sla_monitor.py`
- **Interval:** 3 minutes
- **Logs:** `/logs/sla_monitor.log`

### ✅ CRITICAL FIX: Auto-Start After Server Reboot (July 23, 2025)

#### **Problem Solved**
**Issue:** SLA Monitor did not auto-start after server reboots, requiring manual intervention.

**Root Cause:**
1. Systemd service had incorrect `docker-compose` path
2. No automatic SLA Monitor startup after container initialization

#### **Solution Implemented**

**1. Fixed Systemd Service Path:**
```bash
# Corrected path in /etc/systemd/system/lanet-helpdesk.service
ExecStart=/usr/local/bin/docker-compose -f deployment/docker/docker-compose.yml up -d
# (was incorrectly: /usr/bin/docker-compose)
```

**2. Created Auto-Start Script:**
```bash
# /opt/lanet-helpdesk/scripts/start-sla-monitor.sh
#!/bin/bash
sleep 10
docker exec -d lanet-helpdesk-backend python run_sla_monitor.py
echo SLA Monitor auto-started
```

**3. Updated Systemd Service:**
```ini
[Unit]
Description=LANET Helpdesk Docker Containers
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/lanet-helpdesk
ExecStart=/usr/local/bin/docker-compose -f deployment/docker/docker-compose.yml up -d
ExecStartPost=/bin/sleep 15
ExecStartPost=/opt/lanet-helpdesk/scripts/start-sla-monitor.sh
ExecStop=/usr/local/bin/docker-compose -f deployment/docker/docker-compose.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

#### **Verification After Reboot**
```bash
# Check systemd service status
systemctl status lanet-helpdesk.service

# Verify containers are running
docker ps --format 'table {{.Names}}\t{{.Status}}'

# Confirm SLA Monitor is active
docker exec lanet-helpdesk-backend tail -5 logs/sla_monitor.log

# Should show recent activity like:
# 2025-07-23 14:51:59,671 - sla_monitor - INFO - Processing email queue...
# 2025-07-23 14:52:00,596 - sla_monitor - INFO - SLA monitor job completed successfully
```

### Auto-Start Procedures
1. **Automatic (Recommended):**
   - Systemd service handles container startup
   - Auto-start script launches SLA Monitor after 25 seconds
   - ✅ **WORKING** - Tested after server reboot

2. **Manual Start (If needed):**
   ```bash
   docker exec -d lanet-helpdesk-backend python run_sla_monitor.py
   ```

3. **Verification:**
   ```bash
   # Check if process is running
   docker exec lanet-helpdesk-backend pgrep -f run_sla_monitor.py

   # View recent logs
   docker exec lanet-helpdesk-backend tail -10 logs/sla_monitor.log

   # Monitor in real-time
   docker exec lanet-helpdesk-backend tail -f logs/sla_monitor.log
   ```

### Functionality
- SLA violation monitoring
- Email processing and ticket creation (every 3 minutes)
- Scheduled report processing
- Notification management
- ✅ **UTF-8 Email Support** - Spanish characters display correctly

## Asset Agents Module

### Implementation Status
✅ **Fully Deployed and Functional**

### Database Components
- **Tables:** 
  - `agent_installation_tokens`
  - `agent_token_usage_history`
  - Extended `assets` table with agent fields

- **Functions:**
  - `generate_agent_token(client_id, site_id)`
  - `validate_agent_token(token_value)`

### API Endpoints
- **Token Management:** `/api/agents/clients/{client_id}/sites/{site_id}/tokens`
- **Agent Registration:** `/api/agents/register`
- **Heartbeat:** `/api/agents/heartbeat`

### Token Format
`LANET-{CLIENT_CODE}-{SITE_CODE}-{RANDOM}`

Example: `LANET-CM-O-48F86988`

### Critical Fix Applied
**Issue:** SQL function ambiguity in `generate_agent_token`
**Error:** `column reference "token_value" is ambiguous`
**Solution:** Added table alias to eliminate ambiguity
```sql
-- Fixed query
IF NOT EXISTS (SELECT 1 FROM agent_installation_tokens ait WHERE ait.token_value = new_token_value) THEN
```

## Database Configuration

### Connection Details
- **Container:** lanet-helpdesk-db
- **Engine:** PostgreSQL 17.4
- **Encoding:** UTF-8
- **Locale:** es_MX (Mexican Spanish)

### Recent Schema Changes
1. **Asset Agents Tables** (2025-07-16)
   - Agent installation tokens system
   - Token usage history tracking
   - Extended assets table for agent management

2. **RLS Policies**
   - Multi-tenant data isolation
   - Role-based access control
   - Superadmin protection policies

### Migration Status
All migrations applied successfully:
- `002_add_agent_installation_tokens.sql`
- `002_fix_generate_agent_token.sql`
- `003_fix_generate_agent_token_v2.sql`
- `004_simple_token_generator.sql`

### ⚠️ CRITICAL: UTF-8 Database Backup and Restore Procedures

#### **Problem Solved (July 23, 2025)**
**Issue:** Email templates and notifications showed corrupted Spanish characters:
- `Número` appeared as `N├║mero`
- `Título` appeared as `T├¡tulo`
- `Descripción` appeared as `Descripci├│n`

**Root Cause:** Incorrect database backup/restore procedures that didn't preserve UTF-8 encoding.

#### **CORRECT Backup Procedure for UTF-8**
```bash
# DEVELOPMENT (Windows PowerShell)
$env:PGPASSWORD="Poikl55+*"
pg_dump -h localhost -p 5432 -U postgres -d lanet_helpdesk `
  --encoding=UTF8 `
  --no-owner `
  --no-privileges `
  --clean `
  --if-exists `
  --format=plain `
  --file="backup_utf8_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
```

```bash
# PRODUCTION (Linux)
docker exec lanet-helpdesk-db pg_dump -U postgres -d lanet_helpdesk \
  --encoding=UTF8 \
  --no-owner \
  --no-privileges \
  --clean \
  --if-exists \
  --format=plain > backup_utf8_$(date +%Y%m%d_%H%M%S).sql
```

#### **CORRECT Restore Procedure for UTF-8**
```bash
# 1. Stop backend to prevent connections
docker stop lanet-helpdesk-backend

# 2. Drop and recreate database with UTF-8
docker exec lanet-helpdesk-db psql -U postgres -c 'DROP DATABASE IF EXISTS lanet_helpdesk;'
docker exec lanet-helpdesk-db psql -U postgres -c 'CREATE DATABASE lanet_helpdesk WITH ENCODING UTF8;'

# 3. Restore with UTF-8 encoding
docker exec -i lanet-helpdesk-db psql -U postgres -d lanet_helpdesk < backup_utf8_file.sql

# 4. Restart backend
docker start lanet-helpdesk-backend

# 5. Restart SLA Monitor
docker exec -d lanet-helpdesk-backend python run_sla_monitor.py
```

#### **Verification Commands**
```bash
# Check database encoding
docker exec lanet-helpdesk-db psql -U postgres -l

# Verify Spanish characters in email templates
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c \
  "SELECT name, subject FROM email_templates WHERE name LIKE '%ticket%' LIMIT 2;"

# Test email with Spanish characters
# Create a test ticket and verify email shows: "Número", "Título", "Descripción"
```

### Legacy Backup Procedures (DEPRECATED)
**⚠️ DO NOT USE - These cause UTF-8 corruption:**
```bash
# WRONG - Causes character corruption
pg_dump ... | Out-File -Encoding UTF8 ...
pg_dump ... --inserts --column-inserts ...
```

### Backup Procedures
**Location:** Multiple backup files in `/database/` directory
**Latest UTF-8 Backup:** `backup_utf8_20250723_081132.sql` (✅ Verified working)

**Manual Backup Command (CORRECT):**
```bash
docker exec lanet-helpdesk-db pg_dump -U postgres -d lanet_helpdesk \
  --encoding=UTF8 --no-owner --no-privileges --clean --if-exists \
  > backup_utf8_$(date +%Y%m%d_%H%M%S).sql
```

## SSL/HTTPS Configuration

### Certificate Management
- **Provider:** Let's Encrypt
- **Auto-renewal:** Configured
- **Domains:** helpdesk.lanet.mx

### Nginx Configuration
- **HTTP → HTTPS redirect:** Enabled
- **Security headers:** Implemented
- **SSL protocols:** TLS 1.2+

## Monitoring and Logs

### Log Locations
- **SLA Monitor:** `/opt/lanet-helpdesk/logs/sla_monitor.log`
- **Auto-Recovery:** `/var/log/lanet-recovery.log`
- **Docker Containers:** `docker logs [container_name]`

### Health Checks
- **Backend:** Built-in health endpoint
- **Database:** Connection monitoring
- **Frontend:** HTTP response checks

### Monitoring Commands
```bash
# Container status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# SLA Monitor status
docker exec lanet-helpdesk-backend tail -10 logs/sla_monitor.log

# System resources
htop
df -h
```

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Frontend Container Fails (Exit 128)
**Cause:** System nginx occupying port 80
**Solution:**
```bash
systemctl stop nginx
systemctl disable nginx
docker rm lanet-helpdesk-frontend
docker-compose -f deployment/docker/docker-compose.yml up -d frontend
```

#### 2. SLA Monitor Not Running
**Diagnosis:**
```bash
# Check if process exists
docker exec lanet-helpdesk-backend pgrep -f run_sla_monitor.py

# Check recent logs
docker exec lanet-helpdesk-backend tail -5 logs/sla_monitor.log

# Check systemd service status
systemctl status lanet-helpdesk.service
```
**Solution:**
```bash
# Manual start
docker exec -d lanet-helpdesk-backend python run_sla_monitor.py

# If systemd service failed, restart it
systemctl restart lanet-helpdesk.service

# Verify auto-start script exists and is executable
ls -la /opt/lanet-helpdesk/scripts/start-sla-monitor.sh
chmod +x /opt/lanet-helpdesk/scripts/start-sla-monitor.sh
```

#### 3. Database Connection Issues
**Check:**
```bash
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c "SELECT 1;"
```

#### 4. SSL Certificate Issues
**Renewal:**
```bash
certbot renew --nginx
```

#### 5. Asset Agents Token Generation Error 500
**Cause:** SQL function ambiguity in `generate_agent_token`
**Diagnosis:**
```bash
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c "SELECT generate_agent_token('550e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440001');"
```
**Solution:** Function already fixed with table aliases

#### 6. UTF-8 Character Corruption in Emails
**Symptoms:** Spanish characters appear corrupted in emails:
- `Número` shows as `N├║mero`
- `Título` shows as `T├¡tulo`
- `Descripción` shows as `Descripci├│n`

**Cause:** Database backup/restore without proper UTF-8 encoding

**Diagnosis:**
```bash
# Check current database encoding
docker exec lanet-helpdesk-db psql -U postgres -l | grep lanet_helpdesk

# Test email template characters
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c \
  "SELECT name, subject FROM email_templates LIMIT 2;"
```

**Solution:**
```bash
# 1. Create proper UTF-8 backup (from development)
$env:PGPASSWORD="Poikl55+*"
pg_dump -h localhost -p 5432 -U postgres -d lanet_helpdesk \
  --encoding=UTF8 --no-owner --no-privileges --clean --if-exists \
  --format=plain --file="backup_utf8_corrected.sql"

# 2. Upload to production
scp -i "path/to/ssh_key" -P 57411 backup_utf8_corrected.sql root@104.168.159.24:/tmp/

# 3. Restore with UTF-8 (on production server)
cd /opt/lanet-helpdesk
docker stop lanet-helpdesk-backend
docker exec lanet-helpdesk-db psql -U postgres -c 'DROP DATABASE IF EXISTS lanet_helpdesk;'
docker exec lanet-helpdesk-db psql -U postgres -c 'CREATE DATABASE lanet_helpdesk WITH ENCODING UTF8;'
docker exec -i lanet-helpdesk-db psql -U postgres -d lanet_helpdesk < /tmp/backup_utf8_corrected.sql
docker start lanet-helpdesk-backend
docker exec -d lanet-helpdesk-backend python run_sla_monitor.py

# 4. Verify fix by creating test ticket and checking email
```

### Emergency Recovery Procedures

#### Complete System Recovery
1. **Connect to server:**
   ```bash
   ssh -i "C:\Users\scree\.ssh\lanet_key" -p 57411 root@104.168.159.24
   ```

2. **Navigate to project:**
   ```bash
   cd /opt/lanet-helpdesk
   ```

3. **Stop all containers:**
   ```bash
   docker-compose -f deployment/docker/docker-compose.yml down
   ```

4. **Restart all services:**
   ```bash
   systemctl stop nginx
   docker-compose -f deployment/docker/docker-compose.yml up -d
   docker exec -d lanet-helpdesk-backend python run_sla_monitor.py
   ```

#### Database Recovery
1. **Stop backend:**
   ```bash
   docker stop lanet-helpdesk-backend
   ```

2. **Restore from backup:**
   ```bash
   docker exec -i lanet-helpdesk-db psql -U postgres -d lanet_helpdesk < backup_file.sql
   ```

3. **Restart services:**
   ```bash
   docker start lanet-helpdesk-backend
   ```

#### Post-Reboot Recovery
The system has automated recovery, but manual steps if needed:
1. **Check auto-recovery logs:**
   ```bash
   tail -20 /var/log/lanet-recovery.log
   ```

2. **Manual recovery if auto-recovery failed:**
   ```bash
   /opt/lanet-helpdesk/scripts/post-reboot-fix.sh
   ```

## Development vs Production

### Key Differences
- **Environment:** Production uses Docker containers
- **SSL:** Production has Let's Encrypt certificates
- **Domain:** Production uses helpdesk.lanet.mx
- **Monitoring:** Production has automated monitoring
- **Backups:** Production has scheduled backups
- **Auto-recovery:** Production has post-reboot automation

### Deployment Workflow
1. **Development:** Local testing with development database
2. **Commit:** Push changes to GitHub main branch
3. **CI/CD:** GitHub Actions automatically deploys
4. **Verification:** Check deployment success and functionality
5. **Monitoring:** Ongoing system health monitoring

### Environment Variables
Production containers use environment variables for:
- Database connections
- Email configuration
- API keys and secrets
- Feature flags

## Security Considerations

### Access Control
- **SSH:** Key-based authentication only
- **Database:** Local access only, strong passwords
- **Application:** Role-based access control (RLS)
- **SSL:** HTTPS enforced, secure headers

### Data Protection
- **Multi-tenant:** RLS policies ensure data isolation
- **Backups:** Regular automated backups
- **Encryption:** SSL/TLS for all communications
- **Audit:** Comprehensive logging and monitoring

### Network Security
- **Firewall:** UFW configured for essential ports only
- **SSH:** Non-standard port (57411)
- **SSL:** Strong cipher suites and protocols
- **Headers:** Security headers implemented

## Performance Optimization

### Current Configuration
- **Redis:** Caching and session management
- **PostgreSQL:** Optimized for concurrent connections
- **Nginx:** Static file serving and compression
- **Docker:** Resource limits and health checks

### Monitoring Metrics
- **Response times:** API endpoint performance
- **Database:** Query performance and connections
- **System:** CPU, memory, and disk usage
- **Network:** Bandwidth and connection counts

### Optimization Settings
- **Database connections:** Pooled connections
- **Caching:** Redis for session and application cache
- **Static files:** Nginx compression and caching
- **API:** Rate limiting and request optimization

## Maintenance Procedures

### Regular Maintenance
1. **Weekly:** Review logs and system health
2. **Monthly:** Update system packages
3. **Quarterly:** Review and update SSL certificates
4. **As needed:** Database optimization and cleanup

### Update Procedures
1. **Code updates:** Via GitHub Actions deployment
2. **System updates:** Manual during maintenance windows
3. **Database migrations:** Tested and applied carefully
4. **Container updates:** Coordinated with application updates

### Backup Schedule
- **Automated:** Daily via HostWinds Cloud Backups (19:21 daily)
- **Manual:** Before major changes or migrations
- **Retention:** Multiple backup versions maintained
- **Testing:** Regular backup restoration testing

## Contact and Support

### Key Personnel
- **System Administrator:** Root access to VPS
- **Database Administrator:** PostgreSQL management
- **Application Developer:** Code and feature development

### Emergency Contacts
- **HostWinds Support:** VPS infrastructure issues
- **Let's Encrypt:** SSL certificate problems
- **GitHub:** Repository and deployment issues

### Support Resources
- **Documentation:** This guide and inline code comments
- **Logs:** Comprehensive logging for troubleshooting
- **Monitoring:** Real-time system health monitoring

## Appendix

### Useful Commands Reference

#### Docker Management
```bash
# View all containers
docker ps -a

# View logs
docker logs [container_name] --tail=50

# Execute commands in container
docker exec -it [container_name] bash

# Restart specific container
docker restart [container_name]

# View container resource usage
docker stats

# Clean up unused containers/images
docker system prune
```

#### System Management
```bash
# Check system status
systemctl status lanet-helpdesk

# View system logs
journalctl -u lanet-helpdesk -f

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
htop

# View system uptime
uptime
```

#### Network and Connectivity
```bash
# Test site accessibility
curl -I https://helpdesk.lanet.mx

# Check port availability
netstat -tlnp | grep :80

# Test database connection
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c "SELECT version();"

# Check SSL certificate
openssl s_client -connect helpdesk.lanet.mx:443 -servername helpdesk.lanet.mx
```

#### Database Management
```bash
# Connect to database
docker exec -it lanet-helpdesk-db psql -U postgres -d lanet_helpdesk

# Create backup
docker exec lanet-helpdesk-db pg_dump -U postgres -d lanet_helpdesk > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker exec -i lanet-helpdesk-db psql -U postgres -d lanet_helpdesk < backup_file.sql

# Check database size
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c "SELECT pg_size_pretty(pg_database_size('lanet_helpdesk'));"
```

#### SLA Monitor Management
```bash
# Check if SLA Monitor is running
docker exec lanet-helpdesk-backend ps aux | grep sla

# Start SLA Monitor
docker exec -d lanet-helpdesk-backend python run_sla_monitor.py

# View SLA Monitor logs
docker exec lanet-helpdesk-backend tail -20 logs/sla_monitor.log

# Monitor SLA Monitor in real-time
docker exec lanet-helpdesk-backend tail -f logs/sla_monitor.log
```

### File Locations Reference
- **Project Root:** `/opt/lanet-helpdesk/`
- **Docker Compose:** `/opt/lanet-helpdesk/deployment/docker/docker-compose.yml`
- **Recovery Script:** `/opt/lanet-helpdesk/scripts/post-reboot-fix.sh`
- **SSL Certificates:** `/etc/letsencrypt/`
- **System Logs:** `/var/log/`
- **Application Logs:** `/opt/lanet-helpdesk/logs/`
- **Systemd Service:** `/etc/systemd/system/lanet-helpdesk.service`
- **Database Backups:** `/opt/lanet-helpdesk/database/`

### Configuration Files
- **Nginx:** Managed by Docker container
- **PostgreSQL:** `/var/lib/postgresql/data/` (in container)
- **Environment:** Docker environment variables
- **Crontab:** `crontab -l` to view current entries

### Port Mappings
- **80:** HTTP (redirects to HTTPS)
- **443:** HTTPS (frontend)
- **5001:** Backend API
- **5432:** PostgreSQL database
- **6379:** Redis cache
- **57411:** SSH access

### Important Notes

#### Critical Fixes Applied
1. **Frontend Container Issue:** System nginx disabled permanently
2. **Asset Agents SQL Function:** Ambiguity resolved with table aliases
3. **Auto-Recovery:** Comprehensive post-reboot automation
4. **SLA Monitor Auto-Start:** ✅ **FIXED** - Systemd service with auto-start script (July 23, 2025)
5. **UTF-8 Database Encoding:** ✅ **FIXED** - Proper backup/restore procedures (July 23, 2025)
6. **Spanish Character Corruption:** ✅ **FIXED** - Email templates display correctly

#### Known Limitations
- **Container Timezone:** Containers use UTC internally (application handles timezone conversion)
- **Email in Docker:** SMTP works in development but may have Docker networking issues
- **Resource Limits:** No specific limits set (relies on system resources)

#### ✅ RESOLVED Issues (July 23, 2025)
- **SLA Monitor Auto-Start:** Now starts automatically after server reboot
- **UTF-8 Email Corruption:** Spanish characters (ñ, á, é, í, ó, ú) display correctly
- **Database Encoding:** Proper UTF-8 backup/restore procedures documented

#### Future Improvements
- **Container timezone:** Configure containers to use host timezone
- **Resource limits:** Set appropriate Docker resource constraints
- **Monitoring:** Implement comprehensive application monitoring
- **Backup automation:** Enhanced backup and restoration procedures

---

**Document Version:** 2.0
**Last Updated:** July 23, 2025
**Next Review:** August 23, 2025
**Maintained by:** LANET Development Team

**Major Updates in v2.0:**
- ✅ SLA Monitor auto-start solution documented
- ✅ UTF-8 database backup/restore procedures added
- ✅ Spanish character corruption fix documented
- ✅ Systemd service configuration updated
- ✅ Comprehensive troubleshooting for UTF-8 issues

---

## Quick Reference Card

### Emergency Commands
```bash
# Connect to server
ssh -i "C:\Users\scree\.ssh\lanet_key" -p 57411 root@104.168.159.24

# Check system status
cd /opt/lanet-helpdesk && docker ps

# Restart everything
docker-compose -f deployment/docker/docker-compose.yml restart

# Start SLA Monitor
docker exec -d lanet-helpdesk-backend python run_sla_monitor.py

# Check logs
docker logs lanet-helpdesk-backend --tail=20
```

### Key URLs
- **Production Site:** https://helpdesk.lanet.mx
- **API Base:** https://helpdesk.lanet.mx/api
- **GitHub Repository:** https://github.com/screege/lanet-helpdesk-modular

### Critical Passwords
- **Database:** Poikl55+*
- **Email:** Iyhnbsfg55+*
- **Test Accounts:** See User Credentials section above
