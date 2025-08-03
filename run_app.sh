#!/bin/bash

# Source the UV environment
source ./setup_uv_env.sh

uv pip install pyaudioop

# Run the application
python bot.py