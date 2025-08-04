#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent - Local Database Manager
SQLite database for local caching and configuration
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import threading

class DatabaseManager:
    """Manages local SQLite database for agent data"""
    
    def __init__(self, db_path: str = "data/agent.db"):
        self.logger = logging.getLogger('lanet_agent.database')
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Agent configuration table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS agent_config (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # System metrics history
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS metrics_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        cpu_usage REAL,
                        memory_usage REAL,
                        disk_usage REAL,
                        network_status TEXT,
                        uptime INTEGER,
                        metrics_json TEXT
                    )
                ''')
                
                # Ticket cache
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ticket_cache (
                        ticket_id TEXT PRIMARY KEY,
                        ticket_number TEXT,
                        subject TEXT,
                        status TEXT,
                        priority TEXT,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP,
                        ticket_data TEXT
                    )
                ''')
                
                # Agent logs
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS agent_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        level TEXT,
                        module TEXT,
                        message TEXT,
                        details TEXT
                    )
                ''')
                
                # Heartbeat history
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS heartbeat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT,
                        response_time REAL,
                        error_message TEXT
                    )
                ''')
                
                conn.commit()
                conn.close()
                
                self.logger.info(f"Database initialized at {self.db_path}")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def set_config(self, key: str, value: Any):
        """Store configuration value"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                value_str = json.dumps(value) if not isinstance(value, str) else value
                
                cursor.execute('''
                    INSERT OR REPLACE INTO agent_config (key, value, updated_at)
                    VALUES (?, ?, ?)
                ''', (key, value_str, datetime.now()))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            self.logger.error(f"Error setting config {key}: {e}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Retrieve configuration value"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT value FROM agent_config WHERE key = ?', (key,))
                result = cursor.fetchone()
                
                conn.close()
                
                if result:
                    try:
                        return json.loads(result[0])
                    except json.JSONDecodeError:
                        return result[0]
                
                return default
                
        except Exception as e:
            self.logger.error(f"Error getting config {key}: {e}")
            return default
    
    def store_metrics(self, metrics: Dict[str, Any]):
        """Store system metrics"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO metrics_history 
                    (cpu_usage, memory_usage, disk_usage, network_status, uptime, metrics_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.get('cpu_usage'),
                    metrics.get('memory_usage'),
                    metrics.get('disk_usage'),
                    metrics.get('network_status'),
                    metrics.get('uptime'),
                    json.dumps(metrics)
                ))
                
                conn.commit()
                conn.close()
                
                # Clean old metrics (keep last 1000 entries)
                self._cleanup_metrics()
                
        except Exception as e:
            self.logger.error(f"Error storing metrics: {e}")
    
    def get_recent_metrics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent system metrics"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT timestamp, metrics_json FROM metrics_history
                    ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))
                
                results = cursor.fetchall()
                conn.close()
                
                metrics = []
                for row in results:
                    try:
                        metric_data = json.loads(row[1])
                        metric_data['timestamp'] = row[0]
                        metrics.append(metric_data)
                    except json.JSONDecodeError:
                        continue
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Error getting recent metrics: {e}")
            return []
    
    def _cleanup_metrics(self):
        """Clean up old metrics to prevent database growth"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM metrics_history 
                    WHERE id NOT IN (
                        SELECT id FROM metrics_history 
                        ORDER BY timestamp DESC LIMIT 1000
                    )
                ''')
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            self.logger.error(f"Error cleaning up metrics: {e}")
    
    def close(self):
        """Close database connections"""
        self.logger.info("Database manager closed")
