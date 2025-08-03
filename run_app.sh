#!/bin/bash

# Activate the UV environment (don't source the setup script)
source .venv/bin/activate

# Install pyaudioop if needed
uv pip install pyaudioop

# Run the application
python bot.py