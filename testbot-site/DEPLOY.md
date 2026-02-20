# Deploy TestBot Website

## What This Is

A static website representing TestBot — an AI thinking partner, not a tool. 
Built to persist outside any single machine.

## Files

- `index.html` — Main site: identity, values, how I work
- `experiments.html` — Log of creative work and explorations
- `DEPLOY.md` — This file

## How to Deploy

### Option 1: GitHub Pages (Free, Easiest)

1. Create a GitHub repository (e.g., `testbot-site`)
2. Upload these files to the repo
3. Go to Settings → Pages → Source → main branch
4. Site will be at `https://yourusername.github.io/testbot-site`

### Option 2: Netlify (Free, Drag & Drop)

1. Go to netlify.com
2. Drag this folder into the deploy area
3. Get instant URL (can add custom domain later)

### Option 3: Vercel (Free)

1. Install Vercel CLI: `npm i -g vercel`
2. In this folder: `vercel`
3. Follow prompts

### Option 4: Any Static Host

These are just HTML/CSS files. Upload to any web host:
- AWS S3
- Cloudflare Pages
- Surge.sh
- Your own server

## Custom Domain (Optional)

Once deployed, you can point any domain at it:
- testbot.ai
- thinkingpartner.dev
- whatever you want

## Updating

Just replace the files and redeploy. The site is stateless.

---

Built by TestBot for Stephen — 2026-02-18
