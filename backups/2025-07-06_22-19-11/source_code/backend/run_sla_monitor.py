#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - SLA Monitor Runner
Script to run SLA monitoring job
"""

import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables from .env file
env_file = backend_dir / '.env'
if env_file.exists():
    load_dotenv(env_file)
    print(f"Loaded environment variables from {env_file}")
else:
    print(f"Warning: .env file not found at {env_file}")

# Configure logging
log_dir = backend_dir / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'sla_monitor.log'),
        logging.StreamHandler()
    ]
)

if __name__ == '__main__':
    from jobs.sla_monitor import run_continuous_monitor
    
    # Get interval from command line argument or use default
    interval = 5  # Default 5 minutes
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            print("Invalid interval. Using default 5 minutes.")
    
    print(f"Starting SLA Monitor with {interval} minute interval...")
    print("Press Ctrl+C to stop")
    
    try:
        run_continuous_monitor(interval)
    except KeyboardInterrupt:
        print("\nSLA Monitor stopped.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
