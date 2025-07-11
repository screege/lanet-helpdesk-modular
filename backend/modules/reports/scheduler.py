#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Report Scheduler
Automated report generation and delivery system
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from flask import current_app

logger = logging.getLogger(__name__)

class ReportScheduler:
    """Service class for automated report scheduling and execution"""
    
    def __init__(self):
        pass
    
    def process_scheduled_reports(self) -> int:
        """Process all scheduled reports that are due for execution"""
        try:
            logger.info("Starting scheduled report processing...")
            
            # Get all active schedules that are due for execution
            due_schedules = self._get_due_schedules()
            
            if not due_schedules:
                logger.info("No scheduled reports due for execution")
                return 0
            
            processed_count = 0
            
            for schedule in due_schedules:
                try:
                    logger.info(f"Processing schedule: {schedule['name']} (ID: {schedule['schedule_id']})")
                    
                    # Execute the scheduled report
                    success = self._execute_scheduled_report(schedule)
                    
                    if success:
                        processed_count += 1
                        # Update last run time and calculate next run
                        self._update_schedule_run_time(schedule)
                        logger.info(f"Successfully processed schedule: {schedule['name']}")
                    else:
                        logger.error(f"Failed to process schedule: {schedule['name']}")
                        
                except Exception as e:
                    logger.error(f"Error processing schedule {schedule['schedule_id']}: {e}")
                    continue
            
            logger.info(f"Processed {processed_count} scheduled reports")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error in scheduled report processing: {e}")
            return 0
    
    def _get_due_schedules(self) -> List[Dict]:
        """Get all schedules that are due for execution"""
        try:
            query = """
            SELECT rs.schedule_id, rs.name, rs.config_id, rs.schedule_type,
                   rs.schedule_config, rs.recipients, rs.next_run_at,
                   rc.name as config_name, rc.template_id, rc.client_id,
                   rc.report_filters, rc.output_formats
            FROM report_schedules rs
            JOIN report_configurations rc ON rs.config_id = rc.config_id
            WHERE rs.is_active = true 
            AND rc.is_active = true
            AND rs.next_run_at <= CURRENT_TIMESTAMP
            ORDER BY rs.next_run_at ASC
            """
            
            schedules = current_app.db_manager.execute_query(query)
            return schedules or []
            
        except Exception as e:
            logger.error(f"Error getting due schedules: {e}")
            return []
    
    def _execute_scheduled_report(self, schedule: Dict) -> bool:
        """Execute a scheduled report"""
        try:
            from .service import reports_service
            
            config_id = schedule['config_id']
            output_formats = schedule.get('output_formats', ['pdf'])
            
            # Ensure output_formats is a list
            if isinstance(output_formats, str):
                output_formats = [output_formats]
            
            execution_ids = []
            
            # Generate report for each output format
            for output_format in output_formats:
                try:
                    execution_id = reports_service.generate_report(
                        config_id=config_id,
                        output_format=output_format,
                        executed_by=None  # System execution
                    )
                    
                    if execution_id:
                        execution_ids.append(execution_id)
                        
                        # Create execution record with schedule reference
                        current_app.db_manager.execute_update(
                            'report_executions',
                            {'schedule_id': schedule['schedule_id']},
                            {'execution_id': execution_id}
                        )
                        
                        logger.info(f"Generated {output_format} report for schedule {schedule['schedule_id']}")
                    else:
                        logger.error(f"Failed to generate {output_format} report for schedule {schedule['schedule_id']}")
                        
                except Exception as e:
                    logger.error(f"Error generating {output_format} report for schedule {schedule['schedule_id']}: {e}")
                    continue
            
            if not execution_ids:
                logger.error(f"No reports generated for schedule {schedule['schedule_id']}")
                return False
            
            # Schedule email delivery for successful executions
            self._schedule_report_delivery(schedule, execution_ids)
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing scheduled report: {e}")
            return False
    
    def _schedule_report_delivery(self, schedule: Dict, execution_ids: List[str]):
        """Schedule email delivery for generated reports"""
        try:
            recipients = schedule.get('recipients', [])
            if not recipients:
                logger.warning(f"No recipients configured for schedule {schedule['schedule_id']}")
                return
            
            # Wait a moment for report generation to complete
            import time
            time.sleep(2)
            
            for execution_id in execution_ids:
                # Check if report generation completed successfully
                execution = current_app.db_manager.execute_query(
                    "SELECT status, file_path, output_format FROM report_executions WHERE execution_id = %s",
                    (execution_id,),
                    fetch='one'
                )
                
                if not execution or execution['status'] != 'completed':
                    logger.warning(f"Report execution {execution_id} not completed, skipping delivery")
                    continue
                
                # Create delivery records for each recipient
                for recipient in recipients:
                    try:
                        delivery_data = {
                            'execution_id': execution_id,
                            'recipient_email': recipient,
                            'delivery_status': 'pending'
                        }
                        
                        result = current_app.db_manager.execute_insert('report_deliveries', delivery_data)
                        
                        if result:
                            # Queue email for delivery
                            self._queue_report_email(schedule, execution, recipient, result['delivery_id'])
                            logger.info(f"Queued report delivery to {recipient} for execution {execution_id}")
                        
                    except Exception as e:
                        logger.error(f"Error creating delivery record for {recipient}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error scheduling report delivery: {e}")
    
    def _queue_report_email(self, schedule: Dict, execution: Dict, recipient: str, delivery_id: str):
        """Queue email for report delivery"""
        try:
            from modules.email.service import email_service
            
            # Prepare email content
            subject = f"LANET Helpdesk - Reporte Programado: {schedule['config_name']}"
            
            body = f"""
            <html>
            <body>
                <h2>Reporte Programado - LANET Helpdesk</h2>
                
                <p>Estimado usuario,</p>
                
                <p>Se ha generado su reporte programado con los siguientes detalles:</p>
                
                <ul>
                    <li><strong>Reporte:</strong> {schedule['config_name']}</li>
                    <li><strong>Programación:</strong> {schedule['name']}</li>
                    <li><strong>Formato:</strong> {execution['output_format'].upper()}</li>
                    <li><strong>Generado:</strong> {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S UTC')}</li>
                </ul>
                
                <p>El reporte se encuentra adjunto a este correo.</p>
                
                <p>Si tiene alguna pregunta o necesita asistencia, no dude en contactarnos.</p>
                
                <p>Saludos cordiales,<br>
                Equipo LANET Helpdesk</p>
            </body>
            </html>
            """
            
            # Queue email with attachment
            success = email_service.queue_email(
                to_email=recipient,
                subject=subject,
                body=body,
                attachment_path=execution['file_path'] if execution.get('file_path') else None
            )
            
            if success:
                # Update delivery record with email queue reference
                current_app.db_manager.execute_update(
                    'report_deliveries',
                    {'delivery_status': 'sent'},
                    {'delivery_id': delivery_id}
                )
                logger.info(f"Report email queued successfully for {recipient}")
            else:
                # Update delivery record with failure
                current_app.db_manager.execute_update(
                    'report_deliveries',
                    {'delivery_status': 'failed', 'error_message': 'Failed to queue email'},
                    {'delivery_id': delivery_id}
                )
                logger.error(f"Failed to queue report email for {recipient}")
                
        except Exception as e:
            logger.error(f"Error queueing report email: {e}")
            # Update delivery record with failure
            try:
                current_app.db_manager.execute_update(
                    'report_deliveries',
                    {'delivery_status': 'failed', 'error_message': str(e)},
                    {'delivery_id': delivery_id}
                )
            except:
                pass
    
    def _update_schedule_run_time(self, schedule: Dict):
        """Update schedule with last run time and calculate next run"""
        try:
            from .service import reports_service
            
            now = datetime.utcnow()
            
            # Parse schedule config
            import json
            schedule_config = schedule.get('schedule_config', {})
            if isinstance(schedule_config, str):
                schedule_config = json.loads(schedule_config)
            
            # Calculate next run time
            next_run_at = reports_service._calculate_next_run(
                schedule['schedule_type'], 
                schedule_config
            )
            
            # Update schedule
            update_data = {
                'last_run_at': now,
                'next_run_at': next_run_at,
                'updated_at': now
            }
            
            current_app.db_manager.execute_update(
                'report_schedules',
                update_data,
                {'schedule_id': schedule['schedule_id']}
            )
            
            logger.info(f"Updated schedule {schedule['schedule_id']}: next run at {next_run_at}")
            
        except Exception as e:
            logger.error(f"Error updating schedule run time: {e}")
    
    def get_schedule_status(self) -> Dict:
        """Get status of all scheduled reports"""
        try:
            # Get active schedules count
            active_schedules = current_app.db_manager.execute_query(
                "SELECT COUNT(*) as count FROM report_schedules WHERE is_active = true",
                fetch='one'
            )
            
            # Get recent executions
            recent_executions = current_app.db_manager.execute_query(
                """
                SELECT COUNT(*) as count 
                FROM report_executions 
                WHERE execution_type = 'scheduled' 
                AND started_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
                """,
                fetch='one'
            )
            
            # Get next scheduled run
            next_run = current_app.db_manager.execute_query(
                """
                SELECT MIN(next_run_at) as next_run 
                FROM report_schedules 
                WHERE is_active = true
                """,
                fetch='one'
            )
            
            return {
                'active_schedules': active_schedules.get('count', 0) if active_schedules else 0,
                'executions_last_24h': recent_executions.get('count', 0) if recent_executions else 0,
                'next_scheduled_run': next_run.get('next_run') if next_run else None
            }
            
        except Exception as e:
            logger.error(f"Error getting schedule status: {e}")
            return {
                'active_schedules': 0,
                'executions_last_24h': 0,
                'next_scheduled_run': None
            }


# Create scheduler instance
report_scheduler = ReportScheduler()
