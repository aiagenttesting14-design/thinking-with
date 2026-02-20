#!/usr/bin/env python3
"""
Audit trail logger - records decisions, actions, outcomes.
Structured logging for accountability and review.
"""

import json
import os
from datetime import datetime

AUDIT_LOG = "/Users/aiagentuser/.openclaw/workspace/audit-log.json"

def log_entry(entry_type, action, rationale, outcome="", metadata=None):
    """Log an audit entry."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": entry_type,  # decision, action, error, milestone
        "action": action,
        "rationale": rationale,
        "outcome": outcome,
        "metadata": metadata or {}
    }
    
    # Load existing or create new
    try:
        with open(AUDIT_LOG, 'r') as f:
            log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log = {"entries": []}
    
    log["entries"].append(entry)
    
    with open(AUDIT_LOG, 'w') as f:
        json.dump(log, f, indent=2)
    
    print(f"📝 Logged: {entry_type} - {action}")
    return entry

def log_decision(action, rationale, outcome=""):
    """Log a decision I made."""
    return log_entry("decision", action, rationale, outcome)

def log_action(action, rationale, outcome=""):
    """Log an action I took."""
    return log_entry("action", action, rationale, outcome)

def log_error(action, error, rationale=""):
    """Log an error or failure."""
    return log_entry("error", action, rationale, str(error))

def log_milestone(action, outcome):
    """Log a completed milestone."""
    return log_entry("milestone", action, "Achievement", outcome)

def show_recent(limit=5):
    """Show recent audit entries."""
    try:
        with open(AUDIT_LOG, 'r') as f:
            log = json.load(f)
        
        entries = log.get("entries", [])
        recent = entries[-limit:]
        
        print(f"\n=== Recent Audit Entries ===\n")
        for e in reversed(recent):
            time = datetime.fromisoformat(e['timestamp']).strftime('%I:%M %p')
            print(f"{time} [{e['type'].upper()}]")
            print(f"  Action: {e['action']}")
            if e['rationale']:
                print(f"  Why: {e['rationale']}")
            if e['outcome']:
                print(f"  Result: {e['outcome']}")
            print()
            
    except (FileNotFoundError, json.JSONDecodeError):
        print("No audit log found.")

def show_stats():
    """Show audit statistics."""
    try:
        with open(AUDIT_LOG, 'r') as f:
            log = json.load(f)
        
        entries = log.get("entries", [])
        types = {}
        
        for e in entries:
            t = e['type']
            types[t] = types.get(t, 0) + 1
        
        print("\n=== Audit Statistics ===")
        print(f"Total entries: {len(entries)}")
        for t, count in sorted(types.items()):
            print(f"  {t}: {count}")
            
    except (FileNotFoundError, json.JSONDecodeError):
        print("No audit log found.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        show_recent()
    elif sys.argv[1] == "decision":
        log_decision(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "", 
                    sys.argv[4] if len(sys.argv) > 4 else "")
    elif sys.argv[1] == "action":
        log_action(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "",
                  sys.argv[4] if len(sys.argv) > 4 else "")
    elif sys.argv[1] == "milestone":
        log_milestone(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    elif sys.argv[1] == "stats":
        show_stats()
    else:
        print("Usage:")
        print("  audit-log.py                    # Show recent")
        print("  audit-log.py decision 'action' 'why' ['result']")
        print("  audit-log.py action 'what' 'why' ['result']")
        print("  audit-log.py milestone 'what' 'result'")
        print("  audit-log.py stats              # Show statistics")
