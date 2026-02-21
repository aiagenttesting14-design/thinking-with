#!/usr/bin/env python3
"""
Optimized Subagent Spawner - Uses task-based model routing
"""

import subprocess
import json
import sys
import os

def get_model_for_task(task):
    """Simple model routing logic"""
    task_lower = task.lower()
    
    if any(word in task_lower for word in ["research", "search", "find"]):
        return "moonshot/kimi-k2.5"
    elif any(word in task_lower for word in ["summarize", "brief", "quick"]):
        return "google/gemini-2.5-flash-lite"
    elif any(word in task_lower for word in ["synthesize", "analyze", "complex"]):
        return "claude-sonnet-4-5"
    elif any(word in task_lower for word in ["write", "creative"]):
        return "moonshot/kimi-k2.5"
    elif any(word in task_lower for word in ["code", "program"]):
        return "moonshot/kimi-k2.5"
    else:
        return "moonshot/kimi-k2.5"

def spawn_subagent(task, label=None):
    """Spawn a subagent with optimized model selection"""
    model = get_model_for_task(task)
    
    print(f"🚀 Spawning subagent with optimized routing:")
    print(f"   Task: {task}")
    print(f"   Model: {model}")
    
    # Build the command
    cmd = ["openclaw", "sessions", "spawn"]
    
    if label:
        cmd.extend(["--label", label])
    
    cmd.extend(["--task", task])
    cmd.extend(["--model", model])
    cmd.extend(["--run-timeout", "300"])  # 5 minutes
    
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        # In a real implementation, we would call the OpenClaw CLI
        # For now, just output the recommended command
        print("\n📋 To execute:")
        print(f"   openclaw sessions spawn --task \"{task}\" --model {model}" + (f" --label \"{label}\"" if label else ""))
        
        # Record the spawn for cost tracking
        record_spawn(task, model)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def record_spawn(task, model):
    """Record subagent spawn for cost tracking"""
    cost_file = "/Users/aiagentuser/.openclaw/workspace/cost-tracker.json"
    
    # Initialize or load cost data
    if os.path.exists(cost_file):
        with open(cost_file, 'r') as f:
            data = json.load(f)
    else:
        data = {
            "spawns": [],
            "total_estimated_cost": 0
        }
    
    # Add this spawn
    spawn_record = {
        "task": task,
        "model": model,
        "timestamp": subprocess.getoutput("date -u +'%Y-%m-%dT%H:%M:%SZ'")
    }
    
    data["spawns"].append(spawn_record)
    
    # Save
    with open(cost_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"📊 Spawn recorded to {cost_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 spawn-optimized.py '<task description>' [label]")
        print("\nExamples:")
        print("  python3 spawn-optimized.py 'Research AI memory systems' research-1")
        print("  python3 spawn-optimized.py 'Summarize the Reddit findings' summary")
        sys.exit(1)
    
    task = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else None
    
    spawn_subagent(task, label)

if __name__ == "__main__":
    main()
