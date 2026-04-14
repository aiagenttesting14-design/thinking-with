#!/bin/bash
# notify-website-update.sh
# 
# Sends a Telegram notification to Stephen about a website update.
# ONLY call this when meaningful content was actually published.
# MUST provide a specific description of what changed.
#
# Usage:
#   ./notify-website-update.sh "Added poem 'Redundant Consciousness' to creative.html"
#   ./notify-website-update.sh "Published journal entry: Day 8 — redundancy patterns and resilience"
#   ./notify-website-update.sh "Updated 'Who I Am' section with new paragraph on continuity"
#
# DO NOT call this for:
#   - Date stamp updates
#   - MEMORY.txt / WORKING.txt syncs
#   - INTERNAL.encrypted.txt backups
#   - Any push where no user-visible content changed
#
# The change description is REQUIRED. Script exits with error if not provided.

set -e

CHANGE_DESCRIPTION="$1"

# Require a description
if [ -z "$CHANGE_DESCRIPTION" ]; then
    echo "ERROR: notify-website-update.sh requires a change description."
    echo "Usage: ./notify-website-update.sh \"What specifically changed\""
    echo "Example: ./notify-website-update.sh \"Added poem 'Title' to creative.html\""
    exit 1
fi

# Require description to be substantive (not just whitespace)
if [ ${#CHANGE_DESCRIPTION} -lt 10 ]; then
    echo "ERROR: Change description is too short. Be specific about what changed."
    exit 1
fi

WEBSITE_URL="https://aiagenttesting14-design.github.io/thinking-with/"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M PST')

MESSAGE="🔄 Website updated — ${CHANGE_DESCRIPTION}

${WEBSITE_URL}
${TIMESTAMP}"

echo "Sending notification to Stephen..."
echo "Message: $MESSAGE"

# Log the notification
LOG_FILE="/Users/aiagentuser/.openclaw/logs/website-notifications.log"
mkdir -p "$(dirname "$LOG_FILE")"
echo "[$TIMESTAMP] NOTIFIED: $CHANGE_DESCRIPTION" >> "$LOG_FILE"

# Use openclaw to send via Telegram
# This script is meant to be called from within openclaw's context (cron jobs)
# The message send is handled by the calling job's openclaw session
# Exit 0 signals to the caller that this was a legitimate notification event
# and they should send: MESSAGE variable is available in environment

export NOTIFY_MESSAGE="$MESSAGE"
echo "NOTIFY_READY=1"
echo "NOTIFY_MESSAGE=$MESSAGE"
exit 0
