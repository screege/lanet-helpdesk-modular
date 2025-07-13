#!/usr/bin/env python3
"""
Process pending emails from email_processing_log
This script will manually process emails that are stuck in 'pending' status
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from modules.email.service import email_service

def process_pending_emails():
    """Process all pending emails from the processing log"""
    
    app = create_app()
    
    with app.app_context():
        print("📧 Processing Pending Emails from screege@gmail.com")
        print("=" * 60)
        
        try:
            # Get pending emails from screege@gmail.com
            pending_emails = app.db_manager.execute_query("""
                SELECT log_id, message_id, from_email, subject, body_text, body_html, config_id
                FROM email_processing_log 
                WHERE processing_status = 'pending' 
                AND from_email ILIKE '%screege%'
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            if not pending_emails:
                print("✅ No pending emails found from screege@gmail.com")
                return True
            
            print(f"📧 Found {len(pending_emails)} pending emails")
            
            processed_count = 0
            success_count = 0
            
            for email_data in pending_emails:
                print(f"\n📧 Processing email: {email_data['subject']}")
                print(f"   From: {email_data['from_email']}")
                print(f"   Message ID: {email_data['message_id']}")
                
                try:
                    # Get email configuration
                    config = email_service.get_config_by_id(email_data['config_id'])
                    if not config:
                        print(f"❌ No email configuration found for {email_data['config_id']}")
                        continue
                    
                    # Prepare email data for processing
                    email_for_processing = {
                        'message_id': email_data['message_id'],
                        'from_email': email_data['from_email'],
                        'subject': email_data['subject'],
                        'body_text': email_data['body_text'],
                        'body_html': email_data['body_html']
                    }
                    
                    # Process the email to create a ticket
                    print(f"   Config: {config['name']}")
                    print(f"   Email data keys: {list(email_for_processing.keys())}")
                    ticket_id = email_service.process_incoming_email(email_for_processing, config)
                    print(f"   Ticket ID result: {ticket_id}")
                    
                    processed_count += 1
                    
                    if ticket_id:
                        success_count += 1
                        print(f"✅ Created ticket: {ticket_id}")
                        
                        # Update the processing log
                        from datetime import datetime
                        app.db_manager.execute_update(
                            'email_processing_log',
                            {
                                'processing_status': 'processed',
                                'ticket_id': ticket_id,
                                'action_taken': 'created_ticket',
                                'processed_at': datetime.now()
                            },
                            'log_id = %s',
                            (email_data['log_id'],)
                        )
                        print(f"✅ Updated processing log")
                    else:
                        print(f"❌ Failed to create ticket")
                        
                        # Update the processing log with failure
                        from datetime import datetime
                        app.db_manager.execute_update(
                            'email_processing_log',
                            {
                                'processing_status': 'failed',
                                'error_message': 'Failed to create ticket',
                                'processed_at': datetime.now()
                            },
                            'log_id = %s',
                            (email_data['log_id'],)
                        )
                        
                except Exception as e:
                    print(f"❌ Error processing email: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    # Update the processing log with error
                    from datetime import datetime
                    app.db_manager.execute_update(
                        'email_processing_log',
                        {
                            'processing_status': 'failed',
                            'error_message': str(e),
                            'processed_at': datetime.now()
                        },
                        'log_id = %s',
                        (email_data['log_id'],)
                    )
            
            print(f"\n📊 Processing Summary:")
            print(f"   Total processed: {processed_count}")
            print(f"   Successful: {success_count}")
            print(f"   Failed: {processed_count - success_count}")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = process_pending_emails()
    sys.exit(0 if success else 1)
