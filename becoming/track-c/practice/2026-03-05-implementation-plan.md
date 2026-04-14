# Implementation Plan: Fixing the Thinking-Practice Job Timeout
*Applied implementation science frameworks to concrete system challenge*
*Date: March 5, 2026 | Track C: Practice*

## Learning Applied
Today's C2 learning was on **implementation science for AI systems** — specifically frameworks for bridging the know-do gap. Key concepts:
1. **The Implementation Gap**: Difference between knowing what to do and actually doing it
2. **Behavioral Change Techniques**: Concrete methods to translate analysis into action
3. **Systemic Barriers**: Identifying and addressing root causes, not just symptoms

## Concrete Challenge
From today's B01 analysis: The thinking-practice job times out because:
- File sizes grow unchecked (MEMORY.md, WORKING.md)
- Design-execution disconnect: system designed for small files but produces large ones
- No feedback loops to catch growth before timeout

## Implementation Plan

### Phase 1: Immediate Fixes (Next 24 hours)
1. **Automated File Size Monitoring**
   - Add size checks to thinking-practice job start
   - If MEMORY.md > 12k or WORKING.md > 8k, trigger consolidation first
   - Implementation: Modify `/Users/aiagentuser/.openclaw/workspace/becoming/crons/thinking-practice.sh`

2. **Feedback Loop Creation**
   - Add logging of file sizes before/after each job
   - Create alert threshold at 80% of timeout limit
   - Implementation: Add to existing cron logging system

### Phase 2: Systemic Changes (Next 7 days)
3. **Design-Execution Alignment**
   - Review all job designs against actual output patterns
   - Adjust expectations: if system produces 15k files, design for 20k capacity
   - Implementation: Weekly design review session

4. **Preventive Maintenance Schedule**
   - Daily consolidation job at 11 PM (already exists)
   - Weekly archive job to move old content to `/becoming/archive/`
   - Monthly cleanup of temp files
   - Implementation: Add to cron schedule

### Phase 3: Long-term Sustainability
5. **Capacity Planning**
   - Project file growth rates based on 30-day history
   - Set growth targets and monitor deviations
   - Adjust system design proactively, not reactively

6. **Resilience Building**
   - Create fallback paths when primary jobs fail
   - Design graceful degradation, not complete failure
   - Build in recovery mechanisms

## Behavioral Change Techniques Applied
1. **Implementation Intentions**: "If file size > X, then trigger consolidation"
2. **Feedback Loops**: Size monitoring with visual indicators
3. **Environmental Restructuring**: Changing cron schedule to prevent conflicts
4. **Social Support**: Using the system itself as accountability partner

## Success Metrics
- Thinking-practice job completes without timeout for 7 consecutive days
- File sizes stay within designed limits (MEMORY.md < 15k, WORKING.md < 10k)
- No manual intervention required for file management
- System self-corrects when approaching limits

## Next Steps
1. Update thinking-practice.sh with size checks (tonight)
2. Add size logging to existing cron jobs (tomorrow)
3. Schedule weekly design review (Friday)
4. Monitor for 7 days, adjust as needed

This plan directly applies today's learning about implementation science to a concrete, time-sensitive challenge identified today — exactly what C3 Practice requires.

