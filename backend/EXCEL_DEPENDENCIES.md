# Excel Report Dependencies Documentation

## Overview
This document lists all dependencies required for the Excel report functionality in LANET Helpdesk V3.

## Core Excel Report Dependencies

### Required Packages (in requirements.txt)

#### Excel Generation
- **openpyxl==3.1.2** - Primary Excel file generation library
  - Used for creating .xlsx files with professional formatting
  - Supports styles, fonts, borders, and cell formatting
  - Required for: `_create_clean_excel_report()`, `_create_simple_excel_report()`

#### Data Processing  
- **pandas==2.3.1** - Data manipulation and analysis
  - Used for DataFrame operations and Excel export
  - Required for: `_create_comprehensive_excel_report()`
  - Provides robust Excel export capabilities

#### Database Connectivity
- **psycopg2-binary==2.9.7** - PostgreSQL database adapter
  - Required for all database queries to fetch ticket data
  - Used in: ticket queries, resolution data joins

#### Date/Time Handling
- **pytz==2023.3** - Timezone handling
  - Required for Mexico timezone conversions in reports
  - Used in: date formatting, schedule calculations

#### Web Framework
- **Flask==2.3.3** - Web framework
  - Required for API endpoints and request handling
  - Used in: report generation endpoints

#### PDF Generation (Optional)
- **reportlab==4.0.4** - PDF generation library
  - Used for PDF report formats (alternative to Excel)
  - Required for: PDF export functionality

## Standard Library Dependencies

### Built-in Modules Used
- **csv** - CSV file generation (fallback format)
- **os** - File system operations
- **logging** - Error tracking and debugging
- **datetime** - Date/time operations
- **uuid** - Unique identifier generation
- **traceback** - Error reporting

## Database Schema Dependencies

### Required Tables
- **tickets** - Main ticket data
- **ticket_resolutions** - Resolution text and timestamps
- **clients** - Client information
- **sites** - Site information  
- **users** - Technician assignments

### Critical Joins
```sql
-- Resolution data join (CRITICAL for Excel reports)
LEFT JOIN ticket_resolutions tr ON t.ticket_id = tr.ticket_id
```

## File System Requirements

### Directory Structure
```
backend/
├── modules/reports/
│   └── monthly_reports.py
├── reports_files/          # Generated Excel files
└── requirements.txt
```

### Permissions Required
- Read/Write access to `reports_files/` directory
- Database connection permissions
- File creation permissions

## Version Compatibility

### Python Version
- **Python 3.10+** recommended
- Tested with Python 3.10.9

### Key Version Notes
- **pandas 2.3.1** - Updated from 2.0.3 for better Excel compatibility
- **openpyxl 3.1.2** - Stable version with all required features
- **psycopg2-binary 2.9.7** - Latest stable PostgreSQL adapter

## Installation Commands

### Fresh Installation
```bash
cd backend
pip install -r requirements.txt
```

### Individual Package Installation
```bash
pip install openpyxl==3.1.2
pip install pandas==2.3.1
pip install psycopg2-binary==2.9.7
pip install pytz==2023.3
```

## Troubleshooting

### Common Issues
1. **Excel file corruption** - Resolved by using `_safe_clean_string()` methods
2. **Missing resolution data** - Fixed by joining with `ticket_resolutions` table
3. **Date formatting** - Handled by `_safe_date_format()` methods

### Verification Script
Run `python check_dependencies.py` to verify all dependencies are installed correctly.

## Changes Made for Excel Fix

### Database Query Updates
- Added `LEFT JOIN ticket_resolutions tr ON t.ticket_id = tr.ticket_id`
- Changed from `t.resolution_notes` to `tr.resolution_notes`

### Excel Structure Updates  
- Added separate "Fecha Resolución" and "Resolución" columns
- Updated column widths for 11-column layout
- Enhanced professional formatting

### Requirements Updates
- Updated pandas from 2.0.3 to 2.3.1
- All other dependencies verified and confirmed

## Status: ✅ COMPLETE
All dependencies are properly documented and installed. Excel report functionality is fully operational.
