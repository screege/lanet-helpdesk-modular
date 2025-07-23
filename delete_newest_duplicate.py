import psycopg2

def delete_newest_duplicate():
    """Delete the newest duplicate asset"""
    
    conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
    cur = conn.cursor()
    
    print("🗑️  Deleting newest duplicate asset...")
    
    try:
        # Delete the newer asset (6121963e-7c8c-4031-8cfa-ba4ae32f9d10)
        new_asset_id = '6121963e-7c8c-4031-8cfa-ba4ae32f9d10'
        
        print(f"Deleting asset: {new_asset_id}")
        
        # Delete related records first
        cur.execute("DELETE FROM agent_token_usage_history WHERE asset_id = %s", (new_asset_id,))
        deleted_history = cur.rowcount
        print(f"  Deleted {deleted_history} token usage history records")
        
        # Delete the asset
        cur.execute("DELETE FROM assets WHERE asset_id = %s", (new_asset_id,))
        deleted_assets = cur.rowcount
        print(f"  Deleted {deleted_assets} asset records")
        
        # Commit changes
        conn.commit()
        print("✅ Newest duplicate deleted successfully!")
        
        # Show remaining assets
        print("\n📊 Remaining assets:")
        cur.execute("""
        SELECT a.asset_id, a.name, a.last_seen, c.name as client_name, s.name as site_name
        FROM assets a
        JOIN sites s ON a.site_id = s.site_id
        JOIN clients c ON a.client_id = c.client_id
        WHERE a.name LIKE '%benny%' AND a.status = 'active'
        ORDER BY a.last_seen DESC
        """)
        
        remaining_assets = cur.fetchall()
        for asset in remaining_assets:
            print(f"  Asset: {asset[1]}")
            print(f"  ID: {asset[0]}")
            print(f"  Client: {asset[3]}")
            print(f"  Site: {asset[4]}")
            print(f"  Last seen: {asset[2]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    delete_newest_duplicate()
