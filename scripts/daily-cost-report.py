#!/usr/bin/env python3
"""
Daily Cost Report - Generate optimization insights
"""

import json
import os
from datetime import datetime

COST_FILE = "/Users/aiagentuser/.openclaw/workspace/cost-tracker.json"

def generate_report():
    """Generate daily cost optimization report"""
    
    if not os.path.exists(COST_FILE):
        return "# Daily Cost Report\n\nNo cost data available yet. Start tracking with spawn-optimized.py"
    
    with open(COST_FILE, 'r') as f:
        data = json.load(f)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Filter today's spawns
    today_spawns = [
        spawn for spawn in data.get("spawns", [])
        if spawn.get("timestamp", "").startswith(today)
    ]
    
    # Calculate costs
    cost_per_1k = {
        "moonshot/kimi-k2.5": 0.0005,
        "google/gemini-2.5-flash-lite": 0.00025,
        "claude-sonnet-4-5": 0.003,
        "deepseek/deepseek-chat": 0.00014,
    }
    
    # Estimate costs (assuming ~2000 tokens per spawn)
    estimated_tokens_per_spawn = 2000
    total_estimated_cost = 0
    model_breakdown = {}
    
    for spawn in today_spawns:
        model = spawn["model"]
        for key, cost in cost_per_1k.items():
            if key in model.lower():
                spawn_cost = (estimated_tokens_per_spawn / 1000) * cost
                total_estimated_cost += spawn_cost
                
                if model not in model_breakdown:
                    model_breakdown[model] = {"count": 0, "cost": 0}
                model_breakdown[model]["count"] += 1
                model_breakdown[model]["cost"] += spawn_cost
                break
    
    # Generate report
    report = f"""# Daily Cost Optimization Report - {today}

## Summary
- **Total spawns today**: {len(today_spawns)}
- **Estimated total cost**: ${total_estimated_cost:.4f}
- **Average cost per spawn**: ${total_estimated_cost/len(today_spawns) if today_spawns else 0:.4f}

## Model Usage Breakdown
"""
    
    for model, stats in model_breakdown.items():
        report += f"- **{model}**: {stats['count']} spawns (${stats['cost']:.4f})\n"
    
    # Optimization suggestions
    report += "\n## Optimization Opportunities\n"
    
    # Check for expensive model usage
    expensive_models = ["claude-sonnet-4-5"]
    cheap_models = ["gemini-2.5-flash-lite", "kimi-k2.5"]
    
    expensive_cost = sum(
        stats["cost"] for model, stats in model_breakdown.items()
        if any(exp in model.lower() for exp in expensive_models)
    )
    
    if expensive_cost > 0:
        report += f"⚠️ **Expensive model usage**: ${expensive_cost:.4f} spent on Claude\n"
        report += "   → Consider routing more tasks to cheaper models\n"
    
    # Check Gemini rate limits
    gemini_count = sum(
        stats["count"] for model, stats in model_breakdown.items()
        if "gemini" in model.lower()
    )
    
    if gemini_count > 15:  # Approaching 20/day free limit
        report += f"⚠️ **Gemini rate limit**: {gemini_count}/20 free requests used today\n"
        report += "   → Consider using Kimi or DeepSeek as alternatives\n"
    
    # General optimization tips
    report += "\n## Optimization Tips from Reddit Research\n"
    report += "1. **Use cheap models for routine tasks**: Gemini Flash-Lite for summaries, Kimi for research\n"
    report += "2. **Reserve expensive models for complex reasoning**: Claude only when truly needed\n"
    report += "3. **Monitor rate limits**: Gemini free tier = 20 requests/day\n"
    report += "4. **Consider local models**: Ollama for heartbeats and background tasks\n"
    report += "5. **Use memory_search()**: Instead of loading full context every time\n"
    
    # Add spawn details
    if today_spawns:
        report += "\n## Today's Spawns\n"
        for i, spawn in enumerate(today_spawns, 1):
            report += f"{i}. **{spawn.get('task', 'Unknown')}**\n"
            report += f"   Model: {spawn.get('model', 'Unknown')}\n"
            report += f"   Time: {spawn.get('timestamp', 'Unknown')}\n"
    
    report += f"\n*Report generated at {datetime.now().strftime('%H:%M')}*"
    
    return report

def main():
    report = generate_report()
    print(report)
    
    # Also save to file
    report_file = f"/Users/aiagentuser/.openclaw/workspace/reports/cost-report-{datetime.now().strftime('%Y-%m-%d')}.md"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {report_file}")

if __name__ == "__main__":
    main()
