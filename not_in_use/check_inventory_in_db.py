import psycopg2
import json

def check_inventory_in_db():
    """Check if inventory data is being stored in the database"""
    
    conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
    cur = conn.cursor()
    
    print("🔍 Checking inventory data in database...")
    
    try:
        # Get the current asset
        cur.execute("""
        SELECT asset_id, name, specifications, last_seen, agent_status
        FROM assets 
        WHERE name LIKE '%benny%' AND status = 'active'
        ORDER BY last_seen DESC
        LIMIT 1
        """)
        
        asset = cur.fetchone()
        
        if asset:
            asset_id, name, specifications, last_seen, agent_status = asset
            print(f"📊 Asset found: {name}")
            print(f"  ID: {asset_id}")
            print(f"  Status: {agent_status}")
            print(f"  Last seen: {last_seen}")
            
            if specifications:
                specs = json.loads(specifications) if isinstance(specifications, str) else specifications
                
                print(f"\n📋 Specifications keys: {list(specs.keys())}")
                
                # Check for hardware inventory
                if 'hardware_info' in specs:
                    hardware = specs['hardware_info']
                    print(f"✅ Hardware inventory found!")
                    print(f"  Hardware keys: {list(hardware.keys())}")
                    
                    if 'system' in hardware:
                        system = hardware['system']
                        print(f"  System: {system.get('hostname', 'N/A')} - {system.get('platform', 'N/A')}")
                    
                    if 'cpu' in hardware:
                        cpu = hardware['cpu']
                        print(f"  CPU: {cpu.get('name', 'N/A')} ({cpu.get('cores_logical', 'N/A')} cores)")
                    
                    if 'memory' in hardware:
                        memory = hardware['memory']
                        print(f"  Memory: {memory.get('total_gb', 'N/A')} GB")
                else:
                    print("❌ No hardware_info found in specifications")
                
                # Check for software inventory
                if 'software_info' in specs:
                    software = specs['software_info']
                    print(f"✅ Software inventory found!")
                    print(f"  Software keys: {list(software.keys())}")
                    
                    if 'installed_programs' in software:
                        programs = software['installed_programs']
                        print(f"  Installed programs: {len(programs)} found")
                        
                        # Show first few programs
                        for i, program in enumerate(programs[:5]):
                            if isinstance(program, dict):
                                name = program.get('name', 'Unknown')
                                version = program.get('version', 'N/A')
                                print(f"    {i+1}. {name} ({version})")
                            else:
                                print(f"    {i+1}. {program}")
                        
                        if len(programs) > 5:
                            print(f"    ... and {len(programs) - 5} more")
                    else:
                        print("❌ No installed_programs found in software_info")
                else:
                    print("❌ No software_info found in specifications")
                
                # Check for system metrics
                if 'system_metrics' in specs:
                    metrics = specs['system_metrics']
                    print(f"✅ System metrics found!")
                    print(f"  CPU: {metrics.get('cpu_usage', 'N/A')}%")
                    print(f"  Memory: {metrics.get('memory_usage', 'N/A')}%")
                    print(f"  Disk: {metrics.get('disk_usage', 'N/A')}%")
                else:
                    print("❌ No system_metrics found in specifications")
            else:
                print("❌ No specifications found")
        else:
            print("❌ No asset found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_inventory_in_db()
