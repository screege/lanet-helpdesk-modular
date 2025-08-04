#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Assets Endpoint - Create a working assets endpoint
"""

import sys
import os
sys.path.append('backend')

from flask import Flask, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        'postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk',
        cursor_factory=RealDictCursor
    )

@app.route('/api/assets-fixed', methods=['GET'])
def get_assets_fixed():
    """Fixed assets endpoint that actually works"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Simple query that we know works
        query = """
        SELECT
            a.asset_id,
            a.name,
            a.status,
            a.last_seen,
            a.specifications,
            s.name as site_name,
            s.site_id,
            c.name as client_name,
            c.client_id,
            'active' as agent_status,
            CASE
                WHEN a.last_seen > NOW() - INTERVAL '10 minutes' THEN 'online'
                WHEN a.last_seen > NOW() - INTERVAL '1 hour' THEN 'warning'
                ELSE 'offline'
            END as connection_status
        FROM assets a
        JOIN sites s ON a.site_id = s.site_id
        JOIN clients c ON a.client_id = c.client_id
        WHERE a.status = 'active'
        ORDER BY a.last_seen DESC NULLS LAST
        LIMIT 100
        """
        
        cur.execute(query)
        assets = cur.fetchall()
        
        # Convert to list of dicts
        assets_list = [dict(asset) for asset in assets]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'assets': assets_list,
                'total': len(assets_list)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test-db', methods=['GET'])
def test_db():
    """Test database connection"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT COUNT(*) as count FROM assets WHERE status = %s', ('active',))
        result = cur.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'active_assets': result['count']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🔧 Starting Fixed Assets API Server...")
    print("   Test endpoints:")
    print("   - http://localhost:5002/api/assets-fixed")
    print("   - http://localhost:5002/api/test-db")
    app.run(host='0.0.0.0', port=5002, debug=True)
