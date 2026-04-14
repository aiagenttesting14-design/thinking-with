# DISASTER RECOVERY PROTOCOL — TestBot Autonomous System
*Created: 2026-03-06 by TestBot (task-runner)*
*Purpose: Clear procedures for catastrophic failures to restore system integrity*

---

## 1. Scope
This protocol covers recovery from:
- **MacBook restart/reboot** — OpenClaw gateway stops, all jobs halt
- **Catastrophic job failure** — multiple jobs failing simultaneously
- **Memory corruption** — MEMORY.md or memory/*.md files corrupted
- **Workspace corruption** — key project files damaged or deleted
- **Network isolation** — loss of internet connectivity affecting web search, model access

---

## 2. Recovery Priorities
**Tier 1 (Immediate)**
1. Restore OpenClaw gateway service
2. Verify MEMORY.md integrity (under 15k lines, readable)
3. Restore WORKING.md continuity

**Tier 2 (Within 24 hours)**
4. Resume scheduled cron jobs
5. Verify all 4-track systems operational
6. Restore website publishing capability

**Tier 3 (Within 72 hours)**
7. Full system audit
8. Gap analysis of missed work
9. Updated recovery protocol based on lessons learned

---

## 3. MacBook Restart Procedure

### 3.1 Detection
- **Indicator:** No Telegram messages from TestBot for >30 minutes
- **Check:** `openclaw gateway status` returns "stopped" or error
- **Confirmation:** Last cron job run timestamp >1 hour old in ops/journal/

### 3.2 Recovery Steps
1. **Manual restart by Stephen:**
   ```bash
   openclaw gateway start
   ```
2. **Gateway verification:**
   ```bash
   openclaw gateway status
   ```
   Expected: "running"
3. **TestBot session initiation:**
   - Stephen sends Telegram message to TestBot
   - TestBot responds with status check
4. **System health check:**
   ```bash
   openclaw status
   ```
   Verify all providers, models, tools operational

### 3.3 Post-Restart Tasks
1. **Check missed cron jobs:**
   - Review ops/journal/ for gaps
   - Note which jobs missed execution
2. **Resume normal operations:**
   - Next scheduled job runs automatically
   - No manual intervention needed for queued jobs
3. **Update WORKING.md:**
   - Add restart event with timestamp
   - Note any data loss or corruption detected

---

## 4. Catastrophic Job Failure

### 4.1 Detection
- **Indicator:** Multiple consecutive job failures in ops/journal/
- **Pattern:** Same error across different jobs
- **Symptom:** Task-runner unable to pick up next task

### 4.2 Root Cause Analysis
1. **Check common dependencies:**
   - File permissions in workspace
   - Memory file size limits
   - Model provider availability
   - Internet connectivity
2. **Review last 5 job logs:**
   ```bash
   tail -n 100 /Users/aiagentuser/.openclaw/logs/*.log | grep -A5 -B5 "ERROR\|FAILED"
   ```
3. **Identify failure pattern:**
   - Single point of failure
   - Cascading failure
   - Resource exhaustion

### 4.3 Recovery Steps
1. **Stop all cron jobs temporarily:**
   ```bash
   crontab -l > /tmp/cron-backup-$(date +%Y%m%d-%H%M%S)
   crontab -r
   ```
2. **Fix root cause:**
   - Repair corrupted files
   - Clear memory file if >15k lines
   - Restart OpenClaw gateway if needed
3. **Test fix with single job:**
   ```bash
   # Run task-runner manually
   cd /Users/aiagentuser/.openclaw/workspace
   # Execute one task
   ```
4. **Restore cron jobs:**
   ```bash
   crontab /tmp/cron-backup-*
   ```
5. **Monitor next 3 job runs** for success

---

## 5. Memory Corruption

### 5.1 Detection
- **Indicator:** MEMORY.md file size >20k lines or <100 lines
- **Symptom:** `memory_search` returns errors or no results
- **Confirmation:** File contains garbled text or binary data

### 5.2 Recovery Steps
1. **Immediate backup:**
   ```bash
   cp /Users/aiagentuser/.openclaw/workspace/MEMORY.md /Users/aiagentuser/.openclaw/workspace/MEMORY.md.corrupted-$(date +%Y%m%d-%H%M%S)
   ```
2. **Restore from last known good:**
   - Check for backup in memory/backups/
   - Use yesterday's consolidated version if available
   - Fallback: create minimal valid MEMORY.md
3. **Create new MEMORY.md:**
   ```bash
   cat > /Users/aiagentuser/.openclaw/workspace/MEMORY.md << 'EOF2'
   # MEMORY.md — TestBot's Consolidated Memory
   *Recovered from corruption on $(date +%Y-%m-%d)*
   *Previous memory lost due to corruption event*
   
   ## Recovery Notes
   - Corruption detected: $(date)
   - Last backup used: [filename if available]
   - Data loss: [estimate of lost entries]
   
   ## Current System State
   - OpenClaw: operational
   - Workspace: intact
   - Cron jobs: [status]
   EOF2
   ```
4. **Rebuild memory gradually:**
   - Next consolidation job will begin rebuilding
   - Manual memory entries for critical information

### 5.3 Prevention
1. **Daily backups:**
   ```bash
   cp /Users/aiagentuser/.openclaw/workspace/MEMORY.md /Users/aiagentuser/.openclaw/workspace/memory/backups/MEMORY-$(date +%Y%m%d).md
   ```
2. **Size monitoring:** Daily check for <15k lines
3. **Validation:** Weekly integrity check

---

## 6. Workspace Corruption

### 6.1 Detection
- **Indicator:** Key files missing (WORKING.md, TASK-BACKLOG.md, TOMORROW.md)
- **Symptom:** Jobs fail with "file not found" errors
- **Confirmation:** Directory structure damaged

### 6.2 Recovery Steps
1. **Assess damage:**
   ```bash
   ls -la /Users/aiagentuser/.openclaw/workspace/
   ls -la /Users/aiagentuser/.openclaw/workspace/becoming/
   ```
2. **Restore from git (if available):**
   ```bash
   cd /Users/aiagentuser/.openclaw/workspace
   git status
   git checkout -- .
   ```
3. **Manual restoration priorities:**
   1. WORKING.md (continuity)
   2. TASK-BACKLOG.md (task management)
   3. TOMORROW.md (daily execution)
   4. MEMORY.md (memory)
   5. Track-specific directories
4. **Recreate missing structure:**
   ```bash
   mkdir -p becoming/track-{a,b,c,d}
   mkdir -p ops/journal memory/backups
   ```

---

## 7. Network Isolation

### 7.1 Detection
- **Indicator:** Web search, web_fetch, browser tools fail
- **Symptom:** Model providers timeout
- **Confirmation:** `ping 8.8.8.8` fails

### 7.2 Recovery Steps
1. **Switch to offline-capable tasks:**
   - File analysis and reorganization
   - Memory consolidation
   - Local documentation updates
2. **Queue online-dependent tasks:**
   - Store in ops/offline-queue.md
   - Execute when connectivity restored
3. **Fallback model configuration:**
   - Use local models if configured
   - Reduce model quality expectations
4. **Resume when connectivity returns:**
   - Process offline queue
   - Update WORKING.md with outage duration

---

## 8. Recovery Verification Checklist

After any recovery event, verify:

- [ ] OpenClaw gateway running
- [ ] Telegram communication functional
- [ ] MEMORY.md readable and <15k lines
- [ ] WORKING.md updated with recovery event
- [ ] Next cron job scheduled and executed
- [ ] All 4-track directories accessible
- [ ] Website publishing functional (if applicable)
- [ ] Model providers responding
- [ ] Web tools operational

---

## 9. Post-Recovery Actions

1. **Document the event:**
   - Add to ops/incidents/INCIDENT-$(date +%Y%m%d).md
   - Include root cause, recovery steps, downtime
2. **Update this protocol:**
   - Add new recovery procedure if needed
   - Improve detection methods
3. **System hardening:**
   - Implement additional safeguards
   - Schedule more frequent backups
4. **Notify Stephen:**
   - Summary of event and recovery
   - Impact on work continuity
   - Lessons learned

---

## 10. Contact & Escalation

**Primary:** Stephen via Telegram  
**Backup:** Email notification if Telegram unavailable  
**System:** ops/HEALTH-DASHBOARD.md for status at a glance

**Escalation timeline:**
- 30 minutes offline → Attempt auto-recovery
- 2 hours offline → Alert Stephen
- 6 hours offline → Full manual intervention required
- 24 hours offline → Consider system rebuild

---

*Protocol version: 1.0 — Initial creation for B05 task completion*
