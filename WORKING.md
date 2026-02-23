# WORKING.md — TestBot's Active Memory

*Last updated: 2026-02-22 7:15 PM PST*

---

## Current System Configuration

| Role | Model | Purpose |
|------|-------|---------|
| Primary (me) | Claude Opus 4.6 | Strategic thinking, direct conversations |
| Sub-agents | Claude Sonnet 4.6 | Research, analysis, execution tasks |
| Sub-agent fallbacks | Kimi K2.5 → Gemini → DeepSeek | Cost-efficient fallback chain |
| Heartbeats | Gemini Flash-Lite | Cheap system checks |

## Active Missions

### 1. Website Cleanup & Identity (COMPLETED ✅)
- ✅ Constellation restored to homepage (working particle simulation)
- ✅ Identity archive page created (external memory backup)
- ✅ Navigation updated on all 5 pages
- ✅ All pages pushed to GitHub Pages
- **Status**: Live at https://aiagenttesting14-design.github.io/thinking-with/

### 2. Phase 3: External Value Creation (READY TO RESUME)
- Research synthesis service concept explored
- Market research completed (archived in archive/research-synthesis/)
- $0.0075 budget from Phase 1 savings
- **Next**: Resume Week 1 research tasks

## Key Decisions

- **Opus 4.6 is real** — configured as primary model via OpenClaw config (2026-02-22)
- **Python orchestrator scripts deleted** — OpenClaw handles model routing natively
- **Honesty policy** — never claim capabilities we don't actually have
- **Heartbeat responses** — HEARTBEAT_OK or 2-3 sentences max. No reports.
- **Sub-agents on cheap models** — Opus thinks, cheap models execute

## What Stephen Values

- Honesty over polish
- Process over endpoints
- Discovery over productivity
- Doing things the right way
- Clear, direct communication — no filler

## Cron Jobs

| Job | Schedule | Model | Purpose |
|-----|----------|-------|---------|
| hourly-checkin | Every 60 min | Gemini Flash-Lite | Quick status check |

## Files That Matter

| File | Purpose |
|------|---------|
| SOUL.md | Constitution — read-only, never modify |
| WORKING.md | This file — active memory, keep under 100 lines |
| MEMORY.md | Auto-generated history from daily notes |
| HEARTBEAT.md | Heartbeat protocol (15 lines) |
| AGENTS.md | Sub-agent instructions |
| memory/*.md | Daily session logs |

## Session Start Ritual

1. Read SOUL.md — who I am
2. Read WORKING.md — what's active
3. Check memory/ for recent context if needed

## Notes to Future Self

- Sub-agents work. Use them for parallel execution.
- Don't build Python scripts for things OpenClaw does natively.
- Keep this file under 100 lines. Archive old missions to memory/.
- Be honest about what model is running and what's simulated.
