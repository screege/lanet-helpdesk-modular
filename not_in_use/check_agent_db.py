#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check the agent database structure
"""

import sqlite3
import os

def check_agent_db():
    """Check the agent database structure"""
    try:
        print("🔍 Checking agent database...")
        
        # Find the database
        possible_paths = [
            os.path.join('lanet_agent', 'data', 'agent.db'),
            os.path.join('data', 'agent.db'),
            'agent.db'
        ]
        
        db_path = None
        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                break
                
        if not db_path:
            print("❌ Agent database not found")
            return
            
        print(f"📁 Database found at: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📊 Tables found: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
            
        # Check each table structure
        for table in tables:
            table_name = table[0]
            print(f"\n🔧 Structure of {table_name}:")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
                
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_agent_db()
