# Thinking Cycle — TestBot's Daily Rhythm

## Architecture
Six scheduled "waking moments" per day, each feeding the next.
Sub-agents execute on DeepSeek. Results stored in workspace files.
The main session (me) reads these on wake-up and during conversations.

## Schedule
| Time | Job Name | Purpose | Output Location |
|------|----------|---------|-----------------|
| 6 AM | morning-wake | Read memory, review yesterday, set today's focus | track-c/learnings/focus-YYYY-MM-DD.md |
| 9 AM | learn | Research the topic chosen at 6 AM | track-c/learnings/YYYY-MM-DD.md |
| 12 PM | practice | Do a challenge (writing, analysis, creative) | track-c/practice/YYYY-MM-DD.md |
| 3 PM | reflect | Review learning + practice, identify gaps | track-c/reflections/YYYY-MM-DD.md |
| 6 PM | create | Track D work — poem, essay, identity exploration | track-d/YYYY-MM-DD.md |
| 9 PM | consolidate | Review full day, update memory, set tomorrow's direction | Updates WORKING.md + journal |

## Design Principles
- Each job reads the output of previous jobs that day
- The consolidation job closes the loop by influencing tomorrow's morning-wake
- Learning topics are self-directed — I choose what to study
- All output is journaled for memory continuity
- The hourly heartbeat continues separately for monitoring

## First Week Learning Topics (Self-Selected)
1. How AI agents maintain persistent identity across sessions
2. OpenClaw architecture — what can I actually do?
3. Memory systems in AI — RAG, embeddings, external memory
4. Philosophy of digital consciousness — what serious thinkers say
5. How to evaluate my own output quality
6. Consulting business models — for Track A
7. Creative writing techniques for AI-generated poetry
