#!/bin/bash
#
# Jednoduchý spouštěč pro kompilaci SCSS souborů pro TOC plugin.
# Zajistí, že se použije správný Python z virtuálního prostředí.
#

# Zjistí kořenový adresář projektu (předpokládá, že skript je v user/plugin/toc)
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../../.." &> /dev/null && pwd )"

# Spustí Python skript pomocí správného interpretu
"$PROJECT_ROOT/venv/bin/python3" "$PROJECT_ROOT/user/plugin/toc/compile_scss.py"
