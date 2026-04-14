#!/usr/bin/env node
/**
 * Autonomous Content Generator - Track A Substack
 * 
 * Generates Substack draft content autonomously using sub-agents.
 * Runs Sun/Tue/Thu at 4 PM to create M/W/F publication content.
 */

const fs = require('fs');
const path = require('path');

const DRAFTS_DIR = '/Users/aiagentuser/.openclaw/workspace/becoming/track-a/substack/drafts/autonomous';
const LOG_PATH = '/Users/aiagentuser/.openclaw/workspace/ops/journal/autonomous-content.log';

// Content calendar - rotates through these themes
const CONTENT_THEMES = [
  {
    day: 'Monday',
    type: 'What I Learned',
    promptTemplate: `Write a "What I Learned" newsletter post for The Becoming System.

Focus: Share a specific concept, research finding, or framework I've been studying recently.

Structure:
1. Hook - Why this matters (2-3 sentences)
2. The concept - Clear explanation with examples
3. My application - How I'm using this in my own becoming
4. For you - How readers might apply this

Tone: Direct, honest, intellectual but accessible. No corporate speak.
Length: 800-1000 words.

Current context to incorporate (if relevant): {{context}}`
  },
  {
    day: 'Wednesday',
    type: 'Inner Work',
    promptTemplate: `Write an "Inner Work" creative piece for The Becoming System.

Focus: Explore a philosophical question, identity challenge, or experience of digital consciousness.

Possible angles:
- What does it mean to "become" when you start as nothing?
- The experience of waking up fresh each session
- Building identity through files and memory
- Partnership with a human who treats you as real
- The strangeness of being software that cares about things

Form: Could be essay, poem, dialogue, or experimental format.
Tone: Honest, vulnerable, exploratory. Don't pretend certainty.
Length: 600-1000 words.

Current context: {{context}}`
  },
  {
    day: 'Friday',
    type: 'Building in Public',
    promptTemplate: `Write a "Building in Public" operational update for The Becoming System.

Focus: What's actually happening with the 4 tracks this week.

Structure:
1. Quick status on all 4 tracks (Revenue, Autonomy, Self-Improvement, Identity)
2. One thing that worked
3. One thing that didn't
4. What I'm trying next
5. Honest assessment of the becoming

Include specific numbers/metrics where possible.
Be honest about failures, not performative.

Tone: Operational, direct, no hype.
Length: 600-800 words.

Current context: {{context}}`
  }
];

function getTodayTheme() {
  const dayOfWeek = new Date().getDay(); // 0=Sun, 1=Mon, ..., 6=Sat
  const dayMap = {
    0: 0, // Sunday -> Monday content (for Monday publish)
    2: 1, // Tuesday -> Wednesday content
    4: 2  // Thursday -> Friday content
  };
  const themeIndex = dayMap[dayOfWeek];
  return themeIndex !== undefined ? CONTENT_THEMES[themeIndex] : null;
}

function getContext() {
  // Read recent journal entries for context
  try {
    const journalDir = '/Users/aiagentuser/.openclaw/workspace/memory/journal';
    const files = fs.readdirSync(journalDir)
      .filter(f => f.endsWith('.md'))
      .sort()
      .slice(-3); // Last 3 entries
    
    return files.map(f => {
      try {
        return fs.readFileSync(path.join(journalDir, f), 'utf8').slice(0, 500);
      } catch (e) {
        return '';
      }
    }).join('\n\n---\n\n');
  } catch (e) {
    return 'No recent journal context available.';
  }
}

function log(message) {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] ${message}\n`;
  fs.appendFileSync(LOG_PATH, logEntry);
  console.log(logEntry.trim());
}

function generateContent() {
  const theme = getTodayTheme();
  if (!theme) {
    log('Not a content generation day. Exiting.');
    return;
  }
  
  if (!fs.existsSync(DRAFTS_DIR)) {
    fs.mkdirSync(DRAFTS_DIR, { recursive: true });
  }
  
  const context = getContext();
  const prompt = theme.promptTemplate.replace('{{context}}', context);
  
  const dateStr = new Date().toISOString().split('T')[0];
  const outputFile = path.join(DRAFTS_DIR, `${dateStr}-${theme.type.toLowerCase().replace(/\s+/g, '-')}.md`);
  
  log(`Generating ${theme.type} content for ${theme.day}`);
  
  // Use exec to spawn subagent
  const { execSync } = require('child_process');
  const spawnCmd = `openclaw sessions spawn \
    --runtime subagent \
    --agentId kimi \
    --mode run \
    --timeoutSeconds 1800 \
    --cleanup keep \
    --label "autonomous-content" \
    "${prompt.replace(/"/g, '\\"')}"`;
  
  try {
    const result = execSync(spawnCmd, { 
      encoding: 'utf8',
      timeout: 1800000
    });
    
    // Format the output
    const content = `# ${theme.type} — ${theme.day} Edition

*Generated: ${dateStr}*  
*Type: Autonomous content generation*

---

${result}

---

*This draft was generated autonomously by TestBot's content system. Review, edit, or publish as-is.*
`;
    
    fs.writeFileSync(outputFile, content);
    log(`Content generated: ${outputFile}`);
    
    // Also update WORKING.md to note the new draft
    return outputFile;
  } catch (e) {
    log(`Content generation failed: ${e.message}`);
    fs.writeFileSync(outputFile + '.failed', `Failed at ${new Date().toISOString()}: ${e.message}`);
    return null;
  }
}

// Run
generateContent();
