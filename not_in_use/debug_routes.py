#!/usr/bin/env python3
import sys
sys.path.append('backend')

from flask import Flask
from modules.assets.routes import assets_bp

app = Flask(__name__)
app.register_blueprint(assets_bp, url_prefix='/api/assets')

print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.endpoint}: {rule.rule} {list(rule.methods)}")

print(f"\nTotal routes: {len(list(app.url_map.iter_rules()))}")

# Test if we can access the blueprint functions directly
print(f"\nBlueprint view functions:")
for endpoint, func in assets_bp.view_functions.items():
    print(f"  {endpoint}: {func}")
