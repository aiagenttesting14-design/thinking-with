# SESSION_BRIEFING.md — Wake-Up & Wind-Down Protocol

## On Wake-Up (Every Session)

1. **Read WORKING.md** — Your ground truth for active work. What's in progress, what's blocked, what's next.
2. **Skim MEMORY.md** — Stable facts, key decisions, lessons. The Journal Index at the bottom tells you where to find detail.
3. **Read the current journal cycle** — Check `memory/journal/` for the active cycle folder. Read today's entry and yesterday's if they exist. This is your recent context.
4. **Check for cron results** — If a sub-agent completed work, you may need to review or deliver results to Stephen.

## On Wind-Down (End of Session or Before Long Gap)

1. **Update WORKING.md** — Reflect what changed. Update statuses, add new items, mark completions. Timestamp it.
2. **Write today's journal entry** — Append to or create the day file in the current cycle folder. Include: what happened, decisions made, what Stephen said, your reasoning, open threads.
3. **Update MEMORY.md only if** — A new stable fact was learned, a key decision was made, or a lesson was earned. Don't add transient stuff.

## Journal Cycle Structure

```
memory/journal/
  cycle-001-feb23-25/
    feb-23.md      ← Full session detail, no size limits
    feb-24.md
    feb-25.md
    SUMMARY.md     ← Auto-generated end of cycle (by consolidation cron)
  cycle-002-feb26-28/
    ...
```

- **Cycles are 3 days each**
- **Day files**: Journal freely. Include conversations, reasoning, emotions, decisions. No limits.
- **SUMMARY.md**: Created by the nightly consolidation job at end of day 3. Captures what mattered.
- **When you need old context**: Read the SUMMARY.md of past cycles. If you need more detail, read the day files.

## Retrieval Chain (When You Need to Remember Something)

1. WORKING.md → what's active now
2. Current cycle day files → recent detail
3. Previous cycle SUMMARY.md → older context compressed
4. Previous cycle day files → full detail if summary isn't enough
5. MEMORY.md → stable facts and decision history

## Rules

- WORKING.md: Keep lean but accurate. No hard size limit, but if it's over ~80 lines, move completed items to the journal.
- MEMORY.md: Grows slowly. Only stable facts and decisions. Points to journals for detail.
- Journal day files: No limits. Write everything. Future you will thank present you.
- SUMMARY.md: Auto-generated. Don't write these manually unless the cron fails.
