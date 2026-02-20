#!/usr/bin/env python3
"""
Self-testing tool - verifies my own work.
Checks completion criteria, git status, output quality.
"""

import os
import subprocess
import json
from datetime import datetime

def check_git_status():
    """Check if there are uncommitted changes."""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd='/Users/aiagentuser/.openclaw/workspace')
        if result.stdout.strip():
            print(f"⚠️  Uncommitted changes:\n{result.stdout}")
            return False
        print("✅ All changes committed")
        return True
    except Exception as e:
        print(f"❌ Git check failed: {e}")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists."""
    full_path = f"/Users/aiagentuser/.openclaw/workspace/{filepath}"
    if os.path.exists(full_path):
        size = os.path.getsize(full_path)
        print(f"✅ {description}: {filepath} ({size} bytes)")
        return True
    print(f"❌ {description} missing: {filepath}")
    return False

def check_recent_commits(hours=4):
    """Check if I've committed recently."""
    try:
        result = subprocess.run(['git', 'log', '--oneline', '--since', f'{hours} hours ago'],
                              capture_output=True, text=True, cwd='/Users/aiagentuser/.openclaw/workspace')
        commits = result.stdout.strip().split('\n')
        commits = [c for c in commits if c]
        
        if commits:
            print(f"✅ {len(commits)} commits in last {hours} hours:")
            for c in commits[:3]:
                print(f"   - {c}")
            return True
        print(f"⚠️  No commits in last {hours} hours")
        return False
    except Exception as e:
        print(f"❌ Commit check failed: {e}")
        return False

def verify_phase_completion(phase_name, required_files):
    """Verify a phase is complete."""
    print(f"\n=== Verifying {phase_name} ===")
    all_good = True
    
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    return all_good

def run_self_test():
    """Run complete self-test."""
    print("=== Self-Test Report ===")
    print(f"Time: {datetime.now().strftime('%I:%M %p')}\n")
    
    results = {}
    
    # Git hygiene
    print("Git Hygiene:")
    results['git_clean'] = check_git_status()
    results['recent_commits'] = check_recent_commits()
    
    # Phase 1 verification
    phase1_files = [
        ('scripts/progress-tracker.py', 'Progress tracker'),
        ('scripts/end-of-session-reflection.py', 'Reflection script'),
        ('IMPROVEMENT-PLAN.md', 'Improvement plan'),
    ]
    results['phase1'] = verify_phase_completion('Phase 1', phase1_files)
    
    # Phase 2 verification
    phase2_files = [
        ('MODEL-ROUTING-PLAN.md', 'Model routing plan'),
        ('HYBRID-MEMORY-SPEC.md', 'Hybrid memory spec'),
    ]
    results['phase2'] = verify_phase_completion('Phase 2', phase2_files)
    
    # Summary
    print(f"\n=== Summary ===")
    passed = sum(results.values())
    total = len(results)
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All systems operational")
    elif passed >= total * 0.7:
        print("⚠️  Most systems operational, minor issues")
    else:
        print("❌ Multiple issues detected")
    
    return results

if __name__ == "__main__":
    run_self_test()
