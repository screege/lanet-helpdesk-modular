# UTF-8 Database Procedures for LANET Helpdesk V3

## 📋 Overview

This document provides critical procedures for handling UTF-8 database operations in LANET Helpdesk V3, specifically addressing Spanish character encoding issues that can occur during backup and restore operations.

## ⚠️ Critical Issue Background

### Problem Identified (July 23, 2025)
Spanish characters in email templates and notifications were displaying corrupted:
- `Número` appeared as `N├║mero`
- `Título` appeared as `T├¡tulo`
- `Descripción` appeared as `Descripci├│n`
- `técnico` appeared as `t├®cnico`

### Root Cause
Incorrect database backup and restore procedures that didn't preserve UTF-8 encoding, causing character corruption in production environment.

## ✅ CORRECT Procedures for Future Agents

### 1. Development Environment Backup (Windows)

```powershell
# Set environment variable for password
$env:PGPASSWORD="Poikl55+*"

# Create UTF-8 compliant backup
pg_dump -h localhost -p 5432 -U postgres -d lanet_helpdesk `
  --encoding=UTF8 `
  --no-owner `
  --no-privileges `
  --clean `
  --if-exists `
  --format=plain `
  --file="backup_utf8_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
```

### 2. Production Environment Backup (Linux)

```bash
# Create UTF-8 compliant backup
docker exec lanet-helpdesk-db pg_dump -U postgres -d lanet_helpdesk \
  --encoding=UTF8 \
  --no-owner \
  --no-privileges \
  --clean \
  --if-exists \
  --format=plain > backup_utf8_$(date +%Y%m%d_%H%M%S).sql
```

### 3. File Transfer to Production

```bash
# Upload backup to production server
scp -i "C:\Users\scree\.ssh\lanet_key" -P 57411 \
  "backup_utf8_file.sql" \
  root@104.168.159.24:/tmp/backup_utf8.sql
```

### 4. Production Database Restore

```bash
# Connect to production server
ssh -i "C:\Users\scree\.ssh\lanet_key" -p 57411 root@104.168.159.24

# Navigate to project directory
cd /opt/lanet-helpdesk

# Stop backend to prevent connections
docker stop lanet-helpdesk-backend

# Drop and recreate database with UTF-8 encoding
docker exec lanet-helpdesk-db psql -U postgres -c 'DROP DATABASE IF EXISTS lanet_helpdesk;'
docker exec lanet-helpdesk-db psql -U postgres -c 'CREATE DATABASE lanet_helpdesk WITH ENCODING UTF8;'

# Restore database with UTF-8 encoding
docker exec -i lanet-helpdesk-db psql -U postgres -d lanet_helpdesk < /tmp/backup_utf8.sql

# Restart backend
docker start lanet-helpdesk-backend

# Restart SLA Monitor
docker exec -d lanet-helpdesk-backend python run_sla_monitor.py
```

## 🔍 Verification Procedures

### 1. Check Database Encoding
```bash
# Verify database encoding
docker exec lanet-helpdesk-db psql -U postgres -l | grep lanet_helpdesk
```

### 2. Test Spanish Characters in Email Templates
```bash
# Check email templates for proper Spanish characters
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c \
  "SELECT name, subject FROM email_templates WHERE name LIKE '%ticket%' LIMIT 3;"
```

### 3. End-to-End Test
1. Create a test ticket through the web interface
2. Verify the email notification contains proper Spanish characters:
   - ✅ `Número de Ticket`
   - ✅ `Título`
   - ✅ `Descripción`
   - ✅ `técnico`

## ❌ DEPRECATED Procedures (DO NOT USE)

### Incorrect Backup Methods
```powershell
# WRONG - Causes UTF-8 corruption
pg_dump ... | Out-File -Encoding UTF8 ...
pg_dump ... --inserts --column-inserts ...
pg_dump ... | Out-File -Encoding UTF8NoBOM ...
```

### Why These Fail
- PowerShell's `Out-File` can introduce encoding issues
- `--inserts` and `--column-inserts` can cause binary data corruption
- UTF8NoBOM encoding may not preserve all characters correctly

## 🚨 Emergency Recovery

If UTF-8 corruption is detected in production:

1. **Immediate Assessment:**
   ```bash
   # Check current corruption level
   docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c \
     "SELECT subject FROM email_templates WHERE subject LIKE '%├%';"
   ```

2. **Quick Fix:**
   - Create new UTF-8 backup from development
   - Follow restore procedures above
   - Verify with test ticket creation

## 📝 Checklist for Future Deployments

### Before Database Operations:
- [ ] Verify development database has correct Spanish characters
- [ ] Use correct UTF-8 backup command (no `Out-File`)
- [ ] Test backup file size (should be 6-12MB for full database)
- [ ] Verify backup contains proper encoding headers

### During Restore:
- [ ] Stop backend container first
- [ ] Drop and recreate database with UTF-8 encoding
- [ ] Use direct pipe restore (not copy/paste)
- [ ] Restart all services in correct order

### After Restore:
- [ ] Verify database encoding with `psql -l`
- [ ] Check email templates for Spanish characters
- [ ] Create test ticket and verify email output
- [ ] Restart SLA Monitor
- [ ] Monitor logs for any encoding errors

## 📞 Support Information

### Key Personnel
- **Database Administrator:** Responsible for UTF-8 procedures
- **System Administrator:** Production server access
- **QA Tester:** Email verification testing

### Emergency Contacts
- **Primary:** LANET Development Team
- **Backup:** System Administrator with root access

---

**Document Version:** 1.0  
**Created:** July 23, 2025  
**Last Updated:** July 23, 2025  
**Next Review:** August 23, 2025  
**Maintained by:** LANET Development Team

**Critical Note:** Always test UTF-8 procedures in development environment before applying to production.
