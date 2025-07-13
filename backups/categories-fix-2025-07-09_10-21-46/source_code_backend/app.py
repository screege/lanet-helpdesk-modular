#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Main Application
Complete modular architecture implementation
Based on helpdesk_msp_architecture.md blueprint
"""

import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import logging
from logging.handlers import RotatingFileHandler

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import DatabaseManager
from core.auth import AuthManager
from core.response import ResponseManager
from utils.validators import ValidationUtils
from utils.security import SecurityUtils

# Import module blueprints
from modules.auth.routes import auth_bp
from modules.users.routes import users_bp
from modules.clients.routes import clients_bp
from modules.sites.routes import sites_bp
from modules.tickets.routes import tickets_bp
from modules.categories.routes import categories_bp
from modules.dashboard.routes import dashboard_bp
from modules.sla.routes import sla_bp
from modules.email.routes import email_bp

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['JSON_AS_ASCII'] = False  # Critical for UTF-8 support
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire for development
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
    app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), 'uploads'))
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions - CORS for frontend (supports multiple ports)
    CORS(app,
         origins=['http://localhost:5173', 'http://127.0.0.1:5173',
                 'http://localhost:5174', 'http://127.0.0.1:5174',
                 'http://localhost:5175', 'http://127.0.0.1:5175'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         supports_credentials=True)
    jwt = JWTManager(app)
    
    # Initialize core managers
    app.db_manager = DatabaseManager(app.config['DATABASE_URL'])
    app.auth_manager = AuthManager(app.db_manager)
    app.response_manager = ResponseManager()
    
    # Initialize Redis
    try:
        app.redis_client = redis.from_url(app.config['REDIS_URL'])
        app.redis_client.ping()
        app.logger.info("Redis connection established")
    except Exception as e:
        app.logger.error(f"Redis connection failed: {e}")
        app.redis_client = None
    
    # Setup logging
    setup_logging(app)

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return app.response_manager.error('Token has expired', 401)
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return app.response_manager.error('Invalid token', 401)
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return app.response_manager.error('Authorization token required', 401)
    
    # Request context processors
    @app.before_request
    def before_request():
        """Set up request context and RLS"""
        # AGGRESSIVE request logging for debugging
        print("=" * 80, flush=True)
        print(f"🔥 INCOMING REQUEST: {request.method} {request.url}", flush=True)
        print(f"🔥 Headers: {dict(request.headers)}", flush=True)
        print(f"🔥 Remote addr: {request.remote_addr}", flush=True)
        print("=" * 80, flush=True)

        if request.method == 'POST' and 'tickets' in request.url:
            print("🎫" * 20, flush=True)
            print("🎫 TICKET POST REQUEST DETECTED!", flush=True)
            print(f"🎫 URL: {request.url}", flush=True)
            print(f"🎫 Method: {request.method}", flush=True)
            print(f"🎫 Content-Type: {request.content_type}", flush=True)
            print(f"🎫 Authorization: {request.headers.get('Authorization', 'NONE')[:50]}...", flush=True)
            try:
                data = request.get_json(force=True)
                print(f"🎫 JSON Data: {data}", flush=True)
            except Exception as e:
                print(f"🎫 JSON Parse Error: {e}", flush=True)
                print(f"🎫 Raw Data: {request.get_data()}", flush=True)
            print("🎫" * 20, flush=True)

        g.start_time = datetime.utcnow()

        # Skip RLS setup for auth endpoints
        if request.endpoint and request.endpoint.startswith('auth.'):
            return
            
        # Set up RLS context for authenticated requests
        if request.headers.get('Authorization'):
            try:
                from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
                verify_jwt_in_request()
                
                user_id = get_jwt_identity()
                claims = get_jwt()
                
                if user_id and claims:
                    app.db_manager.set_rls_context(
                        user_id=user_id,
                        user_role=claims.get('role'),
                        client_id=claims.get('client_id'),
                        site_ids=claims.get('site_ids', [])
                    )
                    
                    # Store in g for easy access
                    g.current_user_id = user_id
                    g.current_user_role = claims.get('role')
                    g.current_client_id = claims.get('client_id')
                    g.current_site_ids = claims.get('site_ids', [])
                    
            except Exception as e:
                app.logger.warning(f"RLS context setup failed: {e}")

    print("🔧 BEFORE_REQUEST FUNCTION REGISTERED!", flush=True)

    @app.after_request
    def after_request(response):
        """Log request and add security headers"""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Log request
        duration = datetime.utcnow() - g.start_time
        app.logger.info(f"{request.method} {request.path} - {response.status_code} - {duration.total_seconds():.3f}s")
        
        return response
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        try:
            # Test database connection
            with app.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT 1')
            
            # Test Redis connection
            redis_status = 'connected' if app.redis_client and app.redis_client.ping() else 'disconnected'
            
            return app.response_manager.success({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'database': 'connected',
                'redis': redis_status,
                'version': '3.0.0'
            })
        except Exception as e:
            return app.response_manager.error(f'Health check failed: {str(e)}', 500)
    
    # Register module blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(clients_bp, url_prefix='/api/clients')
    app.register_blueprint(sites_bp, url_prefix='/api/sites')
    app.register_blueprint(tickets_bp, url_prefix='/api/tickets')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(sla_bp, url_prefix='/api/sla')
    app.register_blueprint(email_bp, url_prefix='/api/email')
    
    # Global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return app.response_manager.error('Bad request', 400)
    
    @app.errorhandler(401)
    def unauthorized(error):
        return app.response_manager.error('Unauthorized', 401)
    
    @app.errorhandler(403)
    def forbidden(error):
        return app.response_manager.error('Forbidden', 403)
    
    @app.errorhandler(404)
    def not_found(error):
        return app.response_manager.error('Resource not found', 404)
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal error: {error}')
        return app.response_manager.error('Internal server error', 500)
    
    return app

def setup_logging(app):
    """Setup application logging"""
    if not app.debug:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Setup file handler
        file_handler = RotatingFileHandler(
            os.path.join(logs_dir, 'app.log'),
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('LANET Helpdesk V3 startup')

if __name__ == '__main__':
    import sys
    sys.stdout.flush()
    print("🚀 STARTING FLASK APP WITH DEBUGGING", flush=True)
    app = create_app()
    print("🚀 FLASK APP CREATED, STARTING SERVER", flush=True)
    app.run(host='0.0.0.0', port=5001, debug=True)
