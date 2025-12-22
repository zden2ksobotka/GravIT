#!/bin/bash
# Skript pro kompilaci SCSS stylů pluginu 'blog'
# Spouští se z kořenového adresáře projektu, aby se správně našlo venv.

VENV_PATH="$(dirname "$(realpath "$0")")/../../../venv"

# Kontrola, zda existuje venv
if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Spuštění Python skriptu ve venv
"$VENV_PATH/bin/python3" "$(dirname "$0")"/compile_scss.py

if [ $? -eq 0 ]; then
    echo "Compilation finished successfully."
else
    echo "Compilation failed."
fi

