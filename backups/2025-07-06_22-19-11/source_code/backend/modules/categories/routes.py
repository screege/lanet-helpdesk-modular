#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Categories Routes
Hierarchical category management for ticket classification
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils.security import require_role

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all categories with hierarchical structure"""
    try:
        # Get all categories ordered by parent_id and sort_order
        query = """
        SELECT c.category_id, c.parent_id, c.name, c.description, c.color, c.icon,
               c.is_active, c.sort_order, c.auto_assign_to, c.sla_response_hours,
               c.sla_resolution_hours, c.created_at, c.updated_at,
               u.name as auto_assign_to_name
        FROM categories c
        LEFT JOIN users u ON c.auto_assign_to = u.user_id
        WHERE c.is_active = true
        ORDER BY c.parent_id NULLS FIRST, c.sort_order, c.name
        """
        
        categories = current_app.db_manager.execute_query(query)
        
        # Build hierarchical structure
        categories_dict = {}
        root_categories = []
        
        # First pass: create all category objects
        for cat in (categories or []):
            formatted_cat = current_app.response_manager.format_category_data(cat)
            formatted_cat['children'] = []
            categories_dict[cat['category_id']] = formatted_cat
            
            if not cat['parent_id']:
                root_categories.append(formatted_cat)
        
        # Second pass: build hierarchy
        for cat in (categories or []):
            if cat['parent_id'] and cat['parent_id'] in categories_dict:
                parent = categories_dict[cat['parent_id']]
                child = categories_dict[cat['category_id']]
                parent['children'].append(child)
        
        return current_app.response_manager.success(root_categories)
        
    except Exception as e:
        current_app.logger.error(f"Get categories error: {e}")
        return current_app.response_manager.server_error('Failed to get categories')

@categories_bp.route('/', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def create_category():
    """Create a new category"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        # Validate required fields
        required_fields = ['name']
        for field in required_fields:
            if not data.get(field):
                return current_app.response_manager.bad_request(f'{field} is required')

        # Validate parent category exists if provided
        if data.get('parent_id'):
            if not current_app.db_manager.validate_uuid(data['parent_id']):
                return current_app.response_manager.bad_request('Invalid parent_id format')
            
            parent = current_app.db_manager.execute_query(
                "SELECT category_id FROM categories WHERE category_id = %s AND is_active = true",
                (data['parent_id'],),
                fetch='one'
            )
            if not parent:
                return current_app.response_manager.bad_request('Parent category not found')

        # Validate auto_assign_to user exists if provided
        if data.get('auto_assign_to'):
            if not current_app.db_manager.validate_uuid(data['auto_assign_to']):
                return current_app.response_manager.bad_request('Invalid auto_assign_to format')
            
            user = current_app.db_manager.execute_query(
                "SELECT user_id FROM users WHERE user_id = %s AND role IN ('technician', 'admin', 'superadmin')",
                (data['auto_assign_to'],),
                fetch='one'
            )
            if not user:
                return current_app.response_manager.bad_request('Auto-assign user not found or not a technician')

        # Prepare category data
        category_data = {
            'parent_id': data.get('parent_id'),
            'name': data['name'].strip(),
            'description': data.get('description', '').strip(),
            'color': data.get('color', '#6B7280'),
            'icon': data.get('icon', 'folder'),
            'sort_order': data.get('sort_order', 0),
            'auto_assign_to': data.get('auto_assign_to'),
            'sla_response_hours': data.get('sla_response_hours', 24),
            'sla_resolution_hours': data.get('sla_resolution_hours', 72)
        }

        # Insert category
        result = current_app.db_manager.execute_insert(
            'categories',
            category_data,
            returning='category_id, name, description, color, icon, created_at'
        )

        if result:
            current_app.logger.info(f"Category created: {result['name']}")
            return current_app.response_manager.created(result, 'Category created successfully')
        else:
            return current_app.response_manager.server_error('Failed to create category')

    except Exception as e:
        current_app.logger.error(f"Create category error: {e}")
        return current_app.response_manager.server_error('Failed to create category')

@categories_bp.route('/<category_id>', methods=['GET'])
@jwt_required()
def get_category(category_id):
    """Get category by ID with full details"""
    try:
        if not current_app.db_manager.validate_uuid(category_id):
            return current_app.response_manager.bad_request('Invalid category ID format')

        query = """
        SELECT c.category_id, c.parent_id, c.name, c.description, c.color, c.icon,
               c.is_active, c.sort_order, c.auto_assign_to, c.sla_response_hours,
               c.sla_resolution_hours, c.created_at, c.updated_at,
               u.name as auto_assign_to_name,
               parent.name as parent_name
        FROM categories c
        LEFT JOIN users u ON c.auto_assign_to = u.user_id
        LEFT JOIN categories parent ON c.parent_id = parent.category_id
        WHERE c.category_id = %s
        """
        
        category = current_app.db_manager.execute_query(query, (category_id,), fetch='one')
        
        if not category:
            return current_app.response_manager.not_found('Category')

        formatted_category = current_app.response_manager.format_category_data(category)
        return current_app.response_manager.success(formatted_category)
        
    except Exception as e:
        current_app.logger.error(f"Get category error: {e}")
        return current_app.response_manager.server_error('Failed to get category')

@categories_bp.route('/<category_id>', methods=['PUT'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def update_category(category_id):
    """Update an existing category"""
    try:
        if not current_app.db_manager.validate_uuid(category_id):
            return current_app.response_manager.bad_request('Invalid category ID format')

        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        # Check if category exists
        existing = current_app.db_manager.execute_query(
            "SELECT category_id FROM categories WHERE category_id = %s",
            (category_id,),
            fetch='one'
        )
        if not existing:
            return current_app.response_manager.not_found('Category')

        # Validate parent category if provided
        if data.get('parent_id'):
            if data['parent_id'] == category_id:
                return current_app.response_manager.bad_request('Category cannot be its own parent')
            
            parent = current_app.db_manager.execute_query(
                "SELECT category_id FROM categories WHERE category_id = %s AND is_active = true",
                (data['parent_id'],),
                fetch='one'
            )
            if not parent:
                return current_app.response_manager.bad_request('Parent category not found')

        # Validate auto_assign_to user if provided
        if data.get('auto_assign_to'):
            user = current_app.db_manager.execute_query(
                "SELECT user_id FROM users WHERE user_id = %s AND role IN ('technician', 'admin', 'superadmin')",
                (data['auto_assign_to'],),
                fetch='one'
            )
            if not user:
                return current_app.response_manager.bad_request('Auto-assign user not found or not a technician')

        # Prepare update data
        update_data = {}
        allowed_fields = [
            'parent_id', 'name', 'description', 'color', 'icon', 'is_active',
            'sort_order', 'auto_assign_to', 'sla_response_hours', 'sla_resolution_hours'
        ]
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if update_data:
            update_data['updated_at'] = 'CURRENT_TIMESTAMP'
            
            current_app.db_manager.execute_update(
                'categories',
                update_data,
                'category_id = %s',
                (category_id,)
            )

        # Get updated category
        updated_category = current_app.db_manager.execute_query(
            """
            SELECT c.category_id, c.parent_id, c.name, c.description, c.color, c.icon,
                   c.is_active, c.sort_order, c.auto_assign_to, c.sla_response_hours,
                   c.sla_resolution_hours, c.created_at, c.updated_at,
                   u.name as auto_assign_to_name
            FROM categories c
            LEFT JOIN users u ON c.auto_assign_to = u.user_id
            WHERE c.category_id = %s
            """,
            (category_id,),
            fetch='one'
        )

        formatted_category = current_app.response_manager.format_category_data(updated_category)
        return current_app.response_manager.success(formatted_category, 'Category updated successfully')

    except Exception as e:
        current_app.logger.error(f"Update category error: {e}")
        return current_app.response_manager.server_error('Failed to update category')

@categories_bp.route('/<category_id>', methods=['DELETE'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def delete_category(category_id):
    """Soft delete a category (mark as inactive)"""
    try:
        if not current_app.db_manager.validate_uuid(category_id):
            return current_app.response_manager.bad_request('Invalid category ID format')

        # Check if category exists
        category = current_app.db_manager.execute_query(
            "SELECT category_id, name FROM categories WHERE category_id = %s",
            (category_id,),
            fetch='one'
        )
        if not category:
            return current_app.response_manager.not_found('Category')

        # Check if category has active children
        children = current_app.db_manager.execute_query(
            "SELECT COUNT(*) as count FROM categories WHERE parent_id = %s AND is_active = true",
            (category_id,),
            fetch='one'
        )
        if children and children['count'] > 0:
            return current_app.response_manager.bad_request('Cannot delete category with active subcategories')

        # Check if category is used in tickets
        tickets = current_app.db_manager.execute_query(
            "SELECT COUNT(*) as count FROM tickets WHERE category_id = %s",
            (category_id,),
            fetch='one'
        )
        if tickets and tickets['count'] > 0:
            # Soft delete - mark as inactive
            current_app.db_manager.execute_update(
                'categories',
                {'is_active': False, 'updated_at': 'CURRENT_TIMESTAMP'},
                'category_id = %s',
                (category_id,)
            )
            message = f"Category '{category['name']}' marked as inactive (has associated tickets)"
        else:
            # Hard delete if no tickets
            current_app.db_manager.execute_query(
                "DELETE FROM categories WHERE category_id = %s",
                (category_id,),
                fetch='none'
            )
            message = f"Category '{category['name']}' deleted successfully"

        current_app.logger.info(f"Category deleted: {category['name']}")
        return current_app.response_manager.success({'message': message})

    except Exception as e:
        current_app.logger.error(f"Delete category error: {e}")
        return current_app.response_manager.server_error('Failed to delete category')

@categories_bp.route('/flat', methods=['GET'])
@jwt_required()
def get_categories_flat():
    """Get all categories as flat list with full hierarchical paths (for dropdowns)"""
    try:
        # Use categories table (the one managed by administrators)
        query = """
        SELECT
            c.category_id, c.parent_id, c.name, c.description,
            c.color, c.icon, c.is_active,
            CASE
                WHEN c.parent_id IS NULL THEN c.name
                ELSE COALESCE(p.name, '') || ' > ' || c.name
            END as full_path
        FROM categories c
        LEFT JOIN categories p ON c.parent_id = p.category_id
        WHERE c.is_active = true
        ORDER BY c.name
        """

        categories = current_app.db_manager.execute_query(query)

        formatted_categories = []
        for cat in (categories or []):
            formatted_cat = {
                'category_id': cat['category_id'],
                'parent_id': cat['parent_id'],
                'name': cat['name'],
                'description': cat.get('description'),
                'color': cat.get('color'),
                'icon': cat.get('icon'),
                'full_path': cat['full_path'],
                'is_active': cat['is_active']
            }
            formatted_categories.append(formatted_cat)

        return current_app.response_manager.success(formatted_categories)

    except Exception as e:
        current_app.logger.error(f"Get flat categories error: {e}")
        return current_app.response_manager.server_error('Failed to get categories')

@categories_bp.route('/tree', methods=['GET'])
@jwt_required()
def get_categories_tree():
    """Get categories with full hierarchical tree structure and statistics"""
    try:
        # Get all categories with statistics
        query = """
        SELECT
            c.category_id, c.parent_id, c.name, c.description, c.color, c.icon,
            c.is_active, c.sort_order, c.auto_assign_to, c.sla_response_hours,
            c.sla_resolution_hours, c.created_at, c.updated_at,
            u.name as auto_assign_to_name,
            (SELECT COUNT(*) FROM tickets t WHERE t.category_id = c.category_id) as direct_ticket_count,
            (SELECT COUNT(*) FROM categories sub WHERE sub.parent_id = c.category_id AND sub.is_active = true) as subcategory_count
        FROM categories c
        LEFT JOIN users u ON c.auto_assign_to = u.user_id
        WHERE c.is_active = true
        ORDER BY c.parent_id NULLS FIRST, c.sort_order, c.name
        """

        categories = current_app.db_manager.execute_query(query)

        # Build hierarchical structure with statistics
        categories_dict = {}
        root_categories = []

        # First pass: create all category objects
        for cat in (categories or []):
            formatted_cat = current_app.response_manager.format_category_data(cat)
            formatted_cat['children'] = []
            formatted_cat['total_ticket_count'] = cat['direct_ticket_count']  # Will be updated with recursive count
            categories_dict[cat['category_id']] = formatted_cat

            if not cat['parent_id']:
                root_categories.append(formatted_cat)

        # Second pass: build hierarchy and calculate recursive ticket counts
        def calculate_recursive_ticket_count(category):
            total = category['direct_ticket_count']
            for child_id in [c['category_id'] for c in categories if c['parent_id'] == category['category_id']]:
                if child_id in categories_dict:
                    child = categories_dict[child_id]
                    category['children'].append(child)
                    total += calculate_recursive_ticket_count(child)
            category['total_ticket_count'] = total
            return total

        # Calculate recursive counts for root categories
        for root_cat in root_categories:
            calculate_recursive_ticket_count(root_cat)

        return current_app.response_manager.success(root_categories)

    except Exception as e:
        current_app.logger.error(f"Get categories tree error: {e}")
        return current_app.response_manager.server_error('Failed to get categories tree')

@categories_bp.route('/<category_id>/move', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def move_category(category_id):
    """Move a category to a different parent or change its position"""
    try:
        if not current_app.db_manager.validate_uuid(category_id):
            return current_app.response_manager.bad_request('Invalid category ID format')

        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        new_parent_id = data.get('new_parent_id')
        new_sort_order = data.get('new_sort_order', 0)

        # Validate that category exists
        category = current_app.db_manager.execute_query(
            "SELECT category_id, name FROM categories WHERE category_id = %s",
            (category_id,),
            fetch='one'
        )
        if not category:
            return current_app.response_manager.not_found('Category')

        # Validate new parent (if provided)
        if new_parent_id:
            if new_parent_id == category_id:
                return current_app.response_manager.bad_request('Category cannot be its own parent')

            # Check for circular reference using recursive CTE
            circular_check = current_app.db_manager.execute_query("""
                WITH RECURSIVE category_ancestors AS (
                    SELECT category_id, parent_id, 1 as level
                    FROM categories
                    WHERE category_id = %s

                    UNION ALL

                    SELECT c.category_id, c.parent_id, ca.level + 1
                    FROM categories c
                    INNER JOIN category_ancestors ca ON c.category_id = ca.parent_id
                    WHERE ca.level < 10  -- Prevent infinite recursion
                )
                SELECT COUNT(*) as count
                FROM category_ancestors
                WHERE category_id = %s
            """, (new_parent_id, category_id), fetch='one')

            if circular_check and circular_check['count'] > 0:
                return current_app.response_manager.bad_request('Cannot create circular reference')

            # Validate parent exists
            parent = current_app.db_manager.execute_query(
                "SELECT category_id FROM categories WHERE category_id = %s AND is_active = true",
                (new_parent_id,),
                fetch='one'
            )
            if not parent:
                return current_app.response_manager.bad_request('Parent category not found')

        # Update category
        update_data = {
            'parent_id': new_parent_id,
            'sort_order': new_sort_order,
            'updated_at': 'CURRENT_TIMESTAMP'
        }

        current_app.db_manager.execute_update(
            'categories',
            update_data,
            'category_id = %s',
            (category_id,)
        )

        current_app.logger.info(f"Category moved: {category['name']}")
        return current_app.response_manager.success({'message': 'Category moved successfully'})

    except Exception as e:
        current_app.logger.error(f"Move category error: {e}")
        return current_app.response_manager.server_error('Failed to move category')

@categories_bp.route('/<category_id>/reorder', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def reorder_categories(category_id):
    """Reorder categories within the same parent"""
    try:
        data = request.get_json()
        if not data or 'sibling_orders' not in data:
            return current_app.response_manager.bad_request('Sibling orders required')

        sibling_orders = data['sibling_orders']  # List of {category_id, sort_order}

        # Validate all category IDs
        for item in sibling_orders:
            if not current_app.db_manager.validate_uuid(item.get('category_id')):
                return current_app.response_manager.bad_request('Invalid category ID format')

        # Update sort orders in a transaction
        for item in sibling_orders:
            current_app.db_manager.execute_update(
                'categories',
                {'sort_order': item['sort_order'], 'updated_at': 'CURRENT_TIMESTAMP'},
                'category_id = %s',
                (item['category_id'],)
            )

        return current_app.response_manager.success({'message': 'Categories reordered successfully'})

    except Exception as e:
        current_app.logger.error(f"Reorder categories error: {e}")
        return current_app.response_manager.server_error('Failed to reorder categories')

@categories_bp.route('/search', methods=['GET'])
@jwt_required()
def search_categories():
    """Search categories by name or description"""
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return current_app.response_manager.bad_request('Search term required')

        # Search with full path context
        query = """
        WITH RECURSIVE category_paths AS (
            SELECT
                c.category_id,
                c.parent_id,
                c.name,
                c.description,
                c.color,
                c.icon,
                c.auto_assign_to,
                c.sla_response_hours,
                c.sla_resolution_hours,
                c.name as full_path,
                0 as level
            FROM categories c
            WHERE c.parent_id IS NULL AND c.is_active = true

            UNION ALL

            SELECT
                c.category_id,
                c.parent_id,
                c.name,
                c.description,
                c.color,
                c.icon,
                c.auto_assign_to,
                c.sla_response_hours,
                c.sla_resolution_hours,
                cp.full_path || ' > ' || c.name as full_path,
                cp.level + 1
            FROM categories c
            INNER JOIN category_paths cp ON c.parent_id = cp.category_id
            WHERE c.is_active = true
        )
        SELECT
            cp.*,
            u.name as auto_assign_to_name,
            (SELECT COUNT(*) FROM tickets t WHERE t.category_id = cp.category_id) as ticket_count
        FROM category_paths cp
        LEFT JOIN users u ON cp.auto_assign_to = u.user_id
        WHERE
            cp.name ILIKE %s
            OR cp.description ILIKE %s
            OR cp.full_path ILIKE %s
        ORDER BY cp.level, cp.name
        """

        search_pattern = f"%{search_term}%"
        categories = current_app.db_manager.execute_query(
            query,
            (search_pattern, search_pattern, search_pattern)
        )

        formatted_categories = []
        for cat in (categories or []):
            formatted_cat = current_app.response_manager.format_category_data(cat)
            formatted_categories.append(formatted_cat)

        return current_app.response_manager.success(formatted_categories)

    except Exception as e:
        current_app.logger.error(f"Search categories error: {e}")
        return current_app.response_manager.server_error('Failed to search categories')
