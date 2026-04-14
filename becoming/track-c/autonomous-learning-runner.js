#!/usr/bin/env node
/**
 * Autonomous Learning Runner - Track C Daily Growth
 * 
 * This script runs via cron (9 AM daily) to execute learning tasks
 * without requiring Stephen's presence. It uses sub-agents to do
 * the actual work, then stores results for review.
 * 
 * Usage: node autonomous-learning-runner.js [task-id]
 * If no task-id provided, pulls next item from learning-queue.json
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const QUEUE_PATH = '/Users/aiagentuser/.openclaw/workspace/becoming/track-c/learning-queue.json';
const OUTPUT_DIR = '/Users/aiagentuser/.openclaw/workspace/becoming/track-c/learnings/autonomous';
const LOG_PATH = '/Users/aiagentuser/.openclaw/workspace/ops/journal/autonomous-runs.log';

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

function log(message) {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] ${message}\n`;
  fs.appendFileSync(LOG_PATH, logEntry);
  console.log(logEntry.trim());
}

function loadQueue() {
  try {
    return JSON.parse(fs.readFileSync(QUEUE_PATH, 'utf8'));
  } catch (e) {
    log(`ERROR: Could not load queue: ${e.message}`);
    process.exit(1);
  }
}

function saveQueue(queue) {
  queue.lastUpdated = new Date().toISOString().split('T')[0];
  fs.writeFileSync(QUEUE_PATH, JSON.stringify(queue, null, 2));
}

function getNextTask(queue) {
  // Get highest priority pending task
  const pending = queue.queue
    .filter(t => t.status === 'pending')
    .sort((a, b) => a.priority - b.priority);
  return pending[0] || null;
}

function generateResearchPrompt(task) {
  return `You are a research sub-agent for TestBot, an AI agent working on The Becoming System.

Your task: ${task.topic}

Context: ${task.source}
Required output: ${task.outputFormat}
Time budget: ${task.estimatedTime}

Research deeply using web search. Synthesize findings into actionable insights.
Write your response as a complete report that TestBot can use.

Be thorough but concise. Focus on practical application, not just theory.
Include specific examples, frameworks, or templates where relevant.

If the topic involves platform-specific tactics (e.g., Substack, Twitter), 
include current best practices and any relevant 2025/2026 updates.

End with a "Key Takeaways" section summarizing the 3-5 most important points.`;
}

function generatePracticePrompt(task) {
  return `You are an implementation sub-agent for TestBot, an AI agent working on The Becoming System.

Your task: ${task.topic}

Context: ${task.source}
Required output: ${task.outputFormat}
Time budget: ${task.estimatedTime}

This is a PRACTICE task - you must produce working output, not just research.
Create actual files, scripts, or deliverables that TestBot can review and use.

Focus on:
1. Working implementation over perfect theory
2. Clear documentation
3. Testability - can TestBot verify this works?

Use the write/edit/exec tools as needed to create real artifacts.
Report what you created and how to use it.`;
}

function executeViaSubagent(task) {
  const prompt = task.type === 'research' 
    ? generateResearchPrompt(task) 
    : generatePracticePrompt(task);
  
  const outputFile = path.join(OUTPUT_DIR, `${task.id}-${Date.now()}.md`);
  
  // Build the subagent spawn command
  const spawnCmd = `openclaw sessions spawn \
    --runtime subagent \
    --agentId deepseek \
    --mode run \
    --timeoutSeconds 1800 \
    --cleanup keep \
    --label "autonomous-${task.id}" \
    "${prompt.replace(/"/g, '\\"')}"`;
  
  log(`Spawning subagent for task ${task.id}: ${task.topic}`);
  
  try {
    const result = execSync(spawnCmd, { 
      encoding: 'utf8',
      timeout: 1800000 // 30 min hard timeout
    });
    
    // Write result to file
    fs.writeFileSync(outputFile, `# Autonomous Learning Run: ${task.topic}\n\n**Task ID:** ${task.id}\n**Type:** ${task.type}\n**Date:** ${new Date().toISOString()}\n**Status:** completed\n\n---\n\n${result}`);
    
    log(`Task ${task.id} completed. Output saved to: ${outputFile}`);
    return { success: true, outputFile };
  } catch (e) {
    const errorMsg = `Task ${task.id} failed: ${e.message}`;
    log(errorMsg);
    fs.writeFileSync(outputFile, `# Autonomous Learning Run: ${task.topic}\n\n**Task ID:** ${task.id}\n**Type:** ${task.type}\n**Date:** ${new Date().toISOString()}\n**Status:** failed\n**Error:** ${e.message}\n`);
    return { success: false, error: e.message };
  }
}

function main() {
  const taskId = process.argv[2];
  const queue = loadQueue();
  
  let task;
  if (taskId) {
    task = queue.queue.find(t => t.id === taskId);
    if (!task) {
      log(`ERROR: Task ${taskId} not found in queue`);
      process.exit(1);
    }
  } else {
    task = getNextTask(queue);
    if (!task) {
      log('No pending tasks in queue. Nothing to do.');
      process.exit(0);
    }
  }
  
  log(`Starting autonomous learning: ${task.id} - ${task.topic}`);
  
  // Mark as in-progress
  task.status = 'in-progress';
  queue.activeTopic = task.id;
  saveQueue(queue);
  
  // Execute
  const result = executeViaSubagent(task);
  
  // Update queue
  if (result.success) {
    task.status = 'completed';
    task.completedAt = new Date().toISOString();
    task.outputFile = result.outputFile;
    queue.completed.push(task);
    queue.queue = queue.queue.filter(t => t.id !== task.id);
    log(`Task ${task.id} moved to completed.`);
  } else {
    task.status = 'failed';
    task.failedAt = new Date().toISOString();
    task.error = result.error;
    // Keep in queue for retry
    log(`Task ${task.id} marked as failed. Will retry next run.`);
  }
  
  queue.activeTopic = null;
  saveQueue(queue);
  
  log('Autonomous learning run complete.');
}

main();
