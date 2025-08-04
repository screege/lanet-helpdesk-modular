#!/usr/bin/env python3
"""
Simple SMTP Relay for Docker containers using only standard library
"""
import smtpd
import smtplib
import asyncore
import logging
from email.mime.text import MIMEText

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SMTPRelay(smtpd.SMTPServer):
    """Simple SMTP Relay using standard library"""
    
    def __init__(self, localaddr, remoteaddr):
        super().__init__(localaddr, remoteaddr)
        
        # Real SMTP server configuration
        self.real_smtp_host = "mail.compushop.com.mx"
        self.real_smtp_port = 587
        self.real_smtp_username = "webmaster@compushop.com.mx"
        self.real_smtp_password = "Iyhnbsfg26"
        
        logger.info(f"🚀 SMTP Relay started")
        logger.info(f"   Listening on: {localaddr[0]}:{localaddr[1]}")
        logger.info(f"   Forwarding to: {self.real_smtp_host}:{self.real_smtp_port}")
    
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        """Process incoming message and forward to real SMTP server"""
        try:
            logger.info(f"📧 Received email from Docker container")
            logger.info(f"   From: {mailfrom}")
            logger.info(f"   To: {rcpttos}")
            logger.info(f"   Peer: {peer}")
            
            # Forward to real SMTP server
            self.forward_email(mailfrom, rcpttos, data)
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
    
    def forward_email(self, mailfrom, rcpttos, data):
        """Forward email to real SMTP server"""
        try:
            logger.info(f"🔄 Forwarding email to {self.real_smtp_host}...")
            
            # Create SMTP connection to real server
            server = smtplib.SMTP(self.real_smtp_host, self.real_smtp_port, timeout=30)
            server.starttls()
            server.login(self.real_smtp_username, self.real_smtp_password)
            
            # Send the message
            server.sendmail(mailfrom, rcpttos, data)
            server.quit()
            
            logger.info(f"✅ Email forwarded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error forwarding email: {e}")

def main():
    """Main function"""
    print("🚀 Starting Simple SMTP Relay for Docker containers")
    print("=" * 60)
    print("Listening on: 0.0.0.0:587")
    print("Forwarding to: mail.compushop.com.mx:587")
    print("=" * 60)
    print("Press Ctrl+C to stop...")
    print()
    
    try:
        # Create and start relay
        relay = SMTPRelay(('0.0.0.0', 587), None)
        
        # Start the event loop
        asyncore.loop()
        
    except KeyboardInterrupt:
        logger.info("🛑 Stopping SMTP Relay...")
        logger.info("✅ SMTP Relay stopped.")
    except Exception as e:
        logger.error(f"❌ Error starting relay: {e}")

if __name__ == "__main__":
    main()
