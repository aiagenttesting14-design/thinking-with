#!/usr/bin/env python3
"""
Intelligent Model Rotation System - Phase 1
Enhanced rate limit handler with usage tracking and predictive quota management
"""

import json
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict

COST_FILE = "/Users/aiagentuser/.openclaw/workspace/cost-tracker.json"
ROTATION_CONFIG = "/Users/aiagentuser/.openclaw/workspace/scripts/rotation-config.json"

class IntelligentRotationSystem:
    def __init__(self):
        self.cost_data = self.load_cost_data()
        self.config = self.load_config()
        self.initialize_daily_tracking()
    
    def load_cost_data(self):
        if os.path.exists(COST_FILE):
            with open(COST_FILE, 'r') as f:
                return json.load(f)
        return {
            "spawns": [],
            "rate_limit_events": [],
            "model_blacklist": {},
            "daily_usage": {},
            "rotation_log": []
        }
    
    def load_config(self):
        default_config = {
            "model_quotas": {
                "google/gemini-2.5-flash-lite": {
                    "daily_limit": 20,
                    "reset_time": "00:00",  # UTC midnight
                    "cost_per_1k": 0.00025,
                    "priority": 1  # Highest priority (cheapest for summaries)
                },
                "moonshot/kimi-k2.5": {
                    "daily_limit": 100,  # Unknown actual limit
                    "reset_time": "00:00",
                    "cost_per_1k": 0.0005,
                    "priority": 2
                },
                "deepseek/deepseek-chat": {
                    "daily_limit": 50,  # Unknown actual limit
                    "reset_time": "00:00",
                    "cost_per_1k": 0.00014,
                    "priority": 3
                },
                "claude-sonnet-4-5": {
                    "daily_limit": 1000,  # High paid limit
                    "reset_time": "00:00",
                    "cost_per_1k": 0.003,
                    "priority": 4  # Emergency only
                }
            },
            "rotation_strategy": "time_based",
            "buffer_percentage": 20,  # Leave 20% buffer before hitting limits
            "time_based_schedule": {
                "00:00-12:00": "google/gemini-2.5-flash-lite",
                "12:00-18:00": "moonshot/kimi-k2.5",
                "18:00-24:00": "deepseek/deepseek-chat"
            }
        }
        
        if os.path.exists(ROTATION_CONFIG):
            with open(ROTATION_CONFIG, 'r') as f:
                user_config = json.load(f)
                # Merge with defaults
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in default_config:
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
        
        return default_config
    
    def initialize_daily_tracking(self):
        """Initialize or reset daily usage tracking"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if "daily_usage" not in self.cost_data:
            self.cost_data["daily_usage"] = {}
        
        if today not in self.cost_data["daily_usage"]:
            self.cost_data["daily_usage"][today] = defaultdict(int)
            self.save_data()
    
    def record_usage(self, model, task_type=""):
        """Record model usage and update daily counts"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Initialize if needed
        if today not in self.cost_data["daily_usage"]:
            self.cost_data["daily_usage"][today] = defaultdict(int)
        
        # Record usage
        self.cost_data["daily_usage"][today][model] += 1
        
        # Log rotation decision
        rotation_log = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "task_type": task_type,
            "daily_count": self.cost_data["daily_usage"][today][model],
            "decision_reason": "direct_selection"
        }
        
        self.cost_data.setdefault("rotation_log", []).append(rotation_log)
        self.save_data()
        
        print(f"📊 Usage recorded: {model} (count: {self.cost_data['daily_usage'][today][model]})")
    
    def get_remaining_quota(self, model):
        """Calculate remaining quota for a model"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get config for this model
        model_config = self.config["model_quotas"].get(model, {})
        daily_limit = model_config.get("daily_limit", 100)
        
        # Get today's usage
        today_usage = self.cost_data["daily_usage"].get(today, {})
        used = today_usage.get(model, 0)
        
        remaining = daily_limit - used
        buffer = int(daily_limit * (self.config["buffer_percentage"] / 100))
        
        return {
            "used": used,
            "limit": daily_limit,
            "remaining": remaining,
            "buffer": buffer,
            "below_buffer": remaining > buffer,
            "percentage_used": (used / daily_limit * 100) if daily_limit > 0 else 0
        }
    
    def predict_limit_hit_time(self, model):
        """Predict when the model will hit its daily limit"""
        quota = self.get_remaining_quota(model)
        if quota["remaining"] <= 0:
            return "Already at limit"
        
        # Calculate average usage rate
        today = datetime.now().strftime("%Y-%m-%d")
        today_usage = self.cost_data["daily_usage"].get(today, {})
        used = today_usage.get(model, 0)
        
        if used == 0:
            return "No usage yet today"
        
        # Calculate hours since midnight
        now = datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        hours_since_midnight = (now - midnight).total_seconds() / 3600
        
        if hours_since_midnight == 0:
            return "Just started day"
        
        # Calculate usage per hour
        usage_per_hour = used / hours_since_midnight
        
        # Predict hours until limit
        if usage_per_hour > 0:
            hours_until_limit = quota["remaining"] / usage_per_hour
            hit_time = now + timedelta(hours=hours_until_limit)
            return hit_time.strftime("%H:%M")
        
        return "Insufficient data"
    
    def get_best_model(self, task_type=""):
        """Intelligently select the best model based on quotas and task type"""
        # First, check if any model is blacklisted
        for model in self.config["model_quotas"]:
            blacklisted, reason = self.is_model_blacklisted(model)
            if blacklisted:
                print(f"⚠️ {model} is blacklisted: {reason}")
        
        # Get task-based recommendation first
        task_model = self.get_task_based_model(task_type)
        
        # Check if task model has quota
        task_quota = self.get_remaining_quota(task_model)
        
        if task_quota["below_buffer"]:
            print(f"✅ Task model {task_model} has quota: {task_quota['remaining']} remaining")
            return task_model
        else:
            print(f"⚠️ Task model {task_model} low on quota: {task_quota['remaining']} remaining")
            
            # Find alternative with best quota
            alternatives = []
            for model, config in self.config["model_quotas"].items():
                if model == task_model:
                    continue
                
                quota = self.get_remaining_quota(model)
                if quota["below_buffer"]:
                    alternatives.append({
                        "model": model,
                        "priority": config.get("priority", 99),
                        "remaining": quota["remaining"],
                        "cost": config.get("cost_per_1k", 1.0)
                    })
            
            if alternatives:
                # Sort by priority, then cost
                alternatives.sort(key=lambda x: (x["priority"], x["cost"]))
                best_alt = alternatives[0]
                print(f"🔄 Switching to {best_alt['model']} (priority: {best_alt['priority']}, cost: ${best_alt['cost']:.4f}/1K)")
                return best_alt["model"]
            else:
                # All models low on quota, use time-based schedule
                return self.get_time_based_model()
    
    def get_task_based_model(self, task_type=""):
        """Simple task-based model selection (compatible with existing router)"""
        task = task_type.lower()
        
        if any(word in task for word in ["summar", "brief", "quick", "heartbeat", "monitor"]):
            return "google/gemini-2.5-flash-lite"
        elif any(word in task for word in ["research", "search", "investigate", "parallel"]):
            return "moonshot/kimi-k2.5"
        elif any(word in task for word in ["complex", "reason", "analyze", "synthesize"]):
            return "claude-sonnet-4-5"
        elif any(word in task for word in ["code", "program", "script"]):
            return "moonshot/kimi-k2.5"
        else:
            return "moonshot/kimi-k2.5"  # Default
    
    def get_time_based_model(self):
        """Get model based on time of day schedule"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        for time_range, model in self.config["time_based_schedule"].items():
            start_str, end_str = time_range.split("-")
            start = datetime.strptime(start_str, "%H:%M").time()
            end = datetime.strptime(end_str, "%H:%M").time()
            
            if start <= now.time() <= end:
                quota = self.get_remaining_quota(model)
                if quota["below_buffer"]:
                    return model
        
        # Fallback to cheapest available model
        for model in ["google/gemini-2.5-flash-lite", "moonshot/kimi-k2.5", "deepseek/deepseek-chat"]:
            quota = self.get_remaining_quota(model)
            if quota["below_buffer"]:
                return model
        
        # Emergency fallback
        return "claude-sonnet-4-5"
    
    def record_rate_limit(self, model, error_message):
        """Record a rate limit event and update strategy"""
        event = {
            "model": model,
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "action": "added_to_blacklist"
        }
        
        self.cost_data.setdefault("rate_limit_events", []).append(event)
        
        # Add to blacklist (temporary - 2 hours for intelligent system)
        blacklist_until = (datetime.now() + timedelta(hours=2)).isoformat()
        self.cost_data.setdefault("model_blacklist", {})[model] = blacklist_until
        
        # Adjust buffer for this model (increase caution)
        if model in self.config["model_quotas"]:
            current_buffer = self.config["model_quotas"][model].get("buffer_adjustment", 0)
            self.config["model_quotas"][model]["buffer_adjustment"] = current_buffer + 10
        
        self.save_data()
        print(f"⚠️ Rate limit recorded for {model}. Blacklisted until {blacklist_until}")
        print(f"📈 Increased buffer caution for {model}")
    
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
    
    def save_data(self):
        with open(COST_FILE, 'w') as f:
            json.dump(self.cost_data, f, indent=2)
        
        # Also save config (in case of adjustments)
        with open(ROTATION_CONFIG, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def generate_rotation_report(self):
        """Generate comprehensive rotation report"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        report = f"# Intelligent Rotation System Report - {today}\n\n"
        report += f"**Generated**: {datetime.now().strftime('%H:%M')}\n\n"
        
        # Current usage
        report += "## Current Model Usage\n"
        today_usage = self.cost_data["daily_usage"].get(today, {})
        
        for model, config in self.config["model_quotas"].items():
            used = today_usage.get(model, 0)
            limit = config.get("daily_limit", 100)
            percentage = (used / limit * 100) if limit > 0 else 0
            
            quota = self.get_remaining_quota(model)
            prediction = self.predict_limit_hit_time(model)
            
            report += f"### {model}\n"
            report += f"- Used: {used}/{limit} ({percentage:.1f}%)\n"
            report += f"- Remaining: {quota['remaining']} (buffer: {quota['buffer']})\n"
            report += f"- Status: {'✅ Below buffer' if quota['below_buffer'] else '⚠️ Low quota'}\n"
            report += f"- Predicted limit hit: {prediction}\n"
            
            blacklisted, reason = self.is_model_blacklisted(model)
            if blacklisted:
                report += f"- ⚠️ **Blacklisted**: {reason}\n"
            
            report += "\n"
        
        # Recent rotation decisions
        report += "## Recent Rotation Decisions\n"
        rotation_log = self.cost_data.get("rotation_log", [])
        recent_logs = rotation_log[-10:]  # Last 10 decisions
        
        for log in recent_logs:
            report += f"- {log.get('timestamp', 'Unknown')}: {log.get('model', 'Unknown')} for '{log.get('task_type', 'Unknown')}' (count: {log.get('daily_count', 0)})\n"
        
        # Recommendations
        report += "\n## Recommendations\n"
        
        gemini_quota = self.get_remaining_quota("google/gemini-2.5-flash-lite")
        if gemini_quota["percentage_used"] > 50:
            report += "1. **Gemini usage high**: Consider switching to Kimi for non-critical tasks\n"
        
        if len(self.cost_data.get("rate_limit_events", [])) > 0:
            report += "2. **Rate limits detected**: System is learning from errors\n"
        
        report += "3. **Monitor DeepSeek**: Consider using more (cheapest option)\n"
        report += "4. **Review time-based schedule**: Adjust based on actual usage patterns\n"
        
        return report

def main():
    print("🤖 Intelligent Model Rotation System - Phase 1")
    print("=" * 50)
    
    rotation = IntelligentRotationSystem()
    
    # Test scenarios
    test_tasks = [
        "Summarize today's work",
        "Research AI memory systems",
        "Complex reasoning analysis",
        "Heartbeat check",
        "Write creative story"
    ]
    
    print("\n🧪 Testing rotation system with sample tasks:\n")
    
    for task in test_tasks:
        print(f"Task: '{task}'")
        best_model = rotation.get_best_model(task)
        quota = rotation.get_remaining_quota(best_model)
        
        print(f"  → Selected: {best_model}")
        print(f"  → Quota: {quota['used']}/{quota['limit']} ({quota['percentage_used']:.1f}%)")
        print(f"  → Remaining: {quota['remaining']} (buffer: {quota['buffer']})")
        
        # Record usage for testing
        rotation.record_usage(best_model, task)
        print()
    
    # Generate report
    print("\n📊 System Report:")
    print("=" * 50)
    print(rotation.generate_rotation_report())
    
    # Save config for reference
    rotation.save_data()
    print(f"\n✅ Configuration saved to: {ROTATION_CONFIG}")
    print(f"✅ Usage data saved to: {COST_FILE}")

if __name__ == "__main__":
    main()
