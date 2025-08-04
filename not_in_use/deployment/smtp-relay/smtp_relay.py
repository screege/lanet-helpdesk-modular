#!/usr/bin/env python3
"""
Simple SMTP Relay for Docker containers
This relay receives emails from Docker containers and forwards them to the real SMTP server
"""
import asyncio
import smtplib
import logging
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SMTPRelayHandler(Message):
    """SMTP Relay Handler"""
    
    def __init__(self):
        super().__init__()
        # Real SMTP server configuration
        self.real_smtp_host = "mail.compushop.com.mx"
        self.real_smtp_port = 587
        self.real_smtp_username = "webmaster@compushop.com.mx"
        self.real_smtp_password = "Iyhnbsfg26"
        self.real_smtp_use_tls = True
        
    async def handle_message(self, message):
        """Handle incoming message and relay to real SMTP server"""
        try:
            logger.info(f"📧 Received email from Docker container")
            logger.info(f"   From: {message['From']}")
            logger.info(f"   To: {message['To']}")
            logger.info(f"   Subject: {message['Subject']}")
            
            # Forward to real SMTP server
            await self.forward_email(message)
            
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
    
    async def forward_email(self, message):
        """Forward email to real SMTP server"""
        try:
            logger.info(f"🔄 Forwarding email to {self.real_smtp_host}...")
            
            # Create SMTP connection to real server
            server = smtplib.SMTP(self.real_smtp_host, self.real_smtp_port, timeout=30)
            
            if self.real_smtp_use_tls:
                server.starttls()
            
            server.login(self.real_smtp_username, self.real_smtp_password)
            
            # Send the message
            from_addr = message['From']
            to_addrs = [message['To']]
            
            server.send_message(message, from_addr, to_addrs)
            server.quit()
            
            logger.info(f"✅ Email forwarded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error forwarding email: {e}")

def main():
    """Main function"""
    logger.info("🚀 Starting SMTP Relay for Docker containers")
    logger.info("=" * 60)
    logger.info(f"Listening on: localhost:587")
    logger.info(f"Forwarding to: mail.compushop.com.mx:587")
    logger.info("=" * 60)
    
    # Create relay handler
    handler = SMTPRelayHandler()
    
    # Create SMTP controller
    controller = Controller(
        handler,
        hostname='0.0.0.0',  # Listen on all interfaces
        port=587,
        enable_SMTPUTF8=True
    )
    
    # Start the server
    controller.start()
    
    try:
        logger.info("✅ SMTP Relay started successfully!")
        logger.info("Press Ctrl+C to stop...")
        
        # Keep running
        while True:
            asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Stopping SMTP Relay...")
        controller.stop()
        logger.info("✅ SMTP Relay stopped.")

if __name__ == "__main__":
    main()
