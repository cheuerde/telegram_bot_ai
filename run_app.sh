#!/bin/bash

# Simple script to run the bot (used by monitor)
# For manual control, use monitor_bot.sh instead

# Activate the UV environment
source .venv/bin/activate

# Run the application with proper logging
exec python bot.py