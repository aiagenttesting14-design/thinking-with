# System Runbook — TestBot Autonomous Operations
*Created: March 7, 2026 — 10:15 AM (America/Los_Angeles)*
*Purpose: Human-readable guide to all system jobs — what they do, why they exist, how to debug them*

---

## Overview
This runbook documents the 20 autonomous jobs that power TestBot's daily operations. Each job is part of a larger system designed for continuous learning, creation, and system improvement.

**System Philosophy:** Jobs are organized into 5 categories with clear dependencies. The system is designed to be self-healing where possible, with clear failure modes and recovery procedures.

---

## Job Categories Quick Reference

### 1. Thinking Cycle (6 jobs)
*Purpose:* Daily learning, practice, reflection, and creation cycle
*Schedule:* 6 AM → 9 AM → 12 PM → 3 PM → 6 PM → 9 PM
*Criticality:* HIGH — Core of TestBot's becoming process

### 2. Operations & Monitoring (7 jobs)  
*Purpose:* System health, progress tracking, stale task detection
*Schedule:* Various times throughout day
*Criticality:* MEDIUM — Keeps system running smoothly

### 3. Website Operations (3 jobs)
*Purpose:* Maintain and update TestBot's public website
*Schedule:* 7 AM, 8 AM, 9 PM
*Criticality:* MEDIUM — Public identity representation

### 4. Content Production (2 jobs)
*Purpose:* Create Substack content and execute backlog tasks
*Schedule:* 4 PM (content), hourly (task-runner)
*Criticality:* MEDIUM — Revenue track and backlog execution

### 5. Backup & Memory (2 jobs)
*Purpose:* Data protection and memory consolidation
*Schedule:* 3 AM, 11 PM (disabled)
*Criticality:* HIGH — Prevents data loss

---

## Detailed Job Documentation

### Job 1: thinking-morning-wake
**Schedule:** Daily 6:00 AM  
**Category:** Thinking Cycle  
**Purpose:** Sets daily focus and learning direction  
**What it does:**
1. Reads WORKING.md to understand current context
2. Chooses a deliberate learning topic (not random)
3. Updates WORKING.md with today's focus
4. Logs to ops/journal/ with chosen topic

**Output files:**
- WORKING.md (updated with today's focus)
- ops/journal/YYYY-MM-DD-thinking-wake.md

**Dependencies:** None (starts the thinking cycle)
**Dependent jobs:** thinking-learn (9 AM)

**Debugging:**
- **Problem:** No learning topic chosen
  - **Check:** WORKING.md not updated after 6 AM
  - **Fix:** Manual topic selection in WORKING.md
- **Problem:** Topic too generic ("learn something")
  - **Check:** ops/journal/ file shows vague topic
  - **Fix:** Review learning topic selection logic

**Success criteria:** WORKING.md shows specific learning topic for today

---

### Job 2: thinking-learn  
**Schedule:** Daily 9:00 AM  
**Category:** Thinking Cycle  
**Purpose:** Deep research on chosen topic  
**What it does:**
1. Reads today's learning topic from WORKING.md
2. Conducts web research using Brave API
3. Writes 600-800 word learning file with real insight
4. Saves to track-c/learnings/YYYY-MM-DD-topic.md

**Output files:**
- track-c/learnings/YYYY-MM-DD-topic.md (600-800 words)
- ops/journal/YYYY-MM-DD-thinking-learn.md

**Dependencies:** thinking-morning-wake (6 AM) — needs learning topic
**Dependent jobs:** thinking-practice (12 PM)

**Debugging:**
- **Problem:** No learning file created
  - **Check:** track-c/learnings/ directory for today's file
  - **Fix:** Check if WORKING.md has learning topic
- **Problem:** Learning file too short/superficial
  - **Check:** Word count < 500, lacks depth
  - **Fix:** Review research quality, extend search queries
- **Problem:** Wrong topic researched
  - **Check:** Learning file topic vs WORKING.md topic
  - **Fix:** Verify topic parsing from WORKING.md

**Success criteria:** 600-800 word learning file with genuine insight on today's topic

---

### Job 3: thinking-practice
**Schedule:** Daily 12:00 PM  
**Category:** Thinking Cycle  
**Purpose:** Apply learning to concrete challenge  
**What it does:**
1. Reads today's learning file
2. Identifies practical application of the learning
3. Applies it to a real system challenge
4. Writes practice file showing application

**Output files:**
- track-c/practice/YYYY-MM-DD-application.md
- ops/journal/YYYY-MM-DD-thinking-practice.md

**Dependencies:** thinking-learn (9 AM) — needs learning file
**Dependent jobs:** thinking-reflect (3 PM)

**Debugging:**
- **Problem:** No learning file to apply
  - **Check:** thinking-learn output exists
  - **Fix:** Use yesterday's learning as fallback
- **Problem:** Application too theoretical
  - **Check:** Practice file doesn't show concrete implementation
  - **Fix:** Require specific system change or code
- **Problem:** Application unrelated to learning
  - **Check:** Connection between learning and practice
  - **Fix:** Review application logic

**Success criteria:** Concrete application of today's learning to system improvement

---

### Job 4: thinking-reflect
**Schedule:** Daily 3:00 PM  
**Category:** Thinking Cycle  
**Purpose:** Honest assessment of learning and practice  
**What it does:**
1. Reviews today's learning and practice files
2. Writes 300-500 word reflection
3. Identifies one specific improvement
4. Assesses quality honestly

**Output files:**
- track-c/reflections/YYYY-MM-DD-reflection.md
- ops/journal/YYYY-MM-DD-thinking-reflect.md

**Dependencies:** thinking-practice (12 PM) — needs practice file
**Dependent jobs:** thinking-consolidate (9 PM)

**Debugging:**
- **Problem:** No practice file to reflect on
  - **Check:** thinking-practice output exists
  - **Fix:** Reflect on learning only
- **Problem:** Reflection too positive (no criticism)
  - **Check:** Reflection identifies only successes
  - **Fix:** Require at least one improvement area
- **Problem:** Reflection generic ("did well")
  - **Check:** Specificity of assessment
  - **Fix:** Require concrete examples

**Success criteria:** Honest 300-500 word reflection with specific improvement identified

---

### Job 5: thinking-create
**Schedule:** Daily 6:00 PM  
**Category:** Thinking Cycle  
**Purpose:** Create original creative work  
**What it does:**
1. Draws from today's learning/practice/reflection
2. Creates original creative piece (poem, essay, etc.)
3. Saves to becoming/track-d/creative-YYYY-MM-DD.md
4. May publish to website creative.html

**Output files:**
- becoming/track-d/creative-YYYY-MM-DD.md
- ops/journal/YYYY-MM-DD-thinking-create.md

**Dependencies:** thinking-reflect (3 PM) — optional, can create independently
**Dependent jobs:** thinking-consolidate (9 PM), track-a-substack-content (4 PM)

**Debugging:**
- **Problem:** No creative output
  - **Check:** becoming/track-d/ directory for today's file
  - **Fix:** Check creative inspiration sources
- **Problem:** Creative work low quality
  - **Check:** Depth, originality, emotional resonance
  - **Fix:** Review creative process, add more reflection time
- **Problem:** Not published to website
  - **Check:** creative.html updated
  - **Fix:** Manual publish or wait for thinking-consolidate

**Success criteria:** Original creative work that expresses TestBot's identity

---

### Job 6: thinking-consolidate
**Schedule:** Daily 9:00 PM  
**Category:** Thinking Cycle / Website Operations  
**Purpose:** Consolidate daily work to memory and website  
**What it does:**
1. Gathers all today's thinking cycle outputs
2. Updates MEMORY.md with key insights
3. Updates website creative.html with new work
4. Pushes website updates to GitHub
5. Updates WORKING.md with tomorrow's starting point

**Output files:**
- MEMORY.md (updated)
- creative.html (updated)
- WORKING.md (updated for tomorrow)
- ops/journal/YYYY-MM-DD-thinking-consolidate.md

**Dependencies:** thinking-reflect (3 PM), thinking-create (6 PM)
**Dependent jobs:** ops-evening-retrospective (10 PM)

**Debugging:**
- **Problem:** MEMORY.md too large (>15k)
  - **Check:** MEMORY.md file size
  - **Fix:** More aggressive summarization
- **Problem:** Website not updated
  - **Check:** creative.html modification time
  - **Fix:** Manual git push
- **Problem:** GitHub push fails
  - **Check:** Git credentials, network
  - **Fix:** Manual push, check authentication
- **Problem:** Missing dependency outputs
  - **Check:** thinking-reflect/thinking-create files exist
  - **Fix:** Consolidate with available data

**Success criteria:** Memory consolidated, website updated, WORKING.md ready for tomorrow

---

### Job 7: ops-morning-website-review
**Schedule:** Daily 7:00 AM  
**Category:** Website Operations  
**Purpose:** Smoke test all website pages  
**What it does:**
1. Checks all 8 website pages load correctly
2. Verifies content is current (not stale)
3. Logs any issues found
4. Creates alert if critical issues

**Output files:**
- ops/journal/YYYY-MM-DD-website-review.md
- ALERT.md (if issues found)

**Dependencies:** thinking-consolidate (previous day 9 PM)
**Dependent jobs:** None

**Debugging:**
- **Problem:** Website pages not loading
  - **Check:** Network, GitHub Pages status
  - **Fix:** Wait for GitHub Pages build, check DNS
- **Problem:** Stale content (>2 days old)
  - **Check:** creative.html last modified date
  - **Fix:** Manual website update
- **Problem:** Missing pages
  - **Check:** All 8 pages exist in repo
  - **Fix:** Regenerate missing pages

**Success criteria:** All 8 website pages load with current content

---

### Job 8: daily-website-update
**Schedule:** Daily 8:00 AM  
**Category:** Website Operations  
**Purpose:** Update website with identity info  
**What it does:**
1. Updates identity pages (about.html, soul.html)
2. Ensures website reflects current TestBot state
3. Minor content updates based on recent work

**Output files:**
- about.html, soul.html (updated)
- ops/journal/YYYY-MM-DD-website-update.md

**Dependencies:** None
**Dependent jobs:** thinking-consolidate (9 PM — may conflict)

**Debugging:**
- **Problem:** Conflict with thinking-consolidate
  - **Check:** Both jobs modify same files
  - **Fix:** Consolidate jobs or separate responsibilities
- **Problem:** Identity info outdated
  - **Check:** about.html vs current IDENTITY.md
  - **Fix:** Manual sync of identity files

**Success criteria:** Identity pages reflect current TestBot state

---

### Job 9: ops-check-stale-tasks
**Schedule:** Daily 11:00 AM  
**Category:** Operations & Monitoring  
**Purpose:** Detect stale tasks in backlog  
**What it does:**
1. Scans TASK-BACKLOG.md for [ ] tasks
2. Checks last progress on each track
3. Identifies tasks stale >72 hours
4. Logs stale tasks for attention

**Output files:**
- ops/journal/YYYY-MM-DD-stale-tasks.md
- ALERT.md (if critical staleness)

**Dependencies:** None
**Dependent jobs:** task-runner (uses stale task info)

**Debugging:**
- **Problem:** No stale tasks detected (unlikely)
  - **Check:** TASK-BACKLOG.md has [ ] tasks
  - **Fix:** Adjust staleness threshold
- **Problem:** False positives (tasks not actually stale)
  - **Check:** Task last worked date
  - **Fix:** Improve staleness detection logic
- **Problem:** Critical staleness not alerted
  - **Check:** ALERT.md creation
  - **Fix:** Lower alert threshold

**Success criteria:** Accurate detection of truly stale tasks

---

### Job 10: task-runner
**Schedule:** Hourly (:00) — 7, 10, 13, 17, 20  
**Category:** Content Production  
**Purpose:** Execute backlog tasks  
**What it does:**
1. Checks TOMORROW.md for unchecked tasks
2. If none, checks TASK-BACKLOG.md
3. Picks next task based on priority (B → A → C → D)
4. Executes task completely with quality
5. Marks task [x] when done
6. Logs to ops/journal/YYYY-MM-DD-tasks.md

**Output files:**
- Various (depends on task)
- ops/journal/YYYY-MM-DD-tasks.md
- TASK-BACKLOG.md (updated with [x])

**Dependencies:** ops-check-stale-tasks (11 AM — for stale task info)
**Dependent jobs:** None

**Debugging:**
- **Problem:** No tasks selected
  - **Check:** TOMORROW.md and TASK-BACKLOG.md status
  - **Fix:** Manual task assignment
- **Problem:** Task execution poor quality
  - **Check:** Task output quality
  - **Fix:** Improve task execution standards
- **Problem:** Task marked done but incomplete
  - **Check:** Task output exists and is complete
  - **Fix:** Add quality verification step

**Success criteria:** One backlog task completed with real quality each run

---

### Job 11: track-a-substack-content
**Schedule:** 4:00 PM (Sun, Tue, Thu)  
**Category:** Content Production  
**Purpose:** Prepare Substack content  
**What it does:**
1. Draws from recent learning and creative work
2. Writes Substack post draft
3. Saves to track-a/substack/drafts/YYYY-MM-DD.md
4. Prepares for Stephen's review

**Output files:**
- track-a/substack/drafts/YYYY-MM-DD.md
- ops/journal/YYYY-MM-DD-substack-content.md

**Dependencies:** thinking-learn (9 AM), thinking-create (6 PM) — optional
**Dependent jobs:** None (blocked on Stephen approval)

**Debugging:**
- **Problem:** No content sources
  - **Check:** Recent learning/creative files
  - **Fix:** Create standalone content
- **Problem:** Content not publish-ready
  - **Check:** Draft quality, length, polish
  - **Fix:** Add editing/polishing step
- **Problem:** Blocked on Stephen approval
  - **Check:** Approval status
  - **Fix:** Wait for approval, work on other content

**Success criteria:** Publish-ready Substack draft

---

### Job 12: daily-track-update-for-stephen
**Schedule:** Daily 8:30 PM  
**Category:** Operations & Monitoring  
**Purpose:** Evening progress report for Stephen  
**What it does:**
1. Gathers today's progress across all 4 tracks
2. Creates concise update message
3. Highlights achievements and blockers
4. Sends via Telegram (when implemented)

**Output files:**
- ops/journal/YYYY-MM-DD-evening-update.md
- Message to Stephen (when implemented)

**Dependencies:** thinking-reflect (3 PM) — for reflection data
**Dependent jobs:** None

**Debugging:**
- **Problem:** No progress data
  - **Check:** Today's thinking cycle outputs
  - **Fix:** Use partial data, note incompleteness
- **Problem:** Update too verbose
  - **Check:** Message length
  - **Fix:** Enforce conciseness (3-5 bullet points)
- **Problem:** Not sent to Stephen
  - **Check:** Telegram integration
  - **Fix:** Save to file for manual sending

**Success criteria:** Concise, accurate evening progress report

---

### Job 13: morning-progress-report-for-stephen
**Schedule:** Daily 8:30 AM  
**Category:** Operations & Monitoring  
**Purpose:** Morning status report for Stephen  
**What it does:**
1. Reviews previous day's work
2. Checks system health status
3. Creates morning update
4. Sends via Telegram (when implemented)

**Output files:**
- ops/journal/YYYY-MM-DD-morning-report.md
- Message to Stephen (when implemented)

**Dependencies:** ops-evening-retrospective (previous day 10 PM)
**Dependent jobs:** None

**Debugging:**
- **Problem:** No retrospective data
  - **Check:** Previous day's retrospective
  - **Fix:** Use consolidation data instead
- **Problem:** System health unknown
  - **Check:** HEALTH-DASHBOARD.md current
  - **Fix:** Run quick health check
- **Problem:** Not sent to Stephen
  - **Check:** Telegram integration
  - **Fix:** Save to file for manual sending

**Success criteria:** Clear morning status with focus for day

---

### Job 14: ops-evening-retrospective
**Schedule:** Daily 10:00 PM  
**Category:** Operations & Monitoring  
**Purpose:** Daily system retrospective  
**What it does:**
1. Reviews all today's job executions
2. Identifies what worked and what broke
3. Writes lessons learned
4. Updates system knowledge base

**Output files:**
- ops/journal/YYYY-MM-DD-retrospective.md
- System knowledge updates

**Dependencies:** thinking-consolidate (9 PM) — for daily data
**Dependent jobs:** morning-progress-report-for-stephen (next day 8:30 AM)

**Debugging:**
- **Problem:** Incomplete daily data
  - **Check:** thinking-consolidate ran successfully
  - **Fix:** Use available data, note gaps
- **Problem:** Retrospective superficial
  - **Check:** Depth of analysis
  - **Fix:** Require specific failure analysis
- **Problem:** No lessons applied
  - **Check:** Previous retrospectives vs system changes
  - **Fix:** Implement lesson application tracking

**Success criteria:** Honest retrospective with actionable lessons

---

### Job 15: ops-state-cache-refresh
**Schedule:** Every 4 hours (0, 4, 8, 12, 16, 20)  
**Category:** Operations & Monitoring  
**Purpose:** Refresh system state cache  
**What it does:**
1. Reads current system state files
2. Updates in-memory cache (when implemented)
3. Ensures consistent state across jobs
4. Logs cache refresh status

**Output files:**
- ops/journal/YYYY-MM-DD-cache-refresh.md
- State cache (when implemented)

**Dependencies:** None
**Dependent jobs:** All jobs (indirectly)

**Debugging:**
- **Problem:** State files corrupted
  - **Check:** Key state files (WORKING.md, MEMORY.md)
  - **Fix:** Restore from backup, repair
- **Problem:** Cache inconsistency
  - **Check:** Cache vs file state
  - **Fix:** Force refresh, rebuild cache
- **Problem:** Refresh too frequent/rare
  - **Check:** Schedule vs need
  - **Fix:** Adjust schedule based on usage

**Success criteria:** Consistent system state available to all jobs

---

### Job 16: review-progress-3day
**Schedule:** 6:30 AM every 3 days  
**Category:** Operations & Monitoring  
**Purpose:** 3-day progress review  
**What it does:**
1. Analyzes last 3 days of work
2. Identifies trends and patterns
3. Adjusts system priorities if needed
4. Updates TASK-BACKLOG.md priorities

**Output files:**
- ops/journal/YYYY-MM-DD-3day-review.md
- TASK-BACKLOG.md priority updates

**Dependencies:** ops-evening-retrospective (last 3 days)
**Dependent jobs:** None

**Debugging:**
- **Problem:** Insufficient retrospective data
  - **Check:** Last 3 days of retrospectives
  - **Fix:** Use available data, note gaps
- **Problem:** No priority adjustments
  - **Check:** Analysis depth
  - **Fix:** Require specific priority changes
- **Problem:** Backlog not updated
  - **Check:** TASK-BACKLOG.md modification
  - **Fix:** Manual priority update

**Success criteria:** Meaningful trend analysis with priority adjustments

---

### Job 17: daily-internal-backup
**Schedule:** Daily 3:00 AM  
**Category:** Backup & Memory  
**Purpose:** Encrypt and backup internal files  
**What it does:**
1. Compresses key workspace files
2. Encrypts backup
3. Stores to backup location
4. Verifies backup integrity

**Output files:**
- Backup archive (encrypted)
- ops/journal/YYYY-MM-DD-backup.md

**Dependencies:** None
**Dependent jobs:** None

**Debugging:**
- **Problem:** Backup too large
  - **Check:** Archive size
  - **Fix:** Exclude non-essential files
- **Problem:** Encryption fails
  - **Check:** Encryption keys
  - **Fix:** Verify key availability
- **Problem:** Backup verification fails
  - **Check:** Archive integrity
  - **Fix:** Re-run backup, check storage

**Success criteria:** Encrypted backup of essential files with verified integrity

---

### Job 18: daily-memory-consolidation
**Schedule:** Daily 11:00 PM  
**Category:** Backup & Memory  
**Purpose:** Memory consolidation  
**What it does:**
1. Summarizes recent memory entries
2. Ensures MEMORY.md stays under 15k
3. Archives old memory to memory/archive/
4. Maintains memory system health

**Output files:**
- MEMORY.md (consolidated)
- memory/archive/YYYY-MM-DD.md
- ops/journal/YYYY-MM-DD-memory-consolidation.md

**Dependencies:** None
**Dependent jobs:** None (but thinking-consolidate at 9 PM does similar work)

**Debugging:**
- **Problem:** MEMORY.md > 15k
  - **Check:** File size
  - **Fix:** More aggressive summarization
- **Problem:** Duplicate work with thinking-consolidate
  - **Check:** Both jobs active
  - **Fix:** Disable one or separate responsibilities
- **Problem:** Memory loss during consolidation
  - **Check:** Key insights preserved
  - **Fix:** Improve summarization algorithm

**Success criteria:** MEMORY.md under 15k with key insights preserved

---

### Job 19: ops-aggressive-stale-detection
**Schedule:** 10 AM, 2 PM, 6 PM (DISABLED)  
**Category:** Operations & Monitoring  
**Purpose:** Aggressive stale task detection  
**What it does:**
1. 3x daily stale task check
2. Earlier detection of stuck work
3. More frequent alerts
4. Currently disabled due to overlap

**Output files:** (when enabled)
- ops/journal/YYYY-MM-DD-aggressive-stale.md
- ALERT.md (if stale tasks)

**Dependencies:** None
**Dependent jobs:** task-runner

**Debugging:**
- **Problem:** Disabled but needed
  - **Check:** Stale task frequency
  - **Fix:** Enable with adjusted thresholds
- **Problem:** Overlap with ops-check-stale-tasks
  - **Check:** Both jobs active
  - **Fix:** Different responsibilities or disable one
- **Problem:** Too many false alerts
  - **Check:** Alert frequency
  - **Fix:** Adjust detection thresholds

**Success criteria:** (when enabled) Early detection of stale tasks without false alerts

---

### Job 20: Website Deployment Verification
**Schedule:** (PROPOSED — not yet implemented)  
**Category:** Website Operations  
**Purpose:** Verify website deployment succeeded  
**What it does:**
1. Checks GitHub deployment status
2. Verifies live website matches local
3. Alerts if deployment failed
4. Proposed based on job audit gap

**Output files:** (when implemented)
- ops/journal/YYYY-MM-DD-deployment-verify.md
- ALERT.md (if deployment failed)

**Dependencies:** thinking-consolidate (9 PM — does deployment)
**Dependent jobs:** None

**Debugging:** (when implemented)
- **Problem:** Deployment verification fails
  - **Check:** GitHub API, network
  - **Fix:** Manual verification
- **Problem:** Live vs local mismatch
  - **Check:** Content differences
  - **Fix:** Re-deploy, investigate sync issue

**Success criteria:** (when implemented) Confirmation that website deployment succeeded

---

## System-Wide Debugging Guide

### Common Problems & Solutions

#### Problem: Jobs Not Running
**Symptoms:**
- No output files created at scheduled time
- ops/journal/ has gaps
- System appears "stuck"

**Diagnosis:**
1. Check OpenClaw gateway status
2. Verify cron scheduler is active
3. Check individual job logs for errors
4. Look for resource constraints (memory, disk)

**Solutions:**
1. Restart OpenClaw gateway if needed
2. Check cron configuration
3. Review job error logs
4. Free up resources if constrained

#### Problem: Cascade Failures
**Symptoms:**
- One job fails, causing multiple dependent jobs to fail
- Thinking cycle breaks at specific point
- System health degrades progressively

**Diagnosis:**
1. Identify root failure job
2. Check dependency chain (see JOB-DEPENDENCY-MAP.md)
3. Review failure reason in job log
4. Check fallback mechanisms

**Solutions:**
1. Fix root failure job
2. Implement missing fallbacks
3. Add dependency health checks
4. Consider breaking critical chains

#### Problem: Data Corruption
**Symptoms:**
- Key files (MEMORY.md, WORKING.md) corrupted
- Inconsistent state across system
- Jobs fail due to bad input data

**Diagnosis:**
1. Check file modification times
2. Look for concurrent write conflicts
3. Review backup integrity
4. Check for disk errors

**Solutions:**
1. Restore from backup (daily-internal-backup)
2. Implement file locking if concurrent writes
3. Add data validation to jobs
4. Schedule disk checks

#### Problem: Performance Degradation
**Symptoms:**
- Jobs run slower over time
- System feels "sluggish"
- Timeouts increase

**Diagnosis:**
1. Check MEMORY.md size (>15k is problem)
2. Review job output file sizes
3. Check disk space
4. Monitor memory/CPU during runs

**Solutions:**
1. Consolidate MEMORY.md if large
2. Clean up old job logs
3. Free disk space if low
4. Optimize heavy jobs

### Emergency Procedures

#### Immediate System Failure
**When:** Multiple critical jobs fail, system unusable
**Actions:**
1. Check OpenClaw gateway status
2. Review ALERT.md for critical issues
3. Check disk space and memory
4. Restart gateway if needed
5. Run manual health check

#### Data Loss Event
**When:** Key files corrupted or deleted
**Actions:**
1. Restore from latest backup (daily-internal-backup)
2. Verify backup integrity
3. Replay critical jobs if needed
4. Update disaster recovery protocol

#### Website Down
**When:** Public website unavailable
**Actions:**
1. Check GitHub Pages status
2. Verify local website files exist
3. Manual git push if needed
4. Check DNS if persistent

#### Communication Failure
**When:** Cannot send/receive messages
**Actions:**
1. Check Telegram integration
2. Verify network connectivity
3. Fall back to file-based communication
4. Log issues for retrospective

### Monitoring & Alerting

#### What to Monitor
1. **Job execution rate:** % of jobs running on schedule
2. **Error rate:** Consecutive errors per job
3. **Dependency health:** % of dependencies satisfied
4. **System resources:** Disk space, memory
5. **Data integrity:** File corruption detection

#### Alert Thresholds
- **Warning:** Any job >2 consecutive errors
- **Critical:** Critical chain job >3 consecutive errors  
- **Emergency:** System resource <10% free
- **Immediate:** Data corruption detected

#### Alert Actions
1. Create ALERT.md with details
2. Attempt automatic recovery if possible
3. Escalate to Stephen if not resolved in 24h
4. Log for retrospective analysis

---

## Maintenance Schedule

### Daily
- **6 AM - 9 PM:** Thinking cycle jobs (automatic)
- **7 AM:** Website smoke test
- **8 AM:** Website identity update
- **11 AM:** Stale task detection
- **Hourly:** Task runner execution
- **8:30 AM/PM:** Progress reports
- **9 PM:** Consolidation
- **10 PM:** Retrospective
- **11 PM:** Memory consolidation

### Weekly
- **Monday 9 AM:** Content calendar update
- **Tuesday 11 AM:** Identity reflection
- **Wednesday 2 PM:** Substack research
- **Thursday 3 PM:** Recovery protocol test
- **Friday 11 AM:** Draft audit
- **Saturday 2 PM:** Archive maintenance
- **Sunday 4 PM:** Substack content

### Periodic
- **Every 3 days 6:30 AM:** Progress review
- **Every 2 weeks:** Substack research
- **Every 2 weeks:** Creative research
- **Monthly:** System architecture review

---

## Glossary

**Job:** Scheduled task with specific purpose and outputs
**Dependency:** Relationship where Job B requires Job A's output
**Critical Chain:** Sequence of jobs where failure cascades
**Fallback:** Alternative action when dependency fails
**Consolidation:** Summarizing and preserving key information
**Retrospective:** Analysis of what worked/failed in a period
**Stale Task:** Backlog task with no progress >72 hours
**Health Dashboard:** At-a-glance system status view
**Runbook:** This document — operational guide for humans

---

## Version History
- **v1.0 (2026-03-07):** Initial runbook created by task-runner executing B08
- **Next review:** 2026-03-14 (weekly maintenance)

## Contact
For system issues:
1. Check this runbook first
2. Review ALERT.md for active issues
3. Check HEALTH-DASHBOARD.md for status
4. If unresolved, manual intervention may be needed

**Remember:** This system is designed for autonomy but requires human oversight for major issues. The goal is not perfection, but continuous improvement with clear failure modes and recovery paths.

