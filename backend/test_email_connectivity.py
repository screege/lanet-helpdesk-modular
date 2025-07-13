#!/usr/bin/env python3
"""
Test email connectivity from Docker container
"""
import os
import smtplib
import imaplib
import socket
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_dns_resolution():
    """Test DNS resolution for mail server"""
    print("🔍 Testing DNS resolution...")
    try:
        host = "mail.compushop.com.mx"
        ip = socket.gethostbyname(host)
        print(f"✅ DNS Resolution: {host} -> {ip}")
        return True
    except Exception as e:
        print(f"❌ DNS Resolution failed: {e}")
        return False

def test_smtp_connection():
    """Test SMTP connection"""
    print("\n📧 Testing SMTP connection...")
    try:
        host = "mail.compushop.com.mx"
        port = 587
        username = "webmaster@compushop.com.mx"
        password = "Iyhnbsfg26"
        
        print(f"Connecting to {host}:{port}...")
        
        # Create SMTP connection
        server = smtplib.SMTP(host, port, timeout=30)
        server.set_debuglevel(1)  # Enable debug output
        
        print("Starting TLS...")
        server.starttls()
        
        print("Logging in...")
        server.login(username, password)
        
        print("✅ SMTP connection successful!")
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return False

def test_imap_connection():
    """Test IMAP connection"""
    print("\n📬 Testing IMAP connection...")
    try:
        host = "mail.compushop.com.mx"
        port = 993
        username = "it@compushop.com.mx"
        password = "Iyhnbsfg26+*"
        
        print(f"Connecting to {host}:{port}...")
        
        # Create IMAP connection
        mail = imaplib.IMAP4_SSL(host, port)
        
        print("Logging in...")
        mail.login(username, password)
        
        print("Selecting INBOX...")
        mail.select('INBOX')
        
        print("✅ IMAP connection successful!")
        mail.logout()
        return True
        
    except Exception as e:
        print(f"❌ IMAP connection failed: {e}")
        return False

def test_port_connectivity():
    """Test port connectivity"""
    print("\n🔌 Testing port connectivity...")
    
    ports_to_test = [
        ("mail.compushop.com.mx", 25, "SMTP"),
        ("mail.compushop.com.mx", 587, "SMTP TLS"),
        ("mail.compushop.com.mx", 465, "SMTP SSL"),
        ("mail.compushop.com.mx", 993, "IMAP SSL"),
        ("mail.compushop.com.mx", 143, "IMAP"),
    ]
    
    for host, port, service in ports_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {service} ({port}): Open")
            else:
                print(f"❌ {service} ({port}): Closed")
                
        except Exception as e:
            print(f"❌ {service} ({port}): Error - {e}")

def send_test_email():
    """Send a test email"""
    print("\n📤 Sending test email...")
    try:
        # Email configuration
        smtp_host = "mail.compushop.com.mx"
        smtp_port = 587
        smtp_username = "webmaster@compushop.com.mx"
        smtp_password = "Iyhnbsfg26"
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = "ba@lanet.mx"
        msg['Subject'] = "Docker Email Test - " + str(os.getpid())
        
        body = f"""
        This is a test email sent from Docker container.
        
        Container ID: {os.environ.get('HOSTNAME', 'unknown')}
        Timestamp: {os.popen('date').read().strip()}
        
        If you receive this email, the email system is working correctly.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        text = msg.as_string()
        server.sendmail(smtp_username, "ba@lanet.mx", text)
        server.quit()
        
        print("✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 DOCKER EMAIL CONNECTIVITY TEST")
    print("=" * 50)
    
    # Test DNS resolution
    dns_ok = test_dns_resolution()
    
    # Test port connectivity
    test_port_connectivity()
    
    # Test SMTP connection
    smtp_ok = test_smtp_connection()
    
    # Test IMAP connection
    imap_ok = test_imap_connection()
    
    # Send test email if SMTP works
    if smtp_ok:
        send_test_email()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"DNS Resolution: {'✅' if dns_ok else '❌'}")
    print(f"SMTP Connection: {'✅' if smtp_ok else '❌'}")
    print(f"IMAP Connection: {'✅' if imap_ok else '❌'}")
    
    if dns_ok and smtp_ok and imap_ok:
        print("\n🎉 All email tests passed! Email should work correctly.")
    else:
        print("\n⚠️ Some email tests failed. Check network configuration.")

if __name__ == "__main__":
    main()
