# Scripts Directory

Automation scripts for TestBot's memory and workflow management.

---

## memory-consolidate.py

**Purpose**: Automatically extract significant events from daily notes and update MEMORY.md.

**What it does**:
1. Scans `memory/YYYY-MM-DD.md` files from the last 7 days
2. Extracts significant sections:
   - Completed tasks (markers: COMPLETE, RESOLVED, SUCCESS)
   - Key decisions
   - Important discoveries
   - Mission outcomes
3. Updates MEMORY.md with "Recent History (Auto-Generated)" section
4. Keeps entries concise (~2 lines per event)

**Usage**:
```bash
# Run consolidation (updates MEMORY.md)
python3 scripts/memory-consolidate.py

# Preview without writing
python3 scripts/memory-consolidate.py --dry-run

# Consolidate last 3 days only
python3 scripts/memory-consolidate.py --days 3
```

**When to run**:
- End of each day/session (manual)
- Every 6 hours via cron (automated)
- Before context compaction (advanced)

**Example cron job**:
```bash
openclaw cron add \
  --name memory_consolidation \
  --schedule "0 */6 * * *" \
  --task "cd ~/.openclaw/workspace && python3 scripts/memory-consolidate.py"
```

**Requirements**:
- Python 3
- Daily notes in `memory/YYYY-MM-DD.md` format
- Standard library only (no external dependencies)

**Created**: 2026-02-18 by TestBot  
**Status**: Tested and working

---

## Future Scripts

Add more automation scripts here as they're built:
- Context monitoring (alert when approaching compaction threshold)
- Memory search indexing
- Session archival
- Backup automation
