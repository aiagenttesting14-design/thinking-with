#!/usr/bin/env python3
"""
Model Router Final - Better word boundary detection
"""

import sys
import re

def get_model_for_task(task_description):
    """Return the best model for a given task with better matching"""
    task = task_description.lower()
    words = set(re.findall(r'\b\w+\b', task))  # Get individual words
    
    # Task type detection with word boundaries
    research_words = {"research", "search", "investigate", "scan"}
    summary_words = {"summarize", "brief", "quick", "short", "extract", "recap", "overview"}
    synthesis_words = {"synthesize", "analyze", "reason", "complex", "deep", "evaluate", "critique"}
    creative_words = {"write", "creative", "essay", "story", "article", "poem", "narrative"}
    code_words = {"code", "program", "script", "function", "python", "javascript", "html"}
    verify_words = {"verify", "test", "check", "audit", "review", "validate"}
    heartbeat_words = {"heartbeat", "monitor", "status", "health", "periodic"}
    
    # Check for exact word matches
    if words & summary_words:
        return "google/gemini-2.5-flash-lite"  # Cheapest
    
    elif words & research_words:
        return "moonshot/kimi-k2.5"  # Fast, cheap, good for parallel
    
    elif words & synthesis_words:
        return "claude-sonnet-4-5"  # Best at reasoning
    
    elif words & creative_words:
        return "moonshot/kimi-k2.5"  # Creative and fast
    
    elif words & code_words:
        return "moonshot/kimi-k2.5"  # Good at code
    
    elif words & verify_words:
        return "moonshot/kimi-k2.5"  # Fast verification
    
    elif words & heartbeat_words:
        return "google/gemini-2.5-flash-lite"  # Cheapest for routine
    
    else:
        # Fallback: check for substrings (less precise)
        task_lower = task_description.lower()
        if any(word in task_lower for word in ["summar", "brief", "quick"]):
            return "google/gemini-2.5-flash-lite"
        elif any(word in task_lower for word in ["research", "search", "find "]):  # Space after find
            return "moonshot/kimi-k2.5"
        else:
            return "moonshot/kimi-k2.5"  # Default

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 model-router-final.py '<task description>'")
        print("\nExamples:")
        print("  python3 model-router-final.py 'Research AI memory systems'")
        print("  python3 model-router-final.py 'Summarize the Reddit findings'")
        print("  python3 model-router-final.py 'Analyze complex reasoning patterns'")
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
            
            # Show actual dollar savings for typical task
            tokens_estimate = 2000  # Typical task size
            task_cost = cost * (tokens_estimate / 1000)
            claude_task_cost = claude_cost * (tokens_estimate / 1000)
            savings = claude_task_cost - task_cost
            
            print(f"Cost: ${cost:.4f} per 1K tokens")
            print(f"Task cost (2K tokens): ${task_cost:.4f}")
            print(f"Claude cost (2K tokens): ${claude_task_cost:.4f}")
            print(f"Savings: ${savings:.4f} ({savings_pct:.0f}% cheaper)")
            
            # Monthly projection
            daily_tasks = 5  # Average tasks per day
            monthly_savings = savings * daily_tasks * 30
            print(f"Monthly savings projection: ${monthly_savings:.2f}")
            break

if __name__ == "__main__":
    main()
