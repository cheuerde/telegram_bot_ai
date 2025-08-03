#!/bin/bash

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Remove existing venv if it exists
if [ -d ".venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf .venv
fi

# Create new virtual environment with Python 3.11
echo "Creating virtual environment with Python 3.11..."
uv venv --python=python3.11

# Activate the virtual environment
source .venv/bin/activate

# Make sure we don't have conflicting telegram packages
echo "Removing any conflicting telegram packages..."
uv pip uninstall telegram -y || true

# Install dependencies from existing requirements.txt
echo "Installing dependencies from requirements.txt..."
uv pip install -r requirements.txt

echo "UV environment ready with Python 3.11!"