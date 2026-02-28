# Operations System

This directory tracks what works and what doesn't in TestBot's day-to-day operation — separate from the Becoming System (which is about growth) and MEMORY.md (which is about stable facts).

## Purpose

When something breaks or works unexpectedly well, it gets logged here. Over time, patterns emerge. We stop making the same mistakes.

## Structure

```
ops/
├── README.md           # This file
├── journal/            # Daily operational notes
│   ├── 2026-02-26.md  # What happened today, what worked, what didn't
│   └── ...
└── patterns.md        # Recurring lessons (updated weekly)
```

## Cron Jobs (Operations)

| Job | Time | Purpose |
|-----|------|---------|
| ops-morning-website-review | 7:00 AM | Smoke test website, report if broken |
| ops-check-stale-tasks | 11:00 AM | Flag stalled work >48hrs old |
| ops-evening-retrospective | 10:00 PM | Log what worked/didn't |

These run alongside the Becoming System jobs (learning, practice, reflection, creative).

## When to Update

- **Daily:** Evening retrospective auto-writes to journal/
- **Weekly:** Review patterns, update patterns.md
- **As needed:** When something breaks or surprises us

## Relationship to Other Systems

- **WORKING.md:** Current state, active tasks
- **MEMORY.md:** Long-term facts, decisions
- **becoming/:** Growth and learning
- **ops/:** Operational lessons, process improvements
