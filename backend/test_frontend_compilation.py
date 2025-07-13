#!/usr/bin/env python3
"""
Test frontend compilation and basic functionality
"""

import requests
import time

def test_frontend_compilation():
    """Test that frontend compiles and loads properly"""
    print("🔍 TESTING FRONTEND COMPILATION")
    print("=" * 50)
    
    try:
        # Test frontend accessibility
        print("📱 Testing frontend accessibility...")
        response = requests.get('http://localhost:5173', timeout=10)
        
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            
            # Check for common compilation errors in response
            content = response.text.lower()
            
            error_indicators = [
                'identifier',
                'already been declared',
                'duplicate',
                'syntax error',
                'compilation error'
            ]
            
            has_errors = any(error in content for error in error_indicators)
            
            if has_errors:
                print("⚠️ Potential compilation errors detected in frontend")
                for indicator in error_indicators:
                    if indicator in content:
                        print(f"  - Found: {indicator}")
            else:
                print("✅ No obvious compilation errors detected")
                
            # Check if React is loading properly
            if 'react' in content or 'root' in content:
                print("✅ React appears to be loading")
            else:
                print("⚠️ React may not be loading properly")
                
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing frontend: {e}")
    
    # Test API accessibility
    print(f"\n🔌 Testing API accessibility...")
    try:
        api_response = requests.get('http://localhost:5001/health', timeout=5)
        if api_response.status_code == 200:
            print("✅ API is accessible")
        else:
            print(f"⚠️ API returned: {api_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ API not accessible: {e}")

if __name__ == "__main__":
    test_frontend_compilation()
