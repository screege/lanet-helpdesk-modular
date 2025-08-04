#!/usr/bin/env python3
"""
SMTP Relay for Docker containers
Forwards emails to the real SMTP server
"""
import asyncio
import smtplib
import logging
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message

# Configure logging
logging.basicConfig(level=logging.INFO)
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
        
    async def handle_message(self, message):
        """Handle incoming message and relay to real SMTP server"""
        try:
            logger.info(f"📧 Relaying email: {message['Subject']}")
            
            # Forward to real SMTP server
            await self.forward_email(message)
            
        except Exception as e:
            logger.error(f"❌ Error relaying email: {e}")
    
    async def forward_email(self, message):
        """Forward email to real SMTP server"""
        try:
            # Create SMTP connection to real server
            server = smtplib.SMTP(self.real_smtp_host, self.real_smtp_port, timeout=30)
            server.starttls()
            server.login(self.real_smtp_username, self.real_smtp_password)
            
            # Send the message
            from_addr = message['From']
            to_addrs = [message['To']]
            
            server.send_message(message, from_addr, to_addrs)
            server.quit()
            
            logger.info(f"✅ Email relayed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error forwarding email: {e}")

def main():
    """Main function"""
    logger.info("🚀 Starting SMTP Relay")
    
    # Create relay handler
    handler = SMTPRelayHandler()
    
    # Create SMTP controller
    controller = Controller(
        handler,
        hostname='0.0.0.0',
        port=1025,
        enable_SMTPUTF8=True
    )
    
    # Start the server
    controller.start()
    
    try:
        logger.info("✅ SMTP Relay started on port 1025")
        
        # Keep running
        asyncio.get_event_loop().run_forever()
        
    except KeyboardInterrupt:
        logger.info("🛑 Stopping SMTP Relay...")
        controller.stop()

if __name__ == "__main__":
    main()
