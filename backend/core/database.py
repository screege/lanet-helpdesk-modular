#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Database Manager
Handles PostgreSQL connections, RLS context, and query execution
"""

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
import logging
from typing import Dict, List, Any, Optional, Union
import uuid

class DatabaseManager:
    """Centralized database management with RLS support"""
    
    def __init__(self, database_url: str, min_connections: int = 1, max_connections: int = 20):
        self.database_url = database_url
        self.logger = logging.getLogger(__name__)
        
        try:
            # Create connection pool
            self.pool = ThreadedConnectionPool(
                min_connections,
                max_connections,
                database_url,
                cursor_factory=RealDictCursor
            )
            self.logger.info("Database connection pool created successfully")
        except Exception as e:
            self.logger.error(f"Failed to create database connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool"""
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)
    
    def set_rls_context(self, user_id: str, user_role: str, client_id: str = None, site_ids: List[str] = None):
        """Set RLS context for the current session"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Set user context
                    cur.execute("SELECT set_config('app.current_user_id', %s, false)", (str(user_id),))
                    cur.execute("SELECT set_config('app.current_user_role', %s, false)", (user_role,))
                    
                    # Set client context if provided
                    if client_id:
                        cur.execute("SELECT set_config('app.current_user_client_id', %s, false)", (str(client_id),))
                    
                    # Set site context if provided
                    if site_ids:
                        site_ids_str = ','.join(str(sid) for sid in site_ids)
                        cur.execute("SELECT set_config('app.current_user_site_ids', %s, false)", (site_ids_str,))
                    
                    conn.commit()
                    
        except Exception as e:
            self.logger.error(f"Failed to set RLS context: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None, fetch: str = 'all') -> Union[List[Dict], Dict, None]:
        """Execute a query and return results"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)

                    # Check if this is a modifying query (INSERT, UPDATE, DELETE)
                    is_modifying = query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE'))

                    if fetch == 'all':
                        result = cur.fetchall()
                        if is_modifying:
                            conn.commit()
                        return result
                    elif fetch == 'one':
                        result = cur.fetchone()
                        if is_modifying:
                            conn.commit()
                        return result
                    elif fetch == 'none':
                        conn.commit()
                        return None
                    else:
                        raise ValueError(f"Invalid fetch type: {fetch}")

        except Exception as e:
            self.logger.error(f"Query execution failed: {query[:100]}... Error: {e}")
            raise
    
    def execute_insert(self, table: str, data: Dict[str, Any], returning: str = None) -> Optional[Dict]:
        """Execute an INSERT statement"""
        try:
            # Prepare columns and values
            columns = list(data.keys())
            placeholders = ['%s'] * len(columns)
            values = [data[col] for col in columns]
            
            # Build query
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            if returning:
                query += f" RETURNING {returning}"
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, values)
                    
                    if returning:
                        result = cur.fetchone()
                        conn.commit()
                        return result
                    else:
                        conn.commit()
                        return None
                        
        except Exception as e:
            self.logger.error(f"Insert failed for table {table}: {e}")
            raise
    
    def execute_update(self, table: str, data: Dict[str, Any], where_clause: str, where_params: tuple = None) -> int:
        """Execute an UPDATE statement"""
        try:
            # Prepare SET clause
            set_clauses = [f"{col} = %s" for col in data.keys()]
            values = list(data.values())
            
            # Build query
            query = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {where_clause}"
            
            # Combine values and where parameters
            if where_params:
                values.extend(where_params)
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, values)
                    rows_affected = cur.rowcount
                    conn.commit()
                    return rows_affected
                    
        except Exception as e:
            self.logger.error(f"Update failed for table {table}: {e}")
            raise
    
    def execute_delete(self, table: str, where_clause: str, where_params: tuple = None) -> int:
        """Execute a DELETE statement"""
        try:
            query = f"DELETE FROM {table} WHERE {where_clause}"
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, where_params)
                    rows_affected = cur.rowcount
                    conn.commit()
                    return rows_affected
                    
        except Exception as e:
            self.logger.error(f"Delete failed for table {table}: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email address"""
        query = """
        SELECT user_id, client_id, name, email, password_hash, role, phone, 
               is_active, last_login, created_at, updated_at
        FROM users 
        WHERE email = %s AND is_active = true
        """
        return self.execute_query(query, (email,), fetch='one')
    
    def get_user_sites(self, user_id: str) -> List[Dict]:
        """Get sites assigned to a user"""
        query = """
        SELECT s.site_id, s.name, s.address, s.city, s.state
        FROM sites s
        JOIN user_site_assignments usa ON s.site_id = usa.site_id
        WHERE usa.user_id = %s AND s.is_active = true
        """
        return self.execute_query(query, (user_id,))
    
    def validate_uuid(self, value: str) -> bool:
        """Validate if string is a valid UUID"""
        try:
            uuid.UUID(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def close_pool(self):
        """Close the connection pool"""
        if self.pool:
            self.pool.closeall()
            self.logger.info("Database connection pool closed")
