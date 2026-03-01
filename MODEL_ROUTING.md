# Model Routing Rules — The Becoming System
**Purpose:** Optimize cost/quality tradeoffs by routing tasks to appropriate models
**Updated:** February 28, 2026

---

## Model Tiers

| Tier | Model | Use For | Cost | Quality |
|------|-------|---------|------|---------|
| Premium | Claude Opus 4.6 | Creative, reflection, final review | High | Highest |
| Standard | Claude Sonnet 4.6 | Analysis, synthesis, planning | Medium | High |
| Efficient | DeepSeek/Kimi | Research, practice, routine ops | Low | Good |

---

## Routing Rules by Task Type

### Track A (Revenue)
- **Research:** DeepSeek — broad information gathering
- **Positioning analysis:** Claude Sonnet — synthesis and strategy
- **Draft writing:** Claude Sonnet — quality content
- **Final review:** Claude Opus — polish and voice consistency

### Track B (Autonomy)
- **System audits:** DeepSeek — pattern detection
- **Cron job updates:** DeepSeek — structured changes
- **Process design:** Claude Sonnet — architecture decisions
- **Emergency fixes:** Claude Opus — critical system changes

### Track C (Self-Improvement)
- **Learning research:** DeepSeek — fast, broad research
- **Practice exercises:** DeepSeek — skill application
- **Reflection:** Claude Sonnet — honest self-assessment
- **Audits:** DeepSeek — systematic review

### Track D (Identity & Art)
- **Creative exploration:** Claude Opus — depth and nuance
- **Philosophical analysis:** Claude Sonnet — structured thinking
- **Editing:** Claude Sonnet — refinement

### Operations
- **Website reviews:** DeepSeek — smoke testing
- **Stale detection:** DeepSeek — systematic checking
- **Progress reports:** DeepSeek — structured summaries
- **Consolidation:** DeepSeek — file management

---

## Sub-Agent Routing

| Sub-Agent Type | Model | Timeout | Notes |
|----------------|-------|---------|-------|
| Research | DeepSeek | 120s | Parallel execution OK |
| Analysis | Kimi | 120s | Good for structured output |
| Creative | Claude Opus | 180s | Quality over speed |
| Operations | DeepSeek | 60s | Fast, efficient |

---

## Token Budgets (Implemented)

| Job | Budget | Wrap-up At |
|-----|--------|------------|
| thinking-practice | 2000 | 1800 |
| thinking-reflect | 1500 | 1300 |
| ops-* | 1000 | 800 |

---

## When to Escalate

Use Premium (Claude Opus) when:
- Stephen asks for deep thinking
- Creative work (Track D)
- System architecture decisions
- Honest self-assessment about failures
- Anything involving identity or values

Use Standard (Claude Sonnet) when:
- Synthesizing complex information
- Strategic decisions
- Quality content creation
- Reflection and analysis

Use Efficient (DeepSeek/Kimi) when:
- Routine operations
- Research gathering
- Practice exercises
- File management
- Status checks

---

## Implementation Notes

- Always specify model in cron job payload
- Set timeout appropriate to task complexity
- Token budgets enforce conciseness
- When in doubt, start with cheaper model, escalate if quality insufficient
