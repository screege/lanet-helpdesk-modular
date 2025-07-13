#!/usr/bin/env python3
"""
Simple email test for Docker
"""
import smtplib
import socket
from email.mime.text import MIMEText

def test_email():
    print("🚀 Testing email from Docker container")
    print("=" * 50)
    
    # Test DNS resolution
    try:
        print("🔍 Testing DNS resolution...")
        ip = socket.gethostbyname("mail.compushop.com.mx")
        print(f"✅ DNS: mail.compushop.com.mx -> {ip}")
    except Exception as e:
        print(f"❌ DNS failed: {e}")
        return
    
    # Test SMTP connection
    try:
        print("📧 Testing SMTP connection...")
        server = smtplib.SMTP("mail.compushop.com.mx", 587, timeout=30)
        print("✅ SMTP connection established")
        
        print("🔐 Starting TLS...")
        server.starttls()
        print("✅ TLS started")
        
        print("🔑 Logging in...")
        server.login("webmaster@compushop.com.mx", "Iyhnbsfg26")
        print("✅ Login successful")
        
        print("📤 Sending test email...")
        msg = MIMEText("Test email from Docker container")
        msg['Subject'] = "Docker Email Test"
        msg['From'] = "webmaster@compushop.com.mx"
        msg['To'] = "ba@lanet.mx"
        
        server.send_message(msg)
        server.quit()
        
        print("✅ Email sent successfully!")
        print("🎉 Email system is working!")
        
    except Exception as e:
        print(f"❌ SMTP failed: {e}")

if __name__ == "__main__":
    test_email()
