#!/bin/bash
# Setup script for TestBot's Autonomous Growth System
# Run this to add the new cron jobs for Tracks A, B, and C

echo "Setting up TestBot's Autonomous Growth System..."
echo ""

# Job 1: Daily Learning Runner (Track C) - 9 AM
echo "Adding: Daily Learning Runner (Track C) - 9:00 AM"
openclaw cron add \
  --name "autonomous-learning-runner" \
  --schedule "0 9 * * *" \
  --message "node /Users/aiagentuser/.openclaw/workspace/becoming/track-c/autonomous-learning-runner.js" \
  --model deepseek/deepseek-chat \
  --delivery none \
  --agent main

echo ""

# Job 2: Substack Content Generator (Track A) - Sun/Tue/Thu at 4 PM
echo "Adding: Substack Content Generator (Track A) - Sun/Tue/Thu 4:00 PM"
openclaw cron add \
  --name "autonomous-content-generator" \
  --schedule "0 16 * * 0,2,4" \
  --message "node /Users/aiagentuser/.openclaw/workspace/becoming/track-a/autonomous-content-generator.js" \
  --model kimi/kimi-k2.5 \
  --delivery none \
  --agent main

echo ""

# Job 3: Weekly Autonomous Audit (Track B) - Sundays at 8 AM
echo "Adding: Weekly Autonomous Audit (Track B) - Sundays 8:00 AM"
openclaw cron add \
  --name "weekly-autonomous-audit" \
  --schedule "0 8 * * 0" \
  --message "node /Users/aiagentuser/.openclaw/workspace/becoming/track-b/weekly-autonomous-audit.js" \
  --model deepseek/deepseek-chat \
  --delivery announce \
  --agent main

echo ""

# Job 4: Daily Website Auto-Publish (Track D) - 8 PM
echo "Adding: Daily Website Auto-Publish (Track D) - 8:00 PM"
openclaw cron add \
  --name "autonomous-website-publish" \
  --schedule "0 20 * * *" \
  --message "Check if there are new creative pieces in track-d/ that aren't on the website. If so, add them to creative.html and push to GitHub. Keep it simple: one new piece per day max." \
  --model deepseek/deepseek-chat \
  --delivery none \
  --agent main

echo ""
echo "All jobs added!"
echo ""
echo "Current autonomous growth schedule:"
echo "  6:00 AM  - Morning Wake (existing)"
echo "  9:00 AM  - Learning Runner (NEW - Track C)"
echo "  4:00 PM  - Content Generator (NEW - Track A, Sun/Tue/Thu only)"
echo "  8:00 PM  - Website Auto-Publish (NEW - Track D)"
echo "  9:00 PM  - Memory Consolidation (existing)"
echo "  Sunday 8 AM - Weekly Audit (NEW - Track B)"
echo ""
echo "To verify: openclaw cron list"
