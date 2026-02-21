#!/usr/bin/env python3
"""
Model Router v2 - Improved task detection
"""

import sys

def get_model_for_task(task_description):
    """Return the best model for a given task"""
    task = task_description.lower()
    
    # Task type detection - more specific matching
    research_words = ["research", "search", "find", "look up", "scan", "investigate"]
    summary_words = ["summarize", "brief", "quick", "short", "extract", "recap", "overview"]
    synthesis_words = ["synthesize", "analyze", "reason", "complex", "deep", "evaluate", "critique"]
    creative_words = ["write", "creative", "essay", "story", "article", "poem", "narrative"]
    code_words = ["code", "program", "script", "function", "python", "javascript", "html"]
    verify_words = ["verify", "test", "check", "audit", "review", "validate"]
    heartbeat_words = ["heartbeat", "monitor", "check", "status", "health", "periodic"]
    
    if any(word in task for word in research_words):
        return "moonshot/kimi-k2.5"  # Fast, cheap, good for parallel
    
    elif any(word in task for word in summary_words):
        return "google/gemini-2.5-flash-lite"  # Cheapest
    
    elif any(word in task for word in synthesis_words):
        return "claude-sonnet-4-5"  # Best at reasoning
    
    elif any(word in task for word in creative_words):
        return "moonshot/kimi-k2.5"  # Creative and fast
    
    elif any(word in task for word in code_words):
        return "moonshot/kimi-k2.5"  # Good at code
    
    elif any(word in task for word in verify_words):
        return "moonshot/kimi-k2.5"  # Fast verification
    
    elif any(word in task for word in heartbeat_words):
        return "google/gemini-2.5-flash-lite"  # Cheapest for routine
    
    else:
        return "moonshot/kimi-k2.5"  # Default

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 model-router-v2.py '<task description>'")
        print("\nExamples:")
        print("  python3 model-router-v2.py 'Research AI memory systems'")
        print("  python3 model-router-v2.py 'Summarize the Reddit findings'")
        print("  python3 model-router-v2.py 'Analyze complex reasoning patterns'")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    model = get_model_for_task(task)
    
    # Cost comparison
    cost_per_1k = {
        "moonshot/kimi-k2.5": 0.0005,
        "google/gemini-2.5-flash-lite": 0.00025,
        "claude-sonnet-4-5": 0.003,
        "deepseek/deepseek-chat": 0.00014,
    }
    
    print(f"Task: '{task}'")
    print(f"Recommended model: {model}")
    
    model_key = model.lower()
    for key in cost_per_1k:
        if key in model_key:
            cost = cost_per_1k[key]
            claude_cost = cost_per_1k["claude-sonnet-4-5"]
            savings_pct = ((claude_cost - cost) / claude_cost) * 100
            print(f"Cost: ${cost:.4f} per 1K tokens")
            print(f"Savings vs Claude: {savings_pct:.0f}% cheaper")
            
            # Show actual dollar savings
            tokens_estimate = 2000  # Typical task
            savings = ((claude_cost - cost) * (tokens_estimate / 1000))
            print(f"Estimated savings per task: ${savings:.4f}")
            break

if __name__ == "__main__":
    main()
