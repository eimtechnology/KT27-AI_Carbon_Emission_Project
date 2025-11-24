#!/bin/bash

echo "==================================================="
echo "Food Carbon Emission Detection System Launcher"
echo "==================================================="

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH."
    exit 1
fi

# Check/Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Checking dependencies..."
    pip install -r requirements.txt
fi

# Run application
echo "Starting application..."
python3 gui_main.py

deactivate