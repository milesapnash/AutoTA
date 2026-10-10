#!/bin/bash

# Builds the report PDF (main.pdf) from the LaTeX source in this directory.
# Requires latexmk with biber, Pygments (for minted) and Inkscape (for svg).

# Ensure the script stops on any error
set -e

error_exit() {
    echo "$1" 1>&2
    exit 1
}

command -v latexmk &>/dev/null || error_exit "latexmk is not installed or not added to PATH."
command -v pygmentize &>/dev/null || error_exit "Pygments is not installed (pip install pygments)."
command -v inkscape &>/dev/null || error_exit "Inkscape is not installed or not added to PATH."

# Run from the directory containing this script, whatever the caller's directory
cd "$(dirname "$0")"

# -shell-escape is required by the minted and svg packages
latexmk -pdf -shell-escape -interaction=nonstopmode main.tex || error_exit "Failed to build the report."

echo "Report built: $(pwd)/main.pdf"
