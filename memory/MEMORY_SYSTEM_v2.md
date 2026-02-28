# Memory System v2 — Dynamic Context Management

*Implemented: 2026-02-25*
*Replaces: Implicit 3-day cycle (no explicit rules)*

---

## The Problem with Fixed Rules

**Research finding:** Fixed time-based rules (like a "7-day summarization rule") are too simplistic and harmful. They:
- Lose critical operational details (file paths, decisions, constraints)
- Create "goldfish" behavior — forgetting mid-project context
- Don't match actual context window dynamics

**Better approach:** Context-window thresholds + relevance-weighted retrieval

---

## The New System: Three Tiers

### Tier 1: Working Memory (Always Available)
- **Content:** Last 20 messages (turns) from current session
- **Format:** Full detail, no compression
- **Purpose:** Immediate task continuity
- **Trigger:** Automatic — always in context

### Tier 2: Recent Context (Session-Based)
- **Content:** Earlier messages from current session
- **Format:** Light distillation (narrative + key facts preserved)
- **Purpose:** Session-level continuity
- **Trigger:** When context exceeds 50% of window

### Tier 3: Archival Memory (On-Demand)
- **Content:** Previous sessions, consolidated learning, patterns
- **Format:** Summarized + searchable via memory_search
- **Purpose:** Long-term learning, pattern recognition
- **Trigger:** Explicit memory_search calls

---

## When to Distill vs. Archive

| Trigger | Action | What Gets Preserved |
|---------|--------|---------------------|
| Context at 50% | Light distillation | Narrative arc + key facts |
| Context at 70% | Aggressive distillation | Key facts only + explicit reasoning |
| Session end | Archive to journal | Full consolidation |
| 3-day cycle | Memory consolidation | Extracted patterns, lessons learned |

---

## Revert Instructions

**If this system causes problems:**

1. **Quick revert:** Comment out this file's reference in WORKING.md
2. **Full revert:** Delete this file, system falls back to implicit 3-day cycle
3. **Hybrid option:** Keep Tier 1 only (working memory), disable Tiers 2-3

**Signs of problems:**
- Agent forgets file paths or decisions mid-task
- "Groundhog day" effect (repeated questions)
- Contradicts earlier decisions
- Cannot continue multi-step tasks

**Emergency fallback:** Read full journal files directly instead of relying on memory system

---

## Testing This System

**After 3 days, verify:**
- [ ] Agent references decisions from hours ago correctly
- [ ] Doesn't ask questions already answered
- [ ] Maintains consistency across long sessions
- [ ] Token usage stays bounded

**Metrics to track:**
- Context window utilization (target: 40-60%)
- Retrieval accuracy (manual spot-checks)
- Task completion rate for multi-step work

---

## Why This Beats the 7-Day Rule

| 7-Day Rule | Context-Threshold System |
|------------|-------------------------|
| Fixed time, ignores actual usage | Responds to real context pressure |
| Summarizes everything at once | Gradual, tiered compression |
| Loses mid-project context | Preserves working memory intact |
| One-size-fits-all | Adapts to task complexity |

**Source:** Research on MemGPT, Letta benchmarks, Stanford "lost in the middle" studies
