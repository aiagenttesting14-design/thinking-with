#!/usr/bin/env python3
"""
Token Optimization System - Phase 1 Implementation
Based on Reddit community tips and MODEL-ROUTING-PLAN.md
"""

import json
import os
import datetime
from pathlib import Path

WORKSPACE = Path("/Users/aiagentuser/.openclaw/workspace")
COST_LOG = WORKSPACE / "cost-tracker.json"
MODEL_PLAN = WORKSPACE / "MODEL-ROUTING-PLAN.md"
WORKING_MD = WORKSPACE / "WORKING.md"

class TokenOptimizer:
    def __init__(self):
        self.cost_data = self.load_cost_data()
        self.model_plan = self.parse_model_plan()
        
    def load_cost_data(self):
        """Load or initialize cost tracking data"""
        if COST_LOG.exists():
            with open(COST_LOG, 'r') as f:
                return json.load(f)
        return {
            "daily_costs": {},
            "monthly_total": 0,
            "optimizations_applied": [],
            "last_updated": datetime.datetime.now().isoformat()
        }
    
    def parse_model_plan(self):
        """Parse MODEL-ROUTING-PLAN.md for routing rules"""
        if not MODEL_PLAN.exists():
            return {}
        
        with open(MODEL_PLAN, 'r') as f:
            content = f.read()
        
        # Extract task-based routing table
        import re
        table_pattern = r'\|\s*(\*\*.*?\*\*|\w+)\s*\|\s*(\w+[-\w\.]*)\s*\|\s*(\w+[-\w\.]*)\s*\|\s*(.*?)\s*\|'
        matches = re.findall(table_pattern, content, re.DOTALL)
        
        routing = {}
        for match in matches:
            task_type = match[0].replace('**', '').strip().lower()
            primary = match[1].strip()
            fallback = match[2].strip()
            routing[task_type] = {
                "primary": primary,
                "fallback": fallback,
                "description": match[3].strip()
            }
        
        return routing
    
    def get_model_for_task(self, task_description):
        """Determine best model for a given task"""
        task_lower = task_description.lower()
        
        # Task type detection
        if any(word in task_lower for word in ["research", "search", "find", "look up"]):
            task_type = "research"
        elif any(word in task_lower for word in ["synthesize", "analyze", "reason", "complex"]):
            task_type = "synthesis"
        elif any(word in task_lower for word in ["write", "creative", "essay", "story"]):
            task_type = "creative writing"
        elif any(word in task_lower for word in ["code", "program", "script", "function"]):
            task_type = "code generation"
        elif any(word in task_lower for word in ["summarize", "brief", "quick", "short"]):
            task_type = "quick summaries"
        elif any(word in task_lower for word in ["verify", "test", "check", "audit"]):
            task_type = "verification/testing"
        else:
            task_type = "general"
        
        # Get model from plan
        if task_type in self.model_plan:
            return self.model_plan[task_type]["primary"]
        
        # Default fallback
        return "moonshot/kimi-k2.5"  # Current default
    
    def estimate_cost(self, model, tokens):
        """Estimate cost based on model and token count"""
        # Approximate costs per 1K tokens (in USD)
        cost_per_1k = {
            "moonshot/kimi-k2.5": 0.0005,      # ~$0.50 per million
            "google/gemini-2.5-flash-lite": 0.00025,  # ~$0.25 per million
            "claude-sonnet-4-5": 0.003,        # ~$3.00 per million
            "deepseek/deepseek-chat": 0.00014, # ~$0.14 per million
        }
        
        model_key = model.lower()
        for key in cost_per_1k:
            if key in model_key:
                return (tokens / 1000) * cost_per_1k[key]
        
        return (tokens / 1000) * 0.001  # Default estimate
    
    def record_usage(self, model, tokens, task_type=""):
        """Record token usage and update cost tracking"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if today not in self.cost_data["daily_costs"]:
            self.cost_data["daily_costs"][today] = {
                "total_cost": 0,
                "total_tokens": 0,
                "by_model": {},
                "by_task": {}
            }
        
        cost = self.estimate_cost(model, tokens)
        
        # Update daily totals
        self.cost_data["daily_costs"][today]["total_cost"] += cost
        self.cost_data["daily_costs"][today]["total_tokens"] += tokens
        
        # Update by model
        model_key = model.split("/")[-1] if "/" in model else model
        if model_key not in self.cost_data["daily_costs"][today]["by_model"]:
            self.cost_data["daily_costs"][today]["by_model"][model_key] = {
                "cost": 0,
                "tokens": 0
            }
        self.cost_data["daily_costs"][today]["by_model"][model_key]["cost"] += cost
        self.cost_data["daily_costs"][today]["by_model"][model_key]["tokens"] += tokens
        
        # Update by task if provided
        if task_type:
            if task_type not in self.cost_data["daily_costs"][today]["by_task"]:
                self.cost_data["daily_costs"][today]["by_task"][task_type] = {
                    "cost": 0,
                    "tokens": 0
                }
            self.cost_data["daily_costs"][today]["by_task"][task_type]["cost"] += cost
            self.cost_data["daily_costs"][today]["by_task"][task_type]["tokens"] += tokens
        
        # Update monthly total (simplified)
        self.cost_data["monthly_total"] = sum(
            day["total_cost"] for day in self.cost_data["daily_costs"].values()
        )
        
        self.cost_data["last_updated"] = datetime.datetime.now().isoformat()
        self.save_cost_data()
        
        return cost
    
    def save_cost_data(self):
        """Save cost data to file"""
        with open(COST_LOG, 'w') as f:
            json.dump(self.cost_data, f, indent=2)
    
    def generate_report(self):
        """Generate cost optimization report"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if today not in self.cost_data["daily_costs"]:
            return "No cost data for today."
        
        today_data = self.cost_data["daily_costs"][today]
        
        report = f"""# Token Optimization Report - {today}

## Daily Summary
- **Total Cost**: ${today_data['total_cost']:.4f}
- **Total Tokens**: {today_data['total_tokens']:,}
- **Cost per 1K tokens**: ${(today_data['total_cost'] / (today_data['total_tokens'] / 1000)):.4f}

## Cost by Model
"""
        
        for model, data in today_data["by_model"].items():
            report += f"- **{model}**: ${data['cost']:.4f} ({data['tokens']:,} tokens)\n"
        
        if today_data.get("by_task"):
            report += "\n## Cost by Task Type\n"
            for task, data in today_data["by_task"].items():
                report += f"- **{task}**: ${data['cost']:.4f} ({data['tokens']:,} tokens)\n"
        
        # Add optimization suggestions
        report += "\n## Optimization Suggestions\n"
        
        # Check if expensive models are being used for simple tasks
        expensive_models = ["claude-sonnet-4-5", "claude-haiku-4-5"]
        cheap_models = ["gemini-2.5-flash-lite", "deepseek-chat", "kimi-k2.5"]
        
        expensive_usage = sum(
            data["cost"] for model, data in today_data["by_model"].items()
            if any(exp in model.lower() for exp in expensive_models)
        )
        
        if expensive_usage > today_data["total_cost"] * 0.3:  # More than 30% of cost
            report += "⚠️ **High cost alert**: Expensive models (Claude) account for >30% of daily cost.\n"
            report += "   → Consider routing more tasks to cheaper models (Gemini Flash, Kimi, DeepSeek)\n"
        
        # Check for rate limit issues
        if "gemini" in str(today_data["by_model"]).lower():
            report += "📊 **Gemini usage**: Monitor rate limits (20 req/day free tier)\n"
        
        report += f"\n*Report generated at {datetime.datetime.now().strftime('%H:%M')}*"
        
        return report
    
    def apply_optimization(self, optimization_name, description):
        """Record an optimization that was applied"""
        self.cost_data.setdefault("optimizations_applied", []).append({
            "name": optimization_name,
            "description": description,
            "applied_at": datetime.datetime.now().isoformat()
        })
        self.save_cost_data()

def main():
    """Main function for testing"""
    optimizer = TokenOptimizer()
    
    # Test the system
    print("Token Optimization System - Phase 1")
    print("=" * 50)
    
    # Show model routing
    print("\nModel Routing Rules:")
    for task_type, rules in optimizer.model_plan.items():
        print(f"  {task_type}: {rules['primary']} → {rules['fallback']}")
    
    # Test task detection
    test_tasks = [
        "Research AI memory systems",
        "Write a creative story about autonomy",
        "Summarize this document quickly",
        "Write Python code for data analysis"
    ]
    
    print("\nTask Detection Examples:")
    for task in test_tasks:
        model = optimizer.get_model_for_task(task)
        print(f"  '{task}' → {model}")
    
    # Generate initial report
    print("\n" + optimizer.generate_report())

if __name__ == "__main__":
    main()
