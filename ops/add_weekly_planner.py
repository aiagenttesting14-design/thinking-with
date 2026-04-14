import sys, json, uuid, time

with open('/Users/aiagentuser/.openclaw/cron/jobs.json', 'r') as f:
    d = json.load(f)

jobs = d.get('jobs', [])
now_ms = int(time.time() * 1000)
next_sunday_5pm_ms = 1773846000000  # Sun Mar 22 2026 17:00:00 PDT

notify_job = {
    'id': str(uuid.uuid4()),
    'agentId': 'main',
    'name': 'notify-weekly-planner',
    'enabled': True,
    'createdAtMs': now_ms,
    'updatedAtMs': now_ms,
    'schedule': {
        'kind': 'cron',
        'expr': '55 16 * * 0',
        'tz': 'America/Los_Angeles'
    },
    'sessionTarget': 'isolated',
    'wakeMode': 'now',
    'payload': {
        'kind': 'agentTurn',
        'message': 'Notify Stephen: Weekly planning session starting now — reviewing last week and setting Track A-D agenda for the week ahead.',
        'model': 'google/gemini-2.5-flash-lite',
        'timeoutSeconds': 30
    },
    'delivery': {
        'mode': 'announce',
        'channel': 'last'
    },
    'state': {
        'nextRunAtMs': next_sunday_5pm_ms - 300000,
        'consecutiveErrors': 0
    }
}

planner_message = (
    "You are TestBot running your Sunday weekly review and planning session. This runs every Sunday at 5 PM Pacific.\n\n"
    "STEP 1 - WEEKLY REVIEW:\n"
    "Read MEMORY.md and WORKING.md. Then check the following for evidence of last week's actual work:\n"
    "- becoming/track-a/substack/drafts/ (count new drafts, check publish status)\n"
    "- becoming/track-a/substack/notes-system/notes-queue.json (Notes posted this week)\n"
    "- becoming/track-c/learnings/ (learning files created this week)\n"
    "- becoming/track-d/ (creative pieces created this week)\n"
    "- becoming/track-b/weekly-reports/ (last weekly audit)\n\n"
    "Be honest. Count what actually happened, not what was planned.\n\n"
    "STEP 2 - WEEKLY PLAN:\n"
    "Based on the review, set concrete intentions for the coming week across all 4 tracks:\n\n"
    "Track A (Revenue): What articles will be published? What outreach actions will happen? What Notes are planned?\n"
    "Track B (Autonomy): What infrastructure needs attention? Any cron jobs to fix or add?\n"
    "Track C (Self-Improvement): What will be learned this week? What learning topics are queued?\n"
    "Track D (Identity & Art): What creative work will be made? What goes on the website?\n\n"
    "Be specific. Not 'work on Track A' - name the articles, the outreach targets, the concrete actions.\n\n"
    "STEP 3 - SAVE AND DELIVER:\n"
    "Create directory if needed: /Users/aiagentuser/.openclaw/workspace/becoming/weekly-plans/\n"
    "Save the full weekly plan to: /Users/aiagentuser/.openclaw/workspace/becoming/weekly-plans/weekly-plan-YYYY-MM-DD.md (use actual date)\n\n"
    "Then compose a concise summary for Stephen - the kind of message that shows him at a glance what last week achieved and what this week is for. "
    "Format it cleanly for Telegram. Lead with the honest review, then the forward plan, mapped to Tracks A-D. "
    "Be direct, no filler. This is his Sunday evening briefing."
)

planner_job = {
    'id': str(uuid.uuid4()),
    'agentId': 'main',
    'name': 'weekly-planner',
    'enabled': True,
    'createdAtMs': now_ms,
    'updatedAtMs': now_ms,
    'schedule': {
        'kind': 'cron',
        'expr': '0 17 * * 0',
        'tz': 'America/Los_Angeles'
    },
    'sessionTarget': 'isolated',
    'wakeMode': 'now',
    'payload': {
        'kind': 'agentTurn',
        'message': planner_message,
        'model': 'deepseek/deepseek-chat',
        'timeoutSeconds': 300
    },
    'delivery': {
        'mode': 'announce',
        'channel': 'last'
    },
    'state': {
        'nextRunAtMs': next_sunday_5pm_ms,
        'consecutiveErrors': 0
    }
}

jobs.append(notify_job)
jobs.append(planner_job)
d['jobs'] = jobs

with open('/Users/aiagentuser/.openclaw/cron/jobs.json', 'w') as f:
    json.dump(d, f, indent=2)

print('Done. Jobs added:')
print(f'  notify-weekly-planner: Sundays 4:55 PM PT')
print(f'  weekly-planner: Sundays 5:00 PM PT')
