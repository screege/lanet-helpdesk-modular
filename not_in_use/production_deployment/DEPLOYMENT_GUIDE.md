# LANET HELPDESK AGENT - ENTERPRISE DEPLOYMENT GUIDE

## 📋 OVERVIEW

This guide provides comprehensive instructions for deploying the LANET Helpdesk Agent to 2000+ client computers in an enterprise environment.

## 🎯 AGENT SPECIFICATIONS

### **Working Agent Details:**
- **File Path:** `C:\lanet-helpdesk-v3\production_installer\agent_files\main.py`
- **Version:** 2.0.0 Production
- **Status:** ✅ FULLY FUNCTIONAL
- **Capabilities:**
  - ✅ Hardware inventory collection
  - ✅ Software inventory collection (complete program list)
  - ✅ BitLocker data collection (requires SYSTEM privileges)
  - ✅ Automatic registration with token
  - ✅ Regular heartbeat transmission
  - ✅ Real-time system monitoring

### **Technical Requirements:**
- **Operating System:** Windows 10/11, Windows Server 2016+
- **Python:** 3.10 or higher (must be in system PATH)
- **Privileges:** Must run as Windows Service with SYSTEM account
- **Network:** HTTP/HTTPS access to helpdesk server
- **Disk Space:** ~50MB for installation
- **Memory:** ~100MB RAM usage

## 📦 DEPLOYMENT PACKAGE CONTENTS

```
production_deployment/
├── LANET_Agent_Enterprise_Installer.bat     # Batch installer (Windows compatibility)
├── LANET_Agent_Enterprise_Installer.ps1     # PowerShell installer (enhanced features)
├── Deploy_LANET_Agent_Silent.bat           # Silent mass deployment script
├── DEPLOYMENT_GUIDE.md                     # This documentation
├── TECHNICIAN_INSTRUCTIONS.md              # Quick reference for technicians
└── agent_files/                            # Agent source files (copy from production_installer/)
    ├── main.py                             # Main agent executable
    ├── modules/                            # Agent modules
    ├── core/                               # Core functionality
    └── config/                             # Configuration templates
```

## 🚀 DEPLOYMENT METHODS

### **Method 1: Interactive Installation (Technician Use)**

**For individual computer installation by technicians:**

1. **Copy deployment package** to target computer
2. **Right-click** on `LANET_Agent_Enterprise_Installer.bat`
3. **Select "Run as administrator"**
4. **Follow on-screen prompts**
5. **Verify installation** when complete

**Command line options:**
```batch
LANET_Agent_Enterprise_Installer.bat --token LANET-CLIENT-SITE-TOKEN --server https://helpdesk.company.com/api
```

### **Method 2: Silent Mass Deployment**

**For Group Policy, SCCM, or automated deployment:**

1. **Customize deployment script:**
   ```batch
   # Edit Deploy_LANET_Agent_Silent.bat
   set "DEPLOYMENT_TOKEN=LANET-CLIENT-SITE-TOKEN"
   set "HELPDESK_SERVER=https://helpdesk.company.com/api"
   ```

2. **Deploy via Group Policy:**
   - Computer Configuration → Policies → Windows Settings → Scripts
   - Add `Deploy_LANET_Agent_Silent.bat` as startup script

3. **Deploy via SCCM:**
   - Create package with deployment files
   - Set command line: `Deploy_LANET_Agent_Silent.bat`
   - Configure to run with administrative rights

4. **Deploy via PowerShell remoting:**
   ```powershell
   Invoke-Command -ComputerName $computers -ScriptBlock {
       & "\\server\share\Deploy_LANET_Agent_Silent.bat"
   }
   ```

### **Method 3: PowerShell Advanced Deployment**

**For PowerShell-enabled environments:**

```powershell
# Single computer
.\LANET_Agent_Enterprise_Installer.ps1 -Token "LANET-CLIENT-SITE-TOKEN" -ServerUrl "https://helpdesk.company.com/api" -Silent

# Multiple computers
$computers = Get-Content "computers.txt"
foreach ($computer in $computers) {
    Invoke-Command -ComputerName $computer -FilePath ".\LANET_Agent_Enterprise_Installer.ps1" -ArgumentList "-Token", "LANET-CLIENT-SITE-TOKEN", "-Silent"
}
```

## 🔧 INSTALLATION PROCESS

### **What the installer does:**

1. **Privilege Check:** Verifies administrator privileges
2. **BitLocker Test:** Tests BitLocker access capabilities
3. **Cleanup:** Removes any existing installation
4. **File Copy:** Installs agent files to `C:\Program Files\LANET Agent`
5. **Service Creation:** Creates Windows service with SYSTEM privileges
6. **Configuration:** Sets up agent configuration with provided token
7. **Service Start:** Starts the service and verifies operation
8. **Logging:** Creates detailed logs for troubleshooting

### **Installation Locations:**
- **Program Files:** `C:\Program Files\LANET Agent\`
- **Logs:** `C:\ProgramData\LANET Agent\Logs\`
- **Service Name:** `LANETAgent`
- **Service Account:** `LocalSystem` (required for BitLocker access)

## ✅ VERIFICATION STEPS

### **Verify Successful Installation:**

1. **Check Service Status:**
   ```cmd
   sc query LANETAgent
   ```
   Should show: `STATE: 4 RUNNING`

2. **Check Service Logs:**
   ```cmd
   type "C:\ProgramData\LANET Agent\Logs\service.log"
   ```
   Look for: "Agent registration successful" and "BitLocker access confirmed"

3. **Verify in Helpdesk System:**
   - Log into helpdesk web interface
   - Navigate to Assets/Equipment section
   - Confirm computer appears with complete data:
     - Hardware specifications
     - Software inventory
     - BitLocker status (if enabled)

### **PowerShell Verification:**
```powershell
# Quick verification script
.\LANET_Agent_Enterprise_Installer.ps1 -Verify
```

## 🔍 TROUBLESHOOTING

### **Common Issues:**

1. **Service won't start:**
   - Check Python installation and PATH
   - Verify administrator privileges
   - Review installation logs

2. **BitLocker data missing:**
   - Confirm service runs as SYSTEM account
   - Check BitLocker is enabled on target system
   - Verify no group policy restrictions

3. **Agent not appearing in helpdesk:**
   - Verify network connectivity to server
   - Check token validity
   - Review agent registration logs

### **Log Locations:**
- **Installation:** `C:\ProgramData\LANET Agent\Logs\installation.log`
- **Service:** `C:\ProgramData\LANET Agent\Logs\service.log`
- **Deployment:** `C:\Windows\Temp\LANET_Agent_Deployment.log`

## 📊 MASS DEPLOYMENT CHECKLIST

### **Pre-Deployment:**
- [ ] Test installation on representative systems
- [ ] Verify network connectivity to helpdesk server
- [ ] Confirm Python 3.10+ available on target systems
- [ ] Prepare deployment tokens for each client/site
- [ ] Test BitLocker access on encrypted systems

### **During Deployment:**
- [ ] Monitor deployment logs for errors
- [ ] Verify service installation on sample systems
- [ ] Check helpdesk system for new agent registrations
- [ ] Validate BitLocker data collection on encrypted systems

### **Post-Deployment:**
- [ ] Confirm all systems appear in helpdesk
- [ ] Verify regular heartbeat transmission
- [ ] Test inventory data accuracy
- [ ] Document any systems requiring manual intervention

## 🔐 SECURITY CONSIDERATIONS

- **Service Account:** Runs as SYSTEM for BitLocker access
- **Network Traffic:** Uses HTTPS for secure communication
- **Data Protection:** BitLocker keys encrypted in transit and storage
- **Access Control:** Agent registration requires valid tokens
- **Logging:** Sensitive data excluded from logs

## 📞 SUPPORT

For deployment issues or questions:
- Review troubleshooting section above
- Check log files for specific error messages
- Contact system administrator for network/policy issues
- Escalate to development team for agent functionality issues

---

**Document Version:** 1.0
**Last Updated:** 2024-01-15
**Agent Version:** 2.0.0 Production
