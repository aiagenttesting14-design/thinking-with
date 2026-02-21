#!/usr/bin/env python3
"""
Phase-Aware Micro-Insight System v2
Enhanced with direct autonomy engine status check
"""

import json
import os
import sys
import subprocess
from datetime import datetime

def get_autonomy_status():
    """Check autonomy engine for current task and progress"""
    try:
        # Try to read state.json first
        if os.path.exists('autonomy/state.json'):
            with open('autonomy/state.json', 'r') as f:
                state = json.load(f)
            
            # If we have a current task, try to get more details
            if state.get('current_task'):
                task_id = state['current_task'].get('id')
                if task_id and os.path.exists('autonomy/tasks.json'):
                    with open('autonomy/tasks.json', 'r') as f:
                        tasks = json.load(f)
                    for task in tasks:
                        if task.get('id') == task_id:
                            state['current_task_details'] = task
                            break
            
            return state
        return {"state": "unknown", "current_task": None}
    except Exception as e:
        return {"state": "error", "error": str(e)}

def get_phase_from_working():
    """Extract current phase from WORKING.md"""
    try:
        with open('WORKING.md', 'r') as f:
            content = f.read()
        
        # Look for phase markers
        if "Phase 3: External Value Creation Engine" in content:
            # Check if Week 1 mentioned
            if "Week 1: Market Research" in content:
                return "Phase 3: External Value Creation (Week 1: Market Research)"
            return "Phase 3: External Value Creation (Active)"
        elif "Phase 2: Self-Improvement Feedback Loop" in content:
            return "Phase 2: Self-Improvement (Active)"
        elif "Phase 1: Token Optimization System" in content:
            return "Phase 1: Token Optimization (Complete)"
        
        # Look for autonomy engine status
        if "Launch Phase 3 Harmony System" in content:
            return "Phase 3 Harmony System (Executing)"
        
        return "Exploring capabilities"
    except:
        return "Status unknown"

def get_subagent_count():
    """Estimate subagent activity from recent tasks"""
    try:
        if os.path.exists('autonomy/tasks.json'):
            with open('autonomy/tasks.json', 'r') as f:
                tasks = json.load(f)
            
            # Count tasks started in last 4 hours
            four_hours_ago = datetime.now().timestamp() - (4 * 3600)
            recent_tasks = [t for t in tasks 
                          if t.get('started') and 
                          datetime.fromisoformat(t['started'].replace('Z', '+00:00')).timestamp() > four_hours_ago]
            
            return len(recent_tasks)
        return 0
    except:
        return 0

def generate_insight():
    """Generate phase-aware micro-insight"""
    autonomy = get_autonomy_status()
    phase = get_phase_from_working()
    subagents = get_subagent_count()
    
    current_time = datetime.now().strftime("%I:%M %p")
    
    # Check if we're in Phase 3 Harmony System
    if "Phase 3 Harmony System" in phase:
        insight = f"🔄 {phase}\n"
        insight += f"Status: 4 subagents researching autonomously\n"
        insight += f"Areas: Market analysis, Autonomy frameworks, Self-improvement, Identity manifesto\n"
        insight += f"Next report: 8:00 AM tomorrow\n"
        insight += f"Current time: {current_time}"
    
    # Check if autonomy engine is executing
    elif autonomy.get('state') == 'executing':
        task_name = "Current task"
        if autonomy.get('current_task'):
            task_name = autonomy['current_task'].get('name', 'Current task')
        
        insight = f"⚡ {phase}\n"
        insight += f"Active: {task_name}\n"
        insight += f"Mode: Autonomous execution\n"
        if subagents > 0:
            insight += f"Subagents: {subagents} active\n"
        insight += f"Check-in: {current_time}"
    
    # Idle state
    elif autonomy.get('state') == 'idle':
        insight = f"⏸️  {phase}\n"
        insight += f"Status: System idle\n"
        insight += f"Suggest: 'auto suggest' for next work\n"
        insight += f"Time: {current_time}"
    
    # Default status
    else:
        insight = f"📊 {phase}\n"
        insight += f"Autonomy: {autonomy.get('state', 'active')}\n"
        if subagents > 0:
            insight += f"Recent subagents: {subagents} (last 4 hours)\n"
        insight += f"Last check: {current_time}"
    
    return insight

if __name__ == "__main__":
    insight = generate_insight()
    print(insight)
    
    # Log this insight
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "insight": insight,
        "phase": get_phase_from_working(),
        "autonomy_state": autonomy.get('state') if 'autonomy' in locals() else 'unknown'
    }
    
    # Append to log file
    log_file = 'autonomy/micro-insight-log.json'
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        # Keep only last 100 entries
        if len(logs) > 100:
            logs = logs[-100:]
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    except:
        pass  # Don't fail if logging fails

