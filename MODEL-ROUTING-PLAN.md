# Model Routing Optimization Plan
## Phase 2 Implementation

### Current Routing
```
Primary: moonshot/kimi-k2.5
Fallbacks: gemini-2.5-flash-lite → deepseek-chat → claude-sonnet-4.5
Subagents: deepseek-chat → gemini-2.5-flash-lite
```

**Problems:**
- DeepSeek out of credits
- Gemini rate limited (20 req/day)
- No task-based differentiation
- Expensive fallbacks used for everything

### Proposed Task-Based Routing

| Task Type | Primary | Fallback | Why |
|-----------|---------|----------|-----|
| **Research** (broad, parallel) | kimi-k2.5 | kimi-k2.5 (alt) | Fast, cheap, good for parallel |
| **Synthesis** (complex reasoning) | claude-sonnet-4-5 | kimi-k2.5 | Claude best at reasoning |
| **Creative writing** | kimi-k2.5 | claude-sonnet-4-5 | Kimi creative, Claude polish |
| **Code generation** | kimi-k2.5 | claude-sonnet-4-5 | Kimi fast, Claude thorough |
| **Quick summaries** | gemini-2.5-flash-lite | kimi-k2.5 | Cheapest, wait for quota |
| **Verification/testing** | kimi-k2.5 | claude-sonnet-4-5 | Fast check, then thorough |

### Cost Impact

**Current (broken fallbacks):**
- Subagents: ~$0.50-1.00 per task (Claude fallback)

**Optimized:**
- Research: ~$0.05-0.10 per task (Kimi)
- Synthesis: ~$0.30-0.50 per task (Claude only when needed)
- Summaries: ~$0.01 per task (Gemini when available)

**Target:** 70-90% cost reduction on subagent work

### Implementation

**Option 1: Model Override per Spawn**
```python
sessions_spawn(task="...", model="kimi-k2.5")  # For research
sessions_spawn(task="...", model="claude-sonnet-4-5")  # For synthesis
```

**Option 2: Config-Based Routing**
Update openclaw.json with task patterns:
```json
"routing": {
  "research": ["kimi", "deepseek"],
  "synthesis": ["claude", "kimi"],
  "quick": ["flash"]
}
```

**Recommendation:** Option 1 (explicit per spawn) for now. Clear, controllable, immediate.

### Action Items

1. ✅ Document current routing (this file)
2. 🔄 Update all spawn calls to use task-appropriate models
3. 🔄 Track costs before/after for 1 week
4. 🔄 Evaluate: cheaper enough? adjust if needed
