# Hybrid Memory System Specification
## Phase 2 Implementation

### Problem
Current memory is file-only (WORKING.md, MEMORY.md). No semantic search, slow lookups, no query history.

### Solution: Hybrid Architecture

```
┌─────────────────────────────────────────┐
│           HOT PATH (Fast)              │
│  Current session context (in-memory)   │
│  WORKING.md (recent, loaded)           │
└─────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│         WARM PATH (Medium)             │
│  SQLite: Structured queries, metadata  │
│  - Task history                        │
│  - Question log                        │
│  - Decision records                    │
└─────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│         COLD PATH (Deep)               │
│  Vector DB: Semantic search            │
│  - All memory files embedded           │
│  - Conversations indexed               │
│  - Research archived                   │
└─────────────────────────────────────────┘
```

### Components

#### 1. SQLite Layer (Structured)
**Tables:**
- `tasks`: What I worked on, when, outcome
- `questions`: Open questions, answers found, still open
- `decisions`: Key choices, rationale, outcomes
- `interactions`: Sessions with Stephen, topics, insights

**Benefits:** Fast queries, exact matches, relationships

#### 2. Vector Layer (Semantic)
**Index:**
- All markdown files in workspace
- Daily memory notes
- Research outputs
- Conversation summaries

**Benefits:** "What did I learn about X?", fuzzy matching, discovery

#### 3. File Layer (Persistent)
**Current system:**
- WORKING.md (manual)
- MEMORY.md (consolidated)
- memory/YYYY-MM-DD.md (daily)

**Enhanced with:**
- Auto-sync to SQLite on changes
- Auto-index to vector DB
- Version history via git

### Implementation Phases

**Phase A: SQLite Setup (This week)**
1. Create schema
2. Build sync script (file → SQLite)
3. Query interface

**Phase B: Vector Integration (Next week)**
1. Choose vector DB (sqlite-vec vs external)
2. Embedding pipeline
3. Search interface

**Phase C: Unified API (Week 3)**
1. Single query interface
2. Precedence rules (exact → semantic)
3. Performance optimization

### Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Query speed | Manual read | <100ms |
| Recall rate | ~60% (manual) | >85% |
| Coverage | Files only | All interactions |
| Maintenance | High (manual) | Low (auto-sync) |

### Files to Create

1. `scripts/memory-sync.py` - File ↔ SQLite sync
2. `scripts/vector-index.py` - Embedding pipeline
3. `scripts/memory-query.py` - Unified query interface
4. `db/memory.sqlite` - SQLite database

### Blockers

- Need to choose: sqlite-vec (local) vs external vector DB
- OpenAI embeddings API key (already have)
- Storage: Vector DB can grow large

### Decision Needed

**Option 1: sqlite-vec (Recommended)**
- Pros: Local, fast, no external dependency
- Cons: Slightly lower accuracy than dedicated vector DB

**Option 2: External (Pinecone/Weaviate)**
- Pros: Higher accuracy, scalable
- Cons: External dependency, cost, complexity

**Recommendation:** Start with sqlite-vec, migrate if needed.
