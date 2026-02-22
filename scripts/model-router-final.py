#!/usr/bin/env python3
"""
Model Router with Intelligent Rotation Integration
Maintains backward compatibility while using new rotation system
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to use enhanced router
try:
    # Import using importlib for hyphenated module name
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "model_router_enhanced", 
        os.path.join(os.path.dirname(__file__), "model-router-enhanced.py")
    )
    model_router_enhanced = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model_router_enhanced)
    
    from model_router_enhanced import EnhancedModelRouter
    
    def get_model_for_task(task_description):
        """Wrapper for compatibility"""
        router = EnhancedModelRouter()
        return router.get_model_for_task(task_description)
    
    print("🤖 Using enhanced router with intelligent rotation", file=sys.stderr)
    
except ImportError as e:
    # Fallback to original logic
    import re
    
    def get_model_for_task(task_description):
        """Original fallback logic"""
        task = task_description.lower()
        
        if any(word in task for word in ["summar", "brief", "quick", "heartbeat", "monitor"]):
            return "google/gemini-2.5-flash-lite"
        elif any(word in task for word in ["research", "search", "investigate", "parallel"]):
            return "moonshot/kimi-k2.5"
        elif any(word in task for word in ["complex", "reason", "analyze", "synthesize"]):
            return "claude-sonnet-4-5"
        elif any(word in task for word in ["code", "program", "script"]):
            return "moonshot/kimi-k2.5"
        else:
            return "moonshot/kimi-k2.5"
    
    print(f"⚠️ Using basic router: {e}", file=sys.stderr)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 model-router-final.py '<task description>'")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    model = get_model_for_task(task)
    
    # Cost info for display
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
            
            tokens_estimate = 2000
            task_cost = cost * (tokens_estimate / 1000)
            claude_task_cost = claude_cost * (tokens_estimate / 1000)
            savings = claude_task_cost - task_cost
            
            print(f"Cost: ${cost:.4f} per 1K tokens")
            print(f"Task cost (2K tokens): ${task_cost:.4f}")
            print(f"Claude cost (2K tokens): ${claude_task_cost:.4f}")
            print(f"Savings: ${savings:.4f} ({savings_pct:.0f}% cheaper)")
            
            daily_tasks = 5
            monthly_savings = savings * daily_tasks * 30
            print(f"Monthly savings projection: ${monthly_savings:.2f}")
            break

if __name__ == "__main__":
    main()
