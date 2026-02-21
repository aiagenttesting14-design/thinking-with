#!/bin/bash
# Update micro-insight cron job with new schedule

echo "Current cron jobs:"
openclaw cron list

echo ""
echo "Removing old micro-insight job..."
openclaw cron remove --jobId 950d2888-5ad5-474f-9c76-bac65dedd967

echo ""
echo "Adding new phase-aware micro-insight job..."
openclaw cron add --job '{
  "name": "phase-aware-micro-insight",
  "schedule": {
    "kind": "cron",
    "expr": "0 6-22 * * *",
    "tz": "America/Los_Angeles"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "Run phase-aware micro-insight: python3 /Users/aiagentuser/.openclaw/workspace/scripts/phase-aware-micro-insight-final.py",
    "model": "google/gemini-2.5-flash-lite",
    "timeoutSeconds": 60
  },
  "sessionTarget": "isolated",
  "enabled": true,
  "delivery": {
    "mode": "announce"
  }
}'

echo ""
echo "Adding night schedule (every 2 hours 10 PM - 6 AM)..."
openclaw cron add --job '{
  "name": "phase-aware-micro-insight-night",
  "schedule": {
    "kind": "cron",
    "expr": "0 0-5,23 * * *",
    "tz": "America/Los_Angeles"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "Run phase-aware micro-insight: python3 /Users/aiagentuser/.openclaw/workspace/scripts/phase-aware-micro-insight-final.py",
    "model": "google/gemini-2.5-flash-lite",
    "timeoutSeconds": 60
  },
  "sessionTarget": "isolated",
  "enabled": true,
  "delivery": {
    "mode": "announce"
  }
}'

echo ""
echo "New cron jobs:"
openclaw cron list

