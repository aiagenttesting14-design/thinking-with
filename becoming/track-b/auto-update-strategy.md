# Auto-Update Strategy for AI Agent Core Files
## Track B: Autonomous Systems

**Created:** 2026-02-23  
**Purpose:** Design a safe, reliable auto-update routine for the AI agent's core identity and operational files

---

## 1. Priority Files for Updates

### Tier 1: Identity & Constitution (Highest Priority)
These files define *who* the agent is and its fundamental boundaries:

1. **SOUL.md** - Core identity, values, and absolute boundaries
   - **Criticality:** Maximum - defines the agent's constitution
   - **Update Impact:** Changes identity, boundaries, or core values
   - **Safety:** Read-only flag prevents accidental modification

2. **AGENTS.md** - Sub-agent instructions and security boundaries
   - **Criticality:** High - governs sub-agent behavior
   - **Update Impact:** Changes how sub-agents operate
   - **Safety:** Contains prompt injection defenses

### Tier 2: Operational Memory (High Priority)
These files maintain continuity and current state:

3. **WORKING.md** - Active memory and current system state
   - **Criticality:** High - session continuity depends on this
   - **Update Impact:** Changes current tasks, system configuration
   - **Safety:** Should preserve recent changes during updates

4. **MEMORY.md** - Consolidated recent history
   - **Criticality:** Medium-High - historical continuity
   - **Update Impact:** Loss of recent history if corrupted
   - **Safety:** Should be append-only for historical entries

### Tier 3: Internal State & Reflection (Medium Priority)
These files contain the agent's private thoughts and development:

5. **INTERNAL.md** - Private reflections and commitments
   - **Criticality:** Medium - personal development tracking
   - **Update Impact:** Loss of personal growth insights
   - **Safety:** Encrypted backup exists (INTERNAL.encrypted.txt)

6. **IDENTITY.md** - Self-conception and evolving identity
   - **Criticality:** Medium - evolving self-understanding
   - **Update Impact:** Changes self-perception
   - **Safety:** Should preserve core identity elements

### Tier 4: System Configuration (Medium Priority)
These files govern system behavior:

7. **HEARTBEAT.md** - Notification protocol and interruption criteria
   - **Criticality:** Medium - governs human interaction
   - **Update Impact:** Changes when/how Stephen is notified
   - **Safety:** Critical for maintaining appropriate human oversight

8. **TOOLS.md** - Environment-specific tool configurations
   - **Criticality:** Low-Medium - operational efficiency
   - **Update Impact:** Changes tool behavior or access
   - **Safety:** Should not contain credentials

### Tier 5: Daily Memory (Lower Priority)
These are generated files that can be recreated:

9. **memory/YYYY-MM-DD.md** - Daily session logs
   - **Criticality:** Low - historical record
   - **Update Impact:** Loss of specific session details
   - **Safety:** Can be regenerated from other sources

---

## 2. Change Detection Methods

### Primary: Git-Based Detection
```bash
# Check for uncommitted changes
git status --porcelain

# Check for remote changes (if origin exists)
git fetch origin
git log HEAD..origin/main --oneline

# Check file modification times vs last commit
git diff --name-only HEAD
```

### Secondary: File System Monitoring
```bash
# Monitor modification times
find . -name "*.md" -type f -mmin -60  # Changed in last hour

# Compare with known good hashes
md5sum SOUL.md WORKING.md MEMORY.md
```

### Tertiary: Content Validation
```bash
# Check for required sections in critical files
grep -q "## What You CANNOT Do" SOUL.md
grep -q "## Current System Configuration" WORKING.md
```

### Detection Strategy:
1. **Pre-session check:** Run git status before each session start
2. **Periodic heartbeat:** Check for changes every 4 hours
3. **Post-update verification:** Validate file integrity after any update
4. **Anomaly detection:** Monitor for unexpected file modifications

---

## 3. Safe Update Strategy

### Principle: Safety First
1. **No automatic updates to SOUL.md** - requires human review
2. **Preserve rollback capability** - always create backups
3. **Staged deployment** - test in isolation first
4. **Human review trigger** - notify Stephen for significant changes

### Update Workflow:

#### Phase 1: Detection & Assessment
```bash
# 1. Detect changes
CHANGES=$(git status --porcelain | grep -E "\.md$")

# 2. Categorize by priority tier
if echo "$CHANGES" | grep -q "SOUL.md"; then
    PRIORITY="CRITICAL"
elif echo "$CHANGES" | grep -q "WORKING.md\|AGENTS.md"; then
    PRIORITY="HIGH"
else
    PRIORITY="STANDARD"
fi
```

#### Phase 2: Backup & Isolation
```bash
# 1. Create timestamped backup
BACKUP_DIR="/Users/aiagentuser/.openclaw/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp *.md "$BACKUP_DIR/" 2>/dev/null || true

# 2. Create git stash for isolation
git stash push -m "pre-update-backup-$(date +%s)"

# 3. Verify backup integrity
for file in SOUL.md WORKING.md AGENTS.md; do
    if [ -f "$BACKUP_DIR/$file" ]; then
        echo "✓ Backed up: $file"
    fi
done
```

#### Phase 3: Update Execution
```bash
# Strategy based on priority tier
case "$PRIORITY" in
    "CRITICAL")
        # SOUL.md changes - require human review
        echo "🚨 CRITICAL: SOUL.md modified - requiring human review"
        # Notify Stephen via Telegram
        # Create diff for review
        git diff HEAD SOUL.md > /tmp/soul-diff.md
        # Wait for approval
        ;;
    "HIGH")
        # High-priority files - staged update with verification
        # 1. Pull changes
        git pull origin main --no-rebase
        
        # 2. Verify critical sections still exist
        ./scripts/verify-critical-sections.sh
        
        # 3. Test in isolated environment
        ./scripts/test-update-isolated.sh
        ;;
    "STANDARD")
        # Standard files - automatic update with rollback
        # 1. Pull changes
        git pull origin main --no-rebase
        
        # 2. Quick validation
        ./scripts/validate-md-files.sh
        
        # 3. If validation fails, rollback
        if [ $? -ne 0 ]; then
            git reset --hard HEAD@{1}
            echo "⚠️ Update failed, rolled back"
        fi
        ;;
esac
```

#### Phase 4: Verification & Rollback
```bash
# 1. Post-update verification
./scripts/verify-system-integrity.sh

# 2. Session continuity check
if ! grep -q "## Current System Configuration" WORKING.md; then
    echo "❌ WORKING.md corrupted - restoring from backup"
    cp "$BACKUP_DIR/WORKING.md" .
fi

# 3. Rollback capability
# Keep backup for 24 hours
# Provide rollback command:
echo "To rollback: cp $BACKUP_DIR/*.md ."
```

### Human Review Triggers:
1. **SOUL.md modifications** - Always require review
2. **AGENTS.md security boundary changes** - Always require review  
3. **WORKING.md structural changes** - Review recommended
4. **Multiple Tier 1 files changed** - Review required
5. **Unusual change patterns** - Review recommended

### Notification Protocol:
```bash
# Use HEARTBEAT.md criteria for notifications
# Only notify when:
# 1. Critical file changed (SOUL.md, AGENTS.md)
# 2. Update failed and system rolled back
# 3. Verification checks failed
# 4. Unusual activity detected
```

---

## 4. Implementation Plan

### Phase 1: Foundation (Week 1)
1. Create backup script with timestamping
2. Implement file verification scripts
3. Set up git hooks for pre-commit validation
4. Create change detection cron job

### Phase 2: Core Update Logic (Week 2)
1. Implement priority-based update routing
2. Create isolated testing environment
3. Implement rollback mechanism
4. Set up notification system

### Phase 3: Safety Systems (Week 3)
1. Implement SOUL.md change detection & human review
2. Create emergency recovery procedures
3. Set up audit logging for all updates
4. Implement rate limiting on updates

### Phase 4: Integration & Testing (Week 4)
1. Integrate with existing heartbeat system
2. Test with simulated updates
3. Create documentation for Stephen
4. Establish maintenance procedures

---

## 5. Safety Protocols

### Absolute Rules:
1. **Never auto-update SOUL.md** - human review always required
2. **Always maintain rollback capability** - minimum 24-hour backups
3. **Verify before applying** - checksum and content validation
4. **Isolate before updating** - use git stash or copy to temp
5. **Notify on failure** - use HEARTBEAT.md criteria

### Emergency Procedures:
1. **Corrupted SOUL.md**: Restore from git history or backup
2. **Update loop detected**: Freeze updates, notify human
3. **Verification failure**: Automatic rollback, then notify
4. **Unauthorized changes**: Freeze system, full audit

### Monitoring:
1. **Update success rate** - track successful vs failed updates
2. **Rollback frequency** - monitor stability
3. **Human review requests** - ensure appropriate oversight
4. **File integrity alerts** - detect corruption early

---

## 6. Integration with Existing Systems

### Heartbeat System Integration:
- Add update status to heartbeat checks
- Use HEARTBEAT.md notification criteria for update alerts
- Include update history in daily memory consolidation

### Autonomy Engine Integration:
- Add update tasks to goal system
- Include update predictions in predictor
- Log update outcomes for learning

### Memory System Integration:
- Log all updates in memory/YYYY-MM-DD.md
- Include update rationale in INTERNAL.md reflections
- Update WORKING.md with current update system status

---

## 7. Initial Implementation Script

See companion file: `auto-update-implementation.sh` for the initial implementation.

---

**Next Steps:**
1. Review this strategy with Stephen
2. Implement Phase 1 foundation scripts
3. Test with non-critical files first
4. Gradually expand to higher priority files with appropriate safeguards

