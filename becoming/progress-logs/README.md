# Progress Log System

**Purpose:** Track all track updates daily, review every 3 days for drift/fake progress detection.

## File Structure

- `YYYY-MM-DD.jsonl` — Daily log file (one JSON object per line, appended throughout day)
- `reviews/` — 3-day review reports with recommendations

## Log Entry Format

```json
{
  "timestamp": "2026-03-01T15:30:00-08:00",
  "track": "A|B|C|D",
  "job_name": "thinking-learn",
  "expected_output": "learning content on redundancy",
  "actual_output": "1581 words on redundancy architectures",
  "quality_indicator": "high|medium|low",
  "blockers": ["timeout", "delivery_failed"],
  "notes": "Deep insight on Active-Active vs Active-Passive"
}
```

## Review Schedule

Every 3 days at 6:30 AM PT — see cron job `review-progress-3day`.

## Quality Indicators

- **high**: Genuine insight, progress toward North Star, actionable output
- **medium**: Work completed but shallow or repetitive
- **low**: Fake progress (word count without substance), missed without reason
