# LANET HELPDESK AGENT - ENTERPRISE DEPLOYMENT GUIDE v3.0

## 🏢 OVERVIEW

This enterprise deployment solution provides professional-grade installation tools comparable to industry leaders like **NinjaOne**, **GLPI**, and **Zabbix**. The solution includes GUI-based installers with token validation, silent deployment scripts, and mass deployment tools for enterprise environments.

## 📦 DEPLOYMENT PACKAGE CONTENTS

```
enterprise_deployment/
├── Install_LANET_Agent.bat                    # One-click installer for technicians
├── LANET_Agent_Professional_Installer.ps1     # GUI installer with token validation
├── LANET_Agent_Silent_Enterprise.ps1          # Silent deployment script
├── Deploy_Mass_Installation.ps1               # Mass deployment tool
├── ENTERPRISE_DEPLOYMENT_GUIDE.md             # This documentation
└── TECHNICIAN_QUICK_START.md                  # Quick reference guide
```

## 🎯 DEPLOYMENT METHODS

### **Method 1: One-Click Installation (Recommended for Technicians)**

**Perfect for field technicians - Single double-click execution:**

1. **Copy deployment package** to target computer
2. **Double-click** `Install_LANET_Agent.bat`
3. **Automatic administrator elevation** (no manual right-click needed)
4. **GUI installer opens** with token validation
5. **Complete installation** in 2-3 minutes

**Features:**
- ✅ Automatic administrator privilege elevation
- ✅ GUI interface with real-time token validation
- ✅ Shows client and site information before installation
- ✅ Progress bar with detailed status updates
- ✅ Automatic Windows service installation with SYSTEM privileges
- ✅ BitLocker access verification
- ✅ Installation success confirmation

### **Method 2: Silent Enterprise Deployment**

**For automated deployment via Group Policy, SCCM, or scripting:**

```powershell
# Single computer deployment
.\LANET_Agent_Silent_Enterprise.ps1 -Token "LANET-CLIENT-SITE-TOKEN" -ServerUrl "https://helpdesk.company.com/api"

# With additional options
.\LANET_Agent_Silent_Enterprise.ps1 -Token "LANET-CLIENT-SITE-TOKEN" -ServerUrl "https://helpdesk.company.com/api" -Force -Verify
```

**Command Line Options:**
- `-Token`: Installation token (required)
- `-ServerUrl`: Helpdesk server API URL (required)
- `-Force`: Force reinstallation over existing installation
- `-Verify`: Verify existing installation
- `-Uninstall`: Remove existing installation

### **Method 3: Mass Deployment**

**For deploying to 100+ computers simultaneously:**

1. **Configure** `Deploy_Mass_Installation.ps1`:
   ```powershell
   $DeploymentConfig = @{
       ServerUrl = "https://helpdesk.company.com/api"
       DefaultToken = "LANET-CLIENT-SITE-TOKEN"
       TargetComputers = @("PC001", "PC002", "PC003")
       MaxConcurrentJobs = 10
   }
   ```

2. **Execute** mass deployment:
   ```powershell
   .\Deploy_Mass_Installation.ps1
   ```

3. **Monitor** progress and view detailed logs

## 🔧 TECHNICAL SPECIFICATIONS

### **Windows Service Configuration:**
- **Service Name:** `LANETAgent`
- **Display Name:** `LANET Helpdesk Agent`
- **Account:** `LocalSystem` (SYSTEM privileges)
- **Startup Type:** `Automatic`
- **Dependencies:** None

### **Installation Locations:**
- **Program Files:** `C:\Program Files\LANET Agent\`
- **Configuration:** `C:\Program Files\LANET Agent\config\agent_config.json`
- **Logs:** `C:\ProgramData\LANET Agent\Logs\`
- **Service Wrapper:** `C:\Program Files\LANET Agent\service_wrapper.py`

### **System Requirements:**
- **OS:** Windows 10/11, Windows Server 2016+
- **Python:** 3.10+ (must be in system PATH)
- **Privileges:** Administrator (for installation only)
- **Network:** HTTP/HTTPS access to helpdesk server
- **Disk Space:** ~50MB

### **BitLocker Support:**
- **SYSTEM Privileges:** Required for BitLocker access
- **Recovery Keys:** Automatically collected and transmitted
- **Encryption Status:** Real-time monitoring
- **Volume Detection:** All BitLocker-enabled drives

## 🚀 INSTALLATION PROCESS

### **Automated Installation Steps:**

1. **Privilege Verification:** Confirms administrator privileges
2. **Token Validation:** Validates token with server and shows client/site info
3. **BitLocker Testing:** Tests BitLocker access capabilities
4. **Cleanup:** Removes any existing installation
5. **File Installation:** Copies agent files to program directory
6. **Service Creation:** Creates Windows service with SYSTEM privileges
7. **Configuration:** Generates service configuration with validated token
8. **Service Start:** Starts service and verifies operation
9. **Verification:** Confirms successful installation and service status

### **What Gets Installed:**

```
C:\Program Files\LANET Agent\
├── main.py                    # Main agent executable
├── modules\                   # Agent modules (BitLocker, monitoring, etc.)
├── core\                      # Core functionality
├── config\                    # Configuration files
└── service_wrapper.py         # Windows service wrapper

C:\ProgramData\LANET Agent\Logs\
├── installation.log           # Installation logs
├── service.log               # Service runtime logs
└── silent_installation.log   # Silent deployment logs
```

## ✅ VERIFICATION AND TROUBLESHOOTING

### **Verify Successful Installation:**

**Method 1: Service Status**
```cmd
sc query LANETAgent
```
Expected: `STATE: 4 RUNNING`

**Method 2: PowerShell Verification**
```powershell
Get-Service -Name LANETAgent
```
Expected: `Status: Running`

**Method 3: Automated Verification**
```powershell
.\LANET_Agent_Silent_Enterprise.ps1 -Verify
```

### **Check Installation Logs:**
```powershell
# Installation logs
Get-Content "C:\ProgramData\LANET Agent\Logs\installation.log" -Tail 20

# Service logs
Get-Content "C:\ProgramData\LANET Agent\Logs\service.log" -Tail 20
```

### **Common Issues and Solutions:**

| Issue | Cause | Solution |
|-------|-------|----------|
| "Administrator privileges required" | Not running as admin | Right-click installer → "Run as administrator" |
| "Python not found" | Python not in PATH | Install Python 3.10+ and add to system PATH |
| "Token validation failed" | Invalid token or server URL | Verify token and server connectivity |
| "Service won't start" | Missing dependencies | Check Python installation and agent files |
| "BitLocker data missing" | Service not running as SYSTEM | Verify service account is LocalSystem |

## 🔐 SECURITY FEATURES

### **Enterprise Security Standards:**
- **SYSTEM Privileges:** Service runs with LocalSystem account for BitLocker access
- **Token Validation:** Real-time token verification with server
- **Encrypted Communication:** HTTPS support for secure data transmission
- **Access Control:** Agent registration requires valid tokens
- **Audit Logging:** Comprehensive installation and runtime logging
- **Data Protection:** BitLocker keys encrypted in transit and storage

### **Network Security:**
- **Firewall Friendly:** Uses standard HTTP/HTTPS ports
- **Proxy Support:** Compatible with corporate proxy servers
- **Certificate Validation:** Supports SSL certificate verification
- **Rate Limiting:** Built-in request throttling

## 📊 MASS DEPLOYMENT BEST PRACTICES

### **Pre-Deployment Checklist:**
- [ ] Test installation on representative systems
- [ ] Verify network connectivity to helpdesk server
- [ ] Confirm Python 3.10+ available on target systems
- [ ] Prepare deployment tokens for each client/site
- [ ] Test BitLocker access on encrypted systems
- [ ] Configure deployment scripts with correct parameters

### **Deployment Strategies:**

**Group Policy Deployment:**
1. Copy deployment package to SYSVOL share
2. Create GPO with startup script
3. Link GPO to target OUs
4. Monitor deployment through event logs

**SCCM Deployment:**
1. Create SCCM package with deployment files
2. Set command line: `Install_LANET_Agent.bat`
3. Configure to run with administrative rights
4. Deploy to target collections

**PowerShell Remoting:**
```powershell
$computers = Get-Content "computers.txt"
foreach ($computer in $computers) {
    Invoke-Command -ComputerName $computer -FilePath ".\LANET_Agent_Silent_Enterprise.ps1" -ArgumentList "-Token", "LANET-TOKEN", "-ServerUrl", "https://helpdesk.company.com/api"
}
```

### **Monitoring Deployment:**
- **Real-time Logs:** Monitor deployment logs in real-time
- **Service Verification:** Automated service status checking
- **Helpdesk Integration:** Verify agent registration in helpdesk system
- **Error Reporting:** Centralized error collection and reporting

## 🎉 EXPECTED RESULTS

### **After Successful Deployment:**

**In Helpdesk System (within 5-10 minutes):**
- ✅ Computer appears in assets/equipment list
- ✅ Complete hardware inventory (CPU, RAM, disks, etc.)
- ✅ Full software inventory (all installed programs)
- ✅ BitLocker data (encryption status and recovery keys)
- ✅ Real-time system metrics
- ✅ Regular heartbeat signals

**On Target Computer:**
- ✅ Windows service running as SYSTEM
- ✅ Automatic startup configured
- ✅ BitLocker data collection active
- ✅ Continuous monitoring enabled
- ✅ Detailed logging for troubleshooting

## 📞 SUPPORT AND MAINTENANCE

### **Maintenance Tasks:**
- **Log Rotation:** Logs automatically managed by service
- **Updates:** Deploy new versions using same installation process
- **Monitoring:** Service status monitoring via helpdesk system
- **Troubleshooting:** Comprehensive logging for issue resolution

### **Support Resources:**
- **Installation Logs:** Detailed installation process logging
- **Service Logs:** Runtime operation and error logging
- **Event Logs:** Windows Event Log integration
- **Remote Diagnostics:** Built-in diagnostic capabilities

---

**Document Version:** 3.0.0  
**Last Updated:** 2024-01-15  
**Agent Version:** 3.0.0 Enterprise  
**Compatibility:** Windows 10/11, Windows Server 2016+
