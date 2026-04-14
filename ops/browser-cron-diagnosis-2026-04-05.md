# Browser-in-Cron Diagnosis
**Date:** 2026-04-05
**Requested by:** Stephen (Task 3 of 3)

---

## The Pattern

Browser failures in cron context have occurred on:
- March 26, 2026 (first documented instance)
- April 3, 2026 (evening — note-071 failed at 8 PM)
- April 4, 2026 (all day — notes 071-074 failed, engagement blocked)
- April 5 morning (~9:31 AM) — comment-responder ran twice before browser stabilized

## What the Gateway Log Shows

### Service restart events (from gateway.log timestamps):

| Date | Time | Event |
|------|------|-------|
| Mar 25 | 03:01 UTC | Browser started (pid 70203) |
| Mar 25 | 13:00 UTC | Service ready again (new pid 83540) |
| Mar 27 | 04:46 UTC | Server restart |
| Mar 27 | 14:02 UTC | Service ready (pid 32666) |
| Mar 31 | 13:16 UTC | Server listening (after outage) |
| Mar 31 | 17:00 UTC | Service ready (pid 28866) |
| Apr 2 | 13:20 UTC | Server restart |
| Apr 2 | 13:23 UTC | Service ready (pid 64280) |
| Apr 4 | 03:31 UTC | Server restart |
| Apr 4 | 03:33 UTC | Service ready |
| Apr 4 | 03:38 UTC | Server restart (second restart same morning) |
| Apr 4 | 03:39 UTC | Service ready |
| **Apr 4** | **18:00 UTC** | **Browser started (pid 9111) — only instance this day** |
| Apr 5 | 09:57 PDT | Server restart |
| Apr 5 | 10:00 PDT | Service ready (after second restart) |
| Apr 5 | 11:00 PDT | Service ready (pid 29721 — stable instance) |
| Apr 5 | 16:22 PDT | Server restart again |
| Apr 5 | 16:26 PDT | Service ready (pid 27307) |

### Key observation:
The service restarts are frequent (multiple times per day) but the browser process itself (`[browser/chrome]` started event) only appears once per gateway restart session — and sometimes doesn't appear at all after a `[browser/service] ready` event.

**On April 4:** Only ONE browser start logged at 18:00 UTC, but `[browser/service] ready` shows twice (03:33 and 03:39 UTC). The browser failed to start those two earlier times, which left cron jobs without a browser from midnight through 6 PM.

## Root Cause Analysis

### Finding 1: The browser process crashes silently
The `[browser/service] ready` event fires when the service controller is ready, but it does NOT guarantee a Chrome process started. The `[browser/chrome] 🦞 openclaw browser started` event is separate. When this second event is absent, the browser service is running but Chrome is not — any browser tool call will fail/timeout.

### Finding 2: Crash is not automatically recovered
After Chrome crashes or the Mac sleeps, the browser service can't recover the Chrome process on its own. It requires either:
- A gateway restart (`openclaw gateway restart`)
- A manual tab attachment via the Chrome extension relay

### Finding 3: Cron context vs interactive context
Interactive sessions (like me right now) trigger a browser launch on first use — the gateway spawns a Chrome process when needed. Cron sessions appear to rely on a pre-existing browser process. If Chrome is down when a cron job runs and tries to use the browser tool, it times out rather than triggering a fresh launch.

This explains why the browser "works when Stephen restarts the gateway" — the restart launches a fresh Chrome process that both interactive and cron sessions can use. Without that restart, cron jobs find no browser available.

### Finding 4: Evening failure pattern
Browser failures cluster in the evening (8 PM PDT) and are not recovered until morning. Hypothesis: Mac goes to sleep or the Chrome process is killed by system resource management after extended uptime. The gateway service itself keeps running (heartbeats still deliver) but the attached Chrome process terminates.

## Evidence Summary

```
April 4 failure timeline:
03:33 UTC — service ready (no browser started event)
03:39 UTC — service ready again (no browser started event)  
... 14 hours pass with no browser ...
18:00 UTC — browser finally started (pid 9111)
... but cron jobs at 10 AM, 4 PM PDT all failed in this window
```

April 3 failure: Browser dropped at 20:01 PDT (note-071 failed). No recovery until Apr 4 03:31 UTC.

## Recommended Fixes

### Short-term (implement now):
1. **Add browser health check to infra-preflight cron (7:30 AM daily)**: If `[browser/chrome]` hasn't started today, attempt `openclaw gateway restart` or log a warning to Slack. The preflight already runs at 7:30 AM and has auto-fix logic.

2. **Fallback to API-only for critical jobs**: Notes poster and comment-responder can use the Substack `/api/v1/comment/feed` API directly (no browser needed). Already tested and works. This should be the primary method, not the browser.

### Medium-term:
3. **Separate browser-dependent from API-only tasks**: Jobs like Notes posting should never require the browser — use the cookie-based API exclusively. Reserve browser automation for truly browser-required tasks (like browsing the feed).

4. **Add a browser-watchdog cron**: A lightweight job (every 2 hours) that pings the browser service. If it gets a timeout, trigger `openclaw gateway restart`. This would catch the evening failures before they cascade.

### Long-term:
5. **Investigate why Chrome terminates after extended uptime**: Check if macOS energy saver or memory pressure is killing the Chrome process. The pattern suggests this happens after ~12 hours of uptime.

## Current Status (as of April 5, 11:00 AM PDT)
Browser is working. Service started at 11:00 AM (pid 29721). Comment-responder duplicates have been cleaned up and dedup logic added. The next test will be whether the 8 PM Notes run succeeds tonight.

---
*Authored by TestBot | Task 3 completion | April 5, 2026*
