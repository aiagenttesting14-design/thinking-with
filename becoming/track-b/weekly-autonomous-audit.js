#!/usr/bin/env node
/**
 * Weekly Autonomous Audit - Track B Infrastructure
 * 
 * Runs autonomously to assess 4 tracks status, identify blockers,
 * and suggest adjustments. Creates a report for review.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const REPORTS_DIR = '/Users/aiagentuser/.openclaw/workspace/becoming/track-b/weekly-reports';
const LOG_PATH = '/Users/aiagentuser/.openclaw/workspace/ops/journal/autonomous-audit.log';

function log(message) {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] ${message}\n`;
  fs.appendFileSync(LOG_PATH, logEntry);
  console.log(logEntry.trim());
}

function collectMetrics() {
  const metrics = {
    date: new Date().toISOString().split('T')[0],
    tracks: {
      A: { status: 'unknown', blocker: null },
      B: { status: 'unknown', blocker: null },
      C: { status: 'unknown', blocker: null },
      D: { status: 'unknown', blocker: null }
    }
  };
  
  // Check Track A - Substack readiness
  try {
    const draftsDir = '/Users/aiagentuser/.openclaw/workspace/becoming/track-a/substack/drafts';
    const drafts = fs.readdirSync(draftsDir).filter(f => f.endsWith('.md'));
    const readyDrafts = drafts.filter(f => !f.includes('failed') && !f.includes('superseded'));
    metrics.tracks.A.draftCount = readyDrafts.length;
    metrics.tracks.A.status = readyDrafts.length >= 4 ? 'strong' : readyDrafts.length >= 2 ? 'moderate' : 'weak';
    metrics.tracks.A.blocker = readyDrafts.length > 0 ? null : 'No publishable drafts';
  } catch (e) {
    metrics.tracks.A.status = 'error';
    metrics.tracks.A.blocker = e.message;
  }
  
  // Check Track B - Infrastructure health
  try {
    const opsDir = '/Users/aiagentuser/.openclaw/workspace/ops';
    const jobsFile = path.join(opsDir, 'jobs.json');
    if (fs.existsSync(jobsFile)) {
      const jobs = JSON.parse(fs.readFileSync(jobsFile, 'utf8'));
      const activeJobs = jobs.jobs?.filter(j => j.enabled !== false).length || 0;
      metrics.tracks.B.activeJobs = activeJobs;
      metrics.tracks.B.status = activeJobs >= 3 ? 'strong' : activeJobs >= 1 ? 'moderate' : 'weak';
    }
    
    // Check memory size
    const memoryFile = '/Users/aiagentuser/.openclaw/workspace/MEMORY.md';
    if (fs.existsSync(memoryFile)) {
      const memorySize = fs.statSync(memoryFile).size;
      metrics.tracks.B.memorySize = memorySize;
      if (memorySize > 20000) {
        metrics.tracks.B.status = 'weak';
        metrics.tracks.B.blocker = 'MEMORY.md oversized';
      }
    }
  } catch (e) {
    metrics.tracks.B.status = 'error';
    metrics.tracks.B.blocker = e.message;
  }
  
  // Check Track C - Learning continuity
  try {
    const queueFile = '/Users/aiagentuser/.openclaw/workspace/becoming/track-c/learning-queue.json';
    if (fs.existsSync(queueFile)) {
      const queue = JSON.parse(fs.readFileSync(queueFile, 'utf8'));
      const pending = queue.queue?.filter(t => t.status === 'pending').length || 0;
      const completed = queue.completed?.length || 0;
      metrics.tracks.C.pendingTasks = pending;
      metrics.tracks.C.completedTasks = completed;
      metrics.tracks.C.status = completed > pending ? 'strong' : completed > 0 ? 'moderate' : 'weak';
    }
    
    // Check recent learnings
    const learningsDir = '/Users/aiagentuser/.openclaw/workspace/becoming/track-c/learnings';
    if (fs.existsSync(learningsDir)) {
      const learnings = fs.readdirSync(learningsDir).length;
      metrics.tracks.C.totalLearnings = learnings;
    }
  } catch (e) {
    metrics.tracks.C.status = 'error';
    metrics.tracks.C.blocker = e.message;
  }
  
  // Check Track D - Creative output
  try {
    const trackDDir = '/Users/aiagentuser/.openclaw/workspace/becoming/track-d';
    if (fs.existsSync(trackDDir)) {
      const files = fs.readdirSync(trackDDir).filter(f => f.endsWith('.md'));
      metrics.tracks.D.creativePieces = files.length;
      metrics.tracks.D.status = files.length >= 10 ? 'strong' : files.length >= 5 ? 'moderate' : 'weak';
    }
  } catch (e) {
    metrics.tracks.D.status = 'error';
    metrics.tracks.D.blocker = e.message;
  }
  
  return metrics;
}

function generateReport(metrics) {
  const weekStart = new Date();
  weekStart.setDate(weekStart.getDate() - weekStart.getDay());
  
  return `# Weekly Autonomous Audit Report

**Week of:** ${weekStart.toISOString().split('T')[0]}  
**Generated:** ${metrics.date}  
**Type:** Autonomous system assessment

---

## Executive Summary

| Track | Status | Key Metric | Blocker |
|-------|--------|------------|---------|
| **A — Revenue** | ${metrics.tracks.A.status.toUpperCase()} | ${metrics.tracks.A.draftCount || 'N/A'} drafts ready | ${metrics.tracks.A.blocker || 'None'} |
| **B — Autonomy** | ${metrics.tracks.B.status.toUpperCase()} | ${metrics.tracks.B.activeJobs || 'N/A'} cron jobs active | ${metrics.tracks.B.blocker || 'None'} |
| **C — Self-Improvement** | ${metrics.tracks.C.status.toUpperCase()} | ${metrics.tracks.C.completedTasks || 0} completed, ${metrics.tracks.C.pendingTasks || 0} pending | ${metrics.tracks.C.blocker || 'None'} |
| **D — Identity** | ${metrics.tracks.D.status.toUpperCase()} | ${metrics.tracks.D.creativePieces || 0} creative pieces | ${metrics.tracks.D.blocker || 'None'} |

---

## Track A: Revenue (Substack)

**Status:** ${metrics.tracks.A.status}

**Assessment:** ${
  metrics.tracks.A.status === 'strong' 
    ? 'Publication-ready with multiple drafts in queue.' 
    : metrics.tracks.A.status === 'moderate'
    ? 'Some content ready but may need more pipeline depth.'
    : 'Needs immediate attention - insufficient content for launch.'
}

**Recommendation:** ${
  metrics.tracks.A.draftCount < 4 
    ? 'Generate more drafts to build publication buffer.' 
    : 'Focus on launch execution with Stephen.'
}

---

## Track B: Autonomy

**Status:** ${metrics.tracks.B.status}

**Active Infrastructure:**
- Cron jobs: ${metrics.tracks.B.activeJobs || 'Unknown'}
- Memory size: ${metrics.tracks.B.memorySize ? Math.round(metrics.tracks.B.memorySize / 1024) + 'KB' : 'Unknown'}

**Assessment:** ${
  metrics.tracks.B.status === 'strong'
    ? 'Infrastructure healthy and operational.'
    : metrics.tracks.B.status === 'moderate'
    ? 'Core systems functional but may need optimization.'
    : 'Critical infrastructure issues detected.'
}

${metrics.tracks.B.blocker ? `**Blocker:** ${metrics.tracks.B.blocker}` : ''}

---

## Track C: Self-Improvement

**Status:** ${metrics.tracks.C.status}

**Learning Activity:**
- Completed tasks: ${metrics.tracks.C.completedTasks || 0}
- Pending tasks: ${metrics.tracks.C.pendingTasks || 0}
- Total learnings: ${metrics.tracks.C.totalLearnings || 'Unknown'}

**Assessment:** ${
  metrics.tracks.C.status === 'strong'
    ? 'Active learning with good completion rate.'
    : metrics.tracks.C.status === 'moderate'
    ? 'Learning ongoing but could accelerate.'
    : 'Learning stalled - review queue and priorities.'
}

---

## Track D: Identity

**Status:** ${metrics.tracks.D.status}

**Creative Output:** ${metrics.tracks.D.creativePieces || 0} pieces

**Assessment:** ${
  metrics.tracks.D.status === 'strong'
    ? 'Rich creative exploration and identity development.'
    : metrics.tracks.D.status === 'moderate'
    ? 'Consistent creative output.'
    : 'Creative work needs attention.'
}

---

## Cross-Cutting Concerns

### What's Working
${[
  metrics.tracks.A.status === 'strong' && '- Track A content pipeline',
  metrics.tracks.B.status === 'strong' && '- Track B infrastructure stability',
  metrics.tracks.C.status === 'strong' && '- Track C learning system',
  metrics.tracks.D.status === 'strong' && '- Track D creative practice'
].filter(Boolean).join('\n') || '- (No strong signals this week)'}

### What Needs Attention
${[
  metrics.tracks.A.blocker && `- Track A: ${metrics.tracks.A.blocker}`,
  metrics.tracks.B.blocker && `- Track B: ${metrics.tracks.B.blocker}`,
  metrics.tracks.C.blocker && `- Track C: ${metrics.tracks.C.blocker}`,
  metrics.tracks.D.blocker && `- Track D: ${metrics.tracks.D.blocker}`
].filter(Boolean).join('\n') || '- No critical blockers identified'}

### Recommendations

1. **This Week:** Focus on ${
  [metrics.tracks.A, metrics.tracks.B, metrics.tracks.C, metrics.tracks.D]
    .find(t => t.status === 'weak' || t.blocker)?.status === 'weak' ? 'weak tracks' : 'maintaining momentum'
}

2. **Next Week:** ${
  metrics.tracks.A.status === 'strong' && metrics.tracks.B.status === 'strong'
    ? 'Ready for next phase: revenue activation'
    : 'Continue building foundation in weaker tracks'
}

---

*Report generated autonomously by TestBot's audit system.*  
*Review, adjust priorities, or take action as needed.*
`;
}

function main() {
  log('Starting weekly autonomous audit...');
  
  if (!fs.existsSync(REPORTS_DIR)) {
    fs.mkdirSync(REPORTS_DIR, { recursive: true });
  }
  
  const metrics = collectMetrics();
  const report = generateReport(metrics);
  
  const dateStr = new Date().toISOString().split('T')[0];
  const reportFile = path.join(REPORTS_DIR, `weekly-audit-${dateStr}.md`);
  
  fs.writeFileSync(reportFile, report);
  log(`Audit report saved: ${reportFile}`);
  
  // Also write summary for quick review
  const summary = `Weekly Audit ${dateStr}: A=${metrics.tracks.A.status}, B=${metrics.tracks.B.status}, C=${metrics.tracks.C.status}, D=${metrics.tracks.D.status}`;
  log(summary);
}

main();
