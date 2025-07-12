"""
Professional Report Factory for LANET Helpdesk V3
Combines data generators with formatters to create enterprise-grade reports
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from .report_generators import (
    TicketStatisticsReport, 
    SLAComplianceReport, 
    ClientSummaryReport,
    PDFReportFormatter,
    ExcelReportFormatter
)

logger = logging.getLogger(__name__)

class ReportFactory:
    """Factory class for generating professional reports"""
    
    def __init__(self, db_manager, reports_dir: str):
        self.db_manager = db_manager
        self.reports_dir = reports_dir
        
        # Ensure reports directory exists
        os.makedirs(reports_dir, exist_ok=True)

    def generate_enterprise_report(self, report_data: Dict[str, Any], output_format: str, execution_id: str) -> str:
        """
        Generate enterprise report from dynamic report data.

        Args:
            report_data: Complete report data from EnterpriseReportGenerator
            output_format: Output format ('pdf' or 'excel')
            execution_id: Report execution ID for tracking

        Returns:
            Path to generated report file
        """
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            config_name = report_data['config']['name'].replace(' ', '_').lower()
            file_extension = 'xlsx' if output_format.lower() == 'excel' else 'pdf'
            filename = f"enterprise_{config_name}_{timestamp}.{file_extension}"
            file_path = os.path.join(self.reports_dir, filename)

            if output_format.lower() == 'pdf':
                return self._generate_enterprise_pdf(report_data, file_path)
            else:
                return self._generate_enterprise_excel(report_data, file_path)

        except Exception as e:
            logger.error(f"Error generating enterprise report: {e}")
            raise
    
    def generate_ticket_statistics_report(self, 
                                        user_claims: Dict[str, Any],
                                        output_format: str = 'pdf',
                                        date_from: str = None,
                                        date_to: str = None) -> str:
        """Generate comprehensive ticket statistics report"""
        
        logger.info(f"🎯 Generating ticket statistics report for user {user_claims.get('name')}")
        
        # Generate data
        generator = TicketStatisticsReport(self.db_manager, user_claims)
        data = generator.generate_data(date_from, date_to)
        
        # Create file path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = 'xlsx' if output_format.lower() == 'excel' else output_format
        filename = f"estadisticas_tickets_{timestamp}.{file_extension}"
        file_path = os.path.join(self.reports_dir, filename)
        
        if output_format.lower() == 'pdf':
            return self._generate_pdf_ticket_stats(data, file_path)
        else:
            return self._generate_excel_ticket_stats(data, file_path)
    
    def generate_sla_compliance_report(self,
                                     user_claims: Dict[str, Any],
                                     output_format: str = 'pdf',
                                     date_from: str = None,
                                     date_to: str = None) -> str:
        """Generate SLA compliance report"""
        
        logger.info(f"📊 Generating SLA compliance report for user {user_claims.get('name')}")
        
        # Generate data
        generator = SLAComplianceReport(self.db_manager, user_claims)
        data = generator.generate_data(date_from, date_to)
        
        # Create file path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = 'xlsx' if output_format.lower() == 'excel' else output_format
        filename = f"cumplimiento_sla_{timestamp}.{file_extension}"
        file_path = os.path.join(self.reports_dir, filename)
        
        if output_format.lower() == 'pdf':
            return self._generate_pdf_sla_report(data, file_path)
        else:
            return self._generate_excel_sla_report(data, file_path)
    
    def generate_client_summary_report(self,
                                     user_claims: Dict[str, Any],
                                     output_format: str = 'pdf',
                                     date_from: str = None,
                                     date_to: str = None) -> str:
        """Generate client summary report"""
        
        logger.info(f"🏢 Generating client summary report for user {user_claims.get('name')}")
        
        # Generate data
        generator = ClientSummaryReport(self.db_manager, user_claims)
        data = generator.generate_data(date_from, date_to)
        
        # Create file path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = 'xlsx' if output_format.lower() == 'excel' else output_format
        filename = f"resumen_clientes_{timestamp}.{file_extension}"
        file_path = os.path.join(self.reports_dir, filename)
        
        if output_format.lower() == 'pdf':
            return self._generate_pdf_client_report(data, file_path)
        else:
            return self._generate_excel_client_report(data, file_path)
    
    def generate_quick_report(self,
                            user_claims: Dict[str, Any],
                            output_format: str = 'pdf') -> str:
        """Generate quick overview report with key metrics"""
        
        logger.info(f"⚡ Generating quick report for user {user_claims.get('name')}")
        
        # Generate basic ticket statistics (last 7 days)
        generator = TicketStatisticsReport(self.db_manager, user_claims)
        data = generator.generate_data()
        
        # Create file path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Use .xlsx extension for excel format
        file_extension = 'xlsx' if output_format.lower() == 'excel' else output_format
        filename = f"reporte_rapido_{timestamp}.{file_extension}"
        file_path = os.path.join(self.reports_dir, filename)
        
        if output_format.lower() == 'pdf':
            return self._generate_pdf_quick_report(data, file_path)
        elif output_format.lower() == 'excel':
            # Generate .xlsx file but save as 'excel' format in DB
            file_path = file_path.replace('.excel', '.xlsx')
            return self._generate_excel_quick_report(data, file_path)
        else:
            return self._generate_excel_quick_report(data, file_path)
    
    def _generate_pdf_ticket_stats(self, data: Dict[str, Any], file_path: str) -> str:
        """Generate PDF ticket statistics report"""
        formatter = PDFReportFormatter(file_path)
        
        # Header
        formatter.add_header(
            data['report_title'],
            f"Período: {data['date_range']}"
        )
        
        # Overall statistics
        if data['overall_stats']:
            stats = data['overall_stats']
            summary_data = {
                'Total de Tickets': stats.get('total_tickets', 0),
                'Tickets Abiertos': stats.get('open_tickets', 0),
                'Tickets en Progreso': stats.get('in_progress_tickets', 0),
                'Tickets Pendientes': stats.get('pending_tickets', 0),
                'Tickets Resueltos': stats.get('resolved_tickets', 0),
                'Tickets Cerrados': stats.get('closed_tickets', 0),
                'Tickets Críticos': stats.get('critical_tickets', 0),
                'Tickets Alta Prioridad': stats.get('high_tickets', 0),
                'Tiempo Promedio Resolución (min)': f"{stats.get('avg_resolution_time', 0):.1f}" if stats.get('avg_resolution_time') else 'N/A'
            }
            formatter.add_summary_table(summary_data, "Estadísticas Generales")
        
        # Client statistics (if available)
        if data['client_stats']:
            formatter.add_data_table(
                data['client_stats'],
                "Top 10 Clientes por Volumen de Tickets",
                ['client_name', 'ticket_count', 'open_count', 'closed_count']
            )
        
        # Technician statistics
        if data['technician_stats']:
            formatter.add_data_table(
                data['technician_stats'],
                "Rendimiento de Técnicos",
                ['technician_name', 'assigned_count', 'resolved_count', 'avg_resolution_time']
            )
        
        # Footer
        formatter.add_footer(data['generated_by'], data['generated_at'])
        
        # Build PDF
        formatter.build()
        logger.info(f"✅ PDF ticket statistics report generated: {file_path}")
        return file_path
    
    def _generate_excel_ticket_stats(self, data: Dict[str, Any], file_path: str) -> str:
        """Generate Excel ticket statistics report"""
        formatter = ExcelReportFormatter(file_path)
        formatter.create_workbook()
        
        # Summary sheet
        if data['overall_stats']:
            formatter.add_summary_sheet(data['overall_stats'], 'Estadísticas Generales')
        
        # Client data sheet
        if data['client_stats']:
            formatter.add_data_sheet(data['client_stats'], 'Clientes', 'Top Clientes por Tickets')
        
        # Technician data sheet
        if data['technician_stats']:
            formatter.add_data_sheet(data['technician_stats'], 'Técnicos', 'Rendimiento de Técnicos')
        
        # Trend data sheet
        if data['trend_data']:
            formatter.add_data_sheet(data['trend_data'], 'Tendencias', 'Tendencia Diaria de Tickets')
        
        formatter.save()
        logger.info(f"✅ Excel ticket statistics report generated: {file_path}")
        return file_path
    
    def _generate_pdf_sla_report(self, data: Dict[str, Any], file_path: str) -> str:
        """Generate PDF SLA compliance report"""
        formatter = PDFReportFormatter(file_path)
        
        # Header
        formatter.add_header(
            data['report_title'],
            f"Período: {data['date_range']}"
        )
        
        # SLA statistics
        if data['sla_stats']:
            stats = data['sla_stats']
            summary_data = {
                'Total Tickets con SLA': stats.get('total_tickets_with_sla', 0),
                'Respuesta a Tiempo': stats.get('response_met', 0),
                'Resolución a Tiempo': stats.get('resolution_met', 0),
                'Tiempo Promedio Respuesta (min)': f"{stats.get('avg_response_time', 0):.1f}" if stats.get('avg_response_time') else 'N/A',
                'Tiempo Promedio Resolución (min)': f"{stats.get('avg_resolution_time', 0):.1f}" if stats.get('avg_resolution_time') else 'N/A',
                'Tickets Escalados': stats.get('escalated_tickets', 0)
            }
            formatter.add_summary_table(summary_data, "Cumplimiento SLA General")
        
        # Priority statistics
        if data['priority_stats']:
            formatter.add_data_table(
                data['priority_stats'],
                "Cumplimiento SLA por Prioridad",
                ['priority', 'total_tickets', 'response_met', 'resolution_met', 'avg_response_time', 'avg_resolution_time']
            )
        
        # Footer
        formatter.add_footer(data['generated_by'], data['generated_at'])
        
        # Build PDF
        formatter.build()
        logger.info(f"✅ PDF SLA compliance report generated: {file_path}")
        return file_path
    
    def _generate_excel_sla_report(self, data: Dict[str, Any], file_path: str) -> str:
        """Generate Excel SLA compliance report"""
        formatter = ExcelReportFormatter(file_path)
        formatter.create_workbook()
        
        # Summary sheet
        if data['sla_stats']:
            formatter.add_summary_sheet(data['sla_stats'], 'Cumplimiento SLA')
        
        # Priority breakdown
        if data['priority_stats']:
            formatter.add_data_sheet(data['priority_stats'], 'Por Prioridad', 'SLA por Prioridad')
        
        formatter.save()
        logger.info(f"✅ Excel SLA compliance report generated: {file_path}")
        return file_path
    
    def _generate_pdf_client_report(self, data: Dict[str, Any], file_path: str) -> str:
        """Generate PDF client summary report"""
        formatter = PDFReportFormatter(file_path)
        
        # Header
        formatter.add_header(
            data['report_title'],
            f"Período: {data['date_range']}"
        )
        
        # Client data
        if data['client_data']:
            formatter.add_data_table(
                data['client_data'],
                "Resumen de Clientes",
                ['client_name', 'rfc', 'total_sites', 'total_users', 'total_tickets', 'open_tickets', 'closed_tickets']
            )
        
        # Footer
        formatter.add_footer(data['generated_by'], data['generated_at'])
        
        # Build PDF
        formatter.build()
        logger.info(f"✅ PDF client summary report generated: {file_path}")
        return file_path
    
    def _generate_excel_client_report(self, data: Dict[str, Any], file_path: str) -> str:
        """Generate Excel client summary report"""
        formatter = ExcelReportFormatter(file_path)
        formatter.create_workbook()
        
        # Client data sheet
        if data['client_data']:
            formatter.add_data_sheet(data['client_data'], 'Clientes', 'Resumen de Clientes')
        
        formatter.save()
        logger.info(f"✅ Excel client summary report generated: {file_path}")
        return file_path
    
    def _generate_pdf_quick_report(self, data: Dict[str, Any], file_path: str) -> str:
        """Generate PDF quick report"""
        formatter = PDFReportFormatter(file_path)
        
        # Header
        formatter.add_header(
            "Reporte Rápido - Dashboard Ejecutivo",
            f"Período: {data['date_range']}"
        )
        
        # Key metrics
        if data['overall_stats']:
            stats = data['overall_stats']
            summary_data = {
                'Total de Tickets': stats.get('total_tickets', 0),
                'Tickets Abiertos': stats.get('open_tickets', 0),
                'Tickets Resueltos': stats.get('resolved_tickets', 0),
                'Tickets Críticos': stats.get('critical_tickets', 0),
                'Tiempo Promedio Resolución': f"{stats.get('avg_resolution_time', 0):.1f} min" if stats.get('avg_resolution_time') else 'N/A'
            }
            formatter.add_summary_table(summary_data, "Métricas Clave")
        
        # Footer
        formatter.add_footer(data['generated_by'], data['generated_at'])
        
        # Build PDF
        formatter.build()
        logger.info(f"✅ PDF quick report generated: {file_path}")
        return file_path
    
    def _generate_excel_quick_report(self, data: Dict[str, Any], file_path: str) -> str:
        """Generate Excel quick report"""
        formatter = ExcelReportFormatter(file_path)
        formatter.create_workbook()
        
        # Summary sheet
        if data['overall_stats']:
            formatter.add_summary_sheet(data['overall_stats'], 'Dashboard Ejecutivo')
        
        formatter.save()
        logger.info(f"✅ Excel quick report generated: {file_path}")
        return file_path

    def _generate_enterprise_pdf(self, report_data: Dict[str, Any], file_path: str) -> str:
        """Generate enterprise PDF report with dynamic columns and professional formatting."""
        try:
            formatter = PDFReportFormatter(file_path)

            # Header with report configuration info
            config = report_data['config']
            formatter.add_header(
                config['name'],
                f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Total: {report_data['total_records']} registros"
            )

            # Add summary statistics if available
            if report_data.get('summary'):
                summary = report_data['summary']
                summary_data = {
                    'Total de Registros': summary.get('total_records', 0),
                    'Rango de Fechas': f"{summary.get('date_range', {}).get('from', 'N/A')} - {summary.get('date_range', {}).get('to', 'N/A')}",
                }

                # Add status distribution
                if summary.get('status_distribution'):
                    for status, count in summary['status_distribution'].items():
                        summary_data[f'Estado {status}'] = count

                # Add SLA compliance if available
                if summary.get('sla_compliance', {}).get('total_with_sla', 0) > 0:
                    sla = summary['sla_compliance']
                    response_pct = (sla['response_met'] / sla['total_with_sla']) * 100
                    resolution_pct = (sla['resolution_met'] / sla['total_with_sla']) * 100
                    summary_data['SLA Respuesta'] = f"{response_pct:.1f}%"
                    summary_data['SLA Resolución'] = f"{resolution_pct:.1f}%"

                formatter.add_summary_table(summary_data, "Resumen Ejecutivo")

            # Add data table with dynamic columns
            if report_data.get('data') and report_data.get('columns'):
                # Prepare table headers
                headers = []
                for col in report_data['columns']:
                    label = col.get('custom_label') or col['display_name_es']
                    headers.append(label)

                # Prepare table data (limit to first 100 rows for PDF)
                table_data = []
                for row in report_data['data'][:100]:
                    row_data = []
                    for col in report_data['columns']:
                        value = row.get(col['column_key'], '')
                        # Format value based on column type
                        if col['data_type'] == 'date' and value:
                            if hasattr(value, 'strftime'):
                                value = value.strftime('%d/%m/%Y %H:%M')
                        elif col['data_type'] == 'number' and value is not None:
                            value = str(value)
                        elif value is None:
                            value = 'N/A'
                        row_data.append(str(value))
                    table_data.append(row_data)

                formatter.add_data_table(table_data, headers, "Datos del Reporte")

                # Add note if data was truncated
                if len(report_data['data']) > 100:
                    formatter.add_text(f"Nota: Se muestran los primeros 100 registros de {len(report_data['data'])} totales.")

            # Footer
            formatter.add_footer(
                report_data.get('user_role', 'Usuario'),
                datetime.now().strftime('%d/%m/%Y %H:%M')
            )

            # Build PDF
            formatter.build()
            logger.info(f"✅ Enterprise PDF report generated: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Error generating enterprise PDF: {e}")
            raise

    def _generate_enterprise_excel(self, report_data: Dict[str, Any], file_path: str) -> str:
        """Generate enterprise Excel report with dynamic columns and professional formatting."""
        try:
            formatter = ExcelReportFormatter(file_path)
            formatter.create_workbook()

            # Summary sheet
            if report_data.get('summary'):
                summary_data = {
                    'total_records': report_data['summary'].get('total_records', 0),
                    'date_range': f"{report_data['summary'].get('date_range', {}).get('from', 'N/A')} - {report_data['summary'].get('date_range', {}).get('to', 'N/A')}",
                    'status_distribution': report_data['summary'].get('status_distribution', {}),
                    'priority_distribution': report_data['summary'].get('priority_distribution', {}),
                    'sla_compliance': report_data['summary'].get('sla_compliance', {})
                }
                formatter.add_summary_sheet(summary_data, report_data['config']['name'])

            # Data sheet with dynamic columns
            if report_data.get('data') and report_data.get('columns'):
                # Prepare headers
                headers = []
                for col in report_data['columns']:
                    label = col.get('custom_label') or col['display_name_es']
                    headers.append(label)

                # Prepare data
                excel_data = []
                for row in report_data['data']:
                    row_data = []
                    for col in report_data['columns']:
                        value = row.get(col['column_key'], '')
                        # Handle different data types
                        if col['data_type'] == 'date' and value:
                            if hasattr(value, 'strftime'):
                                value = value.strftime('%d/%m/%Y %H:%M')
                        elif col['data_type'] == 'number' and value is not None:
                            try:
                                value = float(value) if '.' in str(value) else int(value)
                            except (ValueError, TypeError):
                                value = str(value)
                        elif value is None:
                            value = 'N/A'
                        row_data.append(value)
                    excel_data.append(row_data)

                formatter.add_data_sheet(excel_data, headers, "Datos")

            # Chart data sheet if available
            if report_data.get('chart_data'):
                chart_data = []
                for chart_key, chart_info in report_data['chart_data'].items():
                    if chart_info.get('data'):
                        chart_data.extend([
                            [chart_info['title']],
                            ['Categoría', 'Valor']
                        ])
                        for item in chart_info['data']:
                            chart_data.append([item.get('label', ''), item.get('value', 0)])
                        chart_data.append([])  # Empty row separator

                if chart_data:
                    formatter.add_data_sheet(chart_data, [], "Gráficos")

            formatter.save()
            logger.info(f"✅ Enterprise Excel report generated: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Error generating enterprise Excel: {e}")
            raise
