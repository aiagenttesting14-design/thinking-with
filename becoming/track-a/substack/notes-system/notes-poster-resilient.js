#!/usr/bin/env node
/**
 * Resilient Substack Notes Poster
 * 
 * Uses minimal browser evaluate (one JS fetch call) instead of full automation.
 * If browser is unavailable, marks notes as 'browser-unavailable' for retry.
 * 
 * Usage: node notes-poster-resilient.js [--dry-run]
 */

const fs = require('fs');
const path = require('path');

// Configuration
const QUEUE_FILE = path.join(__dirname, 'notes-queue.json');
const COOKIES_FILE = path.join(__dirname, 'substack-cookies.txt');
const SUBSTACK_USER_ID = '468193559';

// Browser gateway config
const GATEWAY_URL = process.env.OPENCLAW_GATEWAY_URL || 'ws://127.0.0.1:18789';
const GATEWAY_TOKEN = process.env.OPENCLAW_GATEWAY_TOKEN;

async function main() {
  const dryRun = process.argv.includes('--dry-run');
  
  console.log(`[${new Date().toISOString()}] Notes poster starting${dryRun ? ' (DRY RUN)' : ''}`);
  
  // Read queue
  const queue = readQueue();
  if (!queue) {
    console.error('Failed to read queue file');
    process.exit(1);
  }
  
  // Find queued notes that are due
  const now = new Date();
  const dueNotes = queue.notes.filter(n => 
    n.status === 'queued' && 
    new Date(n.scheduledFor) <= now
  );
  
  if (dueNotes.length === 0) {
    console.log('No notes due for posting');
    return;
  }
  
  console.log(`Found ${dueNotes.length} note(s) due for posting`);
  
  // Check browser health first (lightweight)
  const browserHealthy = await checkBrowserHealth();
  
  if (!browserHealthy) {
    console.log('Browser unavailable - marking due notes for retry');
    
    // Mark notes as browser-unavailable (not failed) so they retry next window
    for (const note of dueNotes) {
      note.status = 'browser-unavailable';
      note.browserErrorAt = new Date().toISOString();
      console.log(`Marked ${note.id} as browser-unavailable`);
    }
    
    saveQueue(queue);
    
    // Report to Slack if possible
    await reportToSlack(`⚠️ Notes poster: Browser unavailable. ${dueNotes.length} note(s) queued for retry.`);
    
    process.exit(0); // Exit cleanly - this is a retryable condition
  }
  
  // Process one note (rate limiting)
  const note = dueNotes[0];
  console.log(`Posting note ${note.id}: "${note.text.substring(0, 50)}..."`);
  
  if (dryRun) {
    console.log('DRY RUN: Would post:', note.text);
    return;
  }
  
  try {
    const result = await postNoteViaBrowser(note.text);
    
    if (result.success) {
      note.status = 'posted';
      note.postedAt = new Date().toISOString();
      note.substackNoteId = result.noteId;
      delete note.browserErrorAt;
      console.log(`✅ Posted successfully: ${result.noteId}`);
      await reportToSlack(`✅ Posted Note ${note.id}: ${note.text.substring(0, 60)}...`);
    } else {
      throw new Error(result.error || 'Unknown error');
    }
  } catch (error) {
    console.error(`❌ Failed to post: ${error.message}`);
    
    // Determine if this is a browser error or API error
    if (isBrowserError(error)) {
      note.status = 'browser-unavailable';
      note.browserErrorAt = new Date().toISOString();
      await reportToSlack(`⚠️ Browser error posting ${note.id}. Will retry next window.`);
    } else {
      note.status = 'failed';
      note.error = error.message;
      note.failedAt = new Date().toISOString();
      await reportToSlack(`❌ Failed to post ${note.id}: ${error.message}`);
    }
  }
  
  saveQueue(queue);
}

function readQueue() {
  try {
    const data = fs.readFileSync(QUEUE_FILE, 'utf8');
    return JSON.parse(data);
  } catch (err) {
    console.error('Error reading queue:', err.message);
    return null;
  }
}

function saveQueue(queue) {
  try {
    fs.writeFileSync(QUEUE_FILE, JSON.stringify(queue, null, 2));
  } catch (err) {
    console.error('Error saving queue:', err.message);
  }
}

async function checkBrowserHealth() {
  try {
    // Quick health check via gateway
    const response = await fetchWithTimeout(
      `${GATEWAY_URL.replace('ws:', 'http:').replace('wss:', 'https:')}/health`,
      { method: 'GET', timeout: 5000 }
    );
    return response.ok;
  } catch {
    return false;
  }
}

async function postNoteViaBrowser(text) {
  // Use OpenClaw's browser tool via direct gateway call
  // This is the minimal-eval approach: one JS fetch, no page navigation
  
  const postScript = `
    (async () => {
      try {
        const response = await fetch('https://substack.com/api/v1/comment/feed', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({body: ${JSON.stringify(text)}})
        });
        
        if (!response.ok) {
          return {success: false, error: 'HTTP ' + response.status};
        }
        
        const data = await response.json();
        return {
          success: true, 
          noteId: data.id || data.comment?.id
        };
      } catch (e) {
        return {success: false, error: e.message};
      }
    })()
  `;
  
  // Call through OpenClaw gateway
  const gatewayHttp = GATEWAY_URL.replace('ws:', 'http:').replace('wss:', 'https:');
  
  const response = await fetch(`${gatewayHttp}/browser/eval`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${GATEWAY_TOKEN || ''}`
    },
    body: JSON.stringify({
      profile: 'openclaw',
      url: 'https://substack.com/',
      script: postScript
    })
  });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Browser eval failed: ${error}`);
  }
  
  const result = await response.json();
  return result.result || result;
}

function isBrowserError(error) {
  const browserErrors = [
    'browser service unavailable',
    'can\'t reach the openclaw browser',
    'timed out',
    'browser control service',
    'chrome not connected',
    'no browser',
    'browser eval failed'
  ];
  
  const msg = error.message.toLowerCase();
  return browserErrors.some(e => msg.includes(e));
}

async function reportToSlack(message) {
  // Best-effort Slack notification via OpenClaw message API
  try {
    const gatewayHttp = GATEWAY_URL.replace('ws:', 'http:').replace('wss:', 'https:');
    await fetch(`${gatewayHttp}/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${GATEWAY_TOKEN || ''}`
      },
      body: JSON.stringify({
        channel: 'slack',
        target: '#track-a',
        message: message
      })
    });
  } catch {
    // Silent fail - don't let Slack errors break posting
  }
}

async function fetchWithTimeout(url, options = {}) {
  const { timeout = 10000, ...fetchOptions } = options;
  
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, { ...fetchOptions, signal: controller.signal });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}

// Run
main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
