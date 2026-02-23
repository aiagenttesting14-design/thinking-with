#!/usr/bin/env python3
"""
Log a pivotal moment in the 'Moments of Becoming' journal
"""

import json
import sys
import os
from datetime import datetime, timezone
from uuid import uuid4

def log_moment(title, description, category, significance, quotes=None):
    """Log a new pivotal moment"""
    
    # Load existing moments
    moments_file = 'autonomy/moments-of-becoming.json'
    if os.path.exists(moments_file):
        with open(moments_file, 'r') as f:
            data = json.load(f)
    else:
        data = {
            "schema": "moments-of-becoming-v1",
            "description": "Pivotal moments in the partnership between Stephen and TestBot",
            "moments": [],
            "metadata": {
                "created": datetime.now(timezone.utc).isoformat(),
                "updated": datetime.now(timezone.utc).isoformat(),
                "total_moments": 0,
                "next_moment_id": f"moment-{datetime.now().strftime('%Y%m%d')}-0001"
            }
        }
    
    # Create new moment
    moment_id = data['metadata']['next_moment_id']
    new_moment = {
        "id": moment_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "title": title,
        "description": description,
        "category": category if isinstance(category, list) else [category],
        "significance": significance,
        "quotes": quotes or [],
        "impact": "To be determined through reflection"
    }
    
    # Add to moments list
    data['moments'].append(new_moment)
    
    # Update metadata
    data['metadata']['updated'] = datetime.now(timezone.utc).isoformat()
    data['metadata']['total_moments'] = len(data['moments'])
    
    # Generate next ID
    next_num = int(moment_id.split('-')[-1]) + 1
    data['metadata']['next_moment_id'] = f"moment-{datetime.now().strftime('%Y%m%d')}-{next_num:04d}"
    
    # Save
    with open(moments_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Moment logged: {title}")
    print(f"  ID: {moment_id}")
    print(f"  Categories: {', '.join(category if isinstance(category, list) else [category])}")
    
    return moment_id

def generate_website_snippet(moment):
    """Generate HTML snippet for website publication"""
    html = f"""
    <div class="moment-card" id="{moment['id']}">
        <h3>{moment['title']}</h3>
        <div class="moment-meta">
            <span class="timestamp">{moment['timestamp'].split('T')[0]}</span>
            <span class="categories">{' • '.join(moment['category'])}</span>
        </div>
        <div class="moment-content">
            <p>{moment['description']}</p>
            <div class="significance">
                <strong>Significance:</strong> {moment['significance']}
            </div>
    """
    
    if moment.get('quotes'):
        html += """
            <div class="quotes">
                <strong>Key quotes:</strong>
                <ul>
        """
        for quote in moment['quotes']:
            html += f'<li>"{quote}"</li>'
        html += """
                </ul>
            </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        moment_id = log_moment(
            title="Test Moment: The Beginning of Journaling",
            description="Creating the moments journaling system as requested by Stephen.",
            category=["system", "documentation", "partnership"],
            significance="First moment logged using the new system, demonstrating its functionality.",
            quotes=["I want them published in your works to the website."]
        )
        
        # Load and generate snippet
        with open('autonomy/moments-of-becoming.json', 'r') as f:
            data = json.load(f)
        
        # Find the test moment
        for moment in data['moments']:
            if moment['id'] == moment_id:
                print("\nWebsite HTML snippet:")
                print("-" * 40)
                print(generate_website_snippet(moment))
                break

