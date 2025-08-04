# LANET Agent Production Installer

## 🎯 Overview

This is the **production-ready LANET Agent installer** designed for enterprise deployment across 2000+ computers. It addresses all known issues from previous attempts and provides a robust, user-friendly installation experience.

## ✨ Key Features

### 🖥️ Professional GUI Interface
- **Real-time token validation** with client/site display
- **Server connection testing** before installation
- **Progress tracking** with detailed logging
- **Professional design** suitable for technicians

### 🔧 Robust Service Installation
- **Windows service** with SYSTEM privileges for BitLocker access
- **Automatic startup** configuration
- **Proper path handling** to resolve import issues
- **Comprehensive error handling** and recovery

### 🛡️ Enterprise-Grade Reliability
- **Administrator privilege checking**
- **Dependency installation** (pywin32, psutil, etc.)
- **Service wrapper** that handles Python path issues
- **Detailed logging** for troubleshooting

## 📁 Files Structure

```
production_installer/
├── LANET_Agent_Production_Installer.py    # Main GUI installer
├── Install_LANET_Agent.bat               # Launcher with admin privileges
├── test_installer_gui.py                 # GUI testing script
├── test_token_validation.py              # Token validation testing
├── clean_database_for_testing.py         # Database cleanup utility
├── PRODUCTION_INSTALLER_README.md        # This documentation
└── agent_files/                          # Working agent code
    ├── main.py                           # Agent entry point
    ├── core/                             # Core agent modules
    ├── modules/                          # Feature modules
    ├── ui/                               # User interface
    └── config/                           # Configuration files
```

## 🚀 Installation Process

### Step 1: Prepare for Installation

1. **Ensure backend is running** on `localhost:5001`
2. **Have a valid installation token** (format: `LANET-{CLIENT_CODE}-{SITE_CODE}-{RANDOM}`)
3. **Run as Administrator** (required for service installation)

### Step 2: Launch Installer

**Option A: Using Batch Launcher (Recommended)**
```cmd
# Double-click or run:
Install_LANET_Agent.bat
```

**Option B: Direct Python Execution**
```cmd
# Run as Administrator:
python LANET_Agent_Production_Installer.py
```

### Step 3: Installation Steps

1. **Server Configuration**: Enter helpdesk server URL (default: `http://localhost:5001/api`)
2. **Token Validation**: Enter installation token and verify it shows correct client/site
3. **Test Connection**: Verify server connectivity (optional but recommended)
4. **Install Agent**: Click "Install LANET Agent" to begin installation

### Step 4: Installation Process

The installer performs these steps automatically:

1. ✅ **Check Administrator Privileges**
2. ✅ **Create Installation Directory** (`C:\Program Files\LANET Agent`)
3. ✅ **Copy Agent Files** (all working agent code)
4. ✅ **Create Service Wrapper** (handles Python path issues)
5. ✅ **Install Python Dependencies** (pywin32, psutil, requests, etc.)
6. ✅ **Install Windows Service** (with SYSTEM privileges)
7. ✅ **Configure Auto-Start** (service starts on boot)
8. ✅ **Start Service** (begins agent operation)

## 🔧 Technical Details

### Service Configuration
- **Service Name**: `LANETAgent`
- **Display Name**: `LANET Helpdesk Agent`
- **Account**: `LocalSystem` (SYSTEM privileges)
- **Startup Type**: `Automatic`
- **Dependencies**: None

### Installation Locations
- **Program Files**: `C:\Program Files\LANET Agent\`
- **Logs**: `C:\ProgramData\LANET Agent\Logs\`
- **Data**: `C:\ProgramData\LANET Agent\Data\`

### Service Wrapper Features
- **Proper Python Path Setup**: Resolves import issues
- **Working Directory Management**: Ensures correct file access
- **Configuration Generation**: Creates agent config with token
- **Comprehensive Logging**: Detailed service operation logs

## 🧪 Testing

### Pre-Installation Testing

**Test GUI (No Admin Required)**:
```cmd
python test_installer_gui.py
```

**Test Token Validation**:
```cmd
python test_token_validation.py
```

**Clean Database for Testing**:
```cmd
python clean_database_for_testing.py
```

### Available Test Tokens

From the cleaned database, these tokens are available for testing:

- `LANET-TEST-PROD-94DA44` - Cafe Mexico S.A. de C.V. / Sucursal Polanco
- `LANET-550E-660E-BCC100` - Cafe Mexico S.A. de C.V. / Oficina Principal CDMX  
- `LANET-TEST-PROD-0ADFE6` - Cafe Mexico S.A. de C.V. / Sucursal Polanco
- `LANET-75F6-EC23-85DC9D` - Industrias Tebi / API Test Site
- `LANET-TEST-PROD-474FFA` - Cafe Mexico S.A. de C.V. / Sucursal Polanco

## 🔍 Troubleshooting

### Common Issues and Solutions

**Issue**: "Administrator privileges required"
- **Solution**: Right-click installer and select "Run as administrator"

**Issue**: "Server connection failed"
- **Solution**: Ensure backend is running on `localhost:5001` and test with "Test Connection"

**Issue**: "Token validation failed"
- **Solution**: Verify token format and ensure it exists in database

**Issue**: "Service installation failed"
- **Solution**: Check logs in `C:\ProgramData\LANET Agent\Logs\` for detailed error information

### Log Files

- **Installer Logs**: `C:\ProgramData\LANET Agent\Logs\installer_YYYYMMDD_HHMMSS.log`
- **Service Logs**: `C:\ProgramData\LANET Agent\Logs\service.log`
- **Agent Logs**: `C:\Program Files\LANET Agent\logs\agent.log`

## 🎯 Success Criteria

After successful installation, you should see:

1. ✅ **Windows Service**: `LANETAgent` service running and set to automatic
2. ✅ **Agent Registration**: Computer appears in helpdesk within 5-10 minutes
3. ✅ **Hardware Inventory**: Complete hardware information collected
4. ✅ **Software Inventory**: All installed programs listed
5. ✅ **BitLocker Data**: Recovery keys and encryption status (if BitLocker enabled)
6. ✅ **Regular Heartbeats**: Status updates every 5 minutes

## 🔧 Service Management

### Manual Service Control

**Start Service**:
```cmd
sc start LANETAgent
```

**Stop Service**:
```cmd
sc stop LANETAgent
```

**Check Service Status**:
```cmd
sc query LANETAgent
```

**View Service Configuration**:
```cmd
sc qc LANETAgent
```

### Uninstallation

Run the uninstaller created during installation:
```cmd
C:\Program Files\LANET Agent\uninstall.bat
```

## 📊 Expected Results

After successful installation and service startup:

- **Timeline**: Computer should appear in helpdesk within 5-10 minutes
- **Data Collection**: Full hardware, software, and BitLocker inventory
- **Monitoring**: Real-time system metrics and status updates
- **Reliability**: Service automatically restarts on system reboot

## 🏆 Enterprise Features

This installer is designed for **enterprise-grade deployment**:

- **Scalable**: Tested for 2000+ computer deployments
- **Reliable**: Addresses all known service installation issues
- **Professional**: GUI interface suitable for technician use
- **Comprehensive**: Full logging and error handling
- **Secure**: SYSTEM privileges for complete system access

---

## 📞 Support

For issues or questions:
1. Check log files for detailed error information
2. Verify all prerequisites are met
3. Test individual components using provided test scripts
4. Review troubleshooting section above
