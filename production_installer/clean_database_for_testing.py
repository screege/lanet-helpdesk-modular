#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Database Cleanup Script
Cleans existing assets for fresh testing of the production installer
"""

import psycopg2
import logging
from datetime import datetime

def setup_logging():
    """Setup logging for database cleanup"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'database_cleanup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8')
        ]
    )
    return logging.getLogger('DatabaseCleanup')

def clean_database():
    """Clean existing assets and related data for fresh testing"""
    logger = setup_logging()
    
    # Database connection parameters
    db_params = {
        'host': 'localhost',
        'database': 'lanet_helpdesk',
        'user': 'postgres',
        'password': 'Poikl55+*',
        'port': 5432
    }
    
    try:
        logger.info("Starting database cleanup for fresh agent testing...")
        
        # Connect to database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Get count of existing assets before cleanup (agent-created assets)
        cursor.execute("SELECT COUNT(*) FROM assets WHERE asset_type IN ('desktop', 'laptop', 'server')")
        asset_count = cursor.fetchone()[0]
        logger.info(f"Found {asset_count} existing agent-managed assets")
        
        # Get count of token usage history
        cursor.execute("SELECT COUNT(*) FROM agent_token_usage_history")
        usage_count = cursor.fetchone()[0]
        logger.info(f"Found {usage_count} token usage history records")
        
        if asset_count > 0 or usage_count > 0:
            logger.info("Cleaning ALL existing data...")

            # Delete agent token usage history (has foreign key to assets)
            cursor.execute("DELETE FROM agent_token_usage_history")
            deleted_usage = cursor.rowcount
            logger.info(f"Deleted {deleted_usage} token usage history records")

            # Delete ALL assets (not just agent-managed ones)
            cursor.execute("DELETE FROM assets")
            deleted_assets = cursor.rowcount
            logger.info(f"Deleted {deleted_assets} ALL assets")

            # Delete ALL agent tokens for fresh start
            cursor.execute("DELETE FROM agent_tokens")
            deleted_tokens = cursor.rowcount
            logger.info(f"Deleted {deleted_tokens} agent tokens")

            # Reset agent installation token usage counts
            cursor.execute("UPDATE agent_installation_tokens SET usage_count = 0, last_used_at = NULL")
            reset_tokens = cursor.rowcount
            logger.info(f"Reset usage count for {reset_tokens} installation tokens")

            # Commit changes
            conn.commit()
            logger.info("Database cleanup completed successfully")

        else:
            logger.info("Database is already clean - no assets to remove")
        
        # Show current token status
        cursor.execute("""
            SELECT 
                t.token_value,
                c.name as client_name,
                s.name as site_name,
                t.is_active,
                t.usage_count
            FROM agent_installation_tokens t
            JOIN clients c ON t.client_id = c.client_id
            JOIN sites s ON t.site_id = s.site_id
            ORDER BY t.created_at DESC
            LIMIT 5
        """)
        
        tokens = cursor.fetchall()
        if tokens:
            logger.info("Available installation tokens:")
            for token_value, client_name, site_name, is_active, usage_count in tokens:
                status = "Active" if is_active else "Inactive"
                logger.info(f"  {token_value} - {client_name} / {site_name} - {status} (Used: {usage_count})")
        else:
            logger.warning("No installation tokens found - you may need to create tokens first")
        
        cursor.close()
        conn.close()
        
        logger.info("Database cleanup completed - ready for fresh agent testing!")
        return True

    except psycopg2.Error as e:
        logger.error(f"Database error during cleanup: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during cleanup: {e}")
        return False

if __name__ == "__main__":
    print("LANET Agent Database Cleanup")
    print("=" * 50)
    print("This script will clean existing assets for fresh testing")
    print()

    confirm = input("Are you sure you want to clean the database? (yes/no): ").lower().strip()
    if confirm in ['yes', 'y']:
        success = clean_database()
        if success:
            print("\nDatabase cleanup completed successfully!")
            print("You can now test the agent installer with a clean database.")
        else:
            print("\nDatabase cleanup failed. Check the logs for details.")
    else:
        print("Database cleanup cancelled.")

    input("\nPress Enter to exit...")
