# LANET Agent Production BitLocker Deployment Guide

## Overview

This document describes the production-ready solution for deploying LANET Helpdesk agents across 2000+ client computers with automatic BitLocker data collection capabilities. The solution eliminates the need for manual administrator privilege elevation by running the agent as a Windows Service with SYSTEM privileges.

## Problem Statement

- **Current Issue**: Agent fails to collect BitLocker data due to insufficient privileges
- **Production Challenge**: Cannot manually run agent as administrator on 2000+ computers
- **Business Requirement**: Automatic BitLocker recovery key collection for MSP operations
- **Reference**: Commercial MSP tools (NinjaOne, etc.) successfully collect BitLocker data automatically

## Solution Architecture

### Windows Service with SYSTEM Privileges

The solution implements a **Windows Service wrapper** that:

1. **Runs with LocalSystem account** (SYSTEM privileges)
2. **Automatically starts** with Windows boot
3. **Requires no user interaction** or privilege prompts
4. **Provides full BitLocker API access** through SYSTEM account
5. **Enables mass deployment** via GPO, SCCM, or RMM tools

### Key Components

```
LANET Agent Production Deployment
├── Windows Service Wrapper (windows_service.py)
├── Service Installer (install_service.py)
├── Production Deployment Script (deploy_agent_service.ps1)
├── Agent Core (main.py + modules/)
└── BitLocker Collector (modules/bitlocker.py)
```

## Technical Implementation

### 1. Windows Service Wrapper (`lanet_agent/service/windows_service.py`)

**Features:**
- Runs as Windows Service with SYSTEM privileges
- Automatic agent process monitoring and restart
- Comprehensive logging and error handling
- Service lifecycle management (start/stop/restart)

**Key Benefits:**
- **SYSTEM Account**: Full access to BitLocker APIs
- **No User Prompts**: Silent operation in background
- **Automatic Startup**: Starts with Windows boot
- **Process Monitoring**: Restarts agent if it crashes

### 2. Service Installer (`lanet_agent/install_service.py`)

**Features:**
- Automated service installation with proper privileges
- Dependency management (pywin32, psutil, etc.)
- Configuration file creation
- BitLocker access testing

**Installation Process:**
1. Check administrator privileges
2. Install Python dependencies
3. Create installation directory structure
4. Copy agent files
5. Install Windows service with LocalSystem account
6. Configure automatic startup
7. Test BitLocker access

### 3. Production Deployment Script (`deployment/production/deploy_agent_service.ps1`)

**Features:**
- Mass deployment automation
- Silent installation support
- Token-based agent registration
- Comprehensive logging and error handling

**Deployment Capabilities:**
- **GPO Deployment**: Deploy via Group Policy
- **SCCM Integration**: System Center Configuration Manager
- **RMM Tools**: Remote Monitoring and Management platforms
- **Manual Deployment**: Individual computer installation

## Deployment Methods

### Method 1: Individual Computer Installation

```powershell
# Run as Administrator
.\install_service.py

# Or using PowerShell deployment script
.\deploy_agent_service.ps1 -InstallationToken "LANET-CLIENT-SITE-TOKEN"
```

### Method 2: Group Policy Deployment

1. **Create GPO** for agent deployment
2. **Add startup script** with deployment PowerShell
3. **Deploy to target OUs** containing client computers
4. **Automatic installation** on next reboot/login

```powershell
# GPO Startup Script
powershell.exe -ExecutionPolicy Bypass -File "\\server\share\deploy_agent_service.ps1" -InstallationToken "LANET-CLIENT-SITE-TOKEN" -Silent
```

### Method 3: SCCM Deployment

1. **Create SCCM Application** with deployment script
2. **Configure detection rules** for service existence
3. **Deploy to device collections** by client organization
4. **Monitor deployment status** through SCCM console

### Method 4: RMM Tool Deployment

Most RMM tools support PowerShell script execution:

```powershell
# RMM Script Template
param([string]$Token = "LANET-CLIENT-SITE-TOKEN")
Invoke-WebRequest -Uri "https://helpdesk.lanet.mx/downloads/deploy_agent_service.ps1" -OutFile "$env:TEMP\deploy_agent.ps1"
& "$env:TEMP\deploy_agent.ps1" -InstallationToken $Token -Silent
```

## BitLocker Access Verification

### SYSTEM Account Privileges

When running as LocalSystem (SYSTEM account), the service has:

- **Full BitLocker API access** via PowerShell `Get-BitLockerVolume`
- **Recovery key extraction** capabilities
- **Encryption status monitoring**
- **Key protector information** access

### Automatic Data Collection

The service automatically collects:

```json
{
  "supported": true,
  "total_volumes": 1,
  "protected_volumes": 1,
  "volumes": [
    {
      "volume_letter": "C:",
      "volume_label": "Windows-SSD",
      "protection_status": "Protected",
      "encryption_method": "AES-256",
      "encryption_percentage": 100,
      "key_protector_type": "TPM + Recovery Password",
      "recovery_key_id": "8408207F-B330-4818-8B60-5B6C41947562",
      "recovery_key": "190443-417890-133936-228965-700502-251471-531212-335423"
    }
  ]
}
```

## Production Deployment Workflow

### Phase 1: Preparation

1. **Test deployment** on pilot computers
2. **Verify BitLocker access** with test script
3. **Configure deployment tokens** per client/site
4. **Prepare distribution infrastructure**

### Phase 2: Mass Deployment

1. **Deploy via chosen method** (GPO/SCCM/RMM)
2. **Monitor installation progress**
3. **Verify service status** on target computers
4. **Confirm agent registration** in helpdesk system

### Phase 3: Verification

1. **Check service status**: `sc query LANETAgent`
2. **Review service logs**: `C:\Program Files\LANET Agent\logs\`
3. **Verify BitLocker data** in helpdesk dashboard
4. **Monitor ongoing operation**

## Service Management

### Service Commands

```cmd
# Service Status
sc query LANETAgent

# Start Service
sc start LANETAgent

# Stop Service
sc stop LANETAgent

# Service Configuration
sc qc LANETAgent

# Service Logs
type "C:\Program Files\LANET Agent\logs\service.log"
```

### Troubleshooting

**Common Issues:**

1. **Service won't start**
   - Check Python installation
   - Verify file permissions
   - Review service logs

2. **BitLocker access denied**
   - Confirm service runs as LocalSystem
   - Check Windows version compatibility
   - Verify BitLocker is enabled

3. **Agent registration fails**
   - Validate installation token
   - Check network connectivity
   - Review server logs

## Security Considerations

### SYSTEM Account Security

- **Principle of Least Privilege**: Service only accesses required resources
- **Network Isolation**: Agent communicates only with helpdesk server
- **Data Encryption**: All communications use HTTPS/TLS
- **Audit Logging**: Comprehensive logging for security monitoring

### BitLocker Key Protection

- **Encrypted Transmission**: Recovery keys encrypted in transit
- **Secure Storage**: Keys stored with proper access controls
- **Audit Trail**: All key access logged and monitored
- **Compliance**: Meets MSP security requirements

## Testing and Validation

### Pre-Deployment Testing

```bash
# Test BitLocker access
python test_service_bitlocker.py

# Test service installation
python lanet_agent/install_service.py

# Test deployment script
.\deploy_agent_service.ps1 -InstallationToken "TEST-TOKEN" -Silent
```

### Production Validation

1. **Pilot Deployment**: Test on 10-20 computers first
2. **BitLocker Verification**: Confirm data collection works
3. **Performance Testing**: Monitor system impact
4. **Rollback Plan**: Prepare service removal procedures

## Conclusion

This production deployment solution enables:

- ✅ **Automatic BitLocker data collection** without user intervention
- ✅ **Mass deployment** across 2000+ client computers
- ✅ **SYSTEM privileges** for full BitLocker API access
- ✅ **Silent operation** with no user prompts
- ✅ **Enterprise-grade reliability** with automatic restart
- ✅ **Comprehensive logging** for monitoring and troubleshooting

The solution matches the capabilities of commercial MSP tools like NinjaOne while providing the customization and control required for LANET Helpdesk operations.
