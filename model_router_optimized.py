#!/usr/bin/env python3
"""
Optimized Three-Tier Model Router

Tier System:
1. Strategic Tier (Opus 4.6): Complexity 8-10
2. Quality Tier (Sonnet 4.6): Complexity 4-7  
3. Efficient Tier (DeepSeek): Complexity 1-3
"""

import sys
import re
from typing import Dict, List, Tuple
from enum import Enum

class TaskType(Enum):
    SIMPLE = "simple"
    RESEARCH = "research"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    STRATEGIC = "strategic"
    ARCHITECTURE = "architecture"

class ModelTier(Enum):
    STRATEGIC = "strategic"
    QUALITY = "quality"
    EFFICIENT = "efficient"

class ModelRouter:
    def __init__(self):
        self.models = {
            ModelTier.STRATEGIC: "anthropic/claude-opus-4-6",
            ModelTier.QUALITY: "anthropic/claude-sonnet-4-6",
            ModelTier.EFFICIENT: "deepseek/deepseek-chat"
        }
        
        self.costs = {
            ModelTier.STRATEGIC: 0.015,
            ModelTier.QUALITY: 0.003,
            ModelTier.EFFICIENT: 0.00014
        }
        
        # Simplified keyword detection
        self.keywords = {
            "architecture": {"architecture", "architectural", "microservices", "scalable", "framework"},
            "strategic": {"strategic", "strategy", "roadmap", "vision", "plan", "future"},
            "creative": {"write", "create", "creative", "story", "narrative", "compose"},
            "analytical": {"analyze", "analyse", "evaluate", "assess", "study", "interpret"},
            "research": {"research", "search", "find", "explore", "investigate"},
            "simple": {"check", "status", "execute", "run", "backup", "summarize", "notes"}
        }
        
        self.quality_words = {"high quality", "detailed", "thorough", "comprehensive", "best"}
    
    def analyze_task(self, task: str) -> dict:
        """Analyze task and return complexity score and characteristics"""
        task_lower = task.lower()
        words = set(re.findall(r'\b\w+\b', task_lower))
        
        # Detect characteristics
        is_architecture = bool(words & self.keywords["architecture"])
        is_strategic = bool(words & self.keywords["strategic"])
        is_creative = bool(words & self.keywords["creative"])
        is_analytical = bool(words & self.keywords["analytical"])
        is_research = bool(words & self.keywords["research"])
        is_simple = bool(words & self.keywords["simple"])
        
        has_quality = any(q in task_lower for q in self.quality_words)
        word_count = len(words)
        
        # Calculate base complexity
        if is_architecture:
            base = 9
        elif is_strategic:
            base = 8
        elif is_creative:
            base = 6
        elif is_analytical:
            base = 5
        elif is_research:
            base = 3
        elif is_simple:
            base = 2
        else:
            base = 3  # Default
        
        # Adjustments
        adjustments = 0
        if has_quality:
            adjustments += 1
        if word_count > 30:
            adjustments += 1
        if word_count > 60:
            adjustments += 1
        
        # Special cases
        if "documentation" in words and not (is_architecture or is_strategic):
            base = 4  # Documentation is medium complexity
        
        if "heartbeat" in words or "status" in words:
            base = 1  # Heartbeat/status checks are simplest
        
        # Calculate final score
        score = base + adjustments
        score = min(10, max(1, score))
        
        return {
            "score": score,
            "is_architecture": is_architecture,
            "is_strategic": is_strategic,
            "is_creative": is_creative,
            "is_analytical": is_analytical,
            "is_research": is_research,
            "is_simple": is_simple,
            "has_quality": has_quality,
            "word_count": word_count
        }
    
    def route_task(self, task: str) -> Tuple[ModelTier, str, dict]:
        """Route task to appropriate model"""
        analysis = self.analyze_task(task)
        score = analysis["score"]
        
        if score >= 8:
            tier = ModelTier.STRATEGIC
        elif score >= 4:
            tier = ModelTier.QUALITY
        else:
            tier = ModelTier.EFFICIENT
        
        # Quality override: bump up one tier if quality requested
        if analysis["has_quality"] and tier == ModelTier.EFFICIENT:
            tier = ModelTier.QUALITY
        
        return tier, self.models[tier], analysis
    
    def print_report(self, task: str):
        """Print routing report for a task"""
        tier, model, analysis = self.route_task(task)
        
        print("\n" + "="*60)
        print("MODEL ROUTER REPORT")
        print("="*60)
        print(f"Task: {task}")
        print(f"Words: {analysis['word_count']}")
        
        print("\nAnalysis:")
        print(f"  Complexity score: {analysis['score']}/10")
        traits = []
        if analysis["is_architecture"]: traits.append("architecture")
        if analysis["is_strategic"]: traits.append("strategic")
        if analysis["is_creative"]: traits.append("creative")
        if analysis["is_analytical"]: traits.append("analytical")
        if analysis["is_research"]: traits.append("research")
        if analysis["is_simple"]: traits.append("simple")
        if analysis["has_quality"]: traits.append("quality-requested")
        print(f"  Traits: {', '.join(traits) if traits else 'none'}")
        
        print(f"\nRouting: {tier.value.upper()} tier")
        print(f"Model: {model}")
        
        print(f"\nCost: ${self.costs[tier]:.4f}/1K tokens")
        task_cost = self.costs[tier] * 2  # 2K tokens
        print(f"Estimated task cost: ${task_cost:.4f}")
        
        # Compare with Opus
        opus_cost = self.costs[ModelTier.STRATEGIC] * 2
        if tier != ModelTier.STRATEGIC:
            savings = opus_cost - task_cost
            print(f"Savings vs Opus: ${savings:.4f} ({savings/opus_cost*100:.0f}%)")
        
        print("="*60)

def run_comprehensive_test():
    """Run comprehensive test suite"""
    router = ModelRouter()
    
    test_cases = [
        # (task, expected_score, expected_tier)
        ("Design microservices architecture", 9, ModelTier.STRATEGIC),
        ("Create strategic roadmap", 8, ModelTier.STRATEGIC),
        ("Write creative story", 6, ModelTier.QUALITY),
        ("Write high quality creative story", 7, ModelTier.QUALITY),
        ("Analyze data", 5, ModelTier.QUALITY),
        ("Write documentation", 4, ModelTier.QUALITY),
        ("Write high quality documentation", 5, ModelTier.QUALITY),
        ("Research trends", 3, ModelTier.EFFICIENT),
        ("Summarize notes", 2, ModelTier.EFFICIENT),
        ("Execute backup", 3, ModelTier.EFFICIENT),
        ("Check status", 1, ModelTier.EFFICIENT),
        ("Send heartbeat", 1, ModelTier.EFFICIENT),
    ]
    
    print("COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    results = []
    for task, exp_score, exp_tier in test_cases:
        tier, model, analysis = router.route_task(task)
        
        score_match = analysis["score"] == exp_score
        tier_match = tier == exp_tier
        passed = score_match and tier_match
        
        results.append({
            "task": task,
            "passed": passed,
            "score": analysis["score"],
            "exp_score": exp_score,
            "tier": tier.value,
            "exp_tier": exp_tier.value
        })
        
        status = "✓" if passed else "✗"
        print(f"{status} {task:<35} Score: {analysis['score']:2d}/10 (exp: {exp_score:2d}) "
              f"Tier: {tier.value.upper():<9}")
        
        if not passed:
            if not score_match:
                print(f"    Score mismatch: got {analysis['score']}, expected {exp_score}")
            if not tier_match:
                print(f"    Tier mismatch: got {tier.value.upper()}, expected {exp_tier.value.upper()}")
    
    # Summary
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed}/{total} passed ({passed/total*100:.0f}%)")
    
    # Show distribution
    print("\nTier Distribution:")
    tier_counts = {}
    for r in results:
        tier = r["tier"]
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    for tier, count in tier_counts.items():
        print(f"  {tier.upper()}: {count} tasks")
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Three-Tier Model Router")
        print("Usage: python3 model_router_optimized.py '<task>'")
        print("       python3 model_router_optimized.py --test")
        print("\nExamples:")
        print("  python3 model_router_optimized.py 'Design system architecture'")
        print("  python3 model_router_optimized.py 'Write creative story'")
        print("  python3 model_router_optimized.py 'Research AI trends'")
        print("  python3 model_router_optimized.py 'Check system status'")
        return
    
    if sys.argv[1] == "--test":
        run_comprehensive_test()
        return
    
    task = " ".join(sys.argv[1:])
    router = ModelRouter()
    router.print_report(task)

if __name__ == "__main__":
    main()
