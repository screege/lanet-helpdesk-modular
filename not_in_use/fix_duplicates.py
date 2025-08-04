import psycopg2
from datetime import datetime

def fix_duplicates():
    """Fix duplicate assets and data inconsistencies"""
    
    conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
    cur = conn.cursor()
    
    print("🔧 Fixing duplicate assets and data inconsistencies...")
    
    try:
        # 1. Find duplicate assets by computer name
        cur.execute("""
        SELECT name, COUNT(*) as count, STRING_AGG(asset_id::text, ', ') as asset_ids
        FROM assets 
        WHERE name LIKE '%benny%' AND status = 'active'
        GROUP BY name
        HAVING COUNT(*) > 1
        """)
        
        duplicates = cur.fetchall()
        
        if duplicates:
            print(f"\n📊 Found {len(duplicates)} duplicate groups:")
            
            for name, count, asset_ids in duplicates:
                print(f"\n  Asset name: {name}")
                print(f"  Count: {count}")
                print(f"  Asset IDs: {asset_ids}")
                
                # Get details of each duplicate
                asset_id_list = asset_ids.split(', ')
                
                print(f"  Details:")
                for asset_id in asset_id_list:
                    cur.execute("""
                    SELECT a.asset_id, a.name, a.last_seen, a.created_at,
                           c.name as client_name, s.name as site_name
                    FROM assets a
                    JOIN sites s ON a.site_id = s.site_id
                    JOIN clients c ON a.client_id = c.client_id
                    WHERE a.asset_id = %s
                    """, (asset_id,))
                    
                    asset_detail = cur.fetchone()
                    if asset_detail:
                        print(f"    ID: {asset_detail[0]}")
                        print(f"    Last seen: {asset_detail[2]}")
                        print(f"    Created: {asset_detail[3]}")
                        print(f"    Client: {asset_detail[4]}")
                        print(f"    Site: {asset_detail[5]}")
                        print(f"    ---")
                
                # Keep the most recent one, delete the others
                if len(asset_id_list) > 1:
                    # Find the most recent asset
                    placeholders = ','.join(['%s'] * len(asset_id_list))
                    cur.execute(f"""
                    SELECT asset_id, last_seen, created_at
                    FROM assets
                    WHERE asset_id::text IN ({placeholders})
                    ORDER BY last_seen DESC NULLS LAST, created_at DESC
                    LIMIT 1
                    """, asset_id_list)
                    
                    most_recent = cur.fetchone()
                    keep_asset_id = most_recent[0]
                    
                    print(f"  🔄 Keeping most recent asset: {keep_asset_id}")
                    
                    # Delete the others
                    assets_to_delete = [aid for aid in asset_id_list if aid != keep_asset_id]
                    
                    for delete_id in assets_to_delete:
                        print(f"  🗑️  Deleting duplicate asset: {delete_id}")
                        
                        # Delete related records first
                        cur.execute("DELETE FROM agent_token_usage_history WHERE asset_id = %s", (delete_id,))
                        
                        # Delete the asset
                        cur.execute("DELETE FROM assets WHERE asset_id = %s", (delete_id,))
                    
                    print(f"  ✅ Cleaned up {len(assets_to_delete)} duplicate assets")
        else:
            print("\n✅ No duplicates found by computer name")
        
        # 2. Check for MAC address duplicates (if we had MAC addresses)
        cur.execute("""
        SELECT specifications->>'mac_address' as mac_address, 
               COUNT(*) as count,
               STRING_AGG(asset_id::text, ', ') as asset_ids
        FROM assets 
        WHERE specifications->>'mac_address' IS NOT NULL 
        AND specifications->>'mac_address' != ''
        AND status = 'active'
        GROUP BY specifications->>'mac_address'
        HAVING COUNT(*) > 1
        """)
        
        mac_duplicates = cur.fetchall()
        
        if mac_duplicates:
            print(f"\n📊 Found {len(mac_duplicates)} MAC address duplicates:")
            for mac, count, asset_ids in mac_duplicates:
                print(f"  MAC: {mac} -> {count} assets: {asset_ids}")
        else:
            print("\n✅ No MAC address duplicates found")
        
        # 3. Update the remaining asset with correct token information
        print(f"\n🔄 Updating remaining assets with correct client/site information...")
        
        # Get the token that was used most recently
        cur.execute("""
        SELECT t.token_value, t.client_id, t.site_id, c.name as client_name, s.name as site_name
        FROM agent_installation_tokens t
        JOIN clients c ON t.client_id = c.client_id
        JOIN sites s ON t.site_id = s.site_id
        WHERE t.token_value = 'LANET-75F6-D01D-DEB120'
        """)
        
        token_info = cur.fetchone()
        
        if token_info:
            token_value, client_id, site_id, client_name, site_name = token_info
            print(f"  Token: {token_value}")
            print(f"  Should be: {client_name} - {site_name}")
            
            # Update all assets with benny in the name to use correct client/site
            cur.execute("""
            UPDATE assets 
            SET client_id = %s, site_id = %s, updated_at = %s
            WHERE name LIKE '%benny%' AND status = 'active'
            """, (client_id, site_id, datetime.now()))
            
            updated_count = cur.rowcount
            print(f"  ✅ Updated {updated_count} assets with correct client/site")
        
        # Commit all changes
        conn.commit()
        print(f"\n✅ All changes committed successfully!")
        
        # Show final state
        print(f"\n📊 Final state:")
        cur.execute("""
        SELECT a.asset_id, a.name, a.last_seen, c.name as client_name, s.name as site_name
        FROM assets a
        JOIN sites s ON a.site_id = s.site_id
        JOIN clients c ON a.client_id = c.client_id
        WHERE a.name LIKE '%benny%' AND a.status = 'active'
        ORDER BY a.last_seen DESC
        """)
        
        final_assets = cur.fetchall()
        for asset in final_assets:
            print(f"  Asset: {asset[1]}")
            print(f"  ID: {asset[0]}")
            print(f"  Client: {asset[3]}")
            print(f"  Site: {asset[4]}")
            print(f"  Last seen: {asset[2]}")
            print(f"  ---")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_duplicates()
