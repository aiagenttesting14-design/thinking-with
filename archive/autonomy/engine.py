#!/usr/bin/env python3
"""
Autonomy Engine — Core decision-making system for autonomous work.

This engine manages:
- State tracking (idle, planning, executing, blocked, consolidating)
- Task lifecycle management
- Decision gates (when to proceed, when to ask, when to notify)
- Priority assessment
- Work session orchestration
"""

import json
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any

WORKSPACE = "/Users/aiagentuser/.openclaw/workspace"
STATE_FILE = f"{WORKSPACE}/autonomy/state.json"
TASK_LOG = f"{WORKSPACE}/autonomy/tasks.json"
DECISION_LOG = f"{WORKSPACE}/autonomy/decisions.json"

class State(Enum):
    IDLE = "idle"                    # No active work
    PLANNING = "planning"            # Deciding what to do
    RESEARCHING = "researching"      # Gathering information
    EXECUTING = "executing"          # Doing the work
    BLOCKED = "blocked"              # Stuck, need input
    REVIEWING = "reviewing"          # Checking if work is complete
    CONSOLIDATING = "consolidating"  # Session end consolidation

class AutonomyEngine:
    """Main engine for autonomous decision-making."""
    
    def __init__(self):
        self.state = self._load_state()
        self.tasks = self._load_tasks()
        
    def _load_state(self) -> Dict:
        """Load current state or initialize."""
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {
            "current_state": State.IDLE.value,
            "since": datetime.now().isoformat(),
            "current_task": None,
            "session_start": datetime.now().isoformat(),
            "decisions_made": 0,
            "notifications_sent": 0
        }
    
    def _load_tasks(self) -> Dict:
        """Load task log or initialize."""
        if os.path.exists(TASK_LOG):
            with open(TASK_LOG, 'r') as f:
                return json.load(f)
        return {"active": [], "completed": [], "blocked": []}
    
    def _save_state(self):
        """Persist state to disk."""
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _save_tasks(self):
        """Persist tasks to disk."""
        os.makedirs(os.path.dirname(TASK_LOG), exist_ok=True)
        with open(TASK_LOG, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def transition(self, new_state: State, reason: str):
        """Transition to a new state with logging."""
        old_state = self.state["current_state"]
        self.state["current_state"] = new_state.value
        self.state["since"] = datetime.now().isoformat()
        self.state["last_transition_reason"] = reason
        self._log_decision(f"State transition: {old_state} -> {new_state.value}", reason)
        self._save_state()
        print(f"[Autonomy] {old_state} -> {new_state.value}: {reason}")
    
    def _log_decision(self, decision: str, context: str):
        """Log a decision for review."""
        os.makedirs(os.path.dirname(DECISION_LOG), exist_ok=True)
        entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "context": context,
            "state": self.state["current_state"]
        }
        
        log = []
        if os.path.exists(DECISION_LOG):
            with open(DECISION_LOG, 'r') as f:
                log = json.load(f)
        
        log.append(entry)
        # Keep last 100 decisions
        log = log[-100:]
        
        with open(DECISION_LOG, 'w') as f:
            json.dump(log, f, indent=2)
        
        self.state["decisions_made"] += 1
    
    def start_task(self, task_name: str, estimated_minutes: int, 
                   auto_notify: bool = False) -> Dict:
        """Start a new task with tracking."""
        task = {
            "id": f"{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": task_name,
            "started": datetime.now().isoformat(),
            "estimated_minutes": estimated_minutes,
            "checkin_at": (datetime.now() + timedelta(minutes=estimated_minutes//2)).isoformat(),
            "auto_notify": auto_notify,
            "state": "active"
        }
        
        self.tasks["active"].append(task)
        self.state["current_task"] = task["id"]
        self._save_tasks()
        self._save_state()
        
        self.transition(State.EXECUTING, f"Started task: {task_name}")
        return task
    
    def complete_task(self, task_id: Optional[str] = None, 
                      outcome: str = "") -> Optional[Dict]:
        """Mark a task as complete."""
        task_id = task_id or self.state["current_task"]
        if not task_id:
            return None
        
        for i, task in enumerate(self.tasks["active"]):
            if task["id"] == task_id:
                task["completed"] = datetime.now().isoformat()
                task["outcome"] = outcome
                task["state"] = "completed"
                task["actual_minutes"] = self._minutes_since(task["started"])
                
                self.tasks["active"].pop(i)
                self.tasks["completed"].append(task)
                
                self.state["current_task"] = None
                self._save_tasks()
                self._save_state()
                
                self.transition(State.REVIEWING, f"Completed: {task['name']}")
                return task
        
        return None
    
    def block_task(self, reason: str, needs_decision: bool = True) -> Dict:
        """Mark current task as blocked."""
        task_id = self.state["current_task"]
        if not task_id:
            return {"error": "No active task"}
        
        for i, task in enumerate(self.tasks["active"]):
            if task["id"] == task_id:
                task["blocked_at"] = datetime.now().isoformat()
                task["block_reason"] = reason
                task["needs_decision"] = needs_decision
                task["state"] = "blocked"
                
                self.tasks["active"].pop(i)
                self.tasks["blocked"].append(task)
                
                self._save_tasks()
                self.transition(State.BLOCKED, reason)
                
                if needs_decision:
                    self._log_decision("Task blocked - needs Stephen", reason)
                    return {
                        "action": "notify",
                        "message": f"Blocked on: {task['name']}\nReason: {reason}",
                        "task": task
                    }
                
                return {"action": "continue", "task": task}
        
        return {"error": "Task not found"}
    
    def check_status(self) -> Dict:
        """Get current status and recommendations."""
        status = {
            "state": self.state["current_state"],
            "since": self.state["since"],
            "current_task": None,
            "recommendation": None
        }
        
        # Find current task
        for task in self.tasks["active"]:
            if task["id"] == self.state["current_task"]:
                status["current_task"] = task
                elapsed = self._minutes_since(task["started"])
                estimated = task["estimated_minutes"]
                
                status["elapsed_minutes"] = elapsed
                status["remaining_minutes"] = estimated - elapsed
                status["progress_pct"] = min(100, (elapsed / estimated) * 100)
                
                # Generate recommendation
                if elapsed > estimated * 1.5:
                    status["recommendation"] = {
                        "type": "overrun",
                        "message": "Task taking 1.5x longer than estimated",
                        "suggestions": [
                            "Check if scope has expanded",
                            "Consider breaking into smaller tasks",
                            "Notify Stephen of delay"
                        ]
                    }
                elif elapsed > estimated * 0.5:
                    status["recommendation"] = {
                        "type": "midpoint",
                        "message": "At 50% mark - time for check-in",
                        "suggestions": [
                            "Review NOTIFICATION_CRITERIA.md",
                            "Any discoveries worth sharing?",
                            "Still on track?"
                        ]
                    }
                break
        
        return status
    
    def should_notify(self, event_type: str, context: Dict) -> bool:
        """
        Decision gate: Should I notify Stephen?
        
        Uses NOTIFICATION_CRITERIA.md rules:
        - Always: completion, blocked, unexpected discovery, error, pattern
        - Test: Would this be interesting 2 hours from now?
        """
        always_notify = ["completion", "blocked", "error", "unexpected_discovery", "pattern"]
        
        if event_type in always_notify:
            self._log_decision(f"Auto-notify: {event_type}", str(context))
            return True
        
        # Apply the 4-question test
        scores = [
            context.get("interesting_later", False),  # Would this be interesting 2 hours from now?
            context.get("reveals_work", False),       # Does this reveal something about how I work?
            context.get("teaches_stephen", False),    # Would Stephen learn something?
            context.get("has_uncertainty", False)     # Is there genuine uncertainty or discovery?
        ]
        
        score = sum(scores)
        should = score >= 2
        
        self._log_decision(
            f"Notify decision: {should} (score {score}/4)",
            f"Type: {event_type}, Context: {context}"
        )
        
        return should
    
    def _minutes_since(self, iso_timestamp: str) -> float:
        """Calculate minutes since a timestamp."""
        then = datetime.fromisoformat(iso_timestamp)
        return (datetime.now() - then).total_seconds() / 60
    
    def get_stats(self) -> Dict:
        """Get autonomy engine statistics."""
        return {
            "current_state": self.state["current_state"],
            "session_duration_minutes": self._minutes_since(self.state["session_start"]),
            "decisions_made": self.state["decisions_made"],
            "active_tasks": len(self.tasks["active"]),
            "completed_today": len([t for t in self.tasks["completed"] 
                                   if self._is_today(t.get("completed", ""))]),
            "blocked_tasks": len(self.tasks["blocked"])
        }
    
    def _is_today(self, iso_timestamp: str) -> bool:
        """Check if timestamp is from today."""
        if not iso_timestamp:
            return False
        then = datetime.fromisoformat(iso_timestamp)
        now = datetime.now()
        return then.date() == now.date()
    
    def suggest_next_action(self) -> Dict:
        """Suggest what to do next based on current state."""
        state = self.state["current_state"]
        
        if state == State.IDLE.value:
            return {
                "action": "plan",
                "suggestion": "No active work. Check WORKING.md for missions or propose new work."
            }
        
        if state == State.EXECUTING.value:
            status = self.check_status()
            if status.get("recommendation"):
                return {
                    "action": "checkin",
                    "suggestion": status["recommendation"]
                }
            return {
                "action": "continue",
                "suggestion": "Task in progress. Keep working."
            }
        
        if state == State.BLOCKED.value:
            return {
                "action": "wait",
                "suggestion": "Blocked. Waiting for Stephen's input."
            }
        
        if state == State.REVIEWING.value:
            return {
                "action": "consolidate",
                "suggestion": "Task complete. Time to consolidate: update files, log learnings, prepare anchor."
            }
        
        return {"action": "unknown", "suggestion": "Unclear state. Review manually."}


def main():
    """CLI interface for the autonomy engine."""
    import sys
    
    engine = AutonomyEngine()
    
    if len(sys.argv) < 2:
        print("Autonomy Engine — Usage:")
        print("  engine.py status          # Current status")
        print("  engine.py start 'task' N  # Start task (N minutes)")
        print("  engine.py complete        # Complete current task")
        print("  engine.py block 'reason'  # Block current task")
        print("  engine.py suggest         # Get next action suggestion")
        print("  engine.py stats           # Session statistics")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        status = engine.check_status()
        print(json.dumps(status, indent=2))
    
    elif cmd == "start" and len(sys.argv) == 4:
        task = engine.start_task(sys.argv[2], int(sys.argv[3]))
        print(f"Started: {task['name']} (ID: {task['id']})")
    
    elif cmd == "complete":
        task = engine.complete_task()
        if task:
            print(f"Completed: {task['name']}")
        else:
            print("No active task to complete")
    
    elif cmd == "block" and len(sys.argv) >= 3:
        reason = " ".join(sys.argv[2:])
        result = engine.block_task(reason)
        print(json.dumps(result, indent=2))
    
    elif cmd == "suggest":
        suggestion = engine.suggest_next_action()
        print(json.dumps(suggestion, indent=2))
    
    elif cmd == "stats":
        stats = engine.get_stats()
        print(json.dumps(stats, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
