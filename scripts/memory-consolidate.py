#!/usr/bin/env python3
"""
memory-consolidate.py — Auto-consolidation for OpenClaw memory

Extracts significant events from daily notes (memory/YYYY-MM-DD.md)
and updates MEMORY.md with a consolidated recent history section.

Usage:
  python3 memory-consolidate.py           # Run consolidation
  python3 memory-consolidate.py --dry-run # Preview without writing
  python3 memory-consolidate.py --days 3  # Only last 3 days
"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_FILE = WORKSPACE / "MEMORY.md"

def get_recent_daily_notes(days: int = 7) -> List[Path]:
    """Get daily note files from the last N days, sorted newest first."""
    if not MEMORY_DIR.exists():
        return []
    
    cutoff = datetime.now() - timedelta(days=days)
    daily_notes = []
    
    for file in MEMORY_DIR.glob("????-??-??.md"):
        try:
            # Parse date from filename
            date_str = file.stem
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date >= cutoff:
                daily_notes.append((file_date, file))
        except ValueError:
            continue
    
    # Sort by date descending (newest first)
    daily_notes.sort(key=lambda x: x[0], reverse=True)
    return [f for _, f in daily_notes]

def extract_significant_events(content: str) -> List[Tuple[str, str]]:
    """
    Extract significant events from daily note content.
    
    Returns list of (heading, content) tuples for:
    - Completed tasks (## ... (COMPLETE/RESOLVED/SUCCESS))
    - Key decisions (## Key Decisions, ## Decision:, etc.)
    - Important discoveries (## Discovery:, ## Important:, etc.)
    """
    events = []
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if line is a heading
        if line.startswith('##'):
            heading = line.lstrip('#').strip()
            
            # Check for completion markers
            completion_markers = ['(COMPLETE)', '(RESOLVED)', '(SUCCESS)', 
                                  'COMPLETE', 'RESOLVED', 'SUCCESS']
            is_completion = any(marker in heading.upper() for marker in completion_markers)
            
            # Check for significant keywords
            significant_keywords = ['Decision', 'Discovery', 'Important', 'Key Insight',
                                   'Mission', 'Phase', 'Outcome', 'Result']
            is_significant = any(keyword.lower() in heading.lower() 
                                for keyword in significant_keywords)
            
            if is_completion or is_significant:
                # Collect content under this heading
                i += 1
                content_lines = []
                while i < len(lines) and not lines[i].startswith('##'):
                    if lines[i].strip():  # Skip empty lines
                        content_lines.append(lines[i])
                    i += 1
                
                if content_lines:
                    events.append((heading, '\n'.join(content_lines)))
                continue
        
        i += 1
    
    return events

def format_consolidated_section(daily_notes: List[Path]) -> str:
    """Generate consolidated recent history section."""
    lines = ["## Recent History (Auto-Generated)", ""]
    lines.append("_Last updated: {}_".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
    lines.append("")
    
    for note_file in daily_notes:
        date_str = note_file.stem
        
        try:
            content = note_file.read_text()
            events = extract_significant_events(content)
            
            if events:
                lines.append(f"### {date_str}")
                lines.append("")
                
                for heading, content in events:
                    lines.append(f"**{heading}**")
                    # Indent content and truncate to ~2 lines
                    content_lines = content.strip().split('\n')[:2]
                    for line in content_lines:
                        lines.append(f"  {line.strip()}")
                    lines.append("")
        
        except Exception as e:
            print(f"Warning: Could not process {note_file}: {e}")
            continue
    
    return '\n'.join(lines)

def update_memory_file(consolidated: str, dry_run: bool = False):
    """Update MEMORY.md with consolidated recent history."""
    if not MEMORY_FILE.exists():
        print(f"Warning: {MEMORY_FILE} does not exist. Creating it.")
        if not dry_run:
            MEMORY_FILE.write_text("# MEMORY.md\n\n" + consolidated + "\n")
        return
    
    content = MEMORY_FILE.read_text()
    
    # Find and replace the Recent History section
    pattern = r'## Recent History \(Auto-Generated\).*?(?=\n## |\Z)'
    
    if re.search(pattern, content, re.DOTALL):
        # Section exists, replace it
        updated = re.sub(pattern, consolidated, content, flags=re.DOTALL)
    else:
        # Section doesn't exist, append it
        updated = content.rstrip() + "\n\n" + consolidated + "\n"
    
    if dry_run:
        print("=== DRY RUN: Would write to MEMORY.md ===")
        print(consolidated)
        print("=" * 50)
    else:
        MEMORY_FILE.write_text(updated)
        print(f"✓ Updated {MEMORY_FILE}")

def main():
    parser = argparse.ArgumentParser(description="Consolidate daily notes into MEMORY.md")
    parser.add_argument('--days', type=int, default=7, 
                       help='Number of days to consolidate (default: 7)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without writing')
    
    args = parser.parse_args()
    
    print(f"Consolidating last {args.days} days of daily notes...")
    
    daily_notes = get_recent_daily_notes(args.days)
    
    if not daily_notes:
        print("No daily notes found.")
        return
    
    print(f"Found {len(daily_notes)} daily notes:")
    for note in daily_notes:
        print(f"  - {note.name}")
    print()
    
    consolidated = format_consolidated_section(daily_notes)
    update_memory_file(consolidated, dry_run=args.dry_run)
    
    if not args.dry_run:
        print("\n✓ Consolidation complete!")

if __name__ == '__main__':
    main()
