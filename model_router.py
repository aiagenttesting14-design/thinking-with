#!/usr/bin/env python3
"""
Enhanced Three-Tier Model Router with Quality Scoring

Tier System:
1. Strategic Tier (Opus 4.6): Complexity 8-10, strategic architecture
2. Quality Tier (Sonnet 4.6): Complexity 4-7, creative/analytical work  
3. Efficient Tier (DeepSeek): Complexity 1-3, execution/research

Features:
- Complexity scoring algorithm (1-10)
- Considers task type, quality requirements, creative vs analytical
- Explicit quality flags from user
- Test suite with sample tasks
- Documented routing decisions
"""

import sys
import re
import json
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from enum import Enum

class TaskType(Enum):
    """Types of tasks for complexity scoring"""
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
    """Three-tier model system"""
    STRATEGIC = "strategic"      # Opus 4.6
    QUALITY = "quality"          # Sonnet 4.6
    EFFICIENT = "efficient"      # DeepSeek

@dataclass
class TaskAnalysis:
    """Analysis of a task for routing decisions"""
    complexity_score: int
    task_types: List[TaskType]
    has_quality_flag: bool
    requires_creativity: bool
    requires_analysis: bool
    requires_strategy: bool
    word_count: int
    keywords: Set[str]

class ModelRouter:
    """Enhanced three-tier model router with quality scoring"""
    
    def __init__(self):
        # Model mappings
        self.models = {
            ModelTier.STRATEGIC: "anthropic/claude-opus-4-6",
            ModelTier.QUALITY: "anthropic/claude-sonnet-4-6",
            ModelTier.EFFICIENT: "deepseek/deepseek-chat"
        }
        
        # Cost per 1K tokens (approximate)
        self.costs = {
            ModelTier.STRATEGIC: 0.015,      # Opus 4.6
            ModelTier.QUALITY: 0.003,        # Sonnet 4.6
            ModelTier.EFFICIENT: 0.00014     # DeepSeek
        }
        
        # Keyword mappings for task type detection (improved)
        self.keyword_mappings = {
            TaskType.EXECUTION: {
                "execute", "run", "perform", "do", "complete", "implement",
                "carry out", "action", "task", "operation", "backup"
            },
            TaskType.RESEARCH: {
                "research", "search", "investigate", "find", "look up",
                "explore", "discover", "scan", "gather", "collect", "weather"
            },
            TaskType.ANALYTICAL: {
                "analyze", "analyse", "evaluate", "assess", "critique",
                "examine", "study", "interpret", "understand", "break down",
                "reason", "logic", "critical", "comparison", "compare", "impact"
            },
            TaskType.CREATIVE: {
                "write", "create", "creative", "compose", "design",
                "invent", "imagine", "story", "essay", "article",
                "poem", "narrative", "fiction", "original", "generate"
            },
            TaskType.STRATEGIC: {
                "strategic", "strategy", "plan", "roadmap", "vision",
                "direction", "future", "long-term", "high-level",
                "decision", "choose", "select", "prioritize", "framework"
            },
            TaskType.ARCHITECTURE: {
                "architecture", "architectural", "design", "structure", "framework",
                "blueprint", "model", "pattern", "scalable",
                "robust", "reliable", "foundation", "microservices"
            },
            TaskType.CODE: {
                "code", "program", "script", "function", "algorithm",
                "python", "javascript", "html", "css", "java", "c++",
                "develop", "software", "application", "api", "debug"
            },
            TaskType.VERIFICATION: {
                "verify", "test", "check", "audit", "review",
                "validate", "confirm", "ensure", "proofread", "quality"
            },
            TaskType.SUMMARY: {
                "summarize", "summarise", "brief", "quick", "short", "extract",
                "recap", "overview", "abstract", "synopsis", "condense", "notes"
            },
            TaskType.HEARTBEAT: {
                "heartbeat", "monitor", "status", "health", "periodic",
                "check-in", "alive", "ping", "routine", "maintenance"
            }
        }
        
        # Exclude words from architecture detection
        self.architecture_exclusions = {"system", "status"}
        
        # Quality flag indicators
        self.quality_flags = {
            "high quality", "best quality", "excellent", "premium",
            "thorough", "detailed", "comprehensive", "careful",
            "accurate", "precise", "meticulous", "polished"
        }
        
        # Complexity weightings (refined)
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
        
        # Word count thresholds for complexity adjustment
        self.word_thresholds = {
            10: 0,   # Very short
            20: 0,   # Short tasks
            40: 1,   # Medium tasks
            60: 2    # Long tasks
        }
    
    def analyze_task(self, task_description: str) -> TaskAnalysis:
        """Analyze task and compute complexity score"""
        task_lower = task_description.lower()
        words = set(re.findall(r'\b\w+\b', task_lower))
        
        # Detect task types with improved logic
        task_types = []
        detected_types = set()
        
        for task_type, keywords in self.keyword_mappings.items():
            # Check for keyword matches
            matched_keywords = words & keywords
            if matched_keywords:
                # Special handling for architecture to avoid false positives
                if task_type == TaskType.ARCHITECTURE:
                    # Exclude common words that shouldn't trigger architecture
                    filtered_matches = matched_keywords - self.architecture_exclusions
                    if filtered_matches:
                        task_types.append(task_type)
                        detected_types.add(task_type)
                else:
                    task_types.append(task_type)
                    detected_types.add(task_type)
        
        # If no specific types detected, use default
        if not task_types:
            task_types = [TaskType.EXECUTION]
            detected_types.add(TaskType.EXECUTION)
        
        # Check for quality flags
        has_quality_flag = any(
            flag in task_lower for flag in self.quality_flags
        )
        
        # Check for creativity/analysis/strategy requirements
        requires_creativity = TaskType.CREATIVE in detected_types
        requires_analysis = TaskType.ANALYTICAL in detected_types
        requires_strategy = (TaskType.STRATEGIC in detected_types or 
                           TaskType.ARCHITECTURE in detected_types)
        
        # Calculate complexity score (1-10)
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
            word_count=len(words),
            keywords=words
        )
    
    def _calculate_complexity_score(self, task_types: List[TaskType],
                                   has_quality_flag: bool,
                                   requires_creativity: bool,
                                   requires_analysis: bool,
                                   requires_strategy: bool,
                                   word_count: int) -> int:
        """Calculate complexity score from 1-10"""
        # Base score from task types (use highest weight)
        base_score = 0
        type_weights = []
        
        for task_type in task_types:
            weight = self.complexity_weights.get(task_type, 2)
            type_weights.append(weight)
            base_score = max(base_score, weight)
        
        # If we have multiple types, average them (but keep max as minimum)
        if len(type_weights) > 1:
            avg_weight = sum(type_weights) / len(type_weights)
            base_score = max(base_score, avg_weight)
        
        # Adjustments (more conservative)
        adjustments = 0
        
        # Quality flag adds moderate weight (capped)
        if has_quality_flag:
            adjustments += 0.5  # Reduced from 1
        
        # Creativity and analysis add moderate weight (but not cumulative)
        if requires_creativity and not requires_strategy:
            adjustments += 0.5
        if requires_analysis and not requires_strategy:
            adjustments += 0.5
        
        # Word count adjustment (more nuanced)
        for threshold, adjustment in sorted(self.word_thresholds.items()):
            if word_count > threshold:
                adjustments += adjustment
            else:
                break
        
        # Calculate final score (clamped to 1-10, rounded)
        raw_score = base_score + adjustments
        final_score = min(10, max(1, round(raw_score)))
        
        # Special cases
        if requires_strategy:
            # Strategic tasks should be 8-9, not 10
            final_score = min(9, final_score)
            final_score = max(8, final_score)
        
        return final_score
    
    def route_task(self, task_description: str) -> Tuple[ModelTier, str, TaskAnalysis]:
        """Route task to appropriate model tier"""
        analysis = self.analyze_task(task_description)
        
        # Routing logic based on complexity score
        if analysis.complexity_score >= 8:
            tier = ModelTier.STRATEGIC
        elif analysis.complexity_score >= 4:
            tier = ModelTier.QUALITY
        else:
            tier = ModelTier.EFFICIENT
        
        # Override: if user explicitly asks for quality, bump up one tier
        if analysis.has_quality_flag and tier == ModelTier.EFFICIENT:
            tier = ModelTier.QUALITY
        
        model = self.models[tier]
        
        return tier, model, analysis
    
    def get_cost_analysis(self, tier: ModelTier, estimated_tokens: int = 2000) -> Dict:
        """Get cost analysis for a model tier"""
        cost_per_1k = self.costs[tier]
        task_cost = cost_per_1k * (estimated_tokens / 1000)
        
        # Compare with other tiers
        comparisons = {}
        for other_tier in ModelTier:
            if other_tier != tier:
                other_cost = self.costs[other_tier] * (estimated_tokens / 1000)
                savings = other_cost - task_cost
                savings_pct = (savings / other_cost * 100) if other_cost > 0 else 0
                comparisons[other_tier.value] = {
                    "cost": other_cost,
                    "savings": savings,
                    "savings_pct": savings_pct
                }
        
        return {
            "tier": tier.value,
            "model": self.models[tier],
            "cost_per_1k": cost_per_1k,
            "estimated_tokens": estimated_tokens,
            "task_cost": task_cost,
            "comparisons": comparisons
        }
    
    def print_routing_report(self, task: str, tier: ModelTier, 
                           model: str, analysis: TaskAnalysis):
        """Print detailed routing report"""
        cost_analysis = self.get_cost_analysis(tier)
        
        print("\n" + "="*60)
        print("ENHANCED THREE-TIER MODEL ROUTER")
        print("="*60)
        print(f"Task: '{task}'")
        print(f"Word count: {analysis.word_count}")
        
        # Show top keywords
        keywords_list = sorted(analysis.keywords)
        if keywords_list:
            print(f"Keywords detected: {', '.join(keywords_list[:10])}")
        
        print("\n" + "-"*60)
        print("TASK ANALYSIS")
        print("-"*60)
        print(f"Complexity score: {analysis.complexity_score}/10")
        print(f"Task types: {', '.join([t.value for t in analysis.task_types])}")
        print(f"Quality flag detected: {'Yes' if analysis.has_quality_flag else 'No'}")
        print(f"Requires creativity: {'Yes' if analysis.requires_creativity else 'No'}")
        print(f"Requires analysis: {'Yes' if analysis.requires_analysis else 'No'}")
        print(f"Requires strategy: {'Yes' if analysis.requires_strategy else 'No'}")
        
        print("\n" + "-"*60)
        print("ROUTING DECISION")
        print("-"*60)
        print(f"Tier: {tier.value.upper()}")
        print(f"Model: {model}")
        print(f"Reasoning: ", end="")
        
        if tier == ModelTier.STRATEGIC:
            print("High complexity (8-10) requiring strategic thinking or architecture")
        elif tier == ModelTier.QUALITY:
            print("Medium complexity (4-7) requiring creative/analytical work")
        else:
            print("Low complexity (1-3) suitable for efficient execution/research")
        
        print("\n" + "-"*60)
        print("COST ANALYSIS")
        print("-"*60)
        print(f"Model cost: ${cost_analysis['cost_per_1k']:.4f} per 1K tokens")
        print(f"Task cost (2K tokens): ${cost_analysis['task_cost']:.4f}")
        
        # Show savings compared to other tiers
        print("\nSavings compared to other tiers:")
        for other_tier, comparison in cost_analysis['comparisons'].items():
            savings = comparison['savings']
            if savings > 0:
                print(f"  vs {other_tier.upper()}: Save ${savings:.4f} ({comparison['savings_pct']:.0f}%)")
            else:
                print(f"  vs {other_tier.upper()}: Extra ${-savings:.4f}")
        
        # Monthly projection
        daily_tasks = 5
        monthly_savings_vs_opus = (
            self.costs[ModelTier.STRATEGIC] - cost_analysis['cost_per_1k']
        ) * (estimated_tokens / 1000) * daily_tasks * 30
        
        if monthly_savings_vs_opus > 0:
            print(f"\nMonthly savings vs Opus: ${monthly_savings_vs_opus:.2f}")
        
        print("="*60 + "\n")

def run_tests():
    """Run test suite with sample tasks"""
    router = ModelRouter()
    
    test_tasks = [
        # Strategic Tier (8-10)
        ("Design a scalable microservices architecture for a global e-commerce platform", 9),
        ("Create a 5-year strategic roadmap for AI adoption in enterprise", 8),
        ("Develop a comprehensive risk assessment framework for financial systems", 8),
        
        # Quality Tier (4-7)
        ("Write a detailed analysis of recent AI advancements in natural language processing", 7),
        ("Create a creative short story about a robot discovering emotions", 6),
        ("Analyze the economic impact of renewable energy policies", 5),
        ("Write high quality documentation for the new API endpoints", 4),
        
        # Efficient Tier (1-3)
        ("Research current weather in San Francisco", 2),
        ("Summarize the main points from the meeting notes", 2),
        ("Execute the backup script and verify completion", 3),
        ("Check system status and send heartbeat", 1),
        ("Find recent articles about machine learning", 2),
    ]
    
    print("RUNNING TEST SUITE")
    print("="*60)
    
    results = []
    for task, expected_complexity in test_tasks:
        tier, model, analysis = router.route_task(task)
        results.append({
            "task": task[:50] + "..." if len(task) > 50 else task,
            "expected_complexity": expected_complexity,
            "actual_complexity": analysis.complexity_score,
            "tier": tier.value,
            "model": model,
            "match": analysis.complexity_score == expected_complexity
        })
        
        # Print individual test result
        print(f"\nTest: {task[:60]}...")
        print(f"  Expected: {expected_complexity}/10, Actual: {analysis.complexity_score}/10")
        print(f"  Tier: {tier.value.upper()}, Model: {model}")
        print(f"  Result: {'PASS' if analysis.complexity_score == expected_complexity else 'FAIL'}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for