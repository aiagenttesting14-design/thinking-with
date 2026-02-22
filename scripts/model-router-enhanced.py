#!/usr/bin/env python3
"""
Enhanced Model Router with Intelligent Rotation
Combines task-based routing with quota-aware rotation
"""

import sys
import os
import json
from datetime import datetime

class EnhancedModelRouter:
    def __init__(self):
        self.rotation_system = None
        try:
            # Import the rotation system module
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            import importlib.util
            
            spec = importlib.util.spec_from_file_location(
                "intelligent_rotation", 
                os.path.join(os.path.dirname(__file__), "intelligent-rotation-v1.py")
            )
            intelligent_rotation = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(intelligent_rotation)
            
            self.rotation_system = intelligent_rotation.IntelligentRotationSystem()
            print("✅ Intelligent rotation system loaded")
        except Exception as e:
            print(f"⚠️ Failed to load rotation system: {e}")
            print("⚠️ Using basic routing only")
            self.rotation_system = None
    
    def get_model_for_task(self, task_description, force_model=None):
        """Get the best model for a task with intelligent rotation"""
        
        # If force model is specified, use it (for testing or overrides)
        if force_model:
            print(f"🔧 Using forced model: {force_model}")
            if self.rotation_system:
                self.rotation_system.record_usage(force_model, task_description)
            return force_model
        
        # Use intelligent rotation if available
        if self.rotation_system:
            try:
                best_model = self.rotation_system.get_best_model(task_description)
                self.rotation_system.record_usage(best_model, task_description)
                return best_model
            except Exception as e:
                print(f"⚠️ Rotation system error: {e}. Falling back to basic routing.")
        
        # Fallback to basic task-based routing
        return self.get_basic_model_for_task(task_description)
    
    def get_basic_model_for_task(self, task_description):
        """Basic task-based model selection (compatible with original)"""
        task = task_description.lower()
        
        # Word-based matching (from original router)
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
    
    def handle_rate_limit(self, model, error_message):
        """Handle rate limit errors with intelligent system"""
        if self.rotation_system:
            self.rotation_system.record_rate_limit(model, error_message)
            print(f"⚠️ Rate limit handled by intelligent system")
            
            # Get fallback recommendation
            fallback = self.rotation_system.get_best_model("fallback after rate limit")
            print(f"🔄 Recommended fallback: {fallback}")
            return fallback
        else:
            print(f"⚠️ Rate limit for {model}. Basic fallback to Kimi.")
            return "moonshot/kimi-k2.5"
    
    def generate_report(self):
        """Generate routing report"""
        if self.rotation_system:
            return self.rotation_system.generate_rotation_report()
        else:
            return "Basic routing system (intelligent rotation not available)"
    
    def get_cost_comparison(self, model):
        """Get cost comparison for a model"""
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
                claude_cost = cost_per_1k["claude-sonnet-4-5"]
                savings_pct = ((claude_cost - cost) / claude_cost) * 100
                
                return {
                    "cost_per_1k": cost,
                    "savings_vs_claude": savings_pct,
                    "claude_cost": claude_cost
                }
        
        return {"cost_per_1k": 0.003, "savings_vs_claude": 0, "claude_cost": 0.003}

def main():
    if len(sys.argv) < 2:
        print("Enhanced Model Router with Intelligent Rotation")
        print("=" * 50)
        print("Usage: python3 model-router-enhanced.py '<task description>' [force_model]")
        print("\nExamples:")
        print("  python3 model-router-enhanced.py 'Summarize findings'")
        print("  python3 model-router-enhanced.py 'Research AI systems'")
        print("  python3 model-router-enhanced.py 'Complex analysis'")
        print("  python3 model-router-enhanced.py 'Test task' google/gemini-2.5-flash-lite")
        print("\nOptions:")
        print("  force_model: Optional model to force (for testing)")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:-1]) if len(sys.argv) > 2 else sys.argv[1]
    force_model = sys.argv[-1] if len(sys.argv) > 2 and sys.argv[-1].startswith(("google/", "moonshot/", "claude", "deepseek")) else None
    
    router = EnhancedModelRouter()
    
    print(f"\n🎯 Task: '{task}'")
    
    # Get model recommendation
    model = router.get_model_for_task(task, force_model)
    
    print(f"🤖 Recommended model: {model}")
    
    # Cost analysis
    cost_info = router.get_cost_comparison(model)
    print(f"💰 Cost: ${cost_info['cost_per_1k']:.4f} per 1K tokens")
    
    if cost_info['savings_vs_claude'] > 0:
        print(f"💸 Savings vs Claude: {cost_info['savings_vs_claude']:.0f}%")
    
    # Typical task cost (2K tokens)
    tokens_estimate = 2000
    task_cost = cost_info['cost_per_1k'] * (tokens_estimate / 1000)
    claude_task_cost = cost_info['claude_cost'] * (tokens_estimate / 1000)
    savings = claude_task_cost - task_cost
    
    print(f"📊 Task cost (2K tokens): ${task_cost:.4f}")
    print(f"📊 Claude cost (2K tokens): ${claude_task_cost:.4f}")
    print(f"💵 Savings per task: ${savings:.4f}")
    
    # Monthly projection
    daily_tasks = 5
    monthly_savings = savings * daily_tasks * 30
    print(f"📈 Monthly savings projection: ${monthly_savings:.2f}")
    
    # If rotation system is available, show quota info
    if router.rotation_system:
        print("\n📋 Rotation System Status:")
        print("-" * 30)
        
        quota = router.rotation_system.get_remaining_quota(model)
        print(f"Quota: {quota['used']}/{quota['limit']} ({quota['percentage_used']:.1f}%)")
        print(f"Remaining: {quota['remaining']} (buffer: {quota['buffer']})")
        
        prediction = router.rotation_system.predict_limit_hit_time(model)
        print(f"Predicted limit hit: {prediction}")
        
        blacklisted, reason = router.rotation_system.is_model_blacklisted(model)
        if blacklisted:
            print(f"⚠️ Warning: Model is blacklisted ({reason})")
    
    print("\n" + "=" * 50)
    print("✅ Enhanced routing complete")

if __name__ == "__main__":
    main()
