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
                logger.warning(f"Found {len(breaches)} NEW SLA breaches (not previously notified)")

                # Send breach notifications
                notifications_sent = 0
                for breach in breaches:
                    try:
                        # Use the new SLA service method for email notifications
                        success = sla_service.send_sla_breach_notification(breach)
                        if success:
                            notifications_sent += 1
                            logger.info(f"Sent SLA breach notification for ticket {breach.get('ticket_number', breach['ticket_id'])}")
                    except Exception as e:
                        logger.error(f"Failed to send breach notification for ticket {breach['ticket_id']}: {e}")

                logger.info(f"Sent {notifications_sent}/{len(breaches)} SLA breach notifications")
            else:
                logger.info("No NEW SLA breaches found")
            
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
            
            # 4. Send notifications for new tickets and comments
            logger.info("Checking for new ticket notifications...")
            try:
                new_notifications = notifications_service.process_pending_notifications()
                if new_notifications > 0:
                    logger.info(f"Sent {new_notifications} new ticket/comment notifications")
                else:
                    logger.info("No new notifications to send")
            except Exception as e:
                logger.error(f"Error processing new notifications: {e}")

            # 5. Process email queue
            logger.info("Processing email queue...")
            processed_emails = email_service.process_email_queue(20)

            if processed_emails > 0:
                logger.info(f"Processed {processed_emails} emails from queue")
            else:
                logger.info("No emails in queue to process")
            
            # 6. Check for incoming emails (optional - skip if IMAP not configured)
            logger.info("Checking for incoming emails...")
            try:
                config = email_service.get_default_config()
                if config and config.get('enable_email_to_ticket') and config.get('imap_host'):
                    incoming_emails = email_service.check_incoming_emails()

                    if incoming_emails:
                        logger.info(f"Found {len(incoming_emails)} incoming emails")

                        # Process each incoming email
                        processed_tickets = 0
                        for email_data in incoming_emails:
                            ticket_id = email_service.process_incoming_email(email_data, config)
                            if ticket_id:
                                processed_tickets += 1

                        logger.info(f"Created/updated {processed_tickets} tickets from incoming emails")
                    else:
                        logger.info("No new incoming emails")
                else:
                    logger.info("IMAP not configured or email-to-ticket disabled - skipping incoming email check")

            except Exception as e:
                logger.warning(f"Error checking incoming emails (non-critical): {e}")
                logger.info("Continuing SLA monitoring without email processing")

            # 7. Process scheduled reports
            logger.info("Processing scheduled reports...")
            try:
                from modules.reports.scheduler import report_scheduler
                processed_reports = report_scheduler.process_scheduled_reports()

                if processed_reports > 0:
                    logger.info(f"Processed {processed_reports} scheduled reports")
                else:
                    logger.info("No scheduled reports due for processing")

            except Exception as e:
                logger.warning(f"Error processing scheduled reports (non-critical): {e}")
                logger.info("Continuing SLA monitoring without report processing")

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
