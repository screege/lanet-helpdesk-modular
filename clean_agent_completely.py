import sqlite3
import os

def clean_agent_completely():
    """Completely clean agent local database"""
    
    # Path to agent database
    db_path = "lanet_agent/data/agent.db"
    
    if os.path.exists(db_path):
        print("🗑️  Deleting agent local database...")
        os.remove(db_path)
        print("✅ Agent database deleted")
    else:
        print("ℹ️  Agent database not found (already clean)")
    
    # Also clean any backup files
    data_dir = "lanet_agent/data"
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith('.db') or file.endswith('.db-journal'):
                file_path = os.path.join(data_dir, file)
                print(f"🗑️  Deleting {file_path}")
                os.remove(file_path)
    
    print("✅ Agent local storage completely cleaned!")

if __name__ == "__main__":
    clean_agent_completely()
