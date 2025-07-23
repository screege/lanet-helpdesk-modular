import psycopg2

def delete_old_asset():
    """Delete the older duplicate asset"""
    
    conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
    cur = conn.cursor()
    
    print("🗑️  Deleting older duplicate asset...")
    
    try:
        # Delete the older asset (814035f5-9dcf-4c53-80fb-30f26881c3b6)
        old_asset_id = '814035f5-9dcf-4c53-80fb-30f26881c3b6'
        
        print(f"Deleting asset: {old_asset_id}")
        
        # Delete related records first
        cur.execute("DELETE FROM agent_token_usage_history WHERE asset_id = %s", (old_asset_id,))
        deleted_history = cur.rowcount
        print(f"  Deleted {deleted_history} token usage history records")
        
        # Delete the asset
        cur.execute("DELETE FROM assets WHERE asset_id = %s", (old_asset_id,))
        deleted_assets = cur.rowcount
        print(f"  Deleted {deleted_assets} asset records")
        
        # Commit changes
        conn.commit()
        print("✅ Old asset deleted successfully!")
        
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
    delete_old_asset()
