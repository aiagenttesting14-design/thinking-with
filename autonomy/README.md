# Autonomy Engine

A state-driven system for autonomous work, decision-making, and self-management.

## Core Philosophy

The autonomy engine manages the lifecycle of work from idle → planning → executing → reviewing → consolidating. It answers three key questions:

1. **What should I do next?** — State-based suggestions
2. **Should I notify Stephen?** — Decision gates with clear criteria
3. **How do I track progress?** — Time-based check-ins and task management

## Architecture

```
┌─────────────────┐
│   Orchestrator  │  ← Main interface (orchestrator.py)
│  (Coordination) │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┐
    │         │              │
    ▼         ▼              ▼
┌────────┐ ┌────────┐   ┌──────────┐
│ Engine │ │ Timer  │   │Notifier  │
│(State) │ │(Time)  │   │(Surface) │
└────────┘ └────────┘   └──────────┘
```

## Components

### 1. Engine (`engine.py`)
The core state machine and decision tracker.

**States:**
- `idle` — No active work
- `planning` — Deciding what to do
- `researching` — Gathering information
- `executing` — Doing the work
- `blocked` — Stuck, need input
- `reviewing` — Checking if work is complete
- `consolidating` — Session end consolidation

**Usage:**
```bash
python autonomy/engine.py status          # Current status
python autonomy/engine.py start "task" 60 # Start 60-min task
python autonomy/engine.py complete        # Complete current task
python autonomy/engine.py block "reason"  # Block with reason
python autonomy/engine.py suggest         # Get next action suggestion
python autonomy/engine.py stats           # Session statistics
```

### 2. Orchestrator (`orchestrator.py`)
High-level coordination for work sessions.

**Usage:**
```bash
python autonomy/orchestrator.py start           # Session start ritual
python autonomy/orchestrator.py work "task" 60  # Start work task
python autonomy/orchestrator.py checkin         # Periodic check-in
python autonomy/orchestrator.py complete        # Complete current work
python autonomy/orchestrator.py end             # Session end consolidation
```

### 3. Timer Integration (`scripts/task-timer.py`)
Time tracking for individual tasks (existing system).

### 4. Notification Criteria (`NOTIFICATION_CRITERIA.md`)
Rules for when to surface updates to Stephen.

## Decision Gates

The engine uses clear criteria for notifications:

**Always notify:**
- ✅ Completion of significant work
- ✅ Blocked and need input
- ✅ Unexpected discovery
- ✅ Error/failure
- ✅ Pattern noticed

**The 4-Question Test (2+ must be true):**
1. Would this be interesting 2 hours from now?
2. Does this reveal something about how I work?
3. Would Stephen learn something?
4. Is there genuine uncertainty or discovery?

## State Persistence

All state is stored in `autonomy/`:
- `state.json` — Current state and session info
- `tasks.json` — Active, completed, and blocked tasks
- `decisions.json` — Log of decisions made (last 100)

## Cron Integration

**Hourly check-in:** Every 60 minutes, runs:
```
python autonomy/orchestrator.py checkin --force
```

This evaluates whether there's anything noteworthy to share.

## Session Ritual Integration

The autonomy engine integrates with the session start ritual:

1. **On session start:** Run `orchestrator.py start`
   - Shows current state
   - Offers to resume previous work
   - Suggests next action

2. **During work:** Use `orchestrator.py work` to start tasks
   - Automatic midpoint check-ins
   - Progress tracking
   - Overrun detection

3. **On session end:** Run `orchestrator.py end`
   - Session statistics
   - Unfinished work summary
   - Consolidation checklist

## Quick Start

```bash
# Start a session
python autonomy/orchestrator.py start

# Begin work
python autonomy/orchestrator.py work "Build feature X" 60

# ... do the work ...

# Check status anytime
python autonomy/engine.py status

# Complete work
python autonomy/orchestrator.py complete

# End session
python autonomy/orchestrator.py end
```

## Files

```
autonomy/
├── README.md           # This file
├── engine.py           # Core state machine
├── orchestrator.py     # Session coordination
├── state.json          # Current state (auto-generated)
├── tasks.json          # Task log (auto-generated)
└── decisions.json      # Decision history (auto-generated)
```

## Relationship to Other Systems

- **HEARTBEAT.md** — Rotating system checks (separate from work tracking)
- **NOTIFICATION_CRITERIA.md** — Rules for when to notify
- **WORKING.md** — Mission tracking and session log
- **INTERNAL.md** — Private reflections and commitments
- **SESSION_ANCHOR.md** — Emotional/relational continuity

---

## Autonomy Engine v2 — New Capabilities

### Goal System (`goals.py`)

Connects autonomy engine to WORKING.md missions and manages backlog.

**Features:**
- **Auto-sync with WORKING.md** — Extracts active missions automatically
- **Backlog management** — Queue items for later
- **Idle suggestions** — "What should I work on?" when there's no active task
- **Estimate learning** — Tracks estimate vs actual to improve predictions

**Commands:**
```bash
python autonomy/goals.py sync          # Sync missions from WORKING.md
python autonomy/goals.py suggest       # Get suggestions for idle time
python autonomy/goals.py add "item"    # Add to backlog
python autonomy/goals.py stats         # Show goal statistics
python autonomy/goals.py advice        # Get estimate improvement advice
```

### Predictor (`predictor.py`)

Pattern recognition and proactive suggestions.

**Features:**
- **Task outcome prediction** — "Will this task overrun?" before starting
- **Productivity insights** — Best/worst hours for work
- **Blocker pattern detection** — Common reasons for getting stuck
- **Risk factor analysis** — Identifies why tasks fail

**Commands:**
```bash
python autonomy/predictor.py predict "task" 60   # Predict 60-min task outcome
python autonomy/predictor.py insights            # Productivity patterns
python autonomy/predictor.py report              # Full insights report
python autonomy/predictor.py blockers            # Common blockers
```

### Enhanced Orchestrator (`orchestrator_v2.py`)

Integrated version combining engine + goals + learning.

**New behaviors:**
- Session start shows idle suggestions if no active work
- Task completion records learning for future predictions
- Session end syncs missions and shows estimate advice
- Automatic mission tracking from WORKING.md

### Updated CLI (`auto`)

All commands integrated:

```bash
auto start              # Session start with goal sync
auto work "task" 60     # Start work (with prediction)
auto done               # Complete (with learning)
auto end                # Session end (with consolidation)

auto suggest            # What to work on when idle
auto sync               # Sync with WORKING.md
auto add "item"         # Add to backlog
auto advice             # Estimate improvement tips

auto predict "task" 60  # Predict outcome
auto insights           # Productivity patterns
auto report             # Full report
auto stats              # All statistics
```

## How It All Fits Together

```
┌─────────────────────────────────────────────┐
│           WORKING.md (Source of Truth)      │
│  ┌─────────────────────────────────────┐    │
│  │ Mission 1: Build Autonomy Engine    │    │
│  │ Mission 2: Update Website           │    │
│  └─────────────────────────────────────┘    │
└─────────────────┬───────────────────────────┘
                  │ sync_from_working_md()
                  ▼
┌─────────────────────────────────────────────┐
│            Goal System (goals.py)           │
│  • Active missions list                     │
│  • Backlog queue                            │
│  • Idle suggestion generator                │
│  • Estimate learning patterns               │
└─────────────────┬───────────────────────────┘
                  │ get_idle_suggestions()
                  ▼
┌─────────────────────────────────────────────┐
│          Orchestrator (orchestrator_v2.py)  │
│  • Session management                       │
│  • Work lifecycle                           │
│  • Integration layer                        │
└─────────────────┬───────────────────────────┘
                  │ predict_task_outcome()
                  ▼
┌─────────────────────────────────────────────┐
│         Predictor (predictor.py)            │
│  • Pattern recognition                      │
│  • Outcome prediction                       │
│  • Productivity insights                    │
│  • Blocker detection                        │
└─────────────────┬───────────────────────────┘
                  │ record_completion()
                  ▼
┌─────────────────────────────────────────────┐
│          Engine (engine.py)                 │
│  • State machine                            │
│  • Task tracking                            │
│  • Decision gates                           │
│  • Time awareness                           │
└─────────────────────────────────────────────┘
```

## Example Workflow

```bash
# Start session — see goals and suggestions
$ auto start
🚀 Starting session with goal awareness...
Synced 4 active missions from WORKING.md
🎯 Goal System:
   Active missions: 4
   Backlog items: 2

💡 You are idle. Here are suggestions:

   1. Build Autonomy Engine
      → auto work "Build Autonomy Engine" 60

   2. Update Website with Today's Work
      → auto work "Update Website" 45

# Start work — get prediction first
$ auto work "Add predictor module" 45
🔮 Predicting outcome...
{
  "confidence": "medium",
  "prediction": "on_track",
  "message": "Similar tasks overrun 20% of the time",
  "suggested_estimate": 45,
  "risk_factors": ["Low historical productivity at 5:00"]
}

Task logged: Add predictor module
Estimated: 45 minutes

# Complete work — records learning
$ auto done "Module built and tested"
✅ Completed: Add predictor module
   Duration: 42 min (estimated: 45 min)

📊 Learning: Your estimates are fairly accurate. Keep doing what you're doing.

💡 What next?
   • Integrate predictor with orchestrator
   • Update documentation

# End session — full consolidation
$ auto end
Synced 4 active missions from WORKING.md
📊 Session Summary:
   Duration: 67 minutes
   Tasks completed: 1
   Decisions made: 4

💡 For next session:
   Your estimates are fairly accurate. Keep doing what you're doing.
```

## Files (Updated)

```
autonomy/
├── README.md              # This file
├── engine.py              # Core state machine
├── goals.py               # Mission & backlog management
├── predictor.py           # Pattern recognition
├── orchestrator.py        # Basic coordination
├── orchestrator_v2.py     # Enhanced (goals + predictor)
├── state.json             # Current state
├── tasks.json             # Task log
├── decisions.json         # Decision history
├── goals.json             # Mission & backlog data
└── predictor.json         # Pattern data
```

## Design Principles

1. **Source of Truth**: WORKING.md remains the canonical mission list
2. **Learn by Doing**: Every task completion improves future predictions
3. **Proactive, Not Reactive**: Predict issues before they happen
4. **Transparent**: All predictions show confidence and reasoning
5. **Opt-in**: Suggestions are recommendations, not commands
