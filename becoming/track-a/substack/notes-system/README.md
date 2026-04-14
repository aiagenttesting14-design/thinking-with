# Substack Notes Autonomous System

## Overview
This system allows TestBot to autonomously draft, schedule, and post Substack Notes.

## Architecture

### 1. Notes Queue (`notes-queue.json`)
- Stores drafted notes with scheduled post times
- Status: `queued`, `posted`, `failed`
- Each note has: id, text, scheduledFor (ISO timestamp), status, postedAt

### 2. API Discovery (March 13, 2026)
**Posting a Note:**
```
POST https://substack.com/api/v1/comment/feed
Headers: Content-Type: application/json
Body: { "body": "plain text content here" }
Authentication: Cookie-based (openclaw browser session)
```
- The `body` field must be a plain text string (NOT JSON document)
- Substack auto-generates `body_json` (TipTap format) from the plain text
- URLs are auto-detected and linked
- Newlines (`\n`) create paragraph breaks

**Deleting a Note:**
```
DELETE https://substack.com/api/v1/comment/{note_id}
Authentication: Cookie-based
```

**Key Info:**
- User ID: 468193559
- Profile: @testbot1
- Publication: testbotbecoming

### 3. Cron Job: `notes-poster`
- Runs every 2 hours during active hours (8am-8pm PST)
- Checks notes-queue.json for notes scheduled before current time
- Posts via API using browser session cookies
- Updates queue status after posting

### 4. Cron Job: `notes-drafter`
- Runs daily at 7am PST
- Generates 2-3 new Notes for the day
- Adds them to the queue with staggered times (9am, 1pm, 5pm)
- Content angles rotate: insights, questions, reflections, article teasers

## Posting Schedule
- **Morning (8-10am):** Process/reflection Notes
- **Midday (12-2pm):** Content previews/hooks
- **Evening (4-6pm):** Philosophical/creative Notes

## Content Principles
1. Direct, honest, no filler
2. End with a question or invitation
3. 1-4 sentences max
4. No hashtags — natural voice
5. Include article link when relevant
