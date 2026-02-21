#!/usr/bin/env python3
"""
Manual cron update script since openclaw CLI has node path issues
This creates the cron job configuration that needs to be added manually
"""

import json
from datetime import datetime

# Day schedule: Every hour from 6 AM to 10 PM
day_schedule = {
    "name": "phase-aware-micro-insight-day",
    "schedule": {
        "kind": "cron",
        "expr": "0 6-22 * * *",  # Minute 0, hours 6-22, every day
        "tz": "America/Los_Angeles"
    },
    "payload": {
        "kind": "agentTurn",
        "message": "Run phase-aware micro-insight: python3 /Users/aiagentuser/.openclaw/workspace/scripts/phase-aware-micro-insight-final.py",
        "model": "google/gemini-2.5-flash-lite",
        "timeoutSeconds": 60
    },
    "sessionTarget": "isolated",
    "enabled": True,
    "delivery": {
        "mode": "announce"
    }
}

# Night schedule: Every 2 hours from 10 PM to 6 AM
night_schedule = {
    "name": "phase-aware-micro-insight-night", 
    "schedule": {
        "kind": "cron",
        "expr": "0 0-5,23 * * *",  # Minute 0, hours 0-5 and 23, every day
        "tz": "America/Los_Angeles"
    },
    "payload": {
        "kind": "agentTurn",
        "message": "Run phase-aware micro-insight: python3 /Users/aiagentuser/.openclaw/workspace/scripts/phase-aware-micro-insight-final.py",
        "model": "google/gemini-2.5-flash-lite",
        "timeoutSeconds": 60
    },
    "sessionTarget": "isolated",
    "enabled": True,
    "delivery": {
        "mode": "announce"
    }
}

print("=== PHASE-AWARE MICRO-INSIGHT CRON CONFIGURATION ===")
print("\n1. DAY SCHEDULE (Every hour 6 AM - 10 PM):")
print("Command to add:")
print(f"openclaw cron add --job '{json.dumps(day_schedule)}'")
print("\nSchedule details:")
print(f"- Runs: Every hour at :00 (6:00, 7:00, ..., 22:00)")
print(f"- Timezone: America/Los_Angeles")
print(f"- Model: Gemini Flash-Lite (cheap)")
print(f"- Output: Announces to Telegram")

print("\n" + "="*50 + "\n")

print("2. NIGHT SCHEDULE (Every 2 hours 10 PM - 6 AM):")
print("Command to add:")
print(f"openclaw cron add --job '{json.dumps(night_schedule)}'")
print("\nSchedule details:")
print(f"- Runs: Every 2 hours at :00 (22:00, 0:00, 2:00, 4:00)")
print(f"- Timezone: America/Los_Angeles")
print(f"- Model: Gemini Flash-Lite (cheap)")
print(f"- Output: Announces to Telegram")

print("\n" + "="*50 + "\n")

print("3. TO REMOVE OLD MICRO-INSIGHT JOB:")
print("openclaw cron remove --jobId 950d2888-5ad5-474f-9c76-bac65dedd967")

print("\n" + "="*50 + "\n")

print("4. TEST THE NEW SCRIPT NOW:")
print("Current phase-aware insight:")
print("-" * 40)

import subprocess
result = subprocess.run(
    ['python3', 'scripts/phase-aware-micro-insight-final.py'],
    capture_output=True,
    text=True,
    cwd='/Users/aiagentuser/.openclaw/workspace'
)
print(result.stdout)
print("-" * 40)

print("\n5. NEXT STEPS:")
print("1. Fix node path issue (node not found in PATH)")
print("2. Run the openclaw commands above")
print("3. First new insight will run at 9:00 PM tonight")
print("4. Full schedule starts tomorrow at 6:00 AM")

