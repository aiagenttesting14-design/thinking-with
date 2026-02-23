#!/usr/bin/env python3
import json
import os
from datetime import datetime, timedelta

# Restore state to consolidating
state_file = "autonomy/state.json"

with open(state_file, 'r') as f:
    state = json.load(f)

# Restore to consolidating state
state["current_state"] = "consolidating"
state["since"] = "2026-02-22T12:19:31.114902"
state["current_task"] = None
state["last_transition_reason"] = "Completed: Execute Phase 3 Week 1 market research tasks"

with open(state_file, 'w') as f:
    json.dump(state, f, indent=2)

print("State restored to consolidating")
