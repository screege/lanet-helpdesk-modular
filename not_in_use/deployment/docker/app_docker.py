#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Docker-specific Application Entry Point
This file extends the main app.py with Docker-specific CORS configuration
without modifying the development environment
"""

import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend')
sys.path.insert(0, backend_dir)

from app import create_app
from flask_cors import CORS

def create_docker_app():
    """Create Flask app with Docker-specific configuration"""
    # Create the base app
    app = create_app('production')
    
    # Override CORS configuration for Docker environment
    # This allows both development and Docker origins
    CORS(app,
         origins=[
             # Development origins (preserve existing functionality)
             'http://localhost:5173', 'http://127.0.0.1:5173',
             'http://localhost:5174', 'http://127.0.0.1:5174', 
             'http://localhost:5175', 'http://127.0.0.1:5175',
             # Docker origins (add new functionality)
             'http://localhost', 'http://127.0.0.1',
             'http://localhost:80', 'http://127.0.0.1:80',
             'http://localhost:443', 'http://127.0.0.1:443',
             # Production origins (for future use)
             'https://helpdesk.lanet.mx', 'https://api.helpdesk.lanet.mx'
         ],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         supports_credentials=True)
    
    print("🐳 Docker-specific CORS configuration applied", flush=True)
    print(f"🐳 Allowed origins: {app.config.get('CORS_ORIGINS', 'Not set')}", flush=True)
    
    return app

if __name__ == '__main__':
    import sys
    sys.stdout.flush()
    print("🐳 STARTING DOCKER FLASK APP", flush=True)
    app = create_docker_app()
    print("🐳 DOCKER FLASK APP CREATED, STARTING SERVER", flush=True)
    app.run(host='0.0.0.0', port=5001, debug=False)
