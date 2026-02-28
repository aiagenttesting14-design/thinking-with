# HEALTH.md — System Health Check Reference

*Last updated: 2026-02-27 (Day 5)*
*Owner: Track B*
*Purpose: Automated health checks — what to run, when, and what to do when checks fail*

---

## HEALTH CHECK SCHEDULE

| Time | Agent | Check | What to Do if It Fails |
|------|-------|-------|------------------------|
| 6 AM | morning-wake | Yesterday's practice file | Create it immediately |
| 6 AM | morning-wake | Yesterday's reflection file | Create if possible |
| 6 AM | morning-wake | MEMORY.md updated yesterday | Update now |
| 6 AM | morning-wake | WORKING.md current | Update now |
| 12 PM | practice | Today's learning completed | Note in practice file; proceed |
| 9 PM | consolidation | All daily files created | Create missing files |
| 9 PM | consolidation | PROGRESS.md updated | Update now |
| 9 PM | consolidation | Streaks current | Recalculate |
| 9 PM | consolidation | WORKING.md "Just Completed" | Update now |

---

## MORNING HEALTH CHECK (6 AM)

Run this at start of morning-wake sub-agent:

```
YESTERDAY = [today's date - 1 day in format YYYY-MM-DD]

CHECK 1: Practice file
→ Does track-c/practice/[YESTERDAY].md exist?
→ If NO: Create it now. Use today's prompt:
   "Write 300+ words applying ONE concrete technique from yesterday's learning 
   (track-c/learnings/[YESTERDAY].md). Show the technique applied, not just described. 
   Be honest about what worked and didn't. This is backfill — acknowledge that."
→ Do NOT start today's work until this is done.

CHECK 2: Reflection file  
→ Does track-c/reflections/[YESTERDAY].md exist?
→ If NO: Create minimal reflection (200+ words: quality scores, one pattern, one change)
→ If file is <100 words: expand it

CHECK 3: Memory updates
→ Does MEMORY.md contain "Lessons Learned" for yesterday?
→ If NO: Add them from yesterday's learning report
→ Does WORKING.md reflect current state?
→ If "Just Completed" is stale: update it

CHECK 4: Cron job status
→ Did all cron jobs run yesterday? (check system logs if accessible)
→ If any failed: document in WORKING.md

AFTER ALL CHECKS PASS: Proceed with today's morning-wake focus work.
```

---

## MIDDAY HEALTH CHECK (12 PM — integrated with practice agent)

```
CHECK 1: Morning work completed?
→ Does track-c/learnings/[TODAY].md exist?
→ If NO: Note in practice file; proceed with practice anyway using yesterday's learning
→ If YES: Use today's learning for practice

CHECK 2: Any blocked work?
→ Is any track unable to proceed for a reason outside Track B's control?
→ If YES: Document in WORKING.md and (if 3+ days) escalate to Stephen
```

---

## EVENING HEALTH CHECK (9 PM — consolidation agent)

```
TODAY = [current date in format YYYY-MM-DD]

REQUIRED FILES:
[ ] track-c/learnings/[TODAY].md        → EXISTS? SIZE > 200 words?
[ ] track-c/practice/[TODAY].md         → EXISTS? SIZE > 300 words? SHOWS APPLICATION?
[ ] track-c/reflections/[TODAY].md      → EXISTS? SIZE > 200 words? HONEST SCORES?
[ ] track-d/[TODAY].md                  → EXISTS? SIZE > 800 words? GENUINE VOICE?

FOR EACH MISSING FILE:
1. Check if content exists to create it (other files from today)
2. If yes: create it now (minimum viable)
3. If no content available: document the gap honestly in PROGRESS.md

MEMORY UPDATE:
[ ] Update PROGRESS.md: today's row in weekly overview, day-by-day log entry
[ ] Update WORKING.md: "Just Completed" section, current status
[ ] Update MEMORY.md: "Lessons Learned Today" if any significant discoveries
[ ] Recalculate streaks in PROGRESS.md

TRACK A CHECK:
[ ] Any new content in track-a/substack/drafts/?
[ ] If drafts folder empty for 7+ days: flag in WORKING.md

DETERMINE STATUS:
→ GREEN: All 4 files exist and have minimum content
→ YELLOW: 1-2 files missing or below minimum
→ RED: 3+ files missing, or practice missing for 3rd consecutive day

LOG THE STATUS in WORKING.md.
```

---

## WHAT EACH STATUS MEANS

### 🟢 GREEN — System Healthy
All outputs created. All tracks progressing.
Action: Update memory files. Log success. Continue.

### 🟡 YELLOW — System Degraded
1-2 outputs missing or below quality. Single track struggling.
Action: Create missing files. Diagnose root cause. Implement fix in morning audit.
Do NOT escalate to Stephen unless it persists for 3+ days.

### 🔴 RED — System Failure
3+ outputs missing, or critical track stalled.
Action: 
1. Create all missing files immediately (minimum viable)
2. Identify root cause — is this systemic or one-time?
3. If systemic: document fix in PLAYBOOK.md and implement it
4. If practice is RED for 5+ consecutive days: escalate to Stephen

---

## CURRENT SYSTEM STATUS (as of Day 5)

🔴 **Practice sub-system: CRITICAL**
- Practice broken for 3 consecutive days (Feb 25, 26, 27)
- No enforcement mechanism exists
- Fix deployed: Morning audit added to this file and REVIEWS.md
- Next check: Day 6 morning — did morning-wake agent create Day 5 backfill?

🟢 **Learning sub-system: HEALTHY**
- 5/5 days complete, quality 8-9/10
- No intervention needed

🟢 **Creative sub-system: HEALTHY**
- 5/5 days complete, quality 9/10
- Not yet feeding Track A — curation not started

🔴 **Track A sub-system: STALLED**
- Running for 4+ days with no visible output
- Drafts folder empty
- Fix needed: Give Track A agent specific writing task, not open-ended research

🟢 **Memory sub-system: HEALTHY**
- MEMORY.md, WORKING.md updated daily
- No compression needed yet

🟢 **Cron system: HEALTHY**
- 10 jobs running, all active as of today

---

## THE FIX BACKLOG

Issues identified that need fixing, in priority order:

1. **CRITICAL**: Create practice backfill files for Days 3-5 (Feb 25-27)
   - Who: Morning-wake agent (Day 6, Feb 28)
   - What: 3 practice files, 300+ words each
   - Why: Restore streak, demonstrate emergency resumption principle

2. **HIGH**: Track A sub-agent must produce visible output
   - Who: Track A sub-agent (every 4hrs)
   - What: Specific writing prompt → first Substack draft
   - Why: 4+ days of running with zero output is not autonomy

3. **MEDIUM**: Creative pieces need curation review
   - Who: Track B (can be done in any session)
   - What: Read 5 pieces, flag Substack-ready ones, update track-a pipeline
   - Why: D is feeding nothing right now

4. **LOW**: Creative page website update
   - Who: Daily website update cron job
   - What: Configure to pull 5 most recent track-d/ files
   - Why: Creative work should be visible

