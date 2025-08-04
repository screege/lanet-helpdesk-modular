#!/usr/bin/env python3
import sys
sys.path.append('backend')

from flask import Flask
from modules.assets.routes import assets_bp

# Create a simple Flask app
app = Flask(__name__)

# Register the blueprint
app.register_blueprint(assets_bp, url_prefix='/api/assets')

# Test route
@app.route('/test-app')
def test_app():
    return {'message': 'App test working!'}

if __name__ == '__main__':
    print("Starting simple test app...")
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.rule}")
    
    app.run(host='0.0.0.0', port=5002, debug=False)
