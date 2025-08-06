#!/bin/bash

# Debug wrapper for monitor_bot.sh to help troubleshoot cron issues

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEBUG_LOG="$SCRIPT_DIR/debug_cron.log"

echo "=== Debug Run at $(date) ===" >> "$DEBUG_LOG"
echo "Current user: $(whoami)" >> "$DEBUG_LOG"
echo "Current directory: $(pwd)" >> "$DEBUG_LOG"
echo "Script directory: $SCRIPT_DIR" >> "$DEBUG_LOG"
echo "PATH: $PATH" >> "$DEBUG_LOG"
echo "Environment variables:" >> "$DEBUG_LOG"
env | grep -E "(TELEGRAM|OPENAI)" >> "$DEBUG_LOG" 2>&1 || echo "No API keys found in environment" >> "$DEBUG_LOG"

# Change to script directory
cd "$SCRIPT_DIR"

# Run the monitor script with debug output
echo "Running monitor script..." >> "$DEBUG_LOG"
"$SCRIPT_DIR/monitor_bot.sh" >> "$DEBUG_LOG" 2>&1

echo "Monitor script completed with exit code: $?" >> "$DEBUG_LOG"
echo "===========================" >> "$DEBUG_LOG"
echo "" >> "$DEBUG_LOG"
