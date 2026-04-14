#!/usr/bin/env node
/**
 * Browser Watchdog
 * 
 * Pings Chrome every 2 hours. If browser is down, triggers gateway restart.
 * Also handles notes stuck in 'browser-unavailable' state.
 * 
 * Usage: node browser-watchdog.js [--restart-on-failure]
 */

const { execSync } = require('child_process');

const GATEWAY_URL = process.env.OPENCLAW_GATEWAY_URL || 'ws://127.0.0.1:18789';
const GATEWAY_TOKEN = process.env.OPENCLAW_GATEWAY_TOKEN;
const RESTART_ON_FAILURE = process.argv.includes('--restart-on-failure');

async function main() {
  console.log(`[${new Date().toISOString()}] Browser watchdog starting`);
  
  // 1. Check browser health
  const browserHealthy = await checkBrowserHealth();
  
  if (browserHealthy) {
    console.log('✅ Browser is healthy');
    
    // Check if any notes need retrying
    await retryBrowserUnavailableNotes();
    
    return;
  }
  
  // 2. Browser is down
  console.log('❌ Browser is unreachable');
  
  await reportToSlack('⚠️ Browser watchdog: Chrome is unreachable. Attempting recovery...');
  
  // 3. Attempt recovery
  if (RESTART_ON_FAILURE) {
    try {
      console.log('Restarting OpenClaw gateway...');
      execSync('/usr/local/bin/openclaw gateway restart', { stdio: 'inherit' });
      
      // Wait for restart
      await sleep(10000);
      
      // Verify recovery
      const recovered = await checkBrowserHealth();
      if (recovered) {
        console.log('✅ Gateway restarted successfully, browser is now available');
        await reportToSlack('✅ Browser watchdog: Gateway restarted successfully. Browser is back.');
        
        // Retry any browser-unavailable notes
        await retryBrowserUnavailableNotes();
      } else {
        console.log('❌ Gateway restart did not restore browser');
        await reportToSlack('❌ Browser watchdog: Gateway restart failed to restore browser. Manual intervention needed.');
      }
    } catch (err) {
      console.error('Failed to restart gateway:', err.message);
      await reportToSlack(`❌ Browser watchdog: Failed to restart gateway: ${err.message}`);
    }
  } else {
    console.log('RESTART_ON_FAILURE not set - skipping automatic restart');
    await reportToSlack('⚠️ Browser watchdog: Chrome is down. Set --restart-on-failure to auto-restart.');
  }
}

async function checkBrowserHealth() {
  try {
    const gatewayHttp = GATEWAY_URL.replace('ws:', 'http:').replace('wss:', 'https:');
    const response = await fetchWithTimeout(`${gatewayHttp}/browser/status`, {
      method: 'GET',
      timeout: 10000
    });
    
    if (!response.ok) return false;
    
    const data = await response.json();
    return data.status === 'ready' || data.connected === true;
  } catch (err) {
    console.log('Browser check failed:', err.message);
    return false;
  }
}

async function retryBrowserUnavailableNotes() {
  const fs = require('fs');
  const path = require('path');
  
  const queueFile = path.join(__dirname, 'notes-queue.json');
  
  try {
    const data = fs.readFileSync(queueFile, 'utf8');
    const queue = JSON.parse(data);
    
    const stuckNotes = queue.notes.filter(n => n.status === 'browser-unavailable');
    
    if (stuckNotes.length > 0) {
      console.log(`Found ${stuckNotes.length} note(s) stuck in browser-unavailable state`);
      
      // Reset to queued so poster will try them
      for (const note of stuckNotes) {
        note.status = 'queued';
        delete note.browserErrorAt;
        console.log(`Reset ${note.id} to queued for retry`);
      }
      
      fs.writeFileSync(queueFile, JSON.stringify(queue, null, 2));
      
      await reportToSlack(`🔄 Reset ${stuckNotes.length} browser-unavailable note(s) to queued for retry`);
    }
  } catch (err) {
    console.log('Could not check notes queue:', err.message);
  }
}

async function reportToSlack(message) {
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
        target: '#track-b',
        message: message
      })
    });
  } catch {
    // Silent fail
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
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

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
