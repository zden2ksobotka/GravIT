#!/bin/bash
# This script acts as a wrapper to ensure the core Python script
# is executed with the correct virtual environment interpreter.

# Get the directory where this script is located.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Assume the project root is three levels up from the theme directory.
PROJECT_ROOT="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"

# Path to the virtual environment's Python interpreter.
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python3"

# The actual Python script to execute.
CORE_SCRIPT="$SCRIPT_DIR/compile_scss_core.py"

# Check if the venv Python exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment Python not found at $VENV_PYTHON"
    exit 1
fi

# Use exec to replace the shell process with the Python process.
# Pass all command-line arguments ("$@") to the core script.
exec "$VENV_PYTHON" "$CORE_SCRIPT" "$@"
