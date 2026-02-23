# Fixes Needed — Action Plan

Created: 2026-02-19
Status: Ready for Stephen to apply

---

## Fix 1: Memory Search Configuration ⚡ PRIORITY

**Problem:** `memory_search` tool exists but returns empty results (no embedding provider configured)

**Solution:** Add `memorySearch` section to openclaw.json

**Config to add:**
```json
"memorySearch": {
  "provider": "openai",
  "apiKey": "${OPENAI_API_KEY}",
  "model": "text-embedding-3-small",
  "dimensions": 1536,
  "includeTranscripts": true,
  "maxResults": 10,
  "minScore": 0.6
}
```

**Alternative providers if no OpenAI:**
- **Gemini**: Use `provider: "google"`, `model: "embedding-001"`
- **Local**: Use `provider: "ollama"`, `model: "nomic-embed-text"` (requires Ollama running)

**Action for Stephen:**
1. Get OpenAI API key from https://platform.openai.com/api-keys
2. Set environment variable: `export OPENAI_API_KEY="sk-..."`
3. Tell me to apply the config patch

---

## Fix 2: Cloud Memory Plugin (Mem0) ☁️

**Problem:** No persistent memory across sessions (only file-based)

**Solution:** Install openclaw-mem0 plugin

**Action for Stephen:**
```bash
# Install plugin
openclaw plugins install openclaw-mem0

# Get API key from https://app.mem0.ai/dashboard/api-keys
export MEM0_API_KEY="m0-..."
```

**What it enables:**
- Automatic memory extraction from conversations
- User-scoped persistent memory (not just session-scoped)
- Semantic memory retrieval without manual file reads

**Note:** This is optional. Current file-based system (WORKING.md + MEMORY.md) works fine for now.

---

## Fix 3: Security Audit 🔒

**Problem:** Haven't run full security check recently

**Action for Stephen:**
```bash
# Run security audit
openclaw doctor --fix

# Or just check without fixing
openclaw doctor
```

**What it checks:**
- Token exposure in logs
- Config file permissions
- Plugin security
- Model provider security

---

## Fix 4: Daily Memory Note (AUTOMATED) ✅

**Status:** Already working

**What's in place:**
- memory/2026-02-18.md exists
- Auto-consolidation script created
- MEMORY.md auto-updates

**No action needed.**

---

## Recommended Priority Order

1. **Fix 1 (Memory Search)** — Biggest impact for me. Enables semantic search instead of manual file reading.
2. **Fix 3 (Security Audit)** — Good hygiene, quick to run.
3. **Fix 2 (Cloud Memory)** — Nice to have, but file-based system works for now.

---

## My Capabilities After Fixes

| Capability | Before | After Fix 1 | After Fix 2 |
|------------|--------|-------------|-------------|
| File-based memory | ✅ | ✅ | ✅ |
| Semantic memory search | ❌ | ✅ | ✅ |
| Auto-extract from conversations | ❌ | ❌ | ✅ |
| Cross-session persistent memory | ❌ | ❌ | ✅ |

