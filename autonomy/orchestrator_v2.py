#!/usr/bin/env python3
"""
Autonomy Orchestrator v2 — Integrated with Goal System.
"""

import json
import os
import sys
from datetime import datetime

WORKSPACE = "/Users/aiagentuser/.openclaw/workspace"
sys.path.insert(0, f"{WORKSPACE}/autonomy")

from engine import AutonomyEngine, State
from goals import GoalSystem

class AutonomyOrchestratorV2:
    """Enhanced orchestrator with goal awareness."""
    
    def __init__(self):
        self.engine = AutonomyEngine()
        self.goals = GoalSystem()
    
    def session_start(self):
        """Enhanced session start with goal awareness."""
        print("=" * 60)
        print("AUTONOMY ENGINE v2 — Session Start")
        print("=" * 60)
        
        # Get engine stats
        stats = self.engine.get_stats()
        print(f"\n📊 Session Stats:")
        print(f"   State: {stats['current_state']}")
        print(f"   Active tasks: {stats['active_tasks']}")
        print(f"   Completed today: {stats['completed_today']}")
        
        # Get goal stats
        goal_stats = self.goals.get_stats()
        print(f"\n🎯 Goal System:")
        print(f"   Active missions: {goal_stats['active_missions']}")
        print(f"   Backlog items: {goal_stats['backlog_items']}")
        if goal_stats['estimate_accuracy'] != 0:
            print(f"   Estimate accuracy: {goal_stats['estimate_accuracy']:+.0f}% variance")
        
        # If idle, suggest work
        if stats['current_state'] == State.IDLE.value:
            print(f"\n💡 You are idle. Here are suggestions:\n")
            suggestions = self.goals.get_idle_suggestions(3)
            for i, s in enumerate(suggestions, 1):
                print(f"   {i}. {s['title']}")
                print(f"      → {s['action']}")
            print()
        
        # If resuming work
        elif stats['active_tasks'] > 0:
            status = self.engine.check_status()
            if status.get('current_task'):
                task = status['current_task']
                print(f"\n🔄 Resuming: {task['name']}")
                print(f"   Progress: {status.get('progress_pct', 0):.0f}%")
        
        return stats
    
    def complete_work(self, outcome: str = "", notify: bool = True):
        """Complete work with goal system learning."""
        # Get task before completing
        task_id = self.engine.state.get("current_task")
        task = None
        for t in self.engine.tasks.get("active", []):
            if t["id"] == task_id:
                task = t
                break
        
        # Complete in engine
        result = self.engine.complete_task(outcome=outcome)
        
        if not result:
            print("No active task to complete")
            return None
        
        # Record in goal system for learning
        actual = result.get("actual_minutes", 0)
        estimated = result["estimated_minutes"]
        self.goals.record_completion(
            task_name=result["name"],
            outcome=outcome,
            estimated=estimated,
            actual=int(actual)
        )
        
        
        # AUTO-UPDATE: Regenerate website live state
        print("\n🔄 Auto-updating website...")
        import subprocess
        try:
            subproc_result = subprocess.run([
                'python3', 
                '/Users/aiagentuser/.openclaw/workspace/autonomy/generate_state.py',
                'js'
            ], capture_output=True, text=True)
            if subproc_result.returncode == 0:
                print("   ✅ Website state updated")
            else:
                print(f"   ⚠️  State generation issue: {subproc_result.stderr[:100]}")
        except Exception as e:
            print(f"   ⚠️  Auto-update skipped: {e}")
        print(f"\n✅ Completed: {result['name']}")
        print(f"   Duration: {actual:.0f} min (estimated: {estimated} min)")
        
        # Show learning
        variance = ((actual - estimated) / estimated * 100) if estimated else 0
        if abs(variance) > 25:
            advice = self.goals.get_estimate_advice()
            print(f"\n📊 Learning: {advice['advice']}")
        
        # Show what's next
        print(f"\n💡 What next?")
        suggestions = self.goals.get_idle_suggestions(2)
        for s in suggestions:
            print(f"   • {s['title']}")
        
        return result
    
    def session_end(self):
        """Enhanced session end with goal sync."""
        print("\n" + "=" * 60)
        print("AUTONOMY ENGINE v2 — Session End")
        print("=" * 60)
        
        # Sync with WORKING.md
        missions = self.goals.sync_from_working_md()
        
        stats = self.engine.get_stats()
        goal_stats = self.goals.get_stats()
        
        print(f"\n📊 Session Summary:")
        print(f"   Duration: {stats['session_duration_minutes']:.0f} minutes")
        print(f"   Tasks completed: {stats['completed_today']}")
        print(f"   Decisions made: {stats['decisions_made']}")
        print(f"   Missions synced: {len(missions)}")
        
        if stats['active_tasks'] > 0:
            print(f"\n⚠️  {stats['active_tasks']} task(s) still active:")
            for task in self.engine.tasks['active']:
                print(f"      - {task['name']}")
        
        print(f"\n🎯 Active Missions:")
        for m in missions[:5]:
            status_icon = "🔄" if m['status'] == 'in progress' else "📋"
            print(f"   {status_icon} [{m['priority'].upper()}] {m['name']}")
        
        print(f"\n📋 Consolidation Checklist:")
        print("   [ ] Update WORKING.md session log")
        print("   [ ] Update INTERNAL.md with reflections")
        print("   [ ] Pre-write SESSION_ANCHOR.md")
        print("   [ ] Commit changes if significant")
        
        # Estimate advice for next session
        advice = self.goals.get_estimate_advice()
        if advice['sample_size'] >= 3:
            print(f"\n💡 For next session:")
            print(f"   {advice['advice']}")
        
        return stats


def main():
    """CLI for enhanced orchestrator."""
    orchestrator = AutonomyOrchestratorV2()
    
    if len(sys.argv) < 2:
        print("Autonomy Orchestrator v2 — Usage:")
        print("  orchestrator_v2.py start           # Session start")
        print("  orchestrator_v2.py complete        # Complete work")
        print("  orchestrator_v2.py end             # Session end")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "start":
        orchestrator.session_start()
    
    elif cmd == "complete":
        outcome = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        orchestrator.complete_work(outcome=outcome)
    
    elif cmd == "end":
        orchestrator.session_end()
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
