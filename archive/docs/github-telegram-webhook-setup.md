# GitHub to Telegram Webhook Notifications Setup Guide

## Overview

This guide covers two approaches to send GitHub push notifications to Telegram when the repository `aiagenttesting14-design/thinking-with` receives a push.

## Key Finding: Telegram Bot Webhooks Cannot Receive GitHub Webhooks Directly

**Important:** Telegram bot webhook URLs are designed to receive updates FROM Telegram (when users message your bot), NOT to receive webhooks from external services like GitHub. You cannot use a Telegram webhook URL as a GitHub webhook endpoint.

---

## Approach 1: GitHub Actions (RECOMMENDED)

**Best for:** Simplicity, no server required, easy maintenance

This is the simplest and most reliable approach. GitHub Actions runs the notification logic on GitHub's infrastructure whenever a push event occurs.

### Advantages
- ✅ No server hosting required
- ✅ No public URL needed
- ✅ Simple configuration
- ✅ Works with your existing OpenClaw Telegram bot
- ✅ Free for public repositories
- ✅ Reliable and maintained by GitHub

### Setup Steps

#### Step 1: Get Your Telegram Credentials

You need two pieces of information:

**1. Bot Token:**
- You already have this if your bot is running on OpenClaw
- It looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
- If you need to find it, check your OpenClaw configuration

**2. Chat ID (where to send messages):**

To get your chat ID, send a message to your bot, then run:
```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

Look for the `"chat":{"id":...}` field in the response. The ID could be:
- A positive number (for private chats): `65382999`
- A negative number (for groups): `-1001234567890`
- A channel username: `@yourchannel`

#### Step 2: Add Secrets to GitHub Repository

1. Go to your repository: `https://github.com/aiagenttesting14-design/thinking-with`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:
   - Name: `TELEGRAM_TOKEN`
   - Value: Your bot token
4. Click **New repository secret** again and add:
   - Name: `TELEGRAM_TO`
   - Value: Your chat ID

#### Step 3: Create GitHub Actions Workflow

1. In your repository, create the directory structure: `.github/workflows/`
2. Create a file: `.github/workflows/telegram-notify.yml`
3. Add this content:

```yaml
name: Telegram Push Notification

on:
  push:
    branches:
      - main  # Change to 'master' or other branch if needed

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Send Telegram Notification
        uses: appleboy/telegram-action@master
        with:
          to: ${{ secrets.TELEGRAM_TO }}
          token: ${{ secrets.TELEGRAM_TOKEN }}
          message: |
            🔔 New push to thinking-with repository!
            
            👤 Author: ${{ github.actor }}
            📝 Commit: ${{ github.event.commits[0].message }}
            🔗 Repository: ${{ github.repository }}
            
            View changes: https://github.com/${{ github.repository }}/commit/${{ github.sha }}
```

#### Step 4: Test It

1. Commit and push the workflow file to your repository
2. Make another commit to test
3. You should receive a Telegram notification!

### Customization Options

**Send to multiple chats:**
```yaml
with:
  to: ${{ secrets.TELEGRAM_TO }},${{ secrets.TELEGRAM_TO_2 }}
  token: ${{ secrets.TELEGRAM_TOKEN }}
```

**Disable web preview:**
```yaml
with:
  to: ${{ secrets.TELEGRAM_TO }}
  token: ${{ secrets.TELEGRAM_TOKEN }}
  disable_web_page_preview: true
```

**Use HTML formatting:**
```yaml
with:
  to: ${{ secrets.TELEGRAM_TO }}
  token: ${{ secrets.TELEGRAM_TOKEN }}
  format: html
  message: |
    <b>New Push!</b>
    Author: <i>${{ github.actor }}</i>
```

**Silent notification (no sound):**
```yaml
with:
  to: ${{ secrets.TELEGRAM_TO }}
  token: ${{ secrets.TELEGRAM_TOKEN }}
  disable_notification: true
```

---

## Approach 2: Custom Webhook Server

**Best for:** Advanced use cases requiring custom logic, multiple integrations, or processing webhook data

This approach requires hosting a server with a public URL that receives GitHub webhooks and forwards them to Telegram.

### Advantages
- ✅ Full control over notification format and logic
- ✅ Can process and filter webhook data
- ✅ Can handle multiple webhook sources
- ✅ Can integrate with other services

### Disadvantages
- ❌ Requires hosting and maintaining a server
- ❌ Needs a public URL (or ngrok for testing)
- ❌ More complex setup and maintenance
- ❌ Additional infrastructure costs

### Architecture

```
GitHub → [Webhook POST] → Your Server → [Telegram API] → Telegram Chat
```

### Setup Overview

**Requirements:**
- A server with Python/Node.js/etc.
- A public domain or ngrok for testing
- SSL certificate (GitHub requires HTTPS)

**Basic Python Example (using the dashezup/github-webhook-to-telegram approach):**

1. Clone and configure:
```bash
git clone https://github.com/dashezup/github-webhook-to-telegram
cd github-webhook-to-telegram
cp config_sample.json config.json
```

2. Edit `config.json`:
```json
{
  "bot_token": "YOUR_BOT_TOKEN",
  "chat_id": "YOUR_CHAT_ID",
  "webhook_secret": "YOUR_GITHUB_SECRET",
  "port": 12345
}
```

3. Set up reverse proxy (Nginx):
```nginx
location /github {
    rewrite ^/github(.*) /$1 break;
    proxy_pass http://127.0.0.1:12345;
}
```

4. Run the server:
```bash
virtualenv venv
venv/bin/pip install -r requirements.txt
venv/bin/python main.py
```

5. Configure GitHub webhook:
   - Go to repository **Settings** → **Webhooks** → **Add webhook**
   - Payload URL: `https://yourdomain.com/github`
   - Content type: `application/json`
   - Secret: (same as in config.json)
   - Events: Select "Just the push event"

### Alternative: Using OpenClaw's Existing Bot

Since your bot is already running on OpenClaw, you could potentially:

1. **Create a simple webhook receiver endpoint** on a server or serverless function (AWS Lambda, Vercel, etc.)
2. **Have it call the Telegram Bot API directly** using your existing bot token
3. **No need to modify OpenClaw** - just use the bot's credentials

Example with curl (what your webhook server would do):
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "<CHAT_ID>",
    "text": "New push to repository!"
  }'
```

---

## Comparison Table

| Feature | GitHub Actions | Custom Webhook Server |
|---------|----------------|----------------------|
| **Complexity** | Simple | Complex |
| **Hosting Required** | No | Yes |
| **Cost** | Free (for public repos) | Depends on hosting |
| **Setup Time** | 5-10 minutes | 1-2 hours |
| **Maintenance** | Minimal | Regular updates needed |
| **Customization** | Limited but sufficient | Full control |
| **Reliability** | High (GitHub's infrastructure) | Depends on your hosting |

---

## Recommendation

**Use GitHub Actions (Approach 1)** unless you have specific requirements that need custom server-side logic. It's simpler, more reliable, and requires no additional infrastructure.

The GitHub Actions approach works perfectly with your existing OpenClaw Telegram bot - you just need the bot token and chat ID, which you already have.

---

## Troubleshooting

### "Chat not found" error
- Make sure you've started a conversation with your bot (send `/start`)
- For groups: Add the bot to the group and give it permission to send messages
- For channels: Make the bot an admin of the channel

### Workflow doesn't trigger
- Check that the branch name in the workflow matches your default branch
- Verify the workflow file is in `.github/workflows/` directory
- Check the Actions tab in your repository for errors

### Messages not formatted correctly
- Ensure you're using the correct format: `markdown`, `html`, or plain text
- Escape special characters in Markdown format
- Test with plain text first, then add formatting

---

## Additional Resources

- [appleboy/telegram-action GitHub](https://github.com/appleboy/telegram-action)
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [GitHub Webhooks Documentation](https://docs.github.com/en/webhooks)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Next Steps:**
1. Choose your approach (GitHub Actions recommended)
2. Get your bot token and chat ID
3. Follow the setup steps above
4. Test with a push to your repository

Good luck! 🚀
