# Job Dependency Map — March 7, 2026
*Which jobs depend on outputs from other jobs? What breaks if one fails?*

## Overview
This document maps dependencies between the 20 autonomous system jobs. Understanding these dependencies is critical for:
- **Failure impact analysis**: What breaks when job X fails?
- **Recovery sequencing**: What order to restart jobs after system failure?
- **Load distribution**: Which jobs can run in parallel vs. sequentially?
- **System resilience**: Where are single points of failure?

## Dependency Categories

### 1. Sequential Dependencies (Hard Dependencies)
Jobs that **require** outputs from previous jobs to function correctly.

### 2. Data Dependencies (Soft Dependencies)  
Jobs that **use** outputs from other jobs but have fallback mechanisms.

### 3. Temporal Dependencies (Schedule-Based)
Jobs that should run in specific order based on time, not data flow.

### 4. No Dependencies (Independent)
Jobs that operate completely independently.

## Job Dependency Matrix

| Job | Depends On | Type | Impact if Dependency Fails | Fallback |
|-----|------------|------|----------------------------|----------|
| **thinking-practice** (12 PM) | **thinking-learn** (9 AM) | Sequential | Practice has no learning to apply → empty practice file | Use yesterday's learning |
| **thinking-reflect** (3 PM) | **thinking-practice** (12 PM) | Sequential | Reflection has no practice to assess → shallow reflection | Reflect on learning only |
| **thinking-consolidate** (9 PM) | **thinking-reflect** (3 PM) | Sequential | Consolidation misses today's reflection → incomplete memory | Consolidate learning + practice only |
| **thinking-consolidate** (9 PM) | **thinking-create** (6 PM) | Data | Creative work not published to website → website stale | Publish existing creative work |
| **ops-evening-retrospective** (10 PM) | **thinking-consolidate** (9 PM) | Data | Retrospective has incomplete daily data → inaccurate assessment | Use partial consolidation data |
| **daily-track-update-for-stephen** (8:30 PM) | **thinking-reflect** (3 PM) | Data | Evening report missing reflection → incomplete progress picture | Report learning + practice only |
| **morning-progress-report-for-stephen** (8:30 AM) | **ops-evening-retrospective** (10 PM) | Data | Morning report uses stale retrospective → outdated status | Use yesterday's consolidated data |
| **task-runner** (hourly) | **ops-check-stale-tasks** (11 AM) | Temporal | Task-runner may work on stale tasks → inefficient execution | Use last known good task state |
| **track-a-substack-content** (4 PM) | **thinking-create** (6 PM) | Data | Substack content may lack creative insights → generic content | Use learning content instead |
| **review-progress-3day** (6:30 AM every 3 days) | **ops-evening-retrospective** (10 PM) | Data | 3-day review has incomplete daily data → inaccurate trend analysis | Use available retrospective data |

## Critical Dependency Chains

### Chain 1: Thinking Cycle (Most Critical)
```
thinking-morning-wake (6 AM) → thinking-learn (9 AM) → thinking-practice (12 PM) → thinking-reflect (3 PM) → thinking-create (6 PM) → thinking-consolidate (9 PM)
```
**Impact if broken**: Entire daily thinking cycle collapses. Memory consolidation incomplete, website not updated, creative work lost.

**Failure tolerance**: Low. Each job depends on previous output.

**Recovery**: Must restart entire chain from point of failure.

### Chain 2: Progress Reporting
```
thinking-cycle (all day) → thinking-consolidate (9 PM) → ops-evening-retrospective (10 PM) → morning-progress-report-for-stephen (8:30 AM next day)
```
**Impact if broken**: Stephen receives incomplete or outdated progress reports.

**Failure tolerance**: Medium. Reports can use partial data.

**Recovery**: Can regenerate reports from consolidated data.

### Chain 3: Content Production
```
thinking-learn (9 AM) + thinking-create (6 PM) → track-a-substack-content (4 PM) → Substack publication
```
**Impact if broken**: Substack content lacks depth or creative elements.

**Failure tolerance**: Medium. Can use standalone research.

**Recovery**: Create content from available learning files.

## Single Points of Failure

### 1. thinking-consolidate (9 PM)
**Why**: Multiple jobs depend on its outputs:
- Website updates (creative.html, identity pages)
- Memory consolidation (MEMORY.md updates)
- Data for retrospective and progress reports

**Impact if fails**: Website stale, memory incomplete, reports inaccurate.

**Mitigation**: Create backup consolidation job at 10 PM.

### 2. ops-check-stale-tasks (11 AM)
**Why**: task-runner depends on its stale task detection.

**Impact if fails**: Task-runner works on stale tasks, inefficient execution.

**Mitigation**: Add stale detection to task-runner itself.

### 3. daily-internal-backup (3 AM)
**Why**: No other job backs up workspace files.

**Impact if fails**: Data loss risk if system crashes.

**Mitigation**: Add secondary backup job at different time.

## Failure Scenarios & Recovery

### Scenario 1: thinking-learn fails at 9 AM
**Immediate impact**: thinking-practice at 12 PM has nothing to apply.
**Cascade impact**: thinking-reflect at 3 PM has shallow reflection.
**Final impact**: thinking-consolidate at 9 PM has incomplete daily cycle.

**Recovery actions**:
1. thinking-practice should detect missing learning file
2. Use yesterday's learning topic
3. Log the failure for retrospective
4. Continue chain with adapted content

### Scenario 2: thinking-consolidate fails at 9 PM
**Immediate impact**: Website not updated, memory not consolidated.
**Cascade impact**: ops-evening-retrospective at 10 PM has incomplete data.
**Long-term impact**: morning-progress-report-for-stephen next day uses stale data.

**Recovery actions**:
1. Create emergency consolidation job
2. Manual website update if needed
3. Retrospective uses partial data with note
4. Next day's thinking-cycle continues normally

### Scenario 3: task-runner fails for multiple cycles
**Immediate impact**: Backlog tasks not executed.
**Cascade impact**: TASK-BACKLOG.md becomes stale, progress stalls.
**Long-term impact**: System appears "stuck" to Stephen.

**Recovery actions**:
1. ops-check-stale-tasks should detect task-runner failure
2. Alert system should notify
3. Manual intervention may be needed
4. Restart task-runner with priority on oldest tasks

## Recommendations

### 1. Add Dependency Awareness to Jobs
Each job should check if its dependencies ran successfully:
- thinking-practice should check thinking-learn output exists
- thinking-consolidate should check all thinking-cycle outputs exist
- Retrospective should check consolidation completed

### 2. Create Fallback Mechanisms
- When dependency fails, use last known good data
- Log dependency failures for analysis
- Continue execution with degraded functionality

### 3. Implement Health Checks
- Pre-job: Check dependencies met
- Post-job: Verify outputs created
- Periodic: Verify dependency chain integrity

### 4. Add Redundant Critical Paths
- Backup consolidation job
- Secondary stale task detection
- Duplicate backup job at different time

### 5. Document Recovery Procedures
For each critical dependency chain, document:
- How to detect failure
- Immediate recovery steps
- Long-term repair actions
- How to prevent recurrence

## Monitoring Requirements

### Dependency Health Metrics
1. **Dependency satisfaction rate**: % of jobs where all dependencies met
2. **Cascade failure count**: Number of jobs affected by single failure
3. **Recovery time**: Time from dependency failure to system recovery
4. **Fallback usage**: How often jobs use fallback mechanisms

### Alerting Thresholds
- **Warning**: Any job misses >1 dependency for >2 consecutive runs
- **Critical**: Critical chain (thinking-cycle) broken for >1 job
- **Emergency**: Single point of failure job fails >3 consecutive times

## Implementation Priority

### Phase 1 (This Week)
1. Add dependency checks to thinking-practice and thinking-reflect
2. Create backup consolidation job at 10 PM
3. Document recovery procedures for thinking-cycle chain

### Phase 2 (Next Week)
1. Implement dependency health metrics
2. Add alerting for cascade failures
3. Create fallback data sources for critical dependencies

### Phase 3 (Ongoing)
1. Regularly review and update dependency map
2. Test failure scenarios and recovery procedures
3. Optimize dependency chains for resilience

## Conclusion
The system has **moderate dependency risk** with:
- 3 critical dependency chains
- 2 single points of failure  
- Limited fallback mechanisms
- No dependency health monitoring

**Immediate action**: Add dependency checks to thinking-practice and create backup consolidation job.

**Long-term goal**: Build resilient system where single job failures don't cascade through entire system.

---
*Created: 2026-03-07 7:15 AM by task-runner executing B07*
*Next review: 2026-03-14 (weekly dependency audit)*
