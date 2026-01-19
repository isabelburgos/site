"""
MkDocs hooks to fix image paths.

Converts relative Attachments/ paths to absolute /Attachments/ paths
so images work correctly regardless of page depth.
"""

import re

def on_page_markdown(markdown, page, config, files):
    """
    Convert Attachments/ image paths to /Attachments/ (absolute from site root).

    This ensures images work correctly at any page depth in the site.
    """
    # Pattern matches: ![alt](Attachments/path/to/image.jpg)
    # Converts to:     ![alt](/Attachments/path/to/image.jpg)
    pattern = r'!\[([^\]]*)\]\(Attachments/'
    replacement = r'![\1](/Attachments/'

    return re.sub(pattern, replacement, markdown)
