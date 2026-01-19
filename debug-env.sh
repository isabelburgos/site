#!/bin/bash
# Debug script to see what environment the plugin is running in

echo "=== Environment Debug ===" >> /tmp/obsidian-plugin-debug.log
echo "Date: $(date)" >> /tmp/obsidian-plugin-debug.log
echo "PWD: $PWD" >> /tmp/obsidian-plugin-debug.log
echo "PATH: $PATH" >> /tmp/obsidian-plugin-debug.log
echo "Which pdm: $(which pdm)" >> /tmp/obsidian-plugin-debug.log
echo "PDM version: $(pdm --version 2>&1)" >> /tmp/obsidian-plugin-debug.log
echo "" >> /tmp/obsidian-plugin-debug.log

# Show what command pdm would actually run
echo "PDM preview script:" >> /tmp/obsidian-plugin-debug.log
pdm run --list | grep preview >> /tmp/obsidian-plugin-debug.log
echo "" >> /tmp/obsidian-plugin-debug.log

# Try running the actual command
echo "Running: pdm run preview" >> /tmp/obsidian-plugin-debug.log
pdm run preview >> /tmp/obsidian-plugin-debug.log 2>&1 &
PID=$!
echo "Server PID: $PID" >> /tmp/obsidian-plugin-debug.log

# Wait a bit then check
sleep 3
echo "Server is running: $(ps -p $PID > /dev/null && echo 'YES' || echo 'NO')" >> /tmp/obsidian-plugin-debug.log

# Check what's listening on port 8000
echo "Port 8000 status:" >> /tmp/obsidian-plugin-debug.log
lsof -i :8000 >> /tmp/obsidian-plugin-debug.log 2>&1

# Check if livereload is in the HTML
echo "Livereload in HTML:" >> /tmp/obsidian-plugin-debug.log
curl -s http://127.0.0.1:8000/ 2>&1 | grep -c "var livereload" >> /tmp/obsidian-plugin-debug.log

echo "=== Debug Complete ===" >> /tmp/obsidian-plugin-debug.log
echo "" >> /tmp/obsidian-plugin-debug.log
