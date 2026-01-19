#!/usr/bin/env python
"""Debug script to check why livereload isn't working"""

from mkdocs.commands.serve import serve
from mkdocs.config import load_config
import logging

# Set up logging to see everything
logging.basicConfig(level=logging.DEBUG)

# Load config
config = load_config('mkdocs.yml')

# Print config details
print(f"Config loaded successfully")
print(f"docs_dir: {config.docs_dir}")
print(f"watch config: {config.watch}")
print(f"theme dirs: {config.theme.dirs}")

# Try to start server with debug
print("\n=== Starting serve with livereload=True, watch_theme=True ===\n")
serve(
    config_file='mkdocs.yml',
    livereload=True,  # Explicitly enable
    watch_theme=True,
)
