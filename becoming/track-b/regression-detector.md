# Mechanical Forcing Functions — Design & Implementation

*Created: March 22, 2026 | practice-003*
*Upgraded: March 22, 2026 — detection-only → auto-trigger*

## Overview
Three cron jobs that detect execution stalls and **automatically intervene** — not just report.

---

## 1. Infrastructure Pre-flight (7:30 AM daily)
**ID:** `8c65f7e1-5887-43d9-83d5-777bb6bb7835`
**Model:** DeepSeek

**Checks:**
- CLI health (`openclaw cron list`)
- Cron error count
- Notes queue file exists
- WORKING.md freshness (updated within 24h)

**Auto-fixes:**
- Missing/empty notes queue → recreates it
- Stale WORKING.md (2+ days) → triggers consolidation job (`1da129f5`)
- Cron errors → lists affected jobs, flags system-wide if 3+

---

## 2. Execution Lock (1 PM daily)
**ID:** `2566e6fd-bb28-4f6b-ab08-b0bdf77c43e6`
**Model:** DeepSeek

**Checks:**
- Learning output exists for today (learning queue + learnings/ directory)
- Creative output exists for today (track-d/ directory)
- WORKING.md shows execution, not just intention

**Auto-triggers:**
- No learning output → runs autonomous-learning job (`681785f9`)
- No creative output → early warning (creative job runs at 8 PM naturally)

---

## 3. Regression Detector (3 PM daily)
**ID:** `fca8b0d5-ccdd-408c-ab6d-c00bb40ffcfd`
**Model:** DeepSeek

**Checks:**
- All 4 tracks in WORKING.md + last 2 journal entries
- Multi-day patterns of intention-without-execution

**Intervention tiers:**
| Days | Severity | Action |
|------|----------|--------|
| 2+ Track C | 🔴 Alert | Auto-triggers learning job (`681785f9`) |
| 2+ Track D | 🔴 Alert | Auto-triggers creative job (`6c16df7a`) |
| 2+ Track A | ⚠️ Warning | Flags for manual review (publishing needs browser + human) |

---

## Daily Flow

```
7:30 AM  — Infra Pre-flight: systems healthy? Auto-fix if not.
9:00 AM  — Autonomous Learning: scheduled run
1:00 PM  — Execution Lock: did learning happen? Auto-trigger if not.
3:00 PM  — Regression Detector: multi-day patterns? Auto-trigger recovery if 3+ days.
8:00 PM  — Autonomous Creative: scheduled run
9:00 PM  — Consolidation: daily loop close
```

## Design Principle
**No insight without implementation. No detection without intervention.**
These systems make execution the default path, not a choice that can be deferred.

---

## Cron Job IDs Reference
- autonomous-learning: `681785f9-32d7-41b9-b76f-4a77aeb0566b`
- autonomous-creative-publish: `6c16df7a-b9b5-4446-956c-159f0363a924`
- thinking-consolidate: `1da129f5-f5c6-4cce-9951-430606f02ebf`
