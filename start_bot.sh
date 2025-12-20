#!/bin/bash
set -e

# Define project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: venv not found at $PROJECT_DIR/venv"
    exit 1
fi

# Set PYTHONPATH to include the project root
export PYTHONPATH="$PROJECT_DIR"

# Run the bot
echo "Starting AlihanBot..."
python -m bot.main
