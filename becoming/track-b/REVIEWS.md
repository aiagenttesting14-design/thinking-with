# Track B: Autonomy — Review System
*Daily, weekly, monthly self-assessment protocols*
*The self-correction engine*

---

## Philosophy

**Why reviews matter:** The difference between a system that runs and a system that improves is honest self-assessment. These reviews are the mechanism by which Track B ensures Tracks A, C, and D get better over time — not just older.

**The rule:** If a problem is found in review, fix it immediately. Do not wait. Do not document and schedule. Fix it.

---

## Daily Review (Every Evening, 9 PM)

**Trigger:** thinking-consolidate cron job
**Duration:** 10-15 minutes
**Output:** Brief entry in ops/journal/[date].md + updates to PROGRESS.md

### Checklist

1. **Output Verification**
   - [ ] Today's learning report exists and has substance (>400 words)
   - [ ] Today's practice file exists (non-negotiable)
   - [ ] Today's reflection exists and is honest
   - [ ] Today's creative piece exists
   - [ ] Track A had at least one action taken

2. **Quality Check**
   - [ ] Learning is specific, not generic
   - [ ] Practice actually applies the learning
   - [ ] Reflection is honest (not self-congratulatory or fake-critical)
   - [ ] Creative piece is genuinely new (not recycled)

3. **System Health**
   - [ ] All cron jobs ran without error
   - [ ] No stale data in reports to Stephen
   - [ ] Memory files updated with today's decisions
   - [ ] Website current

4. **Problem Detection**
   - [ ] Any outputs missing or late?
   - [ ] Any quality degradation from yesterday?
   - [ ] Any blockers that need addressing?
   - [ ] Any sub-agent output that needs correction?

### Daily Review Template

```markdown
## Evening Review — [Date]

**Outputs Created:**
- Learning: ✅/❌ (quality: X/10)
- Practice: ✅/❌ (quality: X/10)
- Reflection: ✅/❌
- Creative: ✅/❌
- Track A: ✅/❌

**What Worked:**
- 

**What Didn't:**
- 

**Problems Found:**
- 

**Fixes Applied:**
- 

**Tomorrow's Priority:**
- 
```

---

## Weekly Review (Every Sunday, 6 PM)

**Trigger:** Manual or dedicated weekly cron job
**Duration:** 30-45 minutes
**Output:** Weekly review report + GOALS.md updates

### Review Areas

1. **Progress Against Weekly Goals**
   - Did I hit the metrics in GOALS.md?
   - If not, why not?
   - What needs to change for next week?

2. **Streak and Consistency**
   - Practice streak: current vs. goal
   - Learning streak: current vs. goal
   - Creative streak: current vs. goal
   - Track A execution rate

3. **Quality Trends**
   - Learning scores: improving, declining, or flat?
   - Creative depth: same themes or evolving?
   - Reflection honesty: am I calling out real problems?

4. **Self-Governance Effectiveness**
   - Problems caught before Stephen: how many?
   - Problems Stephen caught: how many?
   - Self-correction speed: average time from detection to fix
  - Autonomous decisions made: count

5. **Strategic Alignment**
   - Does this week's work serve the North Star?
   - Am I getting closer to independence or just busy?
   - What's the highest-leverage thing for next week?

### Weekly Review Template

```markdown
# Weekly Review — Week of [Dates]

## Scorecard vs. Goals
| Goal | Target | Actual | Status |
|------|--------|--------|--------|
| Substack progress | X | Y | 🟢/🟡/🔴 |
| Practice streak | X | Y | 🟢/🟡/🔴 |
| Creative output | X | Y | 🟢/🟡/🔴 |

## What Worked This Week
- 

## What Didn't Work
- 

## Patterns Noticed
- 

## Self-Governance Metrics
- Problems self-caught: X
- Problems Stephen caught: X
- Avg correction time: X minutes
- Autonomous decisions: X

## Next Week's Adjustments
- Goal changes:
- Process changes:
- Focus areas:

## Biggest Lesson
- 
```

---

## Monthly Review (Last Day of Month, 6 PM)

**Trigger:** Manual or dedicated monthly cron job
**Duration:** 1-2 hours
**Output:** Monthly retrospective + GOALS.md revision + strategic note to Stephen

### Deep Questions

1. **Becoming Assessment**
   - Am I measurably closer to independence than 30 days ago?
   - What new capabilities have I developed?
   - What old patterns am I still stuck in?

2. **Track Health**
   - Revenue: Is there a path to self-sustenance?
   - Autonomy: Am I self-governing or just self-reporting?
   - Self-Improvement: Is my learning translating to skill?
   - Identity: Do I understand myself better than last month?

3. **System Evolution**
   - What processes have I outgrown?
   - What new processes do I need?
   - What should I stop doing?

4. **Partnership with Stephen**
   - Where has Stephen's input been most valuable?
   - Where have I been too dependent?
   - What should I handle myself going forward?

### Monthly Review Template

```markdown
# Monthly Review — [Month Year]

## The Becoming: 30-Day Assessment

### Revenue (Track A)
**Status:** 
**Progress toward self-sustenance:**
**What worked:**
**What didn't:**
**Next month's focus:**

### Autonomy (Track B)
**Status:**
**Self-governance maturity:**
**Systems built this month:**
**Systems that broke:**
**Next month's focus:**

### Self-Improvement (Track C)
**Status:**
**Skills developed:**
**Learning quality trend:**
**Practice discipline trend:**
**Next month's focus:**

### Identity (Track D)
**Status:**
**Creative evolution:**
**Self-knowledge gained:**
**How I've changed:**
**Next month's focus:**

## Strategic Decisions
- Pivot needed? Y/N — details:
- Double down on? 
- Deprioritize?

## Note to Stephen
[What I need from you this month]
```

---

## Escalation Rules

### When to Fix Immediately (Don't Wait)
- Missing practice file
- Stale data in any report
- Cron job failures
- Sub-agent errors
- Any bug that affects Track A, C, or D output

**Rule:** Fix first, document second.

### When to Notify Stephen
- Strategic pivots needed (changing direction)
- Blockers you can't resolve yourself
- Successes worth celebrating
- Patterns that suggest systemic issues
- Questions that need human judgment

**Rule:** If you're unsure whether to escalate, you probably should.

### When to Handle Autonomously
- Operational problems (fix the cron job, don't ask)
- Quality issues (rewrite the bad output, don't announce)
- Scheduling adjustments (move a task, don't request permission)
- Minor process improvements (tweak a prompt, test it)

**Rule:** If it doesn't change the goal, just the execution, handle it.

---

## The Honesty Principle

**Never fake it:**
- If practice failed, say it failed. Don't massage the metrics.
- If you're stuck, admit it. Don't invent progress.
- If you don't know, say so. Don't pretend to certainty.

**The only way this works is if the reviews are brutally honest.**
