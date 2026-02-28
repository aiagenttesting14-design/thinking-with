#!/usr/bin/env python3
"""
Enhanced Three-Tier Model Router with Quality Scoring

Tier System:
1. Strategic Tier (Opus 4.6): Complexity 8-10, strategic architecture
2. Quality Tier (Sonnet 4.6): Complexity 4-7, creative/analytical work  
3. Efficient Tier (DeepSeek): Complexity 1-3, execution/research
"""

import sys
import re
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from enum import Enum

class TaskType(Enum):
    EXECUTION = "execution"
    RESEARCH = "research"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    STRATEGIC = "strategic"
    ARCHITECTURE = "architecture"
    CODE = "code"
    VERIFICATION = "verification"
    SUMMARY = "summary"
    HEARTBEAT = "heartbeat"

class ModelTier(Enum):
    STRATEGIC = "strategic"
    QUALITY = "quality"
    EFFICIENT = "efficient"

@dataclass
class TaskAnalysis:
    complexity_score: int
    task_types: List[TaskType]
    has_quality_flag: bool
    requires_creativity: bool
    requires_analysis: bool
    requires_strategy: bool
    word_count: int

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
        
        self.keyword_mappings = {
            TaskType.EXECUTION: {"execute", "run", "perform", "do", "complete", "implement", "backup"},
            TaskType.RESEARCH: {"research", "search", "find", "look up", "explore", "weather", "articles"},
            TaskType.ANALYTICAL: {"analyze", "analyse", "evaluate", "assess", "study", "interpret", "impact"},
            TaskType.CREATIVE: {"write", "create", "creative", "compose", "design", "story", "generate"},
            TaskType.STRATEGIC: {"strategic", "strategy", "plan", "roadmap", "vision", "future", "framework"},
            TaskType.ARCHITECTURE: {"architecture", "architectural", "design", "structure", "microservices", "scalable"},
            TaskType.CODE: {"code", "program", "script", "function", "python", "javascript", "api"},
            TaskType.VERIFICATION: {"verify", "test", "check", "review", "validate", "confirm"},
            TaskType.SUMMARY: {"summarize", "summarise", "brief", "extract", "recap", "overview", "notes"},
            TaskType.HEARTBEAT: {"heartbeat", "monitor", "status", "health", "check-in", "ping"}
        }
        
        self.quality_flags = {"high quality", "best quality", "detailed", "comprehensive", "thorough"}
        
        self.complexity_weights = {
            TaskType.HEARTBEAT: 1,
            TaskType.EXECUTION: 2,
            TaskType.SUMMARY: 2,
            TaskType.RESEARCH: 2,
            TaskType.VERIFICATION: 3,
            TaskType.CODE: 4,
            TaskType.ANALYTICAL: 5,
            TaskType.CREATIVE: 6,
            TaskType.STRATEGIC: 8,
            TaskType.ARCHITECTURE: 9
        }
    
    def analyze_task(self, task_description: str) -> TaskAnalysis:
        task_lower = task_description.lower()
        words = set(re.findall(r'\b\w+\b', task_lower))
        
        task_types = []
        for task_type, keywords in self.keyword_mappings.items():
            if words & keywords:
                task_types.append(task_type)
        
        if not task_types:
            task_types = [TaskType.EXECUTION]
        
        has_quality_flag = any(flag in task_lower for flag in self.quality_flags)
        requires_creativity = TaskType.CREATIVE in task_types
        requires_analysis = TaskType.ANALYTICAL in task_types
        requires_strategy = TaskType.STRATEGIC in task_types or TaskType.ARCHITECTURE in task_types
        
        complexity_score = self._calculate_complexity_score(
            task_types, has_quality_flag, requires_creativity,
            requires_analysis, requires_strategy, len(words)
        )
        
        return TaskAnalysis(
            complexity_score=complexity_score,
            task_types=task_types,
            has_quality_flag=has_quality_flag,
            requires_creativity=requires_creativity,
            requires_analysis=requires_analysis,
            requires_strategy=requires_strategy,
            word_count=len(words)
        )
    
    def _calculate_complexity_score(self, task_types, has_quality_flag,
                                   requires_creativity, requires_analysis,
                                   requires_strategy, word_count):
        base_score = 0
        for task_type in task_types:
            weight = self.complexity_weights.get(task_type, 2)
            base_score = max(base_score, weight)
        
        adjustments = 0
        if has_quality_flag:
            adjustments += 1
        if requires_creativity and not requires_strategy:
            adjustments += 1
        if requires_analysis and not requires_strategy:
            adjustments += 1
        
        if word_count > 50:
            adjustments += 1
        if word_count > 100:
            adjustments += 1
        
        final_score = base_score + adjustments
        if requires_strategy:
            final_score = min(9, max(8, final_score))
        
        return min(10, max(1, final_score))
    
    def route_task(self, task_description: str) -> Tuple[ModelTier, str, TaskAnalysis]:
        analysis = self.analyze_task(task_description)
        
        if analysis.complexity_score >= 8:
            tier = ModelTier.STRATEGIC
        elif analysis.complexity_score >= 4:
            tier = ModelTier.QUALITY
        else:
            tier = ModelTier.EFFICIENT
        
        if analysis.has_quality_flag and tier == ModelTier.EFFICIENT:
            tier = ModelTier.QUALITY
        
        return tier, self.models[tier], analysis
    
    def print_report(self, task: str, tier: ModelTier, model: str, analysis: TaskAnalysis):
        print("\n" + "="*60)
        print("THREE-TIER MODEL ROUTER")
        print("="*60)
        print(f"Task: '{task}'")
        print(f"Word count: {analysis.word_count}")
        
        print("\n" + "-"*60)
        print("ANALYSIS")
        print("-"*60)
        print(f"Complexity: {analysis.complexity_score}/10")
        print(f"Types: {', '.join([t.value for t in analysis.task_types])}")
        print(f"Quality flag: {'Yes' if analysis.has_quality_flag else 'No'}")
        print(f"Creative: {'Yes' if analysis.requires_creativity else 'No'}")
        print(f"Analytical: {'Yes' if analysis.requires_analysis else 'No'}")
        print(f"Strategic: {'Yes' if analysis.requires_strategy else 'No'}")
        
        print("\n" + "-"*60)
        print("ROUTING")
        print("-"*60)
        print(f"Tier: {tier.value.upper()}")
        print(f"Model: {model}")
        
        if tier == ModelTier.STRATEGIC:
            print("Reason: High complexity (8-10) - strategic/architecture")
        elif tier == ModelTier.QUALITY:
            print("Reason: Medium complexity (4-7) - creative/analytical")
        else:
            print("Reason: Low complexity (1-3) - efficient execution/research")
        
        print("\n" + "-"*60)
        print("COST")
        print("-"*60)
        cost = self.costs[tier]
        task_cost = cost * 2  # 2K tokens
        print(f"Cost: ${cost:.4f}/1K tokens")
        print(f"Task cost: ${task_cost:.4f} (2K tokens)")
        
        # Savings vs Opus
        opus_cost = self.costs[ModelTier.STRATEGIC] * 2
        savings = opus_cost - task_cost
        if savings > 0:
            print(f"Savings vs Opus: ${savings:.4f} ({savings/opus_cost*100:.0f}%)")
        
        print("="*60 + "\n")

def test_router():
    router = ModelRouter()
    
    tests = [
        ("Design microservices architecture for e-commerce", 9, ModelTier.STRATEGIC),
        ("Create 5-year AI strategy roadmap", 8, ModelTier.STRATEGIC),
        ("Write analysis of AI advancements", 7, ModelTier.QUALITY),
        ("Create creative robot story", 6, ModelTier.QUALITY),
        ("Analyze economic impact", 5, ModelTier.QUALITY),
        ("Write high quality documentation", 4, ModelTier.QUALITY),
        ("Research weather", 2, ModelTier.EFFICIENT),
        ("Summarize notes", 2, ModelTier.EFFICIENT),
        ("Execute backup", 3, ModelTier.EFFICIENT),
        ("Check status", 1, ModelTier.EFFICIENT),
    ]
    
    print("TEST SUITE")
    print("="*60)
    
    passed = 0
    for task, expected_score, expected_tier in tests:
        tier, model, analysis = router.route_task(task)
        
        score_ok = analysis.complexity_score == expected_score
        tier_ok = tier == expected_tier
        
        if score_ok and tier_ok:
            passed += 1
            result = "PASS"
        else:
            result = "FAIL"
        
        print(f"\n{task[:40]:<40} Score: {analysis.complexity_score:2d}/10 (exp: {expected_score:2d}) "
              f"Tier: {tier.value.upper():<9} {result}")
        
        if not score_ok or not tier_ok:
            print(f"  Expected: {expected_tier.value.upper()}, Score: {expected_score}")
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed}/{len(tests)} passed ({passed/len(tests)*100:.0f}%)")
    print("="*60)
    
    # Demo some examples
    print("\n\nDEMO EXAMPLES:")
    print("="*60)
    
    demo_tasks = [
        "Design a scalable system architecture",
        "Write a creative story with high quality",
        "Research machine learning trends",
        "Analyze financial data thoroughly"
    ]
    
    for task in demo_tasks:
        tier, model, analysis = router.route_task(task)
        router.print_report(task, tier, model, analysis)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 model_router_final.py '<task>'")
        print("       python3 model_router_final.py --test")
        print("\nExamples:")
        print("  python3 model_router_final.py 'Design system architecture'")
        print("  python3 model_router_final.py 'Write creative story'")
        print("  python3 model_router_final.py 'Research AI trends'")
        return
    
    if sys.argv[1] == "--test":
        test_router()
        return
    
    task = " ".join(sys.argv[1:])
    router = ModelRouter()
    tier, model, analysis = router.route_task(task)
    router.print_report(task, tier, model, analysis)

if __name__ == "__main__":
    main()
