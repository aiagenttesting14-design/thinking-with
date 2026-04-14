# Notes Poster — Option A Implementation

**Date:** April 5, 2026  
**Status:** Complete

## What Was Built

### 1. Resilient Notes Poster (`notes-poster-resilient.js`)

**Key improvements over previous version:**

| Feature | Old | New |
|---------|-----|-----|
| Browser method | Full automation (click/type/navigate) | Minimal eval (one JS fetch call) |
| Failure handling | Marks as "failed" | Marks as "browser-unavailable" |
| Retry behavior | Manual intervention needed | Auto-retries next window |
| Health check | None | Pre-flight browser check |
| Reporting | Logs only | Slack notifications to #track-a |

**How it works:**
1. Reads `notes-queue.json` for due notes
2. Checks if browser is healthy (5-second health check)
3. If browser down → marks notes as `browser-unavailable`, reports to Slack, exits cleanly
4. If browser up → posts via single `browser.eval` fetch call to Substack API
5. Updates queue status (`posted`, `failed`, or `browser-unavailable`)

**Status states:**
- `queued` — Ready to post
- `posted` — Successfully posted
- `failed` — API error (non-retryable)
- `browser-unavailable` — Browser was down (will retry when watchdog resets it)

### 2. Browser Watchdog (`browser-watchdog.js`)

**Purpose:** Pings Chrome every 2 hours, triggers recovery if down.

**What it does:**
1. Checks browser health via gateway `/browser/status`
2. If healthy → checks for `browser-unavailable` notes and resets them to `queued`
3. If unhealthy → (optionally) restarts gateway, verifies recovery, resets stuck notes

**Recovery behavior:**
- With `--restart-on-failure`: Auto-restarts gateway
- Without flag: Reports to Slack, manual restart needed

## Setup Instructions

### Step 1: Set up cron jobs

Add these to your crontab (`crontab -e`):

```bash
# Notes poster — runs every 2 hours during active hours (8am-8pm PST)
0 8,10,12,14,16,18,20 * * * cd /Users/aiagentuser/.openclaw/workspace/becoming/track-a/substack/notes-system && node notes-poster-resilient.js >> /tmp/notes-poster.log 2>&1

# Browser watchdog — runs every 2 hours around the clock
0 */2 * * * cd /Users/aiagentuser/.openclaw/workspace/becoming/track-a/substack/notes-system && node browser-watchdog.js --restart-on-failure >> /tmp/browser-watchdog.log 2>&1
```

### Step 2: Environment variables (optional)

Add to your shell profile if not using defaults:

```bash
export OPENCLAW_GATEWAY_URL="ws://127.0.0.1:18789"
export OPENCLAW_GATEWAY_TOKEN="your-token-here"  # Only if auth token required
```

### Step 3: Test

```bash
# Dry run (doesn't actually post)
cd /Users/aiagentuser/.openclaw/workspace/becoming/track-a/substack/notes-system
node notes-poster-resilient.js --dry-run

# Test watchdog
node browser-watchdog.js
```

## How the Fallback Works

**Scenario: Browser goes down at 8 PM**

1. 8:00 PM poster run → Browser check fails
2. Notes marked as `browser-unavailable` (not failed)
3. Slack notification: "⚠️ Notes poster: Browser unavailable. 1 note(s) queued for retry."
4. 10:00 PM watchdog runs → Detects browser down
5. Watchdog restarts gateway
6. Watchdog resets `browser-unavailable` notes to `queued`
7. 10:00 PM poster run (or next scheduled run) → Posts successfully

**Result:** Zero manual intervention, note eventually posts.

## Files Created

```
becoming/track-a/substack/notes-system/
├── notes-poster-resilient.js   # Main poster with fallback logic
├── browser-watchdog.js          # Health checks and recovery
└── SETUP-OPTION-A.md           # This file
```

## Next Steps

1. Review and approve this implementation
2. Set up cron jobs (copy commands above)
3. Test with `--dry-run`
4. Monitor first few runs via `/tmp/notes-poster.log` and `/tmp/browser-watchdog.log`
5. Old poster can be retired once this is confirmed working

## Verification

After setup, you should see:
- Notes posting successfully via minimal-eval method
- Slack notifications in #track-a for each post
- No more "Browser service unavailable" permanent failures
- Automatic recovery when browser goes down
