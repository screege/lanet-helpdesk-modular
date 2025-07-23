import psycopg2

def clean_all_benny_assets():
    """Clean all benny assets from server database"""
    
    conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
    cur = conn.cursor()
    
    print("🗑️  Cleaning all benny assets from server database...")
    
    try:
        # Get all benny assets
        cur.execute("""
        SELECT asset_id, name FROM assets 
        WHERE name LIKE '%benny%' AND status = 'active'
        """)
        
        assets = cur.fetchall()
        
        if assets:
            print(f"Found {len(assets)} benny assets to delete:")
            
            for asset_id, name in assets:
                print(f"  - {name} ({asset_id})")
                
                # Delete related records first
                cur.execute("DELETE FROM agent_token_usage_history WHERE asset_id = %s", (asset_id,))
                deleted_history = cur.rowcount
                print(f"    Deleted {deleted_history} token usage history records")
                
                # Delete the asset
                cur.execute("DELETE FROM assets WHERE asset_id = %s", (asset_id,))
                deleted_assets = cur.rowcount
                print(f"    Deleted {deleted_assets} asset records")
            
            # Commit changes
            conn.commit()
            print("✅ All benny assets deleted successfully!")
        else:
            print("ℹ️  No benny assets found (already clean)")
        
        # Show remaining assets count
        cur.execute("SELECT COUNT(*) FROM assets WHERE status = 'active'")
        remaining_count = cur.fetchone()[0]
        print(f"📊 Remaining active assets: {remaining_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    clean_all_benny_assets()
