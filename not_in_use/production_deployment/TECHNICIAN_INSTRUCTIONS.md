# LANET AGENT - TECHNICIAN QUICK REFERENCE

## 🚀 QUICK INSTALLATION (5 MINUTES)

### **Step 1: Copy Files**
Copy the deployment package to the target computer

### **Step 2: Run Installer**
1. **Right-click** `LANET_Agent_Enterprise_Installer.bat`
2. **Select "Run as administrator"**
3. **Wait for completion** (2-3 minutes)

### **Step 3: Verify**
✅ Look for "INSTALLATION SUCCESSFUL!" message  
✅ Service should show as "Running"

## 📋 WHAT THE AGENT COLLECTS

- **Hardware:** CPU, RAM, disks, motherboard, etc.
- **Software:** Complete list of installed programs
- **BitLocker:** Recovery keys and encryption status
- **System Status:** Performance metrics and health

## 🔧 TROUBLESHOOTING

### **Problem: "Administrator privileges required"**
**Solution:** Right-click installer → "Run as administrator"

### **Problem: "Python not found"**
**Solution:** Install Python 3.10+ and add to system PATH

### **Problem: Service won't start**
**Solution:** Check installation log at `C:\ProgramData\LANET Agent\Logs\installation.log`

### **Problem: Computer doesn't appear in helpdesk**
**Solution:** 
1. Check network connectivity
2. Verify token is correct
3. Wait 5-10 minutes for registration

## 📊 VERIFICATION CHECKLIST

After installation, verify these items:

- [ ] Service "LANETAgent" is running
- [ ] Computer appears in helpdesk system within 10 minutes
- [ ] Hardware data is populated
- [ ] Software list is complete
- [ ] BitLocker data shows (if BitLocker is enabled)

## 🔍 QUICK COMMANDS

**Check service status:**
```cmd
sc query LANETAgent
```

**View recent logs:**
```cmd
type "C:\ProgramData\LANET Agent\Logs\service.log"
```

**Restart service:**
```cmd
sc stop LANETAgent
sc start LANETAgent
```

**Uninstall (if needed):**
```powershell
.\LANET_Agent_Enterprise_Installer.ps1 -Uninstall
```

## 📞 ESCALATION

**If installation fails after troubleshooting:**
1. Collect installation log
2. Note exact error message
3. Document system specifications
4. Contact system administrator

---

**For detailed instructions, see DEPLOYMENT_GUIDE.md**
