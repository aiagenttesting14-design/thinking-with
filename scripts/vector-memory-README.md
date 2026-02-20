# Vector Memory System

## Status: Structure Complete, Awaiting API Key

### What's Built
- ✅ SQLite vector table schema
- ✅ Embedding pipeline (urllib-based)
- ✅ File chunking and indexing
- ✅ Cosine similarity search
- ✅ Query interface

### To Activate
Set OPENAI_API_KEY environment variable:
```bash
export OPENAI_API_KEY="your-key-here"
```

### Usage
```bash
# Initialize
python scripts/vector-memory.py init

# Index a file
python scripts/vector-memory.py index memory/2026-02-19.md

# Search
python scripts/vector-memory.py search "what did I learn about autonomy"
```

### Architecture
- **Hot path:** Session context (in-memory)
- **Warm path:** SQLite structured data (this system)
- **Cold path:** Vector embeddings for semantic search (this system)
