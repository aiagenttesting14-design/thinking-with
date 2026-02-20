#!/usr/bin/env python3
"""
Task timer and notifier for autonomous work.
Helps track time spent and decide when to surface updates.
"""

import sys
import json
from datetime import datetime, timedelta

TIME_LOG = "/Users/aiagentuser/.openclaw/workspace/time-log.json"

def log_task_start(task_name, estimated_minutes):
    """Log the start of a task with time estimate."""
    entry = {
        "task": task_name,
        "started": datetime.now().isoformat(),
        "estimated_minutes": estimated_minutes,
        "status": "active"
    }
    
    try:
        with open(TIME_LOG, 'r') as f:
            log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log = {"tasks": []}
    
    log["tasks"].append(entry)
    
    with open(TIME_LOG, 'w') as f:
        json.dump(log, f, indent=2)
    
    checkin_time = datetime.now() + timedelta(minutes=estimated_minutes//2)
    print(f"Task logged: {task_name}")
    print(f"Estimated: {estimated_minutes} minutes")
    print(f"Suggested check-in: {checkin_time.strftime('%H:%M')}")

def get_active_task():
    """Get currently active task if any."""
    try:
        with open(TIME_LOG, 'r') as f:
            log = json.load(f)
        
        for task in reversed(log.get("tasks", [])):
            if task.get("status") == "active":
                return task
        return None
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def suggest_checkin():
    """Suggest whether to check in based on active task."""
    task = get_active_task()
    
    if not task:
        print("No active task. Start one with: task-timer.py start 'task name' minutes")
        return
    
    started = datetime.fromisoformat(task["started"])
    elapsed = (datetime.now() - started).total_seconds() / 60
    estimated = task["estimated_minutes"]
    remaining = estimated - elapsed
    
    print(f"Active: {task['task']}")
    print(f"Elapsed: {elapsed:.0f} minutes")
    print(f"Estimated: {estimated} minutes")
    print(f"Remaining: {remaining:.0f} minutes")
    
    if elapsed > estimated * 1.5:
        print("\n⚠️  Task taking longer than expected. Consider:")
        print("   - Breaking it into smaller pieces")
        print("   - Checking in with Stephen about scope")
        print("   - Documenting what's blocking you")
    elif elapsed > estimated * 0.5:
        print("\n📍 Halfway point. Consider:")
        print("   - Is there anything noteworthy to share?")
        print("   - Are you still on track?")
        print("   - Any discoveries or blocks?")
    else:
        print("\n✓ Early in task. Keep working.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  task-timer.py start 'task name' estimated_minutes")
        print("  task-timer.py status")
        sys.exit(1)
    
    if sys.argv[1] == "start" and len(sys.argv) == 4:
        log_task_start(sys.argv[2], int(sys.argv[3]))
    elif sys.argv[1] == "status":
        suggest_checkin()
    else:
        print("Unknown command")
