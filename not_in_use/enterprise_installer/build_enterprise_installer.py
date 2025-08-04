#!/usr/bin/env python3
"""
Build script for LANET Enterprise Installer
Creates standalone executable with embedded Python runtime
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_installer():
    """Build the enterprise installer"""
    print("🚀 Building LANET Enterprise Installer...")
    
    # Get paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    installer_script = script_dir / "lanet_enterprise_installer.py"
    agent_source = project_root / "deployment" / "packages" / "lanet-agent-windows-v2.py"
    
    # Check if agent source exists
    if not agent_source.exists():
        print(f"❌ Agent source not found: {agent_source}")
        return False
    
    # Create dist directory
    dist_dir = script_dir / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # Copy agent file to installer directory for embedding
    agent_dest = script_dir / "lanet_agent.py"
    shutil.copy2(agent_source, agent_dest)
    print(f"✅ Copied agent file: {agent_dest}")
    
    # PyInstaller command - removed --windowed to allow both GUI and console modes
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",  # Allow console output for debugging
        "--name", "LANET_Agent_Enterprise_Installer_v2",
        "--icon", "NONE",
        "--add-data", f"{agent_dest};.",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.scrolledtext",
        "--hidden-import", "requests",
        "--hidden-import", "psutil",
        "--distpath", str(dist_dir),
        "--workpath", str(script_dir / "build"),
        "--specpath", str(script_dir),
        str(installer_script)
    ]
    
    print("🔨 Running PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=script_dir, check=True, capture_output=True, text=True)
        print("✅ PyInstaller completed successfully")
        
        # Check if executable was created
        exe_path = dist_dir / "LANET_Agent_Enterprise_Installer_v2.exe"
        if exe_path.exists():
            print(f"✅ Installer created: {exe_path}")
            print(f"📦 Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
            
            # Test the installer
            print("🧪 Testing installer...")
            test_result = subprocess.run([str(exe_path), "--help"], 
                                       capture_output=True, text=True, timeout=30)
            if test_result.returncode == 0:
                print("✅ Installer test passed")
                return True
            else:
                print(f"❌ Installer test failed: {test_result.stderr}")
                return False
        else:
            print("❌ Installer executable not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False
    finally:
        # Cleanup temporary files
        if agent_dest.exists():
            agent_dest.unlink()

def main():
    """Main entry point"""
    print("LANET Enterprise Installer Builder")
    print("=" * 40)
    
    # Check dependencies
    try:
        import PyInstaller
        print(f"✅ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        return False
    
    # Build installer
    success = build_installer()
    
    if success:
        print("\n🎉 Enterprise installer built successfully!")
        print("\nUsage:")
        print("  GUI Mode: LANET_Agent_Enterprise_Installer.exe")
        print("  Silent Mode: LANET_Agent_Enterprise_Installer.exe --silent --token 'LANET-XXXX-XXXX-XXXXXX'")
        return True
    else:
        print("\n❌ Build failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
