#!/bin/bash
# Practice Integrity Check — Prevent missing practice files
# Run by morning-wake agent before starting new work

TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)
PRACTICE_DIR="/Users/aiagentuser/.openclaw/workspace/becoming/track-c/practice"

# Check if yesterday's practice exists
if [ ! -f "$PRACTICE_DIR/$YESTERDAY.md" ]; then
    echo "⚠️  MISSING: Practice file for $YESTERDAY"
    echo "ACTION REQUIRED: Complete missed practice before starting new work"
    exit 1
fi

# Check if today's practice exists
if [ -f "$PRACTICE_DIR/$TODAY.md" ]; then
    echo "✅ Practice integrity check passed"
    exit 0
else
    echo "ℹ️  Today's practice not yet created (expected — will be created by thinking-practice job)"
    exit 0
fi
