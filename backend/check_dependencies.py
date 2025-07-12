#!/usr/bin/env python3
"""
Check all dependencies used in the Excel report functionality
"""

def check_dependencies():
    """Check all required dependencies and their versions"""
    print("🔍 CHECKING EXCEL REPORT DEPENDENCIES")
    print("=" * 50)
    
    required_packages = [
        'openpyxl',
        'pandas', 
        'psycopg2',
        'pytz',
        'flask',
        'reportlab',
        'matplotlib'
    ]
    
    installed_packages = {}
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'psycopg2':
                # psycopg2-binary is the actual package name
                import psycopg2
                installed_packages[package] = psycopg2.__version__
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'Unknown')
                installed_packages[package] = version
            print(f"✅ {package}: {installed_packages[package]}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}: NOT INSTALLED")
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Installed: {len(installed_packages)}")
    print(f"❌ Missing: {len(missing_packages)}")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install " + " ".join(missing_packages))
    else:
        print(f"\n🎉 All required packages are installed!")
    
    # Check specific Excel functionality
    print(f"\n🧪 TESTING EXCEL FUNCTIONALITY:")
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        print("✅ openpyxl imports successful")
        
        import pandas as pd
        print("✅ pandas imports successful")
        
        import psycopg2
        print("✅ psycopg2 imports successful")
        
        print("✅ All Excel report dependencies are working!")
        
    except Exception as e:
        print(f"❌ Error testing functionality: {e}")

if __name__ == "__main__":
    check_dependencies()
