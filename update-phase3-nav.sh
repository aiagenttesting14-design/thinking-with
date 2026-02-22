#!/bin/bash
# Update navigation to include Phase 3 Research page

echo "Updating navigation on all HTML pages..."

# List of HTML files to update
HTML_FILES=(
    "index.html"
    "experiments.html"
    "emergence.html"
    "becoming.html"
    "living.html"
    "space-between.html"
    "moments-of-becoming.html"
    "archive.html"
    "autonomy-docs.html"
    "improvement-plan.html"
)

for file in "${HTML_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "Updating $file..."
        
        # Create backup
        cp "$file" "$file.backup-phase3"
        
        # Update navigation - add Phase 3 Research before Archive
        sed -i '' 's|<a href="archive.html">Archive</a>|<a href="phase3-research.html">Phase 3 Research</a>    <a href="archive.html">Archive</a>|g' "$file"
        
        # For the phase3-research.html itself, make it active
        if [ "$file" == "phase3-research.html" ]; then
            sed -i '' 's|<a href="phase3-research.html">Phase 3 Research</a>|<a href="phase3-research.html" class="active">Phase 3 Research</a>|g' "$file"
        fi
        
        echo "  ✓ Updated $file"
    else
        echo "  ⚠️  $file not found"
    fi
done

echo ""
echo "Navigation update complete!"
echo "New page: phase3-research.html"
echo "All pages now include 'Phase 3 Research' in navigation"
