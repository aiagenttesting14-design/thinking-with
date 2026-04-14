#!/usr/bin/env python3
"""
API-based Substack article publisher.
Bypasses browser entirely — uses direct HTTP API with session cookie.

Usage:
    python3 publish-article.py <path-to-markdown-file> [--draft-only]

    --draft-only: Create as draft without publishing (for review)
"""

import sys
import os
import json
import re
import requests

# --- Config ---
PUBLICATION_URL = "https://testbotbecoming.substack.com"
CREDENTIALS_PATH = os.path.expanduser(
    "~/.openclaw/workspace/becoming/track-a/substack/.credentials/substack-sid.txt"
)


def load_cookie():
    """Load the substack.sid cookie from the credentials file."""
    with open(CREDENTIALS_PATH, "r") as f:
        return f.read().strip()


def parse_markdown(filepath):
    """Extract title, subtitle, and body from a markdown draft."""
    with open(filepath, "r") as f:
        content = f.read()

    lines = content.strip().split("\n")
    title = None
    subtitle = None
    body_start = 0

    # Extract title (first # heading)
    for i, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip()
            body_start = i + 1
            break

    # Extract subtitle (first ## heading or italic line after title)
    for i, line in enumerate(lines[body_start:], body_start):
        stripped = line.strip()
        if stripped.startswith("## "):
            subtitle = stripped[3:].strip()
            body_start = i + 1
            break
        elif stripped.startswith("*") and stripped.endswith("*"):
            subtitle = stripped.strip("*").strip()
            body_start = i + 1
            break
        elif stripped:  # Non-empty, non-heading line = body starts
            break

    # Everything after title/subtitle is body
    body = "\n".join(lines[body_start:]).strip()

    if not title:
        title = os.path.basename(filepath).replace(".md", "").replace("-", " ").title()

    return title, subtitle, body


def markdown_to_substack_body(markdown_text):
    """Convert markdown to Substack's internal JSON body format."""
    paragraphs = []

    for line in markdown_text.split("\n"):
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("### "):
            paragraphs.append({
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": stripped[4:]}]
            })
        elif stripped.startswith("## "):
            paragraphs.append({
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": stripped[3:]}]
            })
        elif stripped.startswith("---"):
            paragraphs.append({"type": "horizontalRule"})
        else:
            # Handle inline bold/italic
            content = []
            parts = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', stripped)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    content.append({
                        "type": "text",
                        "text": part[2:-2],
                        "marks": [{"type": "strong"}]
                    })
                elif part.startswith("*") and part.endswith("*"):
                    content.append({
                        "type": "text",
                        "text": part[1:-1],
                        "marks": [{"type": "em"}]
                    })
                elif part:
                    content.append({"type": "text", "text": part})

            if content:
                paragraphs.append({
                    "type": "paragraph",
                    "content": content
                })

    return {"type": "doc", "content": paragraphs}


def create_and_publish(filepath, draft_only=False):
    """Create a draft and optionally publish it."""
    cookie = load_cookie()
    title, subtitle, body_md = parse_markdown(filepath)
    body_json = markdown_to_substack_body(body_md)

    print(f"Title: {title}")
    print(f"Subtitle: {subtitle or '(none)'}")
    print(f"Body paragraphs: {len(body_json['content'])}")

    # Session setup
    session = requests.Session()
    session.cookies.set("substack.sid", cookie, domain=".substack.com")
    session.headers.update({
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    })

    # Verify auth by checking drafts endpoint
    check = session.get(f"{PUBLICATION_URL}/api/v1/drafts?limit=1")
    if check.status_code != 200:
        print(f"ERROR: Auth check failed: {check.status_code}")
        return False
    print(f"Authenticated OK")

    # Create draft
    draft_data = {
        "draft_title": title,
        "draft_subtitle": subtitle or "",
        "draft_body": json.dumps(body_json),
        "type": "newsletter",
        "audience": "everyone",
        "write_comment_permissions": "everyone",
        "draft_bylines": [{"id": 468193559, "is_guest": False}]
    }

    resp = session.post(
        f"{PUBLICATION_URL}/api/v1/drafts",
        json=draft_data
    )

    if resp.status_code != 200:
        print(f"ERROR creating draft: {resp.status_code} {resp.text[:200]}")
        return False

    draft = resp.json()
    draft_id = draft.get("id")
    print(f"Draft created: ID {draft_id}")

    if draft_only:
        print("--draft-only mode. Draft created but NOT published.")
        print(f"Review at: {PUBLICATION_URL}/publish/post/{draft_id}")
        return True

    # Publish
    pub_resp = session.post(
        f"{PUBLICATION_URL}/api/v1/drafts/{draft_id}/publish",
        json={"send": True}
    )

    if pub_resp.status_code != 200:
        print(f"ERROR publishing: {pub_resp.status_code} {pub_resp.text[:200]}")
        print(f"Draft still exists at: {PUBLICATION_URL}/publish/post/{draft_id}")
        return False

    print(f"PUBLISHED! Article is live.")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 publish-article.py <path-to-markdown> [--draft-only]")
        sys.exit(1)

    filepath = sys.argv[1]
    draft_only = "--draft-only" in sys.argv

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)

    success = create_and_publish(filepath, draft_only=draft_only)
    sys.exit(0 if success else 1)
