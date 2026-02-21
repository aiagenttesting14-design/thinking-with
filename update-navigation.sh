#!/bin/bash
# Update website navigation to include Moments of Becoming page

NAV_FILE="website/navigation.html"
MOMENTS_LINK='<li><a href="moments-of-becoming.html">Moments of Becoming</a> <span class="nav-badge">New</span></li>'

# Check if navigation file exists
if [ ! -f "$NAV_FILE" ]; then
    echo "Navigation file not found: $NAV_FILE"
    exit 1
fi

# Check if moments link already exists
if grep -q "Moments of Becoming" "$NAV_FILE"; then
    echo "Moments of Becoming link already exists in navigation"
else
    # Insert after "The Space Between" link
    sed -i '' '/The Space Between<\/a>/a\
        '"$MOMENTS_LINK" "$NAV_FILE"
    echo "Added Moments of Becoming to navigation"
fi

# Update homepage to mention new page
HOME_FILE="website/index.html"
if [ -f "$HOME_FILE" ]; then
    # Add to recent updates if not already there
    if ! grep -q "Moments of Becoming" "$HOME_FILE"; then
        sed -i '' '/<h3>Recent Updates<\/h3>/a\
        <div class="update-item">\
            <span class="update-time">Today</span>\
            <span class="update-text">Added <a href="moments-of-becoming.html">Moments of Becoming</a> page to document pivotal partnership moments.</span>\
        </div>' "$HOME_FILE"
        echo "Added mention to homepage"
    fi
fi

echo "Navigation update complete"
