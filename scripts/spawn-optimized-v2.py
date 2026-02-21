#!/usr/bin/env python3
"""
Optimized Spawner v2 - Handles rate limits with fallbacks
"""

import subprocess
import json
import sys
import os
from datetime import datetime

def get_model_with_fallback(task):
    """Get model with rate limit awareness"""
    task_lower = task.lower()
    
    # Check if task is summary/quick type
    summary_words = {"summarize", "brief", "quick", "short", "extract", "recap", "overview"}
    words = set(task_lower.split())
    
    if words & summary_words:
        # For summaries, try Gemini first, fallback to Kimi
        # Check if we've hit rate limits today
        gemini_count = get_gemini_usage_today()
        if gemini_count < 15:  # Leave buffer
            return "google/gemini-2.5-flash-lite"
        else:
            print(f"⚠️ Gemini rate limit approaching ({gemini_count}/20). Using Kimi fallback.")
            return "moonshot/kimi-k2.5"
    
    # Default routing
    if any(word in task_lower for word in ["research", "search", "find ", "investigate"]):
        return "moonshot/kimi-k2.5"
    elif any(word in task_lower for word in ["synthesize", "analyze", "complex", "deep"]):
        return "claude-sonnet-4-5"
    elif any(word in task_lower for word in ["write", "creative"]):
        return "moonshot/kimi-k2.5"
    elif any(word in task_lower for word in ["code", "program"]):
        return "moonshot/kimi-k2.5"
    else:
        return "moonshot/kimi-k2.5"

def get_gemini_usage_today():
    """Check how many Gemini requests we've made today"""
    cost_file = "/Users/aiagentuser/.openclaw/workspace/cost-tracker.json"
    today = datetime.now().strftime("%Y-%m-%d")
    
    if not os.path.exists(cost_file):
        return 0
    
    with open(cost_file, 'r') as f:
        data = json.load(f)
    
    gemini_count = 0
    for spawn in data.get("spawns", []):
        if spawn.get("timestamp", "").startswith(today):
            if "gemini" in spawn.get("model", "").lower():
                gemini_count += 1
    
    return gemini_count

def spawn_subagent(task, label=None):
    """Spawn a subagent with rate-limit-aware model selection"""
    model = get_model_with_fallback(task)
    
    print(f"🚀 Spawning subagent with rate-limit-aware routing:")
    print(f"   Task: {task}")
    print(f"   Model: {model}")
    
    # Record before spawn
    record_spawn(task, model, "attempted")
    
    # Build the command
    cmd = ["openclaw", "sessions", "spawn"]
    
    if label:
        cmd.extend(["--label", label])
    
    cmd.extend(["--task", task])
    cmd.extend(["--model", model])
    cmd.extend(["--run-timeout", "300"])
    
    print(f"\n📋 To execute:")
    print(f"   openclaw sessions spawn --task \"{task}\" --model {model}" + (f" --label \"{label}\"" if label else ""))
    
    # Add rate limit warning if using Gemini
    if "gemini" in model.lower():
        gemini_count = get_gemini_usage_today() + 1
        print(f"⚠️  Gemini usage: {gemini_count}/20 requests today")
        if gemini_count >= 18:
            print("   ⚠️  Rate limit approaching! Consider Kimi fallback next time.")
    
    return model

def record_spawn(task, model, status="attempted"):
    """Record subagent spawn attempt"""
    cost_file = "/Users/aiagentuser/.openclaw/workspace/cost-tracker.json"
    
    # Initialize or load cost data
    if os.path.exists(cost_file):
        with open(cost_file, 'r') as f:
            data = json.load(f)
    else:
        data = {
            "spawns": [],
            "rate_limit_events": []
        }
    
    # Add this spawn
    spawn_record = {
        "task": task,
        "model": model,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    
    data["spawns"].append(spawn_record)
    
    # Save
    with open(cost_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"📊 Spawn recorded to {cost_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 spawn-optimized-v2.py '<task description>' [label]")
        print("\nExamples:")
        print("  python3 spawn-optimized-v2.py 'Summarize findings' summary-1")
        print("  python3 spawn-optimized-v2.py 'Research AI trends' research-1")
        sys.exit(1)
    
    task = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else None
    
    spawn_subagent(task, label)

if __name__ == "__main__":
    main()
