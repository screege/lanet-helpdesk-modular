import psycopg2

conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
cur = conn.cursor()

print("🔍 Checking for duplicate assets and data inconsistencies...")

# Check current assets and their client/site info
cur.execute("""
SELECT 
    a.asset_id,
    a.name,
    a.agent_status,
    a.last_seen,
    c.name as client_name,
    s.name as site_name,
    a.specifications->>'mac_address' as mac_address,
    a.specifications->>'serial_number' as serial_number,
    a.created_at
FROM assets a
JOIN sites s ON a.site_id = s.site_id
JOIN clients c ON a.client_id = c.client_id
WHERE a.name LIKE '%benny%'
ORDER BY a.created_at DESC
""")

assets = cur.fetchall()
print(f'\n📊 Found {len(assets)} assets with "benny" in name:')
for i, asset in enumerate(assets, 1):
    print(f'\n  Asset #{i}:')
    print(f'    ID: {asset[0]}')
    print(f'    Name: {asset[1]}')
    print(f'    Status: {asset[2]}')
    print(f'    Client: {asset[4]}')
    print(f'    Site: {asset[5]}')
    print(f'    MAC: {asset[6]}')
    print(f'    Serial: {asset[7]}')
    print(f'    Last seen: {asset[3]}')
    print(f'    Created: {asset[8]}')

# Check tokens used
cur.execute("""
SELECT
    t.token_value,
    t.notes,
    c.name as client_name,
    s.name as site_name,
    t.last_used_at,
    t.usage_count
FROM agent_installation_tokens t
JOIN sites s ON t.site_id = s.site_id
JOIN clients c ON t.client_id = c.client_id
WHERE t.last_used_at IS NOT NULL
ORDER BY t.last_used_at DESC
LIMIT 5
""")

tokens = cur.fetchall()
print(f'\n🎫 Recent used tokens ({len(tokens)}):')
for i, token in enumerate(tokens, 1):
    print(f'\n  Token #{i}:')
    print(f'    Token: {token[0]}')
    print(f'    Notes: {token[1]}')
    print(f'    Client: {token[2]}')
    print(f'    Site: {token[3]}')
    print(f'    Last used: {token[4]}')
    print(f'    Usage count: {token[5]}')

# Check for potential duplicates by MAC address
cur.execute("""
SELECT 
    a.specifications->>'mac_address' as mac_address,
    COUNT(*) as count,
    STRING_AGG(a.name, ', ') as asset_names
FROM assets a
WHERE a.specifications->>'mac_address' IS NOT NULL
GROUP BY a.specifications->>'mac_address'
HAVING COUNT(*) > 1
""")

mac_duplicates = cur.fetchall()
if mac_duplicates:
    print(f'\n⚠️  Found {len(mac_duplicates)} MAC address duplicates:')
    for dup in mac_duplicates:
        print(f'    MAC: {dup[0]} -> {dup[1]} assets: {dup[2]}')
else:
    print('\n✅ No MAC address duplicates found')

cur.close()
conn.close()
