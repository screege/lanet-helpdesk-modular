# LANET AGENT - TECHNICIAN QUICK START GUIDE

## 🚀 ONE-CLICK INSTALLATION (2 MINUTES)

### **Step 1: Copy Files**
Copy the `enterprise_deployment` folder to the target computer

### **Step 2: Double-Click Install**
**Double-click** `Install_LANET_Agent.bat`
- ✅ **No right-click needed** - automatic administrator elevation
- ✅ **GUI installer opens** automatically

### **Step 3: Enter Information**
In the GUI installer:
1. **Server URL:** Enter helpdesk server URL (e.g., `https://helpdesk.company.com/api`)
2. **Token:** Enter installation token (format: `LANET-CLIENT-SITE-TOKEN`)
3. **Click "Validate Token"** - shows client and site information
4. **Click "Install LANET Agent Service"** - automatic installation

### **Step 4: Verify Success**
Look for **"Installation Successful!"** message with:
- ✅ Service Status: Running
- ✅ BitLocker access enabled
- ✅ Client and site information confirmed

## 📋 WHAT THE AGENT COLLECTS

- **💻 Hardware:** CPU, RAM, disks, motherboard, BIOS
- **📦 Software:** Complete list of installed programs
- **🔐 BitLocker:** Recovery keys and encryption status (requires SYSTEM privileges)
- **📊 Metrics:** CPU usage, memory, disk space, network status
- **🔄 Real-time:** Continuous monitoring with 5-minute heartbeats

## 🔧 TROUBLESHOOTING

### **"Token validation failed"**
- ✅ Check server URL is correct
- ✅ Verify network connectivity
- ✅ Confirm token is valid and not expired

### **"Python not found"**
- ✅ Install Python 3.10+ from python.org
- ✅ Add Python to system PATH during installation
- ✅ Restart installer after Python installation

### **"Service won't start"**
- ✅ Check installation logs: `C:\ProgramData\LANET Agent\Logs\installation.log`
- ✅ Verify Python is properly installed
- ✅ Ensure no antivirus blocking

### **"Computer doesn't appear in helpdesk"**
- ✅ Wait 5-10 minutes for initial registration
- ✅ Check service is running: `Get-Service LANETAgent`
- ✅ Verify network connectivity to server

## ✅ VERIFICATION CHECKLIST

After installation, verify:

- [ ] Service "LANETAgent" shows as "Running"
- [ ] Computer appears in helpdesk system within 10 minutes
- [ ] Hardware data is populated
- [ ] Software list is complete
- [ ] BitLocker data shows (if BitLocker is enabled)
- [ ] System metrics are updating

## 🔍 QUICK COMMANDS

**Check service status:**
```cmd
sc query LANETAgent
```

**View service logs:**
```cmd
type "C:\ProgramData\LANET Agent\Logs\service.log"
```

**Restart service if needed:**
```cmd
sc stop LANETAgent
sc start LANETAgent
```

**Verify installation:**
```powershell
Get-Service -Name LANETAgent
```

## 🏢 ENTERPRISE FEATURES

### **Automatic Service Installation:**
- ✅ Runs as Windows Service with SYSTEM privileges
- ✅ Auto-starts on system boot
- ✅ Runs continuously in background
- ✅ No user interaction required after installation

### **BitLocker Support:**
- ✅ Collects recovery keys automatically
- ✅ Reports encryption status
- ✅ Works with all BitLocker-enabled drives
- ✅ Requires SYSTEM privileges (automatically configured)

### **Professional Installation:**
- ✅ GUI installer with token validation
- ✅ Real-time server connectivity testing
- ✅ Shows client and site information before installation
- ✅ Progress bar with detailed status updates
- ✅ Comprehensive error handling and logging

## 📞 ESCALATION

**If installation fails after troubleshooting:**

1. **Collect Information:**
   - Installation log: `C:\ProgramData\LANET Agent\Logs\installation.log`
   - Service log: `C:\ProgramData\LANET Agent\Logs\service.log`
   - Exact error message from GUI
   - System specifications (OS version, Python version)

2. **Document Issue:**
   - Computer name and location
   - Installation token used
   - Server URL used
   - Network configuration (proxy, firewall)

3. **Contact Support:**
   - Provide collected logs and information
   - Include screenshots of error messages
   - Specify if this is first installation or upgrade

## 🎯 SUCCESS INDICATORS

**Installation Successful When:**
- ✅ GUI shows "Installation Successful!" message
- ✅ Service status shows "Running"
- ✅ Computer appears in helpdesk within 10 minutes
- ✅ All data types are being collected (hardware, software, BitLocker)
- ✅ Regular heartbeats are being sent

**Expected Timeline:**
- **Installation:** 2-3 minutes
- **Service Start:** 30 seconds
- **First Registration:** 1-2 minutes
- **Data Collection:** 3-5 minutes
- **Helpdesk Appearance:** 5-10 minutes

---

**For detailed technical information, see ENTERPRISE_DEPLOYMENT_GUIDE.md**

**Quick Reference Version:** 3.0.0  
**Agent Version:** 3.0.0 Enterprise
