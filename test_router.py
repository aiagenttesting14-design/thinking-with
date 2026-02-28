#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from model_router import ModelRouter

router = ModelRouter()

# Test cases
test_cases = [
    ("Design a scalable microservices architecture for a global e-commerce platform", 9),
    ("Create a 5-year strategic roadmap for AI adoption in enterprise", 8),
    ("Write a detailed analysis of recent AI advancements", 7),
    ("Create a creative short story about a robot", 6),
    ("Analyze the economic impact of renewable energy", 5),
    ("Write high quality documentation", 4),
    ("Research current weather", 2),
    ("Summarize meeting notes", 2),
    ("Execute backup script", 3),
    ("Check system status", 1),
]

print("Testing Model Router")
print("=" * 60)

for task, expected in test_cases:
    tier, model, analysis = router.route_task(task)
    print(f"\nTask: {task[:40]}...")
    print(f"  Score: {analysis.complexity_score}/10 (expected: {expected})")
    print(f"  Tier: {tier.value.upper()}")
    print(f"  Model: {model}")
    print(f"  Result: {'PASS' if analysis.complexity_score == expected else 'FAIL'}")
