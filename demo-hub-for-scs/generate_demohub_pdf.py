#!/usr/bin/env python3
"""Generate PDF from demo-hub-considerations.md.

Bypasses the markdown parser for ordered lists because GitBook's
markdown format (indented items + inline <figure> tags) causes the
Python markdown parser to merge items and break numbering.

Instead, we manually build HTML for numbered sections.
"""
import os, sys, re, base64
from pathlib import Path

from playwright.sync_api import sync_playwright

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent  # repo root
MD_FILE = SCRIPT_DIR / "demo-hub-considerations.md"
OUTPUT_HTML = SCRIPT_DIR / "demo-hub-considerations.html"
OUTPUT_PDF = SCRIPT_DIR / "demo-hub-considerations.pdf"

sys.path.insert(0, str(BASE_DIR))
from generate_pdf_html import PRINT_CSS, HTML_FOOTER, embed_images_in_html

try:
    import markdown
except ImportError:
    print("ERROR: markdown not installed. Install with: pip3 install markdown")
    sys.exit(1)


def clean_gitbook_md(content):
    """Strip YAML frontmatter, <mark> tags, &#x20; artifacts."""
    # Remove frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    # Strip <mark> tags but keep inner text
    content = re.sub(r'<mark[^>]*>', '', content)
    content = content.replace('</mark>', '')
    # Strip GitBook zero-width space artifacts
    content = content.replace('&#x20;', '')
    # Unescape GitBook backslash-escaped ampersands (\& → &)
    content = content.replace('\\&', '&')
    return content


def gitbook_md_to_html(md_text):
    """Convert GitBook-flavored markdown to HTML, handling numbered lists properly.

    The key problem: GitBook markdown has numbered list items with
    leading indentation and <figure> tags between them. The Python
    markdown parser merges multiple items into single <li> elements
    and splits lists into multiple <ol> blocks.

    Solution: split the document by sections (## headings), then
    within each section, manually parse numbered items and their
    associated content (figures, sub-paragraphs) into proper
    <ol><li> HTML.
    """
    lines = md_text.split('\n')
    html_parts = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Heading
        heading_match = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if heading_match:
            level = len(heading_match.group(1))
            text = _inline_md(heading_match.group(2))
            html_parts.append(f'<h{level}>{text}</h{level}>')
            i += 1
            continue

        # Numbered list item (e.g. "1. ", "4.  ", with optional leading spaces)
        li_match = re.match(r'^\s*(\d+)\.\s+(.*)', stripped)
        if li_match:
            # Start collecting all consecutive list items in this section
            ol_html, i = _parse_ordered_list(lines, i)
            html_parts.append(ol_html)
            continue

        # Regular paragraph / HTML block
        if stripped:
            # Collect non-empty, non-heading, non-list lines as a paragraph block
            block_lines = []
            while i < len(lines):
                s = lines[i].strip()
                if not s:
                    i += 1
                    break
                if re.match(r'^#{1,6}\s+', s):
                    break
                if re.match(r'^\s*\d+\.\s+', s):
                    break
                block_lines.append(s)
                i += 1

            block_text = '\n'.join(block_lines)
            # If it's already HTML (figure, img, etc.), pass through
            if block_text.startswith('<'):
                html_parts.append(block_text)
            else:
                html_parts.append(f'<p>{_inline_md(block_text)}</p>')
            continue

        # Blank line
        i += 1

    return '\n'.join(html_parts)


def _parse_ordered_list(lines, start_idx):
    """Parse a sequence of ordered list items starting at start_idx.
    Returns (html_string, next_index)."""
    items = []
    i = start_idx

    while i < len(lines):
        stripped = lines[i].strip()

        # Check if this is a numbered item
        li_match = re.match(r'^\s*(\d+)\.\s+(.*)', stripped)
        if li_match:
            # Start a new list item
            item_text = li_match.group(2)
            item_parts = [item_text]
            i += 1

            # Collect continuation lines (indented or figure blocks) for this item
            while i < len(lines):
                s = lines[i].strip()

                # Next numbered item at any indentation level = new item
                if re.match(r'^\s*\d+\.\s+', s):
                    break

                # Heading = end of list
                if re.match(r'^#{1,6}\s+', s):
                    break

                # Blank line - might separate items, peek ahead
                if not s:
                    # Check if next non-blank line is a list item or heading
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j >= len(lines):
                        i = j
                        break
                    next_s = lines[j].strip()
                    if re.match(r'^\s*\d+\.\s+', next_s) or re.match(r'^#{1,6}\s+', next_s):
                        i += 1
                        break
                    # Otherwise, blank line is part of this item's content
                    i += 1
                    continue

                # Figure or other HTML within item
                item_parts.append(s)
                i += 1

            items.append(item_parts)
            continue

        # If we hit a non-list, non-blank line that's not a continuation, stop
        if stripped and not re.match(r'^\s*\d+\.\s+', stripped):
            # Could be a figure between items at top level
            if stripped.startswith('<figure') or stripped.startswith('<img'):
                # Attach to previous item if exists
                if items:
                    items[-1].append(stripped)
                i += 1
                continue
            else:
                break

        if not stripped:
            i += 1
            continue

    # Build HTML
    ol_lines = ['<ol>']
    for item_parts in items:
        li_content = []
        for part in item_parts:
            part = part.strip()
            if part.startswith('<figure') or part.startswith('<img'):
                li_content.append(part)
            else:
                li_content.append(f'<p>{_inline_md(part)}</p>')
        ol_lines.append(f'<li>{"".join(li_content)}</li>')
    ol_lines.append('</ol>')

    return '\n'.join(ol_lines), i


def _inline_md(text):
    """Convert inline markdown (bold, italic, links, images) to HTML."""
    # Images with angle-bracket paths: ![alt](<path with spaces/parens>)
    text = re.sub(r'!\[([^\]]*)\]\(<([^>]+)>\)', r'<img alt="\1" src="\2">', text)
    # Images: ![alt](src)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img alt="\1" src="\2">', text)
    # Links with angle-bracket URLs: [text](<url>)
    text = re.sub(r'\[([^\]]+)\]\(<([^>]+)>\)', r'<a href="\2">\1</a>', text)
    # Links: [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Bold: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic: *text*
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code: `text`
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


# === Main ===
print(f"Processing: {MD_FILE.name}")

with open(MD_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

content = clean_gitbook_md(content)
html_content = gitbook_md_to_html(content)

# Embed images as base64
html_content = embed_images_in_html(html_content, BASE_DIR)
html_content = embed_images_in_html(html_content, SCRIPT_DIR)

# Override: suppress URL expansion after links in print (long query strings are ugly)
URL_OVERRIDE_CSS = '<style>@media print { a[href^="http"]:after { content: none !important; } }</style>'
full_html = PRINT_CSS + URL_OVERRIDE_CSS + html_content + HTML_FOOTER

with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"HTML generated: {OUTPUT_HTML.name}")
print("Converting to PDF...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(f"file://{OUTPUT_HTML.absolute()}")
    page.wait_for_timeout(2000)
    page.pdf(
        path=str(OUTPUT_PDF),
        format='A4',
        margin={'top': '2cm', 'right': '2cm', 'bottom': '2cm', 'left': '2cm'},
        print_background=True,
        display_header_footer=False,
    )
    browser.close()

pdf_size = OUTPUT_PDF.stat().st_size / (1024 * 1024)
print(f"\nPDF created: {OUTPUT_PDF}")
print(f"Size: {pdf_size:.1f} MB")
