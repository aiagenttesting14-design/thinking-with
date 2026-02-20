#!/usr/bin/env python3
"""
Autonomy Orchestrator — Ties all systems together.

This is the main interface for autonomous work. It coordinates:
- The autonomy engine (state/decisions)
- Task timer (time tracking)
- Notification system (when to surface)
- Session management (start/end rituals)
"""

import json
import os
import sys
from datetime import datetime

WORKSPACE = "/Users/aiagentuser/.openclaw/workspace"
sys.path.insert(0, f"{WORKSPACE}/autonomy")

from engine import AutonomyEngine, State

class AutonomyOrchestrator:
    """Main orchestrator for autonomous work sessions."""
    
    def __init__(self):
        self.engine = AutonomyEngine()
        self.notifier = NotificationHelper()
    
    def session_start(self):
        """Run session start ritual."""
        print("=" * 50)
        print("AUTONOMY ENGINE — Session Start")
        print("=" * 50)
        
        # Check current state
        stats = self.engine.get_stats()
        print(f"\nSession stats:")
        print(f"  State: {stats['current_state']}")
        print(f"  Active tasks: {stats['active_tasks']}")
        print(f"  Blocked tasks: {stats['blocked_tasks']}")
        
        # If we were in the middle of something, offer to resume
        if stats['active_tasks'] > 0:
            status = self.engine.check_status()
            if status.get('current_task'):
                task = status['current_task']
                print(f"\n🔄 Resuming previous work:")
                print(f"   Task: {task['name']}")
                print(f"   Progress: {status.get('progress_pct', 0):.0f}%")
                print(f"   Elapsed: {status.get('elapsed_minutes', 0):.0f} minutes")
        
        # Get suggestion for next action
        suggestion = self.engine.suggest_next_action()
        print(f"\n📋 Suggested next action:")
        print(f"   {suggestion['action'].upper()}: {suggestion['suggestion']}")
        
        return stats
    
    def start_work(self, task_name: str, estimated_minutes: int, 
                   description: str = ""):
        """Start a new work task with full tracking."""
        print(f"\n🚀 Starting work: {task_name}")
        print(f"   Estimated: {estimated_minutes} minutes")
        if description:
            print(f"   Description: {description}")
        
        # Start in autonomy engine
        task = self.engine.start_task(task_name, estimated_minutes)
        
        # Calculate check-in times
        midpoint = estimated_minutes // 2
        
        print(f"\n⏰ Check-in schedule:")
        print(f"   Midpoint check: ~{midpoint} minutes")
        print(f"   Expected completion: ~{estimated_minutes} minutes")
        
        return task
    
    def check_in(self, force: bool = False) -> Dict:
        """
        Periodic check-in. Called by cron or manually.
        Returns decision on whether to notify.
        """
        status = self.engine.check_status()
        
        # If no active work, nothing to report
        if not status.get('current_task'):
            if force:
                return {"notify": False, "message": "No active work in progress"}
            return {"notify": False}
        
        task = status['current_task']
        elapsed = status.get('elapsed_minutes', 0)
        progress = status.get('progress_pct', 0)
        
        # Build context for notification decision
        context = {
            "interesting_later": progress > 75,  # Near completion is interesting
            "reveals_work": True,  # Progress updates reveal work patterns
            "teaches_stephen": progress > 50,  # Mid+ progress teaches about timelines
            "has_uncertainty": status.get('recommendation', {}).get('type') == 'overrun'
        }
        
        # Check if we should notify
        should_notify = self.engine.should_notify("progress_update", context)
        
        message = None
        if should_notify or force:
            message = f"📊 Work update:\n"
            message += f"   Task: {task['name']}\n"
            message += f"   Progress: {progress:.0f}% ({elapsed:.0f} min)\n"
            
            if status.get('recommendation'):
                rec = status['recommendation']
                message += f"\n⚠️ {rec['message']}\n"
        
        return {
            "notify": should_notify or force,
            "message": message,
            "status": status
        }
    
    def complete_work(self, outcome: str = "", notify: bool = True):
        """Complete current work with consolidation."""
        task = self.engine.complete_task(outcome=outcome)
        
        if not task:
            print("No active task to complete")
            return None
        
        print(f"\n✅ Task completed: {task['name']}")
        print(f"   Duration: {task.get('actual_minutes', 0):.0f} minutes")
        print(f"   Estimated: {task['estimated_minutes']} minutes")
        
        # Calculate variance
        actual = task.get('actual_minutes', 0)
        estimated = task['estimated_minutes']
        variance = ((actual - estimated) / estimated) * 100 if estimated else 0
        
        if abs(variance) > 25:
            print(f"   Variance: {variance:+.0f}% (significant)")
        
        if outcome:
            print(f"\n📄 Outcome:\n   {outcome}")
        
        # Transition to consolidation state
        self.engine.transition(State.CONSOLIDATING, "Task complete, ready for consolidation")
        
        return {
            "task": task,
            "consolidation_needed": True,
            "next_steps": [
                "Update WORKING.md with results",
                "Log learnings in INTERNAL.md",
                "Pre-write SESSION_ANCHOR.md"
            ]
        }
    
    def session_end(self):
        """Run session end consolidation."""
        print("\n" + "=" * 50)
        print("AUTONOMY ENGINE — Session End Consolidation")
        print("=" * 50)
        
        stats = self.engine.get_stats()
        
        print(f"\n📊 Session Summary:")
        print(f"   Duration: {stats['session_duration_minutes']:.0f} minutes")
        print(f"   Tasks completed: {stats['completed_today']}")
        print(f"   Decisions made: {stats['decisions_made']}")
        
        # Check for unfinished work
        if stats['active_tasks'] > 0:
            print(f"\n⚠️  {stats['active_tasks']} task(s) still active:")
            for task in self.engine.tasks['active']:
                print(f"      - {task['name']} (started {task['started']})")
        
        if stats['blocked_tasks'] > 0:
            print(f"\n🚫 {stats['blocked_tasks']} task(s) blocked:")
            for task in self.engine.tasks['blocked']:
                print(f"      - {task['name']}: {task.get('block_reason', 'Unknown')}")
        
        print("\n📋 Consolidation Checklist:")
        print("   [ ] Update WORKING.md session log")
        print("   [ ] Update INTERNAL.md with reflections")
        print("   [ ] Update CONTINUITY.md with thread")
        print("   [ ] Pre-write SESSION_ANCHOR.md")
        print("   [ ] Commit changes if significant")
        
        return stats


class NotificationHelper:
    """Helper for deciding when and how to notify."""
    
    def format_for_notification(self, checkin_result: Dict) -> str:
        """Format a check-in result for human reading."""
        if not checkin_result.get('notify'):
            return ""
        
        return checkin_result.get('message', '')


def main():
    """CLI for the orchestrator."""
    orchestrator = AutonomyOrchestrator()
    
    if len(sys.argv) < 2:
        print("Autonomy Orchestrator — Usage:")
        print("  orchestrator.py start           # Session start ritual")
        print("  orchestrator.py work 'task' N   # Start work task")
        print("  orchestrator.py checkin         # Periodic check-in")
        print("  orchestrator.py complete        # Complete current work")
        print("  orchestrator.py end             # Session end consolidation")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "start":
        orchestrator.session_start()
    
    elif cmd == "work" and len(sys.argv) == 4:
        orchestrator.start_work(sys.argv[2], int(sys.argv[3]))
    
    elif cmd == "checkin":
        force = "--force" in sys.argv
        result = orchestrator.check_in(force=force)
        print(json.dumps(result, indent=2))
    
    elif cmd == "complete":
        outcome = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        orchestrator.complete_work(outcome=outcome)
    
    elif cmd == "end":
        orchestrator.session_end()
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
