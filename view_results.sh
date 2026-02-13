#!/bin/bash

# Wrapper script to view results with correct Python environment

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment and run
source venv/bin/activate
python3 view_results.py
