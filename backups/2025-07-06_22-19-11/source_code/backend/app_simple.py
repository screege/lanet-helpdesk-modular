#!/usr/bin/env python3
"""
Simple Flask app for testing SLA endpoints
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import logging

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import DatabaseManager
from core.auth import AuthManager
from core.response import ResponseManager
from modules.sla.routes import sla_bp

def create_simple_app():
    """Create a simple Flask app for testing"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['DATABASE_URL'] = 'postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk'
    
    # Initialize CORS
    CORS(app, origins=["http://localhost:5173"])
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize managers
    app.db_manager = DatabaseManager(app.config['DATABASE_URL'])
    app.auth_manager = AuthManager(app.db_manager)
    app.response_manager = ResponseManager()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    
    # Test login endpoint (no authentication required)
    @app.route('/api/auth/login', methods=['POST'])
    def test_login():
        """Test login endpoint that always succeeds"""
        try:
            data = request.get_json() or {}
            app.logger.info(f"Login attempt with data: {data}")

            # Always succeed for testing
            access_token = create_access_token(
                identity='test-user',
                additional_claims={
                    'role': 'superadmin',
                    'user_id': 'test-user-id',
                    'client_id': None,
                    'site_ids': []
                }
            )
            return jsonify({
                'success': True,
                'data': {
                    'access_token': access_token,
                    'user': {
                        'user_id': 'test-user-id',
                        'email': 'test@test.com',
                        'role': 'superadmin',
                        'name': 'Test User'
                    }
                }
            })
        except Exception as e:
            app.logger.error(f"Login error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # Test clients endpoint
    @app.route('/api/clients', methods=['GET'])
    def test_clients():
        """Test clients endpoint"""
        try:
            query = "SELECT client_id, name FROM clients WHERE is_active = true LIMIT 10"
            clients = app.db_manager.execute_query(query)
            return jsonify({
                'success': True,
                'data': clients or []
            })
        except Exception as e:
            app.logger.error(f"Error getting clients: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # Register SLA blueprint
    app.register_blueprint(sla_bp, url_prefix='/api/sla')
    
    # Test endpoint
    @app.route('/api/test', methods=['GET'])
    def test():
        return jsonify({'message': 'Simple Flask app is working!'})
    
    return app

if __name__ == '__main__':
    app = create_simple_app()
    print("🚀 Starting simple Flask app for SLA testing...")
    app.run(host='0.0.0.0', port=5001, debug=False)  # No debug to avoid loops
