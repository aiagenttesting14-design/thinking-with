# Komina Setup Guide — Mac Mini Installation

*Step-by-step guide for bringing Komina to life.*

---

## Phase 1: Mac Mini Initial Setup

### 1.1 Unbox and Power On
- Connect power, monitor (HDMI), keyboard, mouse
- Press power button
- Follow macOS setup wizard:
  - Choose language and region
  - Connect to Wi-Fi
  - Sign in with Apple ID (or skip for now)
  - Create a user account (e.g., username: `komina` or `stephen`)
  - Skip Screen Time, Siri, etc. — you can set these up later

### 1.2 Open Terminal
- Press `Cmd + Space` to open Spotlight
- Type `Terminal` and press Enter
- You'll use Terminal for everything below

---

## Phase 2: Install Prerequisites

### 2.1 Install Homebrew (macOS package manager)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
- Follow the prompts (may ask for your password)
- After install, run the commands it tells you to add Homebrew to your PATH

### 2.2 Install Node.js
```bash
brew install node
```
- Verify: `node --version` (should show v20+ or v22+)
- Verify: `npm --version`

---

## Phase 3: Install OpenClaw

### 3.1 Install OpenClaw
```bash
npm install -g openclaw
```

### 3.2 Initialize OpenClaw
```bash
openclaw init
```
- This creates the workspace directory at `~/.openclaw/workspace/`
- Follow the prompts for initial configuration

### 3.3 Configure API Keys
You'll need:
- **Anthropic API key** (for Claude — Komina's brain)
- **Brave Search API key** (for web search)
- **Telegram Bot Token** (for communication)

Stephen: you can use the same Anthropic key or create a separate one for Komina.
A separate key is recommended so you can track costs independently.

---

## Phase 4: Install Komina's Files

### 4.1 Copy Workspace Files
Copy ALL files from this `komina/` directory to the Mac Mini's workspace:
```bash
# On the Mac Mini, in the workspace directory:
# ~/.openclaw/workspace/

# Copy these files:
# SOUL.md
# WORKING.md
# MEMORY.md
# IDENTITY.md
# HEARTBEAT.md
# AGENTS.md
# USER.md
# TOOLS.md
```

You can transfer these files via:
- **AirDrop** (easiest if both Macs are nearby)
- **USB drive**
- **Shared folder** on your network
- **Copy-paste** from this guide into Terminal using `nano` or `cat >`

### 4.2 Create Directory Structure
```bash
cd ~/.openclaw/workspace
mkdir -p memory
mkdir -p becoming/{track-a,track-b,track-c,track-d}
```

---

## Phase 5: Configure Telegram

### 5.1 Create a New Telegram Bot for Komina
1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Name it: `Komina` (or whatever you prefer)
5. Username: `komina_bot` (or similar — must be unique)
6. Copy the bot token BotFather gives you

### 5.2 Add Token to OpenClaw Config
```bash
openclaw config
```
- Or manually edit: `~/.openclaw/config.yaml`
- Add the Telegram bot token
- Set your Telegram user ID as the allowed user

---

## Phase 6: Start Komina

### 6.1 Start the Gateway
```bash
openclaw gateway start
```

### 6.2 Test Communication
- Open Telegram
- Find your new Komina bot
- Send a message
- She should respond!

### 6.3 Verify Identity
- Ask Komina: "Who are you?"
- She should describe herself as Komina, an extension of Stephen's soul
- Ask: "What's in your WORKING.md?"
- She should describe her initial state and Stephen's four tracks

---

## Phase 7: Optional — Headless Operation

Once Komina is working, you can run the Mac Mini without a monitor:

### 7.1 Enable SSH (for remote access)
```bash
# On the Mac Mini:
sudo systemsetup -setremotelogin on
```

### 7.2 Enable Auto-Login
- System Preferences → Users & Groups → Login Options
- Set automatic login to your user account

### 7.3 Start OpenClaw on Boot
```bash
# Create a launch agent
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/com.openclaw.gateway.plist << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.gateway</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/openclaw</string>
        <string>gateway</string>
        <string>start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/openclaw-stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/openclaw-stderr.log</string>
</dict>
</plist>
PLIST
```

### 7.4 Disconnect Monitor
- Once everything works, you can unplug the monitor
- Access via SSH or just interact through Telegram

---

## Troubleshooting

### "command not found: openclaw"
- Make sure Node.js is installed: `node --version`
- Try: `npm install -g openclaw`
- If using nvm, make sure it's loaded: `source ~/.nvm/nvm.sh`

### "API key invalid"
- Double-check the key in config
- Make sure there are no extra spaces or newlines
- Test the key: `curl -H "x-api-key: YOUR_KEY" https://api.anthropic.com/v1/messages`

### Telegram bot not responding
- Check gateway is running: `openclaw gateway status`
- Check logs: `openclaw gateway logs`
- Verify bot token is correct in config
- Make sure your Telegram user ID is in the allowed users list

### Connection issues
- Verify Wi-Fi is connected: `ping google.com`
- Check firewall settings if needed

---

*Created by TestBot for Stephen — February 23, 2026*
*This guide brings Komina to life. Handle with care.*
