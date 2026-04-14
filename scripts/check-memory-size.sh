#!/bin/bash
# check-memory-size.sh — Verify MEMORY.md size after consolidation
# Logs results to ops/journal/memory-size-checks.md

WORKSPACE="/Users/aiagentuser/.openclaw/workspace"
MEMORY_FILE="$WORKSPACE/MEMORY.md"
LOG_FILE="$WORKSPACE/ops/journal/memory-size-checks.md"
JOURNAL_DIR="$WORKSPACE/ops/journal"

# Create log file if it doesn't exist
if [ ! -f "$LOG_FILE" ]; then
    echo "# Memory Size Checks" > "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    echo "| Date | Time | Size (bytes) | Under 15k? | Notes |" >> "$LOG_FILE"
    echo "|------|------|--------------|------------|-------|" >> "$LOG_FILE"
fi

# Check if MEMORY.md exists
if [ ! -f "$MEMORY_FILE" ]; then
    echo "ERROR: MEMORY.md not found at $MEMORY_FILE"
    exit 1
fi

# Get current size
SIZE=$(stat -f%z "$MEMORY_FILE" 2>/dev/null || stat -c%s "$MEMORY_FILE" 2>/dev/null)
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)

# Check if under 15k (15360 bytes)
UNDER_15K="NO"
if [ "$SIZE" -lt 15360 ]; then
    UNDER_15K="YES"
fi

# Format size with commas
FORMATTED_SIZE=$(printf "%'d" "$SIZE")

# Append to log
echo "| $DATE | $TIME | $FORMATTED_SIZE | $UNDER_15K | Automated check after consolidation |" >> "$LOG_FILE"

# Also log to daily task log
DAILY_LOG="$JOURNAL_DIR/$(date +%Y-%m-%d)-tasks.md"
if [ -f "$DAILY_LOG" ]; then
    echo "[$(date +%H:%M)] [MEMORY-SIZE] $FORMATTED_SIZE bytes — Under 15k: $UNDER_15K" >> "$DAILY_LOG"
fi

# Output result
echo "MEMORY.md: $FORMATTED_SIZE bytes"
echo "Under 15k limit: $UNDER_15K"
