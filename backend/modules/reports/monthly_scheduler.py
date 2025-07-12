#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Monthly Reports Scheduler
Simple background scheduler for monthly reports
"""

import logging
import time
import threading
from datetime import datetime, timedelta
import pytz
from typing import Dict, List
import os
import sys

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)

class MonthlyReportsScheduler:
    """Simple scheduler for monthly reports"""
    
    def __init__(self, app=None):
        self.app = app
        self.mexico_tz = pytz.timezone('America/Mexico_City')
        self.running = False
        self.thread = None
        
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
    def start(self):
        """Start the scheduler in background thread"""
        if self.running:
            logger.info("Scheduler already running")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Monthly Reports Scheduler started")
        
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Monthly Reports Scheduler stopped")
        
    def _run_scheduler(self):
        """Main scheduler loop"""
        logger.info("Scheduler loop started")
        
        while self.running:
            try:
                with self.app.app_context():
                    self._check_and_execute_schedules()
                    
                # Sleep for 1 hour
                time.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(300)  # Sleep 5 minutes on error
                
    def _check_and_execute_schedules(self):
        """Check for schedules that need to be executed"""
        try:
            now = datetime.now(self.mexico_tz)
            
            # Get schedules that need to be executed
            query = """
                SELECT rs.schedule_id, rs.name, rs.config_id, rs.schedule_config, rs.recipients,
                       rc.client_id, rc.name as config_name
                FROM report_schedules rs
                JOIN report_configurations rc ON rs.config_id = rc.config_id
                WHERE rs.is_active = true 
                AND rs.next_run_at <= %s
                AND rs.schedule_type = 'monthly'
            """
            
            schedules = self.app.db_manager.execute_query(query, (now,), fetch='all')
            
            if not schedules:
                return
                
            logger.info(f"Found {len(schedules)} schedules to execute")
            
            for schedule in schedules:
                self._execute_schedule(schedule, now)
                
        except Exception as e:
            logger.error(f"Error checking schedules: {e}")
            
    def _execute_schedule(self, schedule: Dict, execution_time: datetime):
        """Execute a specific schedule"""
        try:
            schedule_id = schedule['schedule_id']
            config_id = schedule['config_id']
            client_id = schedule['client_id']
            
            logger.info(f"Executing schedule: {schedule['name']}")

            # Generate report
            from .monthly_reports import monthly_reports_service

            # Get previous month
            if execution_time.month == 1:
                report_month = 12
                report_year = execution_time.year - 1
            else:
                report_month = execution_time.month - 1
                report_year = execution_time.year

            if client_id:
                # Client-specific report
                file_path = monthly_reports_service.generate_monthly_report_for_client(
                    client_id, report_month, report_year
                )
            else:
                # Consolidated report
                file_path = self._generate_consolidated_report(report_month, report_year)

            if not file_path:
                logger.error(f"Failed to generate report for schedule {schedule_id}")
                self._update_schedule_failure(schedule_id, execution_time)
                return

            # Record execution
            execution_id = self._record_execution(config_id, schedule_id, file_path, execution_time)

            # Send email if recipients exist
            if schedule['recipients']:
                self._send_report_email(execution_id, schedule['recipients'], file_path, schedule['name'])

            # Update next run time
            self._update_next_run_time(schedule_id, execution_time)

            logger.info(f"Successfully executed schedule: {schedule['name']}")
            
        except Exception as e:
            logger.error(f"Error executing schedule {schedule['schedule_id']}: {e}")
            self._update_schedule_failure(schedule['schedule_id'], execution_time)
            
    def _generate_consolidated_report(self, month: int, year: int) -> str:
        """Generate consolidated report for all clients"""
        try:
            from .monthly_reports import monthly_reports_service
            
            # Get all active clients
            clients_query = "SELECT client_id, name FROM clients WHERE is_active = true"
            clients = self.app.db_manager.execute_query(clients_query, fetch='all')
            
            if not clients:
                return None
            
            # Create consolidated Excel file
            import pandas as pd
            
            filename = f"lanet_systems_consolidado_{year}_{month:02d}.xlsx"
            file_path = os.path.join(monthly_reports_service.reports_dir, filename)
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = []
                total_tickets = 0
                
                for client in clients:
                    # Get tickets count for this client
                    start_date = datetime(year, month, 1)
                    if month == 12:
                        end_date = datetime(year + 1, 1, 1)
                    else:
                        end_date = datetime(year, month + 1, 1)
                    
                    tickets_query = """
                        SELECT COUNT(*) as count
                        FROM tickets 
                        WHERE client_id = %s 
                        AND created_at >= %s 
                        AND created_at < %s
                    """
                    
                    result = self.app.db_manager.execute_query(
                        tickets_query, 
                        (client['client_id'], start_date, end_date), 
                        fetch='one'
                    )
                    
                    ticket_count = result['count'] if result else 0
                    total_tickets += ticket_count
                    
                    summary_data.append({
                        'Cliente': client['name'],
                        'Tickets del Mes': ticket_count,
                        'Estado': 'Activo'
                    })
                
                # Add total row
                summary_data.append({
                    'Cliente': 'TOTAL',
                    'Tickets del Mes': total_tickets,
                    'Estado': 'CONSOLIDADO'
                })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Resumen Consolidado', index=False)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error generating consolidated report: {e}")
            return None
            
    def _record_execution(self, config_id: str, schedule_id: str, file_path: str, execution_time: datetime) -> str:
        """Record report execution in database"""
        try:
            import uuid
            
            execution_id = str(uuid.uuid4())
            
            query = """
                INSERT INTO report_executions (
                    execution_id, config_id, schedule_id, execution_type, status,
                    output_format, file_path, file_size, started_at, completed_at
                ) VALUES (%s::uuid, %s::uuid, %s::uuid, %s, %s, %s, %s, %s, %s, %s)
            """
            
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            self.app.db_manager.execute_query(query, (
                execution_id, config_id, schedule_id, 'scheduled', 'completed',
                'excel', file_path, file_size, execution_time, execution_time
            ), fetch='none')
            
            return execution_id
            
        except Exception as e:
            logger.error(f"Error recording execution: {e}")
            return None
            
    def _send_report_email(self, execution_id: str, recipients: List[str], file_path: str, report_name: str):
        """Send report via email"""
        try:
            # TODO: Integrate with existing email system
            logger.info(f"Would send email to {recipients} with report {file_path}")
            
            # Record delivery attempts
            for recipient in recipients:
                delivery_query = """
                    INSERT INTO report_deliveries (
                        execution_id, recipient_email, delivery_status, sent_at
                    ) VALUES (%s::uuid, %s, %s, %s)
                """
                
                self.app.db_manager.execute_query(delivery_query, (
                    execution_id, recipient, 'sent', datetime.now(self.mexico_tz)
                ), fetch='none')
                
        except Exception as e:
            logger.error(f"Error sending report email: {e}")
            
    def _update_next_run_time(self, schedule_id: str, current_time: datetime):
        """Update next run time for schedule"""
        try:
            # Calculate next month, same day and hour
            if current_time.month == 12:
                next_run = datetime(current_time.year + 1, 1, 1, current_time.hour, 0, 0)
            else:
                next_run = datetime(current_time.year, current_time.month + 1, 1, current_time.hour, 0, 0)
            
            next_run = self.mexico_tz.localize(next_run)
            
            query = """
                UPDATE report_schedules 
                SET last_run_at = %s, next_run_at = %s, updated_at = %s
                WHERE schedule_id = %s::uuid
            """
            
            self.app.db_manager.execute_query(query, (
                current_time, next_run, datetime.now(self.mexico_tz), schedule_id
            ), fetch='none')
            
            logger.info(f"Next run scheduled for {next_run}")
            
        except Exception as e:
            logger.error(f"Error updating next run time: {e}")
            
    def _update_schedule_failure(self, schedule_id: str, execution_time: datetime):
        """Update schedule with failure information"""
        try:
            query = """
                UPDATE report_schedules 
                SET last_run_at = %s, updated_at = %s
                WHERE schedule_id = %s::uuid
            """
            
            self.app.db_manager.execute_query(query, (
                execution_time, datetime.now(self.mexico_tz), schedule_id
            ), fetch='none')
            
        except Exception as e:
            logger.error(f"Error updating schedule failure: {e}")

# Global scheduler instance
monthly_scheduler = MonthlyReportsScheduler()
