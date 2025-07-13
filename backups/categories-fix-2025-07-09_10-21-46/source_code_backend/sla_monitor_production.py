#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Production SLA Monitor
This is the CORRECT SLA monitor script that should be used in production.
Created during the technical issues resolution session.
"""

import sys
import os
import time
import logging
from datetime import datetime
from flask import Flask

# Add backend to path
sys.path.append(os.path.dirname(__file__))

from core.database import DatabaseManager
from modules.sla.service import sla_service

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'sla_monitor.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('SLA_Monitor_Production')

def setup_flask_app():
    """Setup Flask application context for SLA monitoring"""
    app = Flask(__name__)
    app.config['DATABASE_URL'] = 'postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk'
    
    # Initialize database manager
    app.db_manager = DatabaseManager(app.config['DATABASE_URL'])
    
    return app

def run_single_monitor_cycle():
    """Run a single SLA monitoring cycle using the enhanced SLA service"""
    app = setup_flask_app()
    
    with app.app_context():
        try:
            logger.info("🔍 Starting SLA monitoring cycle")
            
            # Use the enhanced run_sla_monitor method from the SLA service
            # This method was added during our technical issues resolution
            results = sla_service.run_sla_monitor()
            
            if 'error' in results:
                logger.error(f"❌ SLA monitoring failed: {results['error']}")
                return False
            
            # Log results
            logger.info(f"✅ SLA monitoring completed successfully:")
            logger.info(f"   - Breaches found: {results['breaches_found']}")
            logger.info(f"   - Warnings found: {results['warnings_found']}")
            logger.info(f"   - Escalations processed: {results['escalations_processed']}")
            logger.info(f"   - Notifications sent: {results['notifications_sent']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in SLA monitoring cycle: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

def run_continuous_monitor(interval_minutes: int = 15):
    """Run SLA monitoring continuously with specified interval"""
    logger.info(f"🚀 Starting continuous SLA monitoring (interval: {interval_minutes} minutes)")
    
    while True:
        try:
            success = run_single_monitor_cycle()
            
            if success:
                logger.info(f"😴 Sleeping for {interval_minutes} minutes until next cycle")
            else:
                logger.warning(f"⚠️ Last cycle failed, sleeping for {interval_minutes} minutes before retry")
            
            # Sleep until next cycle
            time.sleep(interval_minutes * 60)
            
        except KeyboardInterrupt:
            logger.info("🛑 SLA monitoring stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Unexpected error in monitoring loop: {e}")
            logger.info(f"🔄 Retrying in {interval_minutes} minutes")
            time.sleep(interval_minutes * 60)

def test_sla_monitor():
    """Test SLA monitoring functionality"""
    logger.info("🧪 Testing SLA monitoring functionality")
    
    app = setup_flask_app()
    
    with app.app_context():
        try:
            # Test business hours calculation
            from datetime import datetime, timedelta
            start_time = datetime.now()
            end_time = start_time + timedelta(hours=24)
            
            business_hours = sla_service.calculate_business_hours(start_time, end_time)
            logger.info(f"✅ Business hours calculation test: {business_hours} hours in 24-hour period")
            
            # Test SLA monitoring using the enhanced method
            results = sla_service.run_sla_monitor()
            
            if 'error' in results:
                logger.error(f"❌ SLA monitoring test failed: {results['error']}")
                return False
            
            logger.info(f"✅ SLA monitoring test completed:")
            logger.info(f"   - Breaches: {results['breaches_found']}")
            logger.info(f"   - Warnings: {results['warnings_found']}")
            logger.info(f"   - Escalations: {results['escalations_processed']}")
            logger.info(f"   - Notifications: {results['notifications_sent']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ SLA monitoring test error: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='LANET Helpdesk V3 Production SLA Monitor')
    parser.add_argument('--mode', choices=['test', 'single', 'continuous'], default='single',
                       help='Monitoring mode: test, single cycle, or continuous (default: single)')
    parser.add_argument('--interval', type=int, default=15,
                       help='Interval in minutes for continuous monitoring (default: 15)')
    
    args = parser.parse_args()
    
    # Ensure logs directory exists (already created above)
    pass
    
    if args.mode == 'test':
        logger.info("🧪 Running SLA monitor in TEST mode")
        success = test_sla_monitor()
        sys.exit(0 if success else 1)
    
    elif args.mode == 'single':
        logger.info("🔍 Running SLA monitor in SINGLE CYCLE mode")
        success = run_single_monitor_cycle()
        sys.exit(0 if success else 1)
    
    elif args.mode == 'continuous':
        logger.info(f"🔄 Running SLA monitor in CONTINUOUS mode (interval: {args.interval} minutes)")
        run_continuous_monitor(args.interval)
    
    else:
        logger.error("❌ Invalid mode specified")
        sys.exit(1)
