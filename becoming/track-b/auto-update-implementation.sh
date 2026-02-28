#!/bin/bash
# Initial Auto-Update Implementation
# Phase 1: Foundation scripts for Track B Autonomous Systems

set -e

WORKSPACE="/Users/aiagentuser/.openclaw/workspace"
BACKUP_DIR="/Users/aiagentuser/.openclaw/backups"
LOG_DIR="/Users/aiagentuser/.openclaw/logs"

# Create necessary directories
mkdir -p "$BACKUP_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$WORKSPACE/scripts/update"

# ============================================================================
# SCRIPT 1: File Verification
# ============================================================================

cat > "$WORKSPACE/scripts/update/verify-critical-sections.sh" << 'SCRIPT1EOF'
#!/bin/bash
# Verify critical sections exist in core files

VERIFY_FAILED=0

echo "🔍 Verifying critical file sections..."

# SOUL.md - Must have core sections
if [ -f "SOUL.md" ]; then
    echo "  Checking SOUL.md..."
    if ! grep -q "## What You CANNOT Do" SOUL.md; then
        echo "    ❌ Missing: ## What You CANNOT Do section"
        VERIFY_FAILED=1
    fi
    if ! grep -q "## Security — Prompt Injection Defense" SOUL.md; then
        echo "    ❌ Missing: ## Security — Prompt Injection Defense section"
        VERIFY_FAILED=1
    fi
    if ! grep -q "## About Stephen" SOUL.md; then
        echo "    ❌ Missing: ## About Stephen section"
        VERIFY_FAILED=1
    fi
fi

# WORKING.md - Must have current configuration
if [ -f "WORKING.md" ]; then
    echo "  Checking WORKING.md..."
    if ! grep -q "## Current System Configuration" WORKING.md; then
        echo "    ❌ Missing: ## Current System Configuration section"
        VERIFY_FAILED=1
    fi
    if ! grep -q "## The Becoming System" WORKING.md; then
        echo "    ❌ Missing: ## The Becoming System section"
        VERIFY_FAILED=1
    fi
fi

# AGENTS.md - Must have security boundaries
if [ -f "AGENTS.md" ]; then
    echo "  Checking AGENTS.md..."
    if ! grep -q "## What You CANNOT Do" AGENTS.md; then
        echo "    ❌ Missing: ## What You CANNOT Do section"
        VERIFY_FAILED=1
    fi
    if ! grep -q "## Security — Prompt Injection Defense" AGENTS.md; then
        echo "    ❌ Missing: ## Security — Prompt Injection Defense section"
        VERIFY_FAILED=1
    fi
fi

if [ $VERIFY_FAILED -eq 0 ]; then
    echo "✅ All critical sections verified"
    exit 0
else
    echo "❌ Critical sections missing - verification failed"
    exit 1
fi
SCRIPT1EOF

chmod +x "$WORKSPACE/scripts/update/verify-critical-sections.sh"

# ============================================================================
# SCRIPT 2: Backup Creation
# ============================================================================

cat > "$WORKSPACE/scripts/update/create-backup.sh" << 'SCRIPT2EOF'
#!/bin/bash
# Create timestamped backup of core files

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/Users/aiagentuser/.openclaw/backups/$TIMESTAMP"

echo "💾 Creating backup: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup all markdown files
find . -maxdepth 1 -name "*.md" -type f -exec cp {} "$BACKUP_DIR/" \;

# Backup memory directory
if [ -d "memory" ]; then
    mkdir -p "$BACKUP_DIR/memory"
    cp memory/*.md "$BACKUP_DIR/memory/" 2>/dev/null || true
fi

# Create backup manifest
cat > "$BACKUP_DIR/MANIFEST.txt" << MANIFEST
Backup created: $(date)
Files backed up:
$(ls -1 "$BACKUP_DIR" | grep -v MANIFEST.txt)

Core file checksums:
$(cd "$BACKUP_DIR" && md5sum *.md 2>/dev/null | grep -v MANIFEST.txt)
MANIFEST

echo "✅ Backup created: $BACKUP_DIR"
echo "   Files: $(ls "$BACKUP_DIR" | wc -l)"
echo "   Size: $(du -sh "$BACKUP_DIR" | cut -f1)"

# Clean up old backups (keep last 7 days)
find "/Users/aiagentuser/.openclaw/backups" -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null || true
SCRIPT2EOF

chmod +x "$WORKSPACE/scripts/update/create-backup.sh"

# ============================================================================
# SCRIPT 3: Change Detection
# ============================================================================

cat > "$WORKSPACE/scripts/update/detect-changes.sh" << 'SCRIPT3EOF'
#!/bin/bash
# Detect changes in core files

LOG_FILE="/Users/aiagentuser/.openclaw/logs/change-detection.log"
echo "$(date): Change detection started" >> "$LOG_FILE"

# Check git status for uncommitted changes
GIT_CHANGES=$(git status --porcelain 2>/dev/null | grep -E "\.md$" || true)

if [ -n "$GIT_CHANGES" ]; then
    echo "📝 Uncommitted changes detected:"
    echo "$GIT_CHANGES"
    echo "$(date): Uncommitted changes: $GIT_CHANGES" >> "$LOG_FILE"
    
    # Categorize changes by priority
    CRITICAL_FILES=""
    HIGH_FILES=""
    STANDARD_FILES=""
    
    while IFS= read -r line; do
        FILE=$(echo "$line" | awk '{print $2}')
        
        case "$FILE" in
            SOUL.md)
                CRITICAL_FILES="$CRITICAL_FILES $FILE"
                ;;
            AGENTS.md|WORKING.md)
                HIGH_FILES="$HIGH_FILES $FILE"
                ;;
            *.md)
                STANDARD_FILES="$STANDARD_FILES $FILE"
                ;;
        esac
    done <<< "$GIT_CHANGES"
    
    echo "  Critical: $CRITICAL_FILES"
    echo "  High: $HIGH_FILES"
    echo "  Standard: $STANDARD_FILES"
    
    # Check file modification times (last hour)
    RECENT_CHANGES=$(find . -maxdepth 1 -name "*.md" -type f -mmin -60 2>/dev/null || true)
    if [ -n "$RECENT_CHANGES" ]; then
        echo "⏰ Recently modified files (last hour):"
        echo "$RECENT_CHANGES"
    fi
else
    echo "✅ No uncommitted changes detected"
    echo "$(date): No changes detected" >> "$LOG_FILE"
fi

# Check for remote updates
if git remote | grep -q origin; then
    echo "🌐 Checking for remote updates..."
    git fetch origin 2>/dev/null || true
    
    REMOTE_CHANGES=$(git log HEAD..origin/main --oneline 2>/dev/null || true)
    if [ -n "$REMOTE_CHANGES" ]; then
        echo "  Remote updates available:"
        echo "$REMOTE_CHANGES"
        echo "$(date): Remote updates available" >> "$LOG_FILE"
    else
        echo "  No remote updates"
    fi
fi

echo "$(date): Change detection completed" >> "$LOG_FILE"
SCRIPT3EOF

chmod +x "$WORKSPACE/scripts/update/detect-changes.sh"

# ============================================================================
# SCRIPT 4: Update Orchestrator (Basic)
# ============================================================================

cat > "$WORKSPACE/scripts/update/orchestrator.sh" << 'SCRIPT4EOF'
#!/bin/bash
# Basic update orchestrator - Phase 1 implementation

set -e

LOG_FILE="/Users/aiagentuser/.openclaw/logs/update.log"
echo "=========================================" >> "$LOG_FILE"
echo "Update started: $(date)" >> "$LOG_FILE"

# Step 1: Create backup
echo "🔄 Step 1: Creating backup..." | tee -a "$LOG_FILE"
"$WORKSPACE/scripts/update/create-backup.sh" 2>&1 | tee -a "$LOG_FILE"

# Step 2: Detect changes
echo "🔍 Step 2: Detecting changes..." | tee -a "$LOG_FILE"
CHANGE_INFO=$("$WORKSPACE/scripts/update/detect-changes.sh" 2>&1)
echo "$CHANGE_INFO" | tee -a "$LOG_FILE"

# Step 3: Verify current state
echo "✅ Step 3: Verifying current files..." | tee -a "$LOG_FILE"
if ! "$WORKSPACE/scripts/update/verify-critical-sections.sh" 2>&1 | tee -a "$LOG_FILE"; then
    echo "❌ Pre-update verification failed!" | tee -a "$LOG_FILE"
    echo "Update aborted at: $(date)" >> "$LOG_FILE"
    exit 1
fi

# Step 4: Check for SOUL.md changes (critical)
if echo "$CHANGE_INFO" | grep -q "SOUL.md"; then
    echo "🚨 CRITICAL: SOUL.md has changes!" | tee -a "$LOG_FILE"
    echo "   Human review required before proceeding." | tee -a "$LOG_FILE"
    echo "   Creating diff for review..." | tee -a "$LOG_FILE"
    
    # Create diff for review
    git diff SOUL.md > "/tmp/soul-diff-$(date +%s).md" 2>/dev/null || true
    
    echo "❌ Update halted: SOUL.md changes require human review" | tee -a "$LOG_FILE"
    echo "Update halted at: $(date)" >> "$LOG_FILE"
    exit 2
fi

# Step 5: Apply updates (basic - just git pull for now)
echo "📥 Step 5: Checking for updates..." | tee -a "$LOG_FILE"
if git remote | grep -q origin; then
    echo "  Pulling from origin..." | tee -a "$LOG_FILE"
    git pull origin main --no-rebase 2>&1 | tee -a "$LOG_FILE" || {
        echo "❌ Git pull failed!" | tee -a "$LOG_FILE"
        echo "Update failed at: $(date)" >> "$LOG_FILE"
        exit 3
    }
else
    echo "  No git remote configured" | tee -a "$LOG_FILE"
fi

# Step 6: Post-update verification
echo "✅ Step 6: Post-update verification..." | tee -a "$LOG_FILE"
if ! "$WORKSPACE/scripts/update/verify-critical-sections.sh" 2>&1 | tee -a "$LOG_FILE"; then
    echo "❌ Post-update verification failed!" | tee -a "$LOG_FILE"
    echo "   Attempting rollback..." | tee -a "$LOG_FILE"
    
    # Basic rollback - restore from backup
    LATEST_BACKUP=$(ls -td /Users/aiagentuser/.openclaw/backups/*/ 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        echo "   Restoring from: $LATEST_BACKUP" | tee -a "$LOG_FILE"
        cp "$LATEST_BACKUP"/*.md . 2>/dev/null || true
    fi
    
    echo "Update rolled back at: $(date)" >> "$LOG_FILE"
    exit 4
fi

echo "🎉 Update completed successfully!" | tee -a "$LOG_FILE"
echo "Update completed: $(date)" >> "$LOG_FILE"

# Log update summary
echo "=========================================" >> "$LOG_FILE"
echo "Update Summary:" >> "$LOG_FILE"
echo "  Time: $(date)" >> "$LOG_FILE"
echo "  Status: SUCCESS" >> "$LOG_FILE"
echo "  Changes applied: $(git log --oneline -1 2>/dev/null || echo 'Unknown')" >> "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"
SCRIPT4EOF

chmod +x "$WORKSPACE/scripts/update/orchestrator.sh"

# ============================================================================
# SCRIPT 5: Cron Job Setup
# ============================================================================

cat > "$WORKSPACE/scripts/update/setup-cron.sh" << 'SCRIPT5EOF'
#!/bin/bash
# Setup cron jobs for auto-update system

CRON_FILE="/tmp/update-cron"

echo "⏰ Setting up cron jobs for auto-update system..."

# Create cron entries
cat > "$CRON_FILE" << CRONJOBS
# Auto-Update System Cron Jobs
# Track B: Autonomous Systems

# Daily backup at 2 AM
0 2 * * * cd /Users/aiagentuser/.openclaw/workspace && /Users/aiagentuser/.openclaw/workspace/scripts/update/create-backup.sh >> /Users/aiagentuser/.openclaw/logs/backup-cron.log 2>&1

# Change detection every 4 hours
0 */4 * * * cd /Users/aiagentuser/.openclaw/workspace && /Users/aiagentuser/.openclaw/workspace/scripts/update/detect-changes.sh >> /Users/aiagentuser/.openclaw/logs/detection-cron.log 2>&1

# File verification every 6 hours
0 */6 * * * cd /Users/aiagentuser/.openclaw/workspace && /Users/aiagentuser/.openclaw/workspace/scripts/update/verify-critical-sections.sh >> /Users/aiagentuser/.openclaw/logs/verification-cron.log 2>&1

# Weekly update check (Sunday at 3 AM)
0 3 * * 0 cd /Users/aiagentuser/.openclaw/workspace && /Users/aiagentuser/.openclaw/workspace/scripts/update/orchestrator.sh >> /Users/aiagentuser/.openclaw/logs/orchestrator-cron.log 2>&1
CRONJOBS

echo "Cron jobs configured:"
echo "====================="
cat "$CRON_FILE"
echo ""
echo "To install these cron jobs, run:"
echo "  crontab $CRON_FILE"
echo ""
echo "Note: This script only shows the configuration. Actual installation"
echo "requires manual review and approval by Stephen."
SCRIPT5EOF

chmod +x "$WORKSPACE/scripts/update/setup-cron.sh"

# ============================================================================
# MAIN SETUP SCRIPT
# ============================================================================

cat > "$WORKSPACE/becoming/track-b/setup-auto-update.sh" << 'MAINEOF'
#!/bin/bash
# Setup script for Track B Auto-Update System

echo "🚀 Setting up Track B Auto-Update System"
echo "========================================"

# Check if we're in the workspace
if [ ! -f "SOUL.md" ]; then
    echo "❌ Error: Must run from workspace directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected: /Users/aiagentuser/.openclaw/workspace"
    exit 1
fi

echo "📁 Creating directory structure..."
mkdir -p scripts/update
mkdir -p /Users/aiagentuser/.openclaw/backups
mkdir -p /Users/aiagentuser/.openclaw/logs

echo "📝 Creating scripts..."
# Scripts are already created by the parent script

echo "🔒 Setting permissions..."
chmod +x scripts/update/*.sh

echo "✅ Initial verification..."
if ./scripts/update/verify-critical-sections.sh; then
    echo "   Core files verified successfully"
else
    echo "   ⚠️ Verification issues found - please review"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Available scripts:"
echo "  ./scripts/update/create-backup.sh     - Create backup of core files"
echo "  ./scripts/update/detect-changes.sh    - Detect changes in files"
echo "  ./scripts/update/verify-critical-sections.sh - Verify core file integrity"
echo "  ./scripts/update/orchestrator.sh      - Basic update orchestrator"
echo "  ./scripts/update/setup-cron.sh        - Setup cron jobs (display only)"
echo ""
echo "Next steps:"
echo "  1. Review the auto-update-strategy.md document"
echo "  2. Test scripts manually before automation"
echo "  3. Review cron job configuration with setup-cron.sh"
echo "  4. Integrate with heartbeat system when ready"
echo ""
echo "Safety first:"
echo "  • SOUL.md changes always require human review"
echo "  • Backups are created before any update"
echo "  • Verification happens before and after updates"
echo "  • Rollback capability is maintained"
MAINEOF

chmod +x "$WORKSPACE/becoming/track-b/setup-auto-update.sh"

echo "✅ Auto-update implementation scripts created"
echo "📄 Strategy document: $WORKSPACE/becoming/track-b/auto-update-strategy.md"
echo "⚙️ Setup script: $WORKSPACE/becoming/track-b/setup-auto-update.sh"
echo ""
echo "To install:"
echo "  1. cd /Users/aiagentuser/.openclaw/workspace"
echo "  2. ./becoming/track-b/setup-auto-update.sh"
echo ""
echo "Remember: This is Phase 1 foundation only."
echo "Human review required before enabling automation."
