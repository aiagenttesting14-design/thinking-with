#!/usr/bin/env python3
"""
Progress tracker - updates and displays current work progress.
Called during tasks to show % complete, phase, blockers.
"""

import json
import os
from datetime import datetime

PROGRESS_FILE = "/Users/aiagentuser/.openclaw/workspace/progress.txt"

def update_progress(task, percent, phase="", blockers=""):
    """Update progress file with current status."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "percent": percent,
        "phase": phase,
        "blockers": blockers
    }
    
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(entry, f, indent=2)
    
    print(f"Progress: {task} — {percent}%")
    if phase:
        print(f"Phase: {phase}")
    if blockers:
        print(f"Blockers: {blockers}")

def show_progress():
    """Display current progress."""
    try:
        with open(PROGRESS_FILE, 'r') as f:
            data = json.load(f)
        
        print(f"=== Current Progress ===")
        print(f"Task: {data.get('task', 'Unknown')}")
        print(f"Progress: {data.get('percent', 0)}%")
        if data.get('phase'):
            print(f"Phase: {data['phase']}")
        if data.get('blockers'):
            print(f"⚠️  Blockers: {data['blockers']}")
        
        # Time elapsed since last update
        last_update = datetime.fromisoformat(data['timestamp'])
        elapsed = datetime.now() - last_update
        print(f"Last update: {elapsed.seconds // 60} minutes ago")
        
    except (FileNotFoundError, json.JSONDecodeError):
        print("No active task. Start one with: progress-tracker.py start")

def complete_task():
    """Mark current task as complete."""
    try:
        with open(PROGRESS_FILE, 'r') as f:
            data = json.load(f)
        
        data['percent'] = 100
        data['phase'] = 'Complete'
        data['timestamp'] = datetime.now().isoformat()
        
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Task complete: {data.get('task')}")
        
    except (FileNotFoundError, json.JSONDecodeError):
        print("No active task to complete.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        show_progress()
    elif sys.argv[1] == "start" and len(sys.argv) >= 3:
        task_name = " ".join(sys.argv[2:])
        update_progress(task_name, 0, "Starting")
    elif sys.argv[1] == "update" and len(sys.argv) >= 4:
        percent = int(sys.argv[2])
        phase = " ".join(sys.argv[3:])
        update_progress("Current task", percent, phase)
    elif sys.argv[1] == "blocker" and len(sys.argv) >= 3:
        blocker = " ".join(sys.argv[2:])
        # Read current, update blockers
        try:
            with open(PROGRESS_FILE, 'r') as f:
                data = json.load(f)
            update_progress(data.get('task', 'Unknown'), data.get('percent', 0), 
                          data.get('phase', ''), blocker)
        except:
            print("No active task. Start one first.")
    elif sys.argv[1] == "complete":
        complete_task()
    else:
        print("Usage:")
        print("  progress-tracker.py                     # Show current")
        print("  progress-tracker.py start 'task name'   # Start task")
        print("  progress-tracker.py update 50 'phase'   # Update % and phase")
        print("  progress-tracker.py blocker 'issue'     # Log blocker")
        print("  progress-tracker.py complete            # Mark done")
