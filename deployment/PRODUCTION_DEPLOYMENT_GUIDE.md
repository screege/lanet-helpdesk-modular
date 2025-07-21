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

### Auto-Start Procedures
1. **Manual Start:**
   ```bash
   docker exec -d lanet-helpdesk-backend python run_sla_monitor.py
   ```

2. **Auto-Start:** Included in post-reboot script

3. **Verification:**
   ```bash
   docker exec lanet-helpdesk-backend ps aux | grep sla
   docker exec lanet-helpdesk-backend tail -5 logs/sla_monitor.log
   ```

### Functionality
- SLA violation monitoring
- Email processing and ticket creation
- Scheduled report processing
- Notification management

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

### Backup Procedures
**Location:** Multiple backup files in `/database/` directory
**Latest:** `backup_complete_rls_rbac_20250715_094016.sql`

**Manual Backup Command:**
```bash
docker exec lanet-helpdesk-db pg_dump -U postgres -d lanet_helpdesk > backup_$(date +%Y%m%d_%H%M%S).sql
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
docker exec lanet-helpdesk-backend ps aux | grep sla
```
**Solution:**
```bash
docker exec -d lanet-helpdesk-backend python run_sla_monitor.py
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
4. **SLA Monitor:** Integrated startup and monitoring

#### Known Limitations
- **Container Timezone:** Containers use UTC internally (application handles timezone conversion)
- **Email in Docker:** SMTP works in development but may have Docker networking issues
- **Resource Limits:** No specific limits set (relies on system resources)

#### Future Improvements
- **Container timezone:** Configure containers to use host timezone
- **Resource limits:** Set appropriate Docker resource constraints
- **Monitoring:** Implement comprehensive application monitoring
- **Backup automation:** Enhanced backup and restoration procedures

---

**Document Version:** 1.0
**Last Updated:** July 21, 2025
**Next Review:** August 21, 2025
**Maintained by:** LANET Development Team

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
