# LANET Agent Installer - Deployment Instructions

## 📋 Overview
This is a standalone executable installer for the LANET Helpdesk Agent.
No additional software or dependencies are required on target computers.

## 🚀 Deployment Instructions

### For Technicians:
1. **Copy** `LANET_Agent_Installer.exe` to the target computer
2. **Right-click** the installer and select "Run as administrator"
3. **Choose installation mode**:
   - **Quick Install**: Uses default settings (recommended for mass deployment)
   - **Custom Install**: Allows token and server configuration
4. **Click "Install LANET Agent"** and wait for completion
5. **Verify** the installation was successful

### Installation Modes:

#### Quick Install (Recommended)
- Uses pre-configured settings
- Minimal user interaction
- Ideal for mass deployment across multiple computers
- Uses default test token for immediate functionality

#### Custom Install
- Allows server URL configuration
- Requires valid installation token
- Real-time token validation
- Shows client and site information

## ✅ Success Indicators
After successful installation:
- Windows service "LANETAgent" is running
- Computer appears in helpdesk within 5-10 minutes
- Complete hardware and software inventory collected
- BitLocker data available (if BitLocker is enabled)

## 🔧 Technical Details
- **Service Name**: LANETAgent
- **Service Account**: LocalSystem (SYSTEM privileges)
- **Installation Path**: C:\Program Files\LANET Agent
- **Logs**: C:\ProgramData\LANET Agent\Logs
- **Auto-Start**: Enabled (starts on system boot)

## 🆘 Troubleshooting
- Ensure installer is run as administrator
- Check Windows Event Log for service errors
- Review installation logs in temp directory
- Verify network connectivity to helpdesk server

## 📞 Support
For technical support, contact the IT department with:
- Computer name and IP address
- Installation log files
- Error messages (if any)
