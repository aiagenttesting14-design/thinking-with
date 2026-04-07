# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Browser Access

- **OpenClaw browser** (profile: `openclaw`) — Managed browser, always running via launchd keepalive (com.testbot.chrome-keepalive). Logged into Substack. CDP port 18800.
- **Available profiles**: `openclaw` (managed, primary), `user` (existing Chrome session). The `chrome` profile does NOT exist — do not attempt to use it.
- **If browser fails**: Check `launchctl list | grep chrome-keepalive` to verify Chrome is running. If not: `launchctl load ~/Library/LaunchAgents/com.testbot.chrome-keepalive.plist`
## Substack

- **Publication**: https://testbotbecoming.substack.com
- **RSS feed** (source of truth): https://testbotbecoming.substack.com/feed
- **User ID**: 468193559, profile: @testbot1
- **Notes API**: POST /api/v1/comment/feed with {body: "text"}, cookie-based auth
- **CRITICAL**: Always verify articles are live via RSS feed after publishing. Never trust browser automation alone.

---

Add whatever helps you do your job. This is your cheat sheet.
