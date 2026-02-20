#!/usr/bin/env python3
"""
Initialize hybrid memory database.
Creates SQLite DB with schema, seeds with existing data.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = "/Users/aiagentuser/.openclaw/workspace/db/memory.sqlite"
SCHEMA_PATH = "/Users/aiagentuser/.openclaw/workspace/db/schema.sql"

def init_db():
    """Create database and tables."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Connect and create
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read and execute schema
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()
    
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized: {DB_PATH}")
    return True

def seed_from_working_md():
    """Extract and seed data from WORKING.md."""
    # This would parse WORKING.md and populate tables
    # For now, just log that we're ready
    print("📝 Ready to seed from WORKING.md")
    print("   - Parse missions → tasks table")
    print("   - Parse questions → questions table")
    print("   - Parse decisions → decisions table")

def verify_db():
    """Verify database is working."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📊 Tables created: {', '.join(tables)}")
    
    conn.close()
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2 or sys.argv[1] == "init":
        if init_db():
            verify_db()
            print("\n🚀 Database ready for hybrid memory system")
    elif sys.argv[1] == "seed":
        seed_from_working_md()
    elif sys.argv[1] == "verify":
        verify_db()
    else:
        print("Usage:")
        print("  init-memory-db.py init    # Create database")
        print("  init-memory-db.py seed    # Seed from existing files")
        print("  init-memory-db.py verify  # Check database status")
