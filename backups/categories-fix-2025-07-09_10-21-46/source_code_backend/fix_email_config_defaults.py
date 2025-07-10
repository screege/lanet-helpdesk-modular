#!/usr/bin/env python3
"""
Fix email configuration defaults for ticket creation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def fix_email_config_defaults():
    """Fix email configuration defaults"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Fixing Email Configuration Defaults")
        print("=" * 50)
        
        try:
            # Check current email configuration
            print("1. Checking current email configuration...")
            
            config = app.db_manager.execute_query("""
                SELECT config_id, name, default_category_id, default_priority, auto_assign_to
                FROM email_configurations 
                WHERE is_active = true
                LIMIT 1
            """, fetch='one')
            
            if not config:
                print("❌ No active email configuration found")
                return
            
            print(f"✅ Found email configuration: {config['name']}")
            print(f"   Config ID: {config['config_id']}")
            print(f"   Default Category ID: {config['default_category_id']}")
            print(f"   Default Priority: {config['default_priority']}")
            print(f"   Auto Assign To: {config['auto_assign_to']}")
            
            # Check if we need to set a default category
            if not config['default_category_id']:
                print("\n2. Setting default category...")
                
                # Find a default category to use
                category = app.db_manager.execute_query("""
                    SELECT category_id, name 
                    FROM categories 
                    WHERE is_active = true 
                    ORDER BY sort_order, name 
                    LIMIT 1
                """, fetch='one')
                
                if category:
                    print(f"   Found category: {category['name']} ({category['category_id']})")
                    
                    # Update the email configuration
                    app.db_manager.execute_query("""
                        UPDATE email_configurations 
                        SET default_category_id = %s
                        WHERE config_id = %s
                    """, (category['category_id'], config['config_id']), fetch='none')
                    
                    print("✅ Updated email configuration with default category")
                else:
                    print("❌ No categories found. Creating a default category...")
                    
                    # Create a default category
                    category_data = {
                        'name': 'General',
                        'description': 'Categoría general para tickets por email',
                        'color': '#6B7280',
                        'icon': 'folder',
                        'is_active': True,
                        'sort_order': 0,
                        'sla_response_hours': 24,
                        'sla_resolution_hours': 72
                    }
                    
                    category_id = app.db_manager.execute_insert('categories', category_data)
                    
                    if category_id:
                        print(f"✅ Created default category: {category_id}")
                        
                        # Update the email configuration
                        app.db_manager.execute_query("""
                            UPDATE email_configurations 
                            SET default_category_id = %s
                            WHERE config_id = %s
                        """, (category_id, config['config_id']), fetch='none')
                        
                        print("✅ Updated email configuration with new default category")
                    else:
                        print("❌ Failed to create default category")
            else:
                print("✅ Email configuration already has a default category")
            
            # Check if we need to set default priority
            if not config['default_priority']:
                print("\n3. Setting default priority...")
                
                app.db_manager.execute_query("""
                    UPDATE email_configurations 
                    SET default_priority = 'media'
                    WHERE config_id = %s
                """, (config['config_id'],), fetch='none')
                
                print("✅ Set default priority to 'media'")
            else:
                print("✅ Email configuration already has a default priority")
            
            # Verify the final configuration
            print("\n4. Verifying final configuration...")
            
            final_config = app.db_manager.execute_query("""
                SELECT ec.config_id, ec.name, ec.default_category_id, ec.default_priority, 
                       c.name as category_name
                FROM email_configurations ec
                LEFT JOIN categories c ON ec.default_category_id = c.category_id
                WHERE ec.config_id = %s
            """, (config['config_id'],), fetch='one')
            
            if final_config:
                print(f"✅ Final configuration:")
                print(f"   Name: {final_config['name']}")
                print(f"   Default Category: {final_config['category_name']} ({final_config['default_category_id']})")
                print(f"   Default Priority: {final_config['default_priority']}")
                print("\n🎉 Email configuration defaults fixed successfully!")
            else:
                print("❌ Failed to verify final configuration")
            
        except Exception as e:
            print(f"❌ Error fixing email configuration defaults: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_email_config_defaults()
