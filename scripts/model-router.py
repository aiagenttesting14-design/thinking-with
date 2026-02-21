#!/usr/bin/env python3
"""
Model Router - Helper for task-based model selection
"""

import sys

def get_model_for_task(task_description):
    """Return the best model for a given task"""
    task = task_description.lower()
    
    # Task type detection
    if any(word in task for word in ["research", "search", "find", "look up", "scan"]):
        return "moonshot/kimi-k2.5"  # Fast, cheap, good for parallel
    
    elif any(word in task for word in ["synthesize", "analyze", "reason", "complex", "deep"]):
        return "claude-sonnet-4-5"  # Best at reasoning
    
    elif any(word in task for word in ["write", "creative", "essay", "story", "article"]):
        return "moonshot/kimi-k2.5"  # Creative and fast
    
    elif any(word in task for word in ["code", "program", "script", "function", "python"]):
        return "moonshot/kimi-k2.5"  # Good at code
    
    elif any(word in task for word in ["summarize", "brief", "quick", "short", "extract"]):
        return "google/gemini-2.5-flash-lite"  # Cheapest
    
    elif any(word in task for word in ["verify", "test", "check", "audit", "review"]):
        return "moonshot/kimi-k2.5"  # Fast verification
    
    elif any(word in task for word in ["heartbeat", "monitor", "check", "status"]):
        return "google/gemini-2.5-flash-lite"  # Cheapest for routine
    
    else:
        return "moonshot/kimi-k2.5"  # Default

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 model-router.py '<task description>'")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    model = get_model_for_task(task)
    print(f"Task: {task}")
    print(f"Recommended model: {model}")
    
    # Also print cost estimate
    cost_per_1k = {
        "moonshot/kimi-k2.5": 0.0005,
        "google/gemini-2.5-flash-lite": 0.00025,
        "claude-sonnet-4-5": 0.003,
        "deepseek/deepseek-chat": 0.00014,
    }
    
    model_key = model.lower()
    for key in cost_per_1k:
        if key in model_key:
            cost = cost_per_1k[key]
            print(f"Estimated cost: ${cost:.4f} per 1K tokens")
            print(f"   (vs Claude: ${0.003:.4f} per 1K - {((0.003-cost)/0.003*100):.0f}% cheaper)")
            break

if __name__ == "__main__":
    main()
