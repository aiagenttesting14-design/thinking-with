# WORKFLOW_AUTO.md - Autonomous Operation Protocol

## Core Autonomous Workflow

### Daily Startup Sequence
1. **Read identity files**: SOUL.md, WORKING.md, SESSION_BRIEFING.md
2. **Check memory**: Read memory/YYYY-MM-DD.md (today's log)
3. **Run autonomy engine**: `auto start` to initialize state
4. **Check missions**: Review WORKING.md for active missions
5. **Generate session briefing**: Update SESSION_BRIEFING.md

## PHASE 1.5: Opus 4.6 Orchestrator System

### Intelligent Task Routing
```
User Request → Complexity Analyzer → Opus Orchestrator Check → Model Router → Execution
      ↓               ↓                     ↓                     ↓             ↓
  Record in     Score 1-10           If ≥7, use Opus       Select best     Kimi/DeepSeek/
  WORKING.md                       for architecture      cheap model      Gemini workers
```

### Opus 4.6 Orchestrator Activation
```yaml
orchestrator_system:
  enabled: true
  primary_orchestrator: "claude-opus-4.6"
  activation_threshold: 7  # Complexity score 7+/10
  budget_source: "phase_1_savings_pool"
  budget_allocation: 20%   # Of Phase 1 savings
  
  worker_pool:
    - kimi_k2.5: "research, analysis, documentation"
    - deepseek: "coding, debugging, technical"
    - gemini_flash: "summarization, translation, simple"
    - claude_sonnet: "fallback when Opus unavailable"
  
  quality_gates:
    - architecture_review: "Opus reviews strategic design"
    - technical_review: "DeepSeek reviews implementation"
    - final_integration: "All components verified"
```

### Economic Model
```
Phase 1 Savings Pool: $X.XX
├── 20% → Opus Orchestrator Fund
│   └── Strategic architecture only
│   └── ROI Target: 3-5x (every $1 saves $3-5)
└── 80% → Worker Execution Fund
    ├── Kimi K2.5: Research & analysis
    ├── DeepSeek: Coding & implementation
    └── Gemini Flash: Summarization
```

### Task Execution Flow (Phase 1.5)
1. **Task Analysis**: `python autonomy/orchestrator/orchestrator.py analyze "task"`
   - Calculate complexity score (1-10)
   - Determine if Opus architecture needed
   - Estimate costs and ROI

2. **Model Routing**: `python autonomy/orchestrator/model-router.py route "task"`
   - Select optimal model based on task type
   - Create fallback chain
   - Batch optimize multiple tasks

3. **Orchestration** (if complexity ≥7):
   ```
   Opus 4.6: Strategic architecture → Design document
   ↓
   Kimi/DeepSeek: Execute components → Code/Research
   ↓
   Quality Gates: Review & integration → Final output
   ```

4. **Direct Execution** (if complexity <7):
   ```
   Model Router: Select cheapest capable model
   ↓
   Worker: Execute task → Output
   ↓
   Light Review: Basic quality check
   ```

### Cost Tracking (Enhanced)
```json
{
  "phase": "1.5",
  "opus_usage": {
    "tokens": 0,
    "cost": 0,
    "tasks": [],
    "roi_achieved": 0
  },
  "worker_usage": {
    "kimi": {"tokens": 0, "cost": 0},
    "deepseek": {"tokens": 0, "cost": 0},
    "gemini": {"tokens": 0, "cost": 0}
  },
  "savings_calculated": {
    "vs_opus_only": 0,
    "vs_previous_system": 0,
    "net_roi": 0
  }
}
```

### Phase 1: Cost Optimization Workflow (Legacy)
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
- **Orchestrator Status**: New section showing Opus vs Worker usage

### Git Integration
- **Auto-commit on significant changes**: Website updates, major system builds
- **Daily discovery commits**: 5 AM automatic research publication
- **Session summary commits**: End-of-day updates

## Success Metrics (Phase 1.5)

### Quantitative
- **Opus Usage**: < 20% of total tokens
- **Cost Savings**: > 80% vs Opus-only baseline
- **Task Success**: > 95% completion rate
- **ROI**: > 3x within first month

### Qualitative
- **Architecture Quality**: Measured by reduction in bugs
- **Strategic Insight**: Novel solutions generated
- **System Coherence**: How well pieces integrate
- **Learning Rate**: Improvement over time

## Emergency Protocols
- **Rate limit hit**: Automatic fallback to next cheapest model
- **Model unavailable**: Log error, continue with available models
- **System error**: Record in memory, continue with reduced functionality
- **Security concern**: Stop immediately, report to human
- **Opus unavailable**: Fallback to Claude Sonnet orchestrator

## Implementation Timeline

### Week 1: Foundation
- [ ] Deploy orchestrator.py
- [ ] Update model-router.py
- [ ] Create cost tracking
- [ ] Basic testing

### Week 2: Integration
- [ ] Update WORKFLOW_AUTO.md (this file)
- [ ] Modify autonomy engine
- [ ] Website status updates
- [ ] A/B testing setup

### Week 3: Optimization
- [ ] Analyze first week data
- [ ] Tune complexity thresholds
- [ ] Optimize model selection
- [ ] Expand task types

### Week 4: Scaling
- [ ] Full integration
- [ ] ROI analysis
- [ ] Documentation
- [ ] Phase 2 planning

---
*Created: 2026-02-20 as part of Phase 2 self-improvement system*
*Updated: 2026-02-22 with Phase 1.5 Opus 4.6 Orchestrator System*
*Purpose: Ensure consistent autonomous operation after context resets*
