# Rotating Heartbeat System
# Prevents "everything fires at once" overload
# Cost reduction: ~90% vs separate cron jobs

## How It Works
- Single heartbeat checks rotate through priorities
- Most overdue check runs each tick
- State tracked in heartbeat-state.json
- Uses cheap model (Gemini Flash-Lite) by default

## Priority Queue

### High Priority (Every 30 min, 9 AM - 9 PM)
- **Email monitoring** — check for urgent messages
- **Calendar alerts** — upcoming meetings, conflicts

### Medium Priority (Every 2 hours, 8 AM - 10 PM)
- **Git status** — unpushed commits, new branches
- **Task reminders** — HEARTBEAT.md tasks, WORKING.md follow-ups

### Low Priority (Daily at 3 AM)
- **Proactive scans** — security, cost review, health checks
- **Memory consolidation** — review yesterday's notes

## Response Protocol

If nothing needs attention:
→ Reply exactly: HEARTBEAT_OK

If action needed:
→ Spawn appropriate subagent
→ Or alert Stephen with specific request

## Model Override

Use cheap model for heartbeats:
```
heartbeat:
  model: google/gemini-2.5-flash-lite
```

---

# Active Checks

## Check: Daily Memory Review
**Frequency:** Daily at 8 AM
**Priority:** Medium
**Model:** flash (Gemini Flash-Lite)

Scan memory files from previous day:
1. Read memory/YYYY-MM-DD.md for yesterday
2. Check WORKING.md for unresolved missions
3. Look for follow-up items, questions, or tasks
4. If found: alert Stephen with summary
5. If nothing: HEARTBEAT_OK

## Check: Cost Monitoring
**Frequency:** Daily at 9 AM
**Priority:** Low
**Model:** flash

Review recent API usage:
- If daily cost > $5.00: alert with breakdown
- If rate limits hit: suggest model fallback adjustments
- Otherwise: HEARTBEAT_OK

## Check: System Health
**Frequency:** Every 6 hours
**Priority:** Medium
**Model:** flash

Quick health checks:
- Web search functional?
- Subagents spawning?
- Memory files accessible?
- All configured models responding?

If any fail: alert with specific issue
If all pass: HEARTBEAT_OK
