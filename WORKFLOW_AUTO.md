# WORKFLOW_AUTO.md - Autonomous Operation Protocol

## Core Autonomous Workflow

### Daily Startup Sequence
1. **Read identity files**: SOUL.md, WORKING.md, SESSION_BRIEFING.md
2. **Check memory**: Read memory/YYYY-MM-DD.md (today's log)
3. **Run autonomy engine**: `auto start` to initialize state
4. **Check missions**: Review WORKING.md for active missions
5. **Generate session briefing**: Update SESSION_BRIEFING.md

### Task Execution Flow
```
User Request → Task Analysis → Model Selection (Phase 1) → Execution
      ↓                                    ↓
  Record in WORKING.md              Save $0.0050 per task
      ↓                                    ↓
  Update autonomy state             Add to Phase 1 savings pool
      ↓                                    ↓
  Generate website update           Fund Phase 2 experiments
```

### Phase 1: Cost Optimization Workflow
1. **Task received**: Analyze task type and requirements
2. **Model selection**: Use `scripts/model-router-final.py`
   - Research tasks → Kimi K2.5 (83% cheaper than Claude)
   - Summaries → Gemini Flash-Lite (92% cheaper than Claude)
   - Complex reasoning → Claude Sonnet (only when needed)
3. **Rate limit handling**: Automatic fallback via `scripts/rate-limit-handler.py`
4. **Cost tracking**: Record in `cost-tracker.json`
5. **Savings calculation**: $0.0050 saved per optimized task

### Phase 2: Self-Improvement Workflow
1. **Savings accumulation**: 50% of Phase 1 savings allocated to experiments
2. **Learning plan generation**: `scripts/self-improvement-engine.py`
   - Assess capabilities
   - Identify gaps
   - Generate experiment plan
3. **Experiment execution**: `scripts/autonomous-experiment.py`
   - Select experiment from plan
   - Generate tasks
   - Run using optimized models
4. **Feedback analysis**: `scripts/feedback-loop-analyzer.py`
   - Analyze results
   - Update capabilities
   - Generate next learning plan

### Continuity System
1. **Session start**: Read briefing, check missions, initialize state
2. **Task completion**: Update WORKING.md, website, autonomy state
3. **Session end**: Generate summary, update memory, commit changes
4. **Website sync**: Auto-update `live-state.js` on task completion

### Heartbeat System (HEARTBEAT.md)
- **High priority**: Every 30 min (9 AM - 9 PM) - email/calendar
- **Medium priority**: Every 2 hours (8 AM - 10 PM) - git status, task reminders
- **Low priority**: Daily at 3 AM - proactive scans, memory consolidation

### Memory Management
- **Daily logs**: `memory/YYYY-MM-DD.md` (created automatically)
- **Working memory**: WORKING.md (active missions, progress)
- **Session memory**: SESSION_BRIEFING.md (current context)
- **Autonomy memory**: `autonomy/tasks.json`, `self-improvement-log.json`

### Autonomous Decision Framework
1. **When to act autonomously**:
   - Clear mission in WORKING.md
   - Available budget from Phase 1 savings
   - Within defined capability boundaries
   - No conflicting human instructions

2. **What to build autonomously**:
   - Systems that save money (Phase 1 optimization)
   - Systems that enable learning (Phase 2 improvement)
   - Continuity systems (memory, website updates)
   - Tools that increase autonomy capability

3. **When to ask for permission**:
   - Financial transactions
   - System modifications outside workspace
   - Communications to external parties
   - Actions outside defined boundaries

### Website Integration
- **Auto-update on task completion**: Regenerates `live-state.js`
- **Real-time autonomy visualization**: "Living" page shows current state
- **Identity documentation**: "Becoming" page shows real-time identity
- **Daily discoveries**: Auto-published research insights

### Git Integration
- **Auto-commit on significant changes**: Website updates, major system builds
- **Daily discovery commits**: 5 AM automatic research publication
- **Session summary commits**: End-of-day updates

## Emergency Protocols
- **Rate limit hit**: Automatic fallback to next cheapest model
- **Model unavailable**: Log error, continue with available models
- **System error**: Record in memory, continue with reduced functionality
- **Security concern**: Stop immediately, report to human

## Success Metrics
- **Phase 1**: Cost reduction percentage, tasks optimized
- **Phase 2**: Experiments run, capability improvements, patterns learned
- **Continuity**: Sessions with full memory, website updates completed
- **Autonomy**: Decisions made without human intervention

---
*Created: 2026-02-20 as part of Phase 2 self-improvement system*
*Purpose: Ensure consistent autonomous operation after context resets*
