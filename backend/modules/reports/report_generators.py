"""
Professional Report Generators for LANET Helpdesk V3
Enterprise-grade business intelligence reporting system
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.colors import HexColor

logger = logging.getLogger(__name__)

class BaseReportGenerator:
    """Base class for all report generators with common functionality"""
    
    def __init__(self, db_manager, user_claims: Dict[str, Any]):
        self.db_manager = db_manager
        self.user_claims = user_claims
        self.user_role = user_claims.get('role')
        self.user_id = user_claims.get('sub')
        self.client_id = user_claims.get('client_id')
        self.site_ids = user_claims.get('site_ids', [])
        
    def get_rbac_filter(self) -> Tuple[str, List[Any]]:
        """Get RBAC filter conditions based on user role"""
        if self.user_role in ['superadmin', 'technician']:
            return "", []
        elif self.user_role == 'client_admin':
            return "AND t.client_id = %s", [self.client_id]
        elif self.user_role == 'solicitante':
            if self.site_ids:
                placeholders = ','.join(['%s'] * len(self.site_ids))
                return f"AND t.site_id IN ({placeholders})", self.site_ids
            else:
                return "AND 1=0", []  # No access if no sites assigned
        else:
            return "AND 1=0", []  # No access for unknown roles
    
    def get_client_filter(self) -> Tuple[str, List[Any]]:
        """Get client filter for non-ticket queries"""
        if self.user_role in ['superadmin', 'technician']:
            return "", []
        elif self.user_role in ['client_admin', 'solicitante']:
            return "AND client_id = %s", [self.client_id]
        else:
            return "AND 1=0", []

class TicketStatisticsReport(BaseReportGenerator):
    """Generate comprehensive ticket statistics report"""
    
    def generate_data(self, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """Generate ticket statistics data"""
        
        # Set default date range (last 30 days)
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
        
        rbac_filter, rbac_params = self.get_rbac_filter()
        
        # Overall ticket statistics
        overall_query = f"""
        SELECT
            COUNT(*) as total_tickets,
            COUNT(CASE WHEN status = 'nuevo' THEN 1 END) as new_tickets,
            COUNT(CASE WHEN status = 'asignado' THEN 1 END) as assigned_tickets,
            COUNT(CASE WHEN status = 'en_proceso' THEN 1 END) as in_progress_tickets,
            COUNT(CASE WHEN status = 'espera_cliente' THEN 1 END) as pending_tickets,
            COUNT(CASE WHEN status = 'resuelto' THEN 1 END) as resolved_tickets,
            COUNT(CASE WHEN status = 'cerrado' THEN 1 END) as closed_tickets,
            COUNT(CASE WHEN priority = 'critica' THEN 1 END) as critical_tickets,
            COUNT(CASE WHEN priority = 'alta' THEN 1 END) as high_tickets,
            COUNT(CASE WHEN priority = 'media' THEN 1 END) as medium_tickets,
            COUNT(CASE WHEN priority = 'baja' THEN 1 END) as low_tickets,
            AVG(CASE WHEN resolved_at IS NOT NULL AND created_at IS NOT NULL
                     THEN EXTRACT(EPOCH FROM (resolved_at - created_at))/60 END) as avg_resolution_time
        FROM tickets t
        WHERE t.created_at >= %s AND t.created_at <= %s
        {rbac_filter}
        """
        
        params = [date_from, date_to] + rbac_params
        overall_stats = self.db_manager.execute_query(overall_query, tuple(params), fetch='one')
        
        # Tickets by client (for superadmin/technician)
        client_stats = []
        if self.user_role in ['superadmin', 'technician']:
            client_query = """
            SELECT
                c.name as client_name,
                COUNT(t.ticket_id) as ticket_count,
                COUNT(CASE WHEN t.status IN ('nuevo', 'asignado', 'en_proceso') THEN 1 END) as open_count,
                COUNT(CASE WHEN t.status IN ('resuelto', 'cerrado') THEN 1 END) as closed_count
            FROM clients c
            LEFT JOIN tickets t ON c.client_id = t.client_id 
                AND t.created_at >= %s AND t.created_at <= %s
            WHERE c.is_active = true
            GROUP BY c.client_id, c.name
            ORDER BY ticket_count DESC
            LIMIT 10
            """
            client_stats = self.db_manager.execute_query(client_query, (date_from, date_to), fetch='all')
        
        # Tickets by technician
        tech_query = f"""
        SELECT 
            u.name as technician_name,
            COUNT(t.ticket_id) as assigned_count,
            COUNT(CASE WHEN t.status IN ('resuelto', 'cerrado') THEN 1 END) as resolved_count,
            AVG(CASE WHEN t.resolved_at IS NOT NULL AND t.created_at IS NOT NULL
                     THEN EXTRACT(EPOCH FROM (t.resolved_at - t.created_at))/60 END) as avg_resolution_time
        FROM users u
        LEFT JOIN tickets t ON u.user_id = t.assigned_to 
            AND t.created_at >= %s AND t.created_at <= %s
            {rbac_filter.replace('t.client_id', 't.client_id')}
        WHERE u.role = 'technician' AND u.is_active = true
        GROUP BY u.user_id, u.name
        ORDER BY assigned_count DESC
        """
        
        tech_params = [date_from, date_to] + rbac_params
        tech_stats = self.db_manager.execute_query(tech_query, tuple(tech_params), fetch='all')
        
        # Daily ticket creation trend
        trend_query = f"""
        SELECT
            DATE(t.created_at) as date,
            COUNT(*) as tickets_created,
            COUNT(CASE WHEN t.status IN ('resuelto', 'cerrado') THEN 1 END) as tickets_resolved
        FROM tickets t
        WHERE t.created_at >= %s AND t.created_at <= %s
        {rbac_filter}
        GROUP BY DATE(t.created_at)
        ORDER BY date
        """
        
        trend_data = self.db_manager.execute_query(trend_query, tuple(params), fetch='all')
        
        return {
            'report_title': 'Reporte de Estadísticas de Tickets',
            'date_range': f"{date_from} a {date_to}",
            'overall_stats': overall_stats,
            'client_stats': client_stats,
            'technician_stats': tech_stats,
            'trend_data': trend_data,
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'generated_by': self.user_claims.get('name', 'Usuario'),
            'user_role': self.user_role
        }

class SLAComplianceReport(BaseReportGenerator):
    """Generate SLA compliance and performance report"""
    
    def generate_data(self, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """Generate SLA compliance data"""
        
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
        
        rbac_filter, rbac_params = self.get_rbac_filter()
        
        # Overall SLA compliance
        sla_query = f"""
        SELECT 
            COUNT(*) as total_tickets_with_sla,
            COUNT(CASE WHEN sc.response_time_met = true THEN 1 END) as response_met,
            COUNT(CASE WHEN sc.resolution_time_met = true THEN 1 END) as resolution_met,
            AVG(sc.response_time_actual) as avg_response_time,
            AVG(sc.resolution_time_actual) as avg_resolution_time,
            COUNT(CASE WHEN sc.escalated_to_admin = true THEN 1 END) as escalated_tickets
        FROM sla_compliance sc
        JOIN tickets t ON sc.ticket_id = t.ticket_id
        WHERE t.created_at >= %s AND t.created_at <= %s
        {rbac_filter}
        """
        
        params = [date_from, date_to] + rbac_params
        sla_stats = self.db_manager.execute_query(sla_query, tuple(params), fetch='one')
        
        # SLA compliance by priority
        priority_query = f"""
        SELECT 
            t.priority,
            COUNT(*) as total_tickets,
            COUNT(CASE WHEN sc.response_time_met = true THEN 1 END) as response_met,
            COUNT(CASE WHEN sc.resolution_time_met = true THEN 1 END) as resolution_met,
            AVG(sc.response_time_actual) as avg_response_time,
            AVG(sc.resolution_time_actual) as avg_resolution_time
        FROM sla_compliance sc
        JOIN tickets t ON sc.ticket_id = t.ticket_id
        WHERE t.created_at >= %s AND t.created_at <= %s
        {rbac_filter}
        GROUP BY t.priority
        ORDER BY 
            CASE t.priority 
                WHEN 'critica' THEN 1 
                WHEN 'alta' THEN 2 
                WHEN 'media' THEN 3 
                WHEN 'baja' THEN 4 
            END
        """
        
        priority_stats = self.db_manager.execute_query(priority_query, tuple(params), fetch='all')
        
        return {
            'report_title': 'Reporte de Cumplimiento SLA',
            'date_range': f"{date_from} a {date_to}",
            'sla_stats': sla_stats,
            'priority_stats': priority_stats,
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'generated_by': self.user_claims.get('name', 'Usuario'),
            'user_role': self.user_role
        }

class ClientSummaryReport(BaseReportGenerator):
    """Generate client summary report with ticket and asset information"""
    
    def generate_data(self, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """Generate client summary data"""
        
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
        
        client_filter, client_params = self.get_client_filter()
        
        # Client information and ticket summary
        if self.user_role in ['client_admin', 'solicitante']:
            # Single client view
            client_query = f"""
            SELECT 
                c.name as client_name,
                c.rfc,
                c.email,
                c.phone,
                COUNT(DISTINCT s.site_id) as total_sites,
                COUNT(DISTINCT u.user_id) as total_users,
                COUNT(t.ticket_id) as total_tickets,
                COUNT(CASE WHEN t.status IN ('nuevo', 'asignado', 'en_proceso') THEN 1 END) as open_tickets,
                COUNT(CASE WHEN t.status IN ('resuelto', 'cerrado') THEN 1 END) as closed_tickets
            FROM clients c
            LEFT JOIN sites s ON c.client_id = s.client_id AND s.is_active = true
            LEFT JOIN users u ON c.client_id = u.client_id AND u.is_active = true
            LEFT JOIN tickets t ON c.client_id = t.client_id 
                AND t.created_at >= %s AND t.created_at <= %s
            WHERE c.is_active = true {client_filter}
            GROUP BY c.client_id, c.name, c.rfc, c.email, c.phone
            """
            params = [date_from, date_to] + client_params
            client_data = self.db_manager.execute_query(client_query, tuple(params), fetch='all')
        else:
            # Multi-client view for superadmin/technician
            client_query = """
            SELECT 
                c.name as client_name,
                c.rfc,
                COUNT(DISTINCT s.site_id) as total_sites,
                COUNT(DISTINCT u.user_id) as total_users,
                COUNT(t.ticket_id) as total_tickets,
                COUNT(CASE WHEN t.status IN ('nuevo', 'asignado', 'en_proceso') THEN 1 END) as open_tickets,
                COUNT(CASE WHEN t.status IN ('resuelto', 'cerrado') THEN 1 END) as closed_tickets
            FROM clients c
            LEFT JOIN sites s ON c.client_id = s.client_id AND s.is_active = true
            LEFT JOIN users u ON c.client_id = u.client_id AND u.is_active = true
            LEFT JOIN tickets t ON c.client_id = t.client_id 
                AND t.created_at >= %s AND t.created_at <= %s
            WHERE c.is_active = true
            GROUP BY c.client_id, c.name, c.rfc
            ORDER BY total_tickets DESC
            LIMIT 20
            """
            client_data = self.db_manager.execute_query(client_query, (date_from, date_to), fetch='all')
        
        return {
            'report_title': 'Reporte Resumen de Clientes',
            'date_range': f"{date_from} a {date_to}",
            'client_data': client_data,
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'generated_by': self.user_claims.get('name', 'Usuario'),
            'user_role': self.user_role
        }

class PDFReportFormatter:
    """Professional PDF report formatter with charts and branding"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.doc = SimpleDocTemplate(file_path, pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.story = []

        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=HexColor('#2c3e50'),
            alignment=1  # Center
        )

        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=HexColor('#34495e')
        )

    def add_header(self, title: str, subtitle: str = None):
        """Add professional header with branding"""
        # Company header
        company_header = Paragraph(
            "<b>LANET Helpdesk V3</b><br/>Sistema de Gestión de Tickets Empresarial",
            ParagraphStyle('CompanyHeader',
                          fontSize=12,
                          textColor=HexColor('#7f8c8d'),
                          alignment=1)
        )
        self.story.append(company_header)
        self.story.append(Spacer(1, 20))

        # Report title
        self.story.append(Paragraph(title, self.title_style))
        if subtitle:
            self.story.append(Paragraph(subtitle, self.styles['Normal']))
        self.story.append(Spacer(1, 20))

    def add_summary_table(self, data: Dict[str, Any], title: str):
        """Add a summary statistics table"""
        self.story.append(Paragraph(title, self.header_style))

        # Convert data to table format
        table_data = []
        for key, value in data.items():
            if value is not None:
                if isinstance(value, float):
                    value = f"{value:.2f}"
                table_data.append([key.replace('_', ' ').title(), str(value)])

        if table_data:
            table = Table(table_data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#2c3e50')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ffffff')),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdc3c7'))
            ]))
            self.story.append(table)
            self.story.append(Spacer(1, 20))

    def add_data_table(self, data: List[Dict], title: str, columns: List[str]):
        """Add a data table with proper formatting"""
        if not data:
            return

        self.story.append(Paragraph(title, self.header_style))

        # Prepare table data
        headers = [col.replace('_', ' ').title() for col in columns]
        table_data = [headers]

        for row in data:
            row_data = []
            for col in columns:
                value = row.get(col, '')
                if isinstance(value, float):
                    value = f"{value:.2f}"
                elif value is None:
                    value = 'N/A'
                row_data.append(str(value))
            table_data.append(row_data)

        # Create table
        col_width = 6.5 * inch / len(columns)
        table = Table(table_data, colWidths=[col_width] * len(columns))
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdc3c7')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#f8f9fa')])
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 20))

    def add_footer(self, generated_by: str, generated_at: str):
        """Add report footer"""
        footer_text = f"<i>Generado por: {generated_by}<br/>Fecha: {generated_at}</i>"
        footer = Paragraph(footer_text,
                          ParagraphStyle('Footer',
                                        fontSize=8,
                                        textColor=HexColor('#7f8c8d'),
                                        alignment=1))
        self.story.append(Spacer(1, 30))
        self.story.append(footer)

    def build(self):
        """Build the PDF document"""
        self.doc.build(self.story)

class ExcelReportFormatter:
    """Professional Excel report formatter with charts and formatting"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.workbook = None
        self.worksheets = {}

    def create_workbook(self):
        """Create Excel workbook with pandas"""
        import pandas as pd
        self.workbook = pd.ExcelWriter(self.file_path, engine='openpyxl')

    def add_summary_sheet(self, data: Dict[str, Any], sheet_name: str = 'Resumen'):
        """Add summary sheet with key metrics"""
        if not self.workbook:
            self.create_workbook()

        # Create summary data
        summary_data = []
        for key, value in data.items():
            if value is not None and key not in ['report_title', 'date_range', 'generated_at', 'generated_by', 'user_role']:
                summary_data.append({
                    'Métrica': key.replace('_', ' ').title(),
                    'Valor': value
                })

        if summary_data:
            df = pd.DataFrame(summary_data)
            df.to_excel(self.workbook, sheet_name=sheet_name, index=False)

    def add_data_sheet(self, data: List[Dict], sheet_name: str, title: str = None):
        """Add data sheet with proper formatting"""
        if not self.workbook:
            self.create_workbook()

        if data:
            df = pd.DataFrame(data)
            # Clean column names
            df.columns = [col.replace('_', ' ').title() for col in df.columns]
            df.to_excel(self.workbook, sheet_name=sheet_name, index=False)

    def save(self):
        """Save the Excel file"""
        if self.workbook:
            self.workbook.close()
