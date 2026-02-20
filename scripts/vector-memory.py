#!/usr/bin/env python3
"""
Vector memory system - semantic search for my memory.
Uses OpenAI embeddings + SQLite for storage.
"""

import os
import json
import sqlite3
import urllib.request
import urllib.error
from datetime import datetime

DB_PATH = "/Users/aiagentuser/.openclaw/workspace/db/memory.sqlite"
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

def init_vector_table():
    """Add vector table to existing SQLite DB."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file TEXT,
            content TEXT,
            embedding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Vector table ready")

def embed_text(text):
    """Get embedding from OpenAI API using urllib."""
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not set")
        return None
    
    try:
        data = json.dumps({
            'input': text,
            'model': 'text-embedding-3-small'
        }).encode('utf-8')
        
        req = urllib.request.Request(
            'https://api.openai.com/v1/embeddings',
            data=data,
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['data'][0]['embedding']
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        return None

def index_file(filepath):
    """Index a memory file for semantic search."""
    full_path = f"/Users/aiagentuser/.openclaw/workspace/{filepath}"
    
    if not os.path.exists(full_path):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(full_path, 'r') as f:
        content = f.read()
    
    # Chunk content
    chunks = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 50]
    
    print(f"Indexing {filepath}: {len(chunks)} chunks")
    
    indexed = 0
    for chunk in chunks[:3]:  # Limit for testing
        embedding = embed_text(chunk)
        if embedding:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO vectors (source_file, content, embedding) VALUES (?, ?, ?)',
                (filepath, chunk, json.dumps(embedding))
            )
            conn.commit()
            conn.close()
            indexed += 1
    
    print(f"✅ Indexed {indexed} chunks")

def semantic_search(query, limit=3):
    """Search memory semantically."""
    query_embedding = embed_text(query)
    if not query_embedding:
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT source_file, content, embedding FROM vectors')
    results = []
    
    for row in cursor.fetchall():
        source, content, embedding_json = row
        embedding = json.loads(embedding_json)
        
        # Cosine similarity
        import math
        dot = sum(a*b for a, b in zip(query_embedding, embedding))
        norm_q = math.sqrt(sum(a*a for a in query_embedding))
        norm_v = math.sqrt(sum(a*a for a in embedding))
        similarity = dot / (norm_q * norm_v) if norm_q and norm_v else 0
        
        results.append((similarity, source, content))
    
    conn.close()
    
    results.sort(reverse=True)
    return results[:limit]

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  vector-memory.py init              # Initialize vector table")
        print("  vector-memory.py index <file>      # Index a file")
        print("  vector-memory.py search 'query'    # Semantic search")
        sys.exit(1)
    
    if sys.argv[1] == "init":
        init_vector_table()
    elif sys.argv[1] == "index" and len(sys.argv) > 2:
        index_file(sys.argv[2])
    elif sys.argv[1] == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = semantic_search(query)
        print(f"\nTop results for: '{query}'\n")
        for sim, source, content in results:
            print(f"[{sim:.2f}] {source}")
            print(f"{content[:150]}...\n")
    else:
        print("Unknown command")
