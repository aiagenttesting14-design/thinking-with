#!/usr/bin/env python3
"""
Rate Limit Handler - Automatically handles API rate limits
"""

import json
import os
from datetime import datetime, timedelta

COST_FILE = "/Users/aiagentuser/.openclaw/workspace/cost-tracker.json"

class RateLimitHandler:
    def __init__(self):
        self.cost_data = self.load_cost_data()
    
    def load_cost_data(self):
        if os.path.exists(COST_FILE):
            with open(COST_FILE, 'r') as f:
                return json.load(f)
        return {
            "spawns": [],
            "rate_limit_events": [],
            "model_blacklist": {}
        }
    
    def record_rate_limit(self, model, error_message):
        """Record a rate limit event"""
        event = {
            "model": model,
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "action": "added_to_blacklist"
        }
        
        self.cost_data.setdefault("rate_limit_events", []).append(event)
        
        # Add to blacklist (temporary - 1 hour)
        blacklist_until = (datetime.now() + timedelta(hours=1)).isoformat()
        self.cost_data.setdefault("model_blacklist", {})[model] = blacklist_until
        
        self.save_data()
        print(f"⚠️ Rate limit recorded for {model}. Blacklisted until {blacklist_until}")
    
    def is_model_blacklisted(self, model):
        """Check if a model is currently blacklisted"""
        blacklist = self.cost_data.get("model_blacklist", {})
        if model in blacklist:
            blacklist_until = blacklist[model]
            try:
                blacklist_time = datetime.fromisoformat(blacklist_until)
                if datetime.now() < blacklist_time:
                    return True, f"Blacklisted until {blacklist_until}"
                else:
                    # Remove expired blacklist
                    del blacklist[model]
                    self.save_data()
                    return False, "Blacklist expired"
            except:
                return False, "Invalid blacklist timestamp"
        return False, "Not blacklisted"
    
    def get_fallback_model(self, original_model, task_type=""):
        """Get fallback model when original is rate-limited"""
        fallback_map = {
            "google/gemini-2.5-flash-lite": "moonshot/kimi-k2.5",
            "moonshot/kimi-k2.5": "deepseek/deepseek-chat",
            "deepseek/deepseek-chat": "moonshot/kimi-k2.5",
            "claude-sonnet-4-5": "moonshot/kimi-k2.5"  # Fallback from expensive to cheap
        }
        
        fallback = fallback_map.get(original_model, "moonshot/kimi-k2.5")
        
        # Special handling for summary tasks
        if "summar" in task_type.lower() and original_model == "google/gemini-2.5-flash-lite":
            print(f"📝 Summary task: Falling back from Gemini to Kimi (still 83% cheaper than Claude)")
        
        return fallback
    
    def save_data(self):
        with open(COST_FILE, 'w') as f:
            json.dump(self.cost_data, f, indent=2)
    
    def generate_rate_limit_report(self):
        """Generate report on rate limit events"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        today_events = [
            event for event in self.cost_data.get("rate_limit_events", [])
            if event.get("timestamp", "").startswith(today)
        ]
        
        if not today_events:
            return "No rate limit events today. ✅"
        
        report = f"# Rate Limit Report - {today}\n\n"
        report += f"**Total events today**: {len(today_events)}\n\n"
        
        for i, event in enumerate(today_events, 1):
            report += f"{i}. **{event.get('model', 'Unknown')}**\n"
            report += f"   Time: {event.get('timestamp', 'Unknown')}\n"
            report += f"   Error: {event.get('error', 'Unknown')}\n"
            report += f"   Action: {event.get('action', 'Unknown')}\n\n"
        
        # Current blacklist status
        blacklist = self.cost_data.get("model_blacklist", {})
        if blacklist:
            report += "## Currently Blacklisted Models\n"
            for model, until in blacklist.items():
                report += f"- **{model}**: Until {until}\n"
        
        # Recommendations
        report += "\n## Recommendations\n"
        
        gemini_events = len([e for e in today_events if "gemini" in e.get("model", "").lower()])
        if gemini_events > 0:
            report += "1. **Gemini rate limits**: Use Kimi for summaries when Gemini is limited\n"
            report += "2. **Monitor usage**: Keep Gemini under 15 requests/day for buffer\n"
            report += "3. **Consider DeepSeek**: Even cheaper than Kimi ($0.14 vs $0.50 per million)\n"
        
        return report

def main():
    handler = RateLimitHandler()
    
    # Test: Record the Gemini rate limit we just encountered
    handler.record_rate_limit(
        "google/gemini-2.5-flash-lite",
        "API rate limit reached. Please try again later."
    )
    
    # Check blacklist status
    gemini_blacklisted, reason = handler.is_model_blacklisted("google/gemini-2.5-flash-lite")
    print(f"Gemini blacklisted? {gemini_blacklisted} ({reason})")
    
    # Get fallback
    fallback = handler.get_fallback_model("google/gemini-2.5-flash-lite", "summarize findings")
    print(f"Fallback for Gemini: {fallback}")
    
    # Generate report
    print("\n" + handler.generate_rate_limit_report())

if __name__ == "__main__":
    main()
