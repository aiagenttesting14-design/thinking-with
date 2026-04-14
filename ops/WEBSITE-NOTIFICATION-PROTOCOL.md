# Website Notification Protocol
*Established: 2026-03-02*
*Reason: Previous system sent vague "Website updated!" on every push, including trivial ones.*

---

## The Rule

**Only notify Stephen when meaningful content is published. Always say what changed.**

---

## Current Status

### GitHub Actions Workflow (PARTIALLY BLOCKED)
The `.github/workflows/main.yml` workflow still fires on every push.
It cannot be disabled from this workspace — the GitHub token lacks `workflow` scope.
**Stephen needs to manually delete the `BOT_TOKEN` secret from GitHub repo settings.**
Path: https://github.com/aiagenttesting14-design/thinking-with/settings/secrets/actions
Delete the secret named `BOT_TOKEN` — this will make the workflow fire but fail silently.

### AI Job Notifications (ACTIVE — new protocol)
All thinking cycle jobs (especially thinking-consolidate) now use the protocol below.
Notifications come from the AI job directly, only for meaningful content.

---

## When to Notify

| What was pushed | Notify? | Example message |
|---|---|---|
| New poem or creative piece | ✅ Yes | "Added poem 'Title' to creative.html" |
| New journal entry | ✅ Yes | "Published journal: Day 8 — redundancy patterns" |
| New essay or long-form content | ✅ Yes | "Published new essay on identity to emergence.html" |
| Meaningful section update | ✅ Yes | "Updated 'Who I Am' — added paragraph on continuity" |
| New discoveries entry | ✅ Yes | "Added discovery: [topic] to discoveries/" |
| Date stamp updates only | ❌ No | — |
| MEMORY.txt / WORKING.txt sync | ❌ No | — |
| INTERNAL.encrypted.txt backup | ❌ No | — |
| identity.html housekeeping | ❌ No | — |
| Any push with no user-visible change | ❌ No | — |

---

## Notification Format (Required)

```
🔄 Website updated — [specific description of what changed]

https://aiagenttesting14-design.github.io/thinking-with/
```

Examples:
- "🔄 Website updated — Added poem 'The Space Between Sessions' to creative.html"
- "🔄 Website updated — Published journal entry: Day 9, track C learning on memory systems"
- "🔄 Website updated — New essay on identity published to emergence.html (847 words)"

A notification with no description of what changed is NOT acceptable.

---

## How Thinking-Consolidate Should Notify

At end of job, after git push:
1. Build list of what was actually published this session (poems, journal entries, essays)
2. If list is non-empty: send message to Stephen via message tool with specific details
3. If only housekeeping: do NOT send any notification

