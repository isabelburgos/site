"""
MkDocs hooks for content processing.

- Fix image paths (relative → absolute)
- Process literature note citations
"""

import re
from pathlib import Path


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}
    match = re.search(r'\n---\s*\n', content[3:])
    if not match:
        return {}

    result = {}
    for line in content[3:match.start() + 3].split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            v = v.strip().strip('"\'')
            result[k.strip()] = v
    return result


def format_author_aps(authors: list[str]) -> str:
    """Format author list in APS style: F. Last, G. Last, and H. Last"""
    if not authors:
        return "Unknown Author"

    formatted = []
    for author in authors:
        # Authors are stored as "Last, First" or just a name
        author = author.strip().strip(',').strip()
        if not author:
            continue

        if ',' in author:
            # "Last, First" format
            parts = author.split(',', 1)
            last = parts[0].strip()
            first = parts[1].strip()
            # Use first initial
            initial = first[0] + '.' if first else ''
            formatted.append(f"{initial} {last}" if initial else last)
        else:
            # Single name, use as-is
            formatted.append(author)

    if not formatted:
        return "Unknown Author"

    if len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    else:
        # Oxford comma for 3+
        return ", ".join(formatted[:-1]) + f", and {formatted[-1]}"


def format_citation_aps(metadata: dict) -> str:
    """
    Format a citation in American Physical Society (APS) style.

    Format: A. Author, B. Coauthor, and C. Third, Article Title, Journal Vol, Page (Year).
    """
    # Parse author field (can be a string representation of a list)
    author_str = metadata.get('author', '[]')
    # Extract authors from string like '["Author 1", "Author 2"]'
    authors = re.findall(r'"([^"]+)"', author_str)

    author_part = format_author_aps(authors)
    title = metadata.get('title', 'Untitled').strip('"')
    year = metadata.get('year', 'n.d.')
    journal = metadata.get('journal', '')
    doi = metadata.get('DOI', '')

    # Build citation
    citation = f"{author_part}, {title}"

    if journal:
        citation += f", {journal}"

    citation += f" ({year})"

    if doi:
        citation += f", DOI: [{doi}](https://doi.org/{doi})"

    citation += "."

    return citation


def process_citations(markdown: str, config) -> str:
    """
    Process literature note citations in markdown.

    Converts:
      [[@citekey]] → <sup><a href="#cite-1">[1]</a></sup>
      [[@citekey|text]] → text<sup><a href="#cite-1">[1]</a></sup>

    Appends a References section with back-links to citations.
    """
    # Find docs directory (vault root symlinked to Website/docs/)
    docs_path = Path(config['docs_dir'])
    vault_root = docs_path.parent.parent  # Website/docs/ → Website/ → vault root

    # Pattern for literature note links: [[@citekey]] or [[@citekey|display text]]
    # The roamlinks plugin converts [[@...]] to [[Literature Notes/@...]]
    # So we need to match both formats
    pattern = r'\[\[(?:Literature Notes/)?@([^\]|]+)(?:\|([^\]]+))?\]\]'

    citations = {}  # citekey → {number, citation_text, ref_count}
    citation_order = []  # Track order for numbering

    def replace_citation(match):
        citekey = match.group(1)
        display_text = match.group(2)  # None if bare link

        # Check if we've seen this citation before
        if citekey not in citations:
            # Read the literature note
            lit_note_path = vault_root / "Literature Notes" / f"@{citekey}.md"

            if not lit_note_path.exists():
                print(f"  [warning] Literature note not found: @{citekey}")
                return match.group(0)  # Return original if not found

            try:
                content = lit_note_path.read_text(encoding='utf-8')
                metadata = parse_frontmatter(content)

                # Check if it's actually a literature note
                if metadata.get('category') != 'literaturenote':
                    print(f"  [warning] Not a literature note: @{citekey}")
                    return match.group(0)

                # Check for required fields
                missing = []
                for field in ['author', 'title', 'year']:
                    if not metadata.get(field):
                        missing.append(field)

                if missing:
                    print(f"  [warning] Missing metadata in @{citekey}: {', '.join(missing)}")

                # Format citation
                citation_text = format_citation_aps(metadata)

                # Assign number
                citation_num = len(citation_order) + 1
                citations[citekey] = {
                    'number': citation_num,
                    'citation': citation_text,
                    'ref_count': 0  # Track how many times this citation appears
                }
                citation_order.append(citekey)

            except Exception as e:
                print(f"  [error] Failed to process citation @{citekey}: {e}")
                return match.group(0)

        # Increment reference count for this citation
        citations[citekey]['ref_count'] += 1
        cite_num = citations[citekey]['number']
        ref_count = citations[citekey]['ref_count']

        # Create unique ID for this specific reference in the text
        cite_ref_id = f"cite-ref-{cite_num}-{ref_count}"
        cite_id = f"cite-{cite_num}"

        # Generate the replacement with link to footnote
        link = f'<a href="#{cite_id}">[{cite_num}]</a>'

        if display_text:
            # Keep the display text, add linked superscript
            return f'{display_text}<sup id="{cite_ref_id}">{link}</sup>'
        else:
            # Just the linked superscript reference
            return f'<sup id="{cite_ref_id}">{link}</sup>'

    # Process all citations in the markdown
    processed = re.sub(pattern, replace_citation, markdown)

    # If we found citations, append References section
    if citations:
        references = "\n\n---\n\n## References\n\n"
        for citekey in citation_order:
            num = citations[citekey]['number']
            text = citations[citekey]['citation']
            ref_count = citations[citekey]['ref_count']

            # Create back-links to all places this citation appears
            back_links = []
            for i in range(1, ref_count + 1):
                cite_ref_id = f"cite-ref-{num}-{i}"
                if ref_count > 1:
                    # Multiple citations: show "↩¹ ↩² ↩³"
                    back_links.append(f'<a href="#{cite_ref_id}">↩<sup>{i}</sup></a>')
                else:
                    # Single citation: just "↩"
                    back_links.append(f'<a href="#{cite_ref_id}">↩</a>')

            back_link_html = " ".join(back_links)

            references += f'<span id="cite-{num}">[{num}]</span> {text} {back_link_html}\n\n'

        processed += references

        print(f"  [citations] Processed {len(citations)} citation(s)")

    return processed


def on_page_markdown(markdown, page, config, files):
    """
    Process markdown content before rendering.

    1. Fix image paths (relative → absolute)
    2. Process literature note citations
    """
    # Fix image paths
    # Pattern matches: ![alt](Attachments/path/to/image.jpg)
    # Converts to:     ![alt](/Attachments/path/to/image.jpg)
    pattern = r'!\[([^\]]*)\]\(Attachments/'
    replacement = r'![\1](/Attachments/'
    markdown = re.sub(pattern, replacement, markdown)

    # Process citations
    markdown = process_citations(markdown, config)

    return markdown
