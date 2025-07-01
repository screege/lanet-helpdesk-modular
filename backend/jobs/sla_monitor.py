#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - SLA Monitor Job
Background job for SLA monitoring, breach detection, and escalation
"""

import time
import logging
from datetime import datetime
from app import create_app

def run_sla_monitor():
    """Main SLA monitoring job"""
    app = create_app()
    
    with app.app_context():
        logger = logging.getLogger('sla_monitor')
        logger.info("Starting SLA monitor job")
        
        try:
            from modules.sla.service import sla_service
            from modules.notifications.service import notifications_service
            from modules.email.service import email_service
            
            # 1. Check for SLA breaches
            logger.info("Checking for SLA breaches...")
            breaches = sla_service.check_sla_breaches()
            
            if breaches:
                logger.warning(f"Found {len(breaches)} SLA breaches")
                
                # Send breach notifications
                for breach in breaches:
                    try:
                        if breach['breach_type'] == 'response':
                            notifications_service.send_sla_breach(
                                breach['ticket_id'], 
                                'response', 
                                0  # Already breached
                            )
                        elif breach['breach_type'] == 'resolution':
                            notifications_service.send_sla_breach(
                                breach['ticket_id'], 
                                'resolution', 
                                0  # Already breached
                            )
                    except Exception as e:
                        logger.error(f"Failed to send breach notification for ticket {breach['ticket_id']}: {e}")
            else:
                logger.info("No SLA breaches found")
            
            # 2. Check for SLA warnings (2 hours before breach)
            logger.info("Checking for SLA warnings...")
            warnings = sla_service.check_sla_warnings(2)
            
            if warnings:
                logger.info(f"Found {len(warnings)} SLA warnings")
                
                # Send warning notifications
                for warning in warnings:
                    try:
                        if warning['warning_type'] == 'response':
                            notifications_service.send_sla_warning(
                                warning['ticket_id'], 
                                'response', 
                                2  # 2 hours remaining
                            )
                        elif warning['warning_type'] == 'resolution':
                            notifications_service.send_sla_warning(
                                warning['ticket_id'], 
                                'resolution', 
                                2  # 2 hours remaining
                            )
                    except Exception as e:
                        logger.error(f"Failed to send warning notification for ticket {warning['ticket_id']}: {e}")
            else:
                logger.info("No SLA warnings found")
            
            # 3. Process escalations
            logger.info("Processing escalations...")
            escalated = sla_service.process_escalations()
            
            if escalated > 0:
                logger.info(f"Escalated {escalated} tickets")
            else:
                logger.info("No tickets escalated")
            
            # 4. Process email queue
            logger.info("Processing email queue...")
            processed_emails = email_service.process_email_queue(20)
            
            if processed_emails > 0:
                logger.info(f"Processed {processed_emails} emails from queue")
            else:
                logger.info("No emails in queue to process")
            
            # 5. Check for incoming emails
            logger.info("Checking for incoming emails...")
            try:
                incoming_emails = email_service.check_incoming_emails()
                
                if incoming_emails:
                    logger.info(f"Found {len(incoming_emails)} incoming emails")
                    
                    # Process each incoming email
                    processed_tickets = 0
                    for email_data in incoming_emails:
                        config = email_service.get_default_config()
                        if config:
                            ticket_id = email_service.process_incoming_email(email_data, config)
                            if ticket_id:
                                processed_tickets += 1
                    
                    logger.info(f"Created/updated {processed_tickets} tickets from incoming emails")
                else:
                    logger.info("No new incoming emails")
                    
            except Exception as e:
                logger.error(f"Error checking incoming emails: {e}")
            
            logger.info("SLA monitor job completed successfully")
            
        except Exception as e:
            logger.error(f"SLA monitor job failed: {e}")
            raise

def run_continuous_monitor(interval_minutes=5):
    """Run SLA monitor continuously"""
    logger = logging.getLogger('sla_monitor')
    logger.info(f"Starting continuous SLA monitor (interval: {interval_minutes} minutes)")
    
    while True:
        try:
            run_sla_monitor()
            logger.info(f"Sleeping for {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)
            
        except KeyboardInterrupt:
            logger.info("SLA monitor stopped by user")
            break
        except Exception as e:
            logger.error(f"SLA monitor error: {e}")
            logger.info(f"Retrying in {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/sla_monitor.log'),
            logging.StreamHandler()
        ]
    )
    
    # Run continuous monitor
    run_continuous_monitor()
